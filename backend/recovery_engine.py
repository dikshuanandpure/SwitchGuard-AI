from backend.ai_recovery_agent import analyze_recovery
def choose_recovery_action(event, incident=None):
    """
    AI-inspired recovery decision engine.

    Possible actions:
    - RETRY_NOW
    - RETRY_LATER
    - SWITCH_PAYMENT_ROUTE
    - ASK_CUSTOMER_ALTERNATIVE_METHOD
    - NO_ACTION
    """

    # ----------------------------------------
    # PAYMENT ALREADY SUCCESSFUL
    # ----------------------------------------

    if event.get("status") == "SUCCESS":

        return {
            "action": "NO_ACTION",
            "reason": "PAYMENT_ALREADY_SUCCESSFUL",
            "priority": "LOW"
        }


    # ----------------------------------------
    # GET ERROR CODE SAFELY
    # ----------------------------------------

    error_code = event.get(
        "error_code",
        "UNKNOWN_ERROR"
    )


    # ----------------------------------------
    # HIGH CONFIDENCE BANK OUTAGE
    # ----------------------------------------

    if incident is not None:

        decision = incident.get(
            "decision",
            ""
        )

        confidence = incident.get(
            "confidence",
            0
        )


        if decision == "HIGH_CONFIDENCE_OUTAGE":

            return {
                "action": "SWITCH_PAYMENT_ROUTE",
                "reason": "HIGH_CONFIDENCE_BANK_OUTAGE",
                "priority": "CRITICAL",
                "confidence": confidence
            }


        # ----------------------------------------
        # POSSIBLE BANK OUTAGE
        # ----------------------------------------

        if decision == "POSSIBLE_OUTAGE_MONITOR":

            return {
                "action": "RETRY_LATER",
                "reason": "POSSIBLE_BANK_OUTAGE",
                "priority": "HIGH",
                "confidence": confidence
            }


    # ----------------------------------------
    # TEMPORARY TECHNICAL FAILURES
    # ----------------------------------------

    if error_code in [

        "NETWORK_ERROR",

        "UPI_TIMEOUT"

    ]:

        return {
            "action": "RETRY_NOW",
            "reason": "TEMPORARY_TECHNICAL_FAILURE",
            "priority": "MEDIUM"
        }


    # ----------------------------------------
    # BANK RESPONSE TIMEOUT
    # ----------------------------------------

    if error_code == "BANK_TIMEOUT":

        return {
            "action": "RETRY_LATER",
            "reason": "BANK_RESPONSE_TIMEOUT",
            "priority": "HIGH"
        }


    # ----------------------------------------
    # PAYMENT METHOD REJECTED
    # ----------------------------------------

    if error_code in [

        "INSUFFICIENT_FUNDS",

        "CARD_DECLINED"

    ]:

        return {
            "action":
                "ASK_CUSTOMER_ALTERNATIVE_METHOD",

            "reason":
                "PAYMENT_METHOD_REJECTED",

            "priority":
                "MEDIUM"
        }


    # ----------------------------------------
    # DEFAULT SAFE RECOVERY
    # ----------------------------------------

    return {
        "action": "RETRY_LATER",
        "reason": "UNKNOWN_FAILURE_PATTERN",
        "priority": "LOW"
    }

# ========================================
# RECOVERY EXECUTION ENGINE
# ========================================

MAX_RECOVERY_ATTEMPTS = 3


def execute_recovery(event, incident=None):
    """
    Executes a bounded recovery workflow.

    Safety / stopping rules:
    - Never recover an already successful payment
    - Maximum 3 recovery attempts
    - Stops when recovery succeeds
    - Stops and escalates after retry limit
    """

    transaction_id = event.get(
        "transaction_id",
        event.get("id", "UNKNOWN_TXN")
    )

    amount = float(
        event.get("amount", 0)
    )

    attempts = int(
        event.get("recovery_attempts", 0)
    )

    # ----------------------------------------
    # PAYMENT ALREADY SUCCESSFUL
    # ----------------------------------------

    if event.get("status") == "SUCCESS":

        return {
            "transaction_id": transaction_id,
            "action": "NO_ACTION",
            "result": "NOT_REQUIRED",
            "reason": "PAYMENT_ALREADY_SUCCESSFUL",
            "attempts": attempts,
            "recovered_amount": 0,
            "stopped": True
        }

    # ----------------------------------------
    # STOPPING RULE
    # ----------------------------------------

    if attempts >= MAX_RECOVERY_ATTEMPTS:

        return {
            "transaction_id": transaction_id,
            "action": "STOP_AND_ESCALATE",
            "result": "RECOVERY_STOPPED",
            "reason": "MAXIMUM_RECOVERY_ATTEMPTS_REACHED",
            "attempts": attempts,
            "recovered_amount": 0,
            "stopped": True,
            "manual_review_required": True
        }

    # ----------------------------------------
    # CHOOSE RECOVERY ACTION
    # ----------------------------------------
    ai_analysis = analyze_recovery(
    event,
    incident
)
  
    decision = choose_recovery_action(
        event,
        incident
    )

    action = decision["action"]
    ai_recommendation = ai_analysis.get(
     "recommended_action",
    action
)
    new_attempts = attempts + 1

    # ----------------------------------------
    # NO ACTION
    # ----------------------------------------

    if action == "NO_ACTION":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "result": "NOT_REQUIRED",
            "reason": decision["reason"],
            "priority": decision["priority"],
            "attempts": attempts,
            "recovered_amount": 0,
            "stopped": True
        }

    # ----------------------------------------
    # RECOVERY SIMULATION
    # ----------------------------------------

    # Deterministic result based on transaction ID
    # This keeps demo behavior reproducible.

    transaction_score = sum(
        ord(char)
        for char in str(transaction_id)
    ) % 100


    success_threshold = {

        "RETRY_NOW": 70,

        "RETRY_LATER": 55,

        "SWITCH_PAYMENT_ROUTE": 85,

        "ASK_CUSTOMER_ALTERNATIVE_METHOD": 40

    }.get(
        action,
        30
    )


    recovered = (
        transaction_score <
        success_threshold
    )


    # ----------------------------------------
    # SUCCESSFUL RECOVERY
    # ----------------------------------------

    if recovered:

        return {
            "transaction_id": transaction_id,
            "action": action,
            "result": "RECOVERED",
            "reason": decision["reason"],
            "priority": decision["priority"],
            "ai_recommendation": ai_recommendation,
            "attempts": new_attempts,
            "recovered_amount": amount,
            "stopped": True,
            "manual_review_required": False
        }


    # ----------------------------------------
    # FAILED ATTEMPT
    # ----------------------------------------

    return {
        "transaction_id": transaction_id,
        "action": action,
        "result": "RECOVERY_FAILED",
        "reason": decision["reason"],
        "priority": decision["priority"],
        "ai_recommendation": ai_recommendation,
        "attempts": new_attempts,
        "recovered_amount": 0,
        "stopped": new_attempts >= MAX_RECOVERY_ATTEMPTS,
        "manual_review_required":
            new_attempts >= MAX_RECOVERY_ATTEMPTS
    }