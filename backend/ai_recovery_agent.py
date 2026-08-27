def analyze_recovery(event, incident=None):
    """
    AI-inspired Recovery Agent.

    Analyzes:
    - Failure type
    - Transaction amount
    - Previous recovery attempts
    - Bank outage confidence

    Returns:
    - Recovery probability
    - Recommended action
    - AI reasoning
    - Risk level
    """

    error_code = event.get(
        "error_code",
        "UNKNOWN_ERROR"
    )

    amount = float(
        event.get("amount", 0)
    )

    attempts = int(
        event.get("recovery_attempts", 0)
    )

    outage_confidence = 0

    if incident:

        outage_confidence = float(
            incident.get(
                "confidence",
                0
            )
        )


    # ----------------------------------------
    # BASE RECOVERY PROBABILITY
    # ----------------------------------------

    recovery_probability = 50


    if error_code in [

        "NETWORK_ERROR",

        "UPI_TIMEOUT"

    ]:

        recovery_probability = 75


    elif error_code == "BANK_TIMEOUT":

        recovery_probability = 60


    elif error_code in [

        "INSUFFICIENT_FUNDS",

        "CARD_DECLINED"

    ]:

        recovery_probability = 35


    # ----------------------------------------
    # OUTAGE INTELLIGENCE
    # ----------------------------------------

    if outage_confidence >= 80:

        recovery_probability = 85


    elif outage_confidence >= 50:

        recovery_probability = max(
            recovery_probability,
            65
        )


    # ----------------------------------------
    # ATTEMPT PENALTY
    # ----------------------------------------

    recovery_probability -= (
        attempts * 15
    )


    recovery_probability = max(
        0,
        min(
            recovery_probability,
            100
        )
    )


    # ----------------------------------------
    # AI REASONING + RISK
    # ----------------------------------------

    if outage_confidence >= 80:

        action = "SWITCH_PAYMENT_ROUTE"

        reasoning = (
            "High-confidence bank outage detected. "
            "Retrying the same route may fail again, "
            "so an alternative payment route is recommended."
        )

        risk_level = "HIGH"


    elif attempts >= 3:

        action = "ESCALATE"

        reasoning = (
            "Maximum recovery attempts reached. "
            "Automatic recovery is stopped and "
            "manual review is required."
        )

        risk_level = "HIGH"


    elif error_code in [

        "NETWORK_ERROR",

        "UPI_TIMEOUT"

    ]:

        action = "RETRY_NOW"

        reasoning = (
            "The failure appears temporary. "
            "An immediate retry has a relatively "
            "high probability of recovery."
        )

        risk_level = "MEDIUM"


    elif error_code == "BANK_TIMEOUT":

        action = "RETRY_LATER"

        reasoning = (
            "The bank is not responding reliably. "
            "Waiting before another attempt may "
            "improve the recovery chance."
        )

        risk_level = "MEDIUM"


    elif error_code in [

        "INSUFFICIENT_FUNDS",

        "CARD_DECLINED"

    ]:

        action = "ASK_CUSTOMER_ALTERNATIVE_METHOD"

        reasoning = (
            "The current payment method is unlikely "
            "to succeed. An alternative method is recommended."
        )

        risk_level = "LOW"


    else:

        action = "RETRY_LATER"

        reasoning = (
            "The failure pattern is uncertain. "
            "A delayed retry is safer than repeated "
            "immediate attempts."
        )

        risk_level = "MEDIUM"


    return {

        "recovery_probability":
            round(
                recovery_probability,
                1
            ),

        "recommended_action":
            action,

        "reasoning":
            reasoning,

        "risk_level":
            risk_level,

        "outage_confidence":
            outage_confidence,

        "amount_at_risk":
            amount

    }