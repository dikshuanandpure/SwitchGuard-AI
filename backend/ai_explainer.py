def generate_ai_explanation(result, confidence, decision):
    """
    Generate an explainable assessment for the
    outage detection decision.
    """

    failure_rate = result["failure_rate"] * 100
    failed_transactions = result["failed_transactions"]
    dominant_error = result["dominant_error"]
    error_concentration = result["error_concentration"] * 100

    reasons = []

    # ----------------------------------------
    # FAILURE RATE ANALYSIS
    # ----------------------------------------

    if failure_rate >= 90:
        reasons.append(
            f"Very high failure rate detected: "
            f"{failure_rate:.1f}%"
        )

    elif failure_rate >= 70:
        reasons.append(
            f"High failure rate detected: "
            f"{failure_rate:.1f}%"
        )

    else:
        reasons.append(
            f"Failure rate is {failure_rate:.1f}%"
        )

    # ----------------------------------------
    # FAILURE VOLUME
    # ----------------------------------------

    reasons.append(
        f"{failed_transactions} failed transactions observed"
    )

    # ----------------------------------------
    # ERROR PATTERN
    # ----------------------------------------

    if dominant_error:

        reasons.append(
            f"Dominant error pattern: "
            f"{dominant_error}"
        )

    # ----------------------------------------
    # ERROR CONCENTRATION
    # ----------------------------------------

    if error_concentration >= 80:

        reasons.append(
            f"Highly consistent error pattern: "
            f"{error_concentration:.1f}% concentration"
        )

    elif error_concentration < 50:

        reasons.append(
            f"Failures have mixed causes: "
            f"{error_concentration:.1f}% concentration"
        )

    # ----------------------------------------
    # FINAL RECOMMENDATION
    # ----------------------------------------

    if decision == "HIGH_CONFIDENCE_OUTAGE":

        risk_level = "CRITICAL"

        recommendation = (
            "Switch the payment route immediately "
            "to reduce further transaction failures."
        )

    elif decision == "POSSIBLE_OUTAGE_MONITOR":

        risk_level = "HIGH"

        recommendation = (
            "Monitor the bank closely and delay "
            "automatic retries until more evidence "
            "is available."
        )

    elif decision == "MIXED_FAILURE_PATTERN":

        risk_level = "MEDIUM"

        recommendation = (
            "Do not classify this as a systemic outage. "
            "Investigate individual failure causes."
        )

    else:

        risk_level = "LOW"

        recommendation = (
            "Continue monitoring. There is currently "
            "insufficient evidence of a systemic outage."
        )

    return {
        "risk_level": risk_level,
        "confidence": confidence,
        "reasons": reasons,
        "recommendation": recommendation
    }