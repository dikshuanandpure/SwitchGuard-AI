from backend.recovery_engine import (
    choose_recovery_action,
    execute_recovery
)


def run_recovery_simulation():

    print("\n====================================")
    print(" SWITCHGUARD AI RECOVERY SIMULATION ")
    print("====================================\n")


    test_cases = [

        {
            "name": "Successful Payment",

            "event": {
                "transaction_id": "TXN001",
                "status": "SUCCESS",
                "error_code": None,
                "amount": 1000
            },

            "incident": None
        },


        {
            "name": "Network Error",

            "event": {
                "transaction_id": "TXN002",
                "status": "FAILED",
                "error_code": "NETWORK_ERROR",
                "amount": 2500
            },

            "incident": None
        },


        {
            "name": "UPI Timeout",

            "event": {
                "transaction_id": "TXN003",
                "status": "FAILED",
                "error_code": "UPI_TIMEOUT",
                "amount": 1500
            },

            "incident": None
        },


        {
            "name": "Bank Timeout",

            "event": {
                "transaction_id": "TXN004",
                "status": "FAILED",
                "error_code": "BANK_TIMEOUT",
                "amount": 5000
            },

            "incident": None
        },


        {
            "name": "Insufficient Funds",

            "event": {
                "transaction_id": "TXN005",
                "status": "FAILED",
                "error_code": "INSUFFICIENT_FUNDS",
                "amount": 3000
            },

            "incident": None
        },


        {
            "name": "High Confidence Bank Outage",

            "event": {
                "transaction_id": "TXN006",
                "status": "FAILED",
                "error_code": "BANK_TIMEOUT",
                "amount": 10000
            },

            "incident": {
                "decision":
                    "HIGH_CONFIDENCE_OUTAGE",

                "confidence":
                    95
            }
        },


        {
            "name": "Possible Bank Outage",

            "event": {
                "transaction_id": "TXN007",
                "status": "FAILED",
                "error_code": "BANK_TIMEOUT",
                "amount": 4000
            },

            "incident": {
                "decision":
                    "POSSIBLE_OUTAGE_MONITOR",

                "confidence":
                    70
            }
        }

    ]


    # ====================================
    # RECOVERY METRICS
    # ====================================

    total_processed = 0

    failed_transactions = 0

    revenue_at_risk = 0

    recovery_attempts = 0

    successfully_recovered = 0

    recovery_failed = 0

    revenue_recovered = 0


    print("------------------------------------")
    print(" PROCESSING RECOVERY BATCH ")
    print("------------------------------------")


    for test in test_cases:

        event = test["event"]

        incident = test["incident"]


        total_processed += 1


        # --------------------------------
        # TRACK FAILED PAYMENT VALUE
        # --------------------------------

        if event["status"] == "FAILED":

            failed_transactions += 1

            revenue_at_risk += event["amount"]


        # --------------------------------
        # AI DECISION
        # --------------------------------

        decision = choose_recovery_action(
            event,
            incident
        )


        # --------------------------------
        # EXECUTE RECOVERY
        # --------------------------------

        result = execute_recovery(
            event,
            incident
        )


        # --------------------------------
        # UPDATE METRICS
        # --------------------------------

        if result["action"] != "NO_ACTION":

            recovery_attempts += 1


        if result["result"] == "RECOVERED":

            successfully_recovered += 1

            revenue_recovered += (
                result["recovered_amount"]
            )


        elif result["result"] == "RECOVERY_FAILED":

            recovery_failed += 1


        # --------------------------------
        # PRINT RESULT
        # --------------------------------

        print("\nScenario:", test["name"])

        print(
            "Transaction:",
            event["transaction_id"]
        )

        print(
            "Amount: ₹",
            event["amount"]
        )

        print(
            "AI Action:",
            decision["action"]
        )

        print(
            "Recovery Result:",
            result["result"]
        )

        print(
            "Attempts:",
            result["attempts"]
        )

        print(
            "Recovered Amount: ₹",
            result["recovered_amount"]
        )

        print("------------------------------------")


    # ====================================
    # FINAL RECOVERY PERFORMANCE
    # ====================================

    if revenue_at_risk > 0:

        recovery_rate = (
            revenue_recovered /
            revenue_at_risk
        ) * 100

    else:

        recovery_rate = 0


    print("\n====================================")
    print(" RECOVERY PERFORMANCE ")
    print("====================================")

    print(
        "Transactions Processed:",
        total_processed
    )

    print(
        "Failed Transactions:",
        failed_transactions
    )

    print(
        "Revenue At Risk: ₹",
        revenue_at_risk
    )

    print(
        "Recovery Attempts:",
        recovery_attempts
    )

    print(
        "Successfully Recovered:",
        successfully_recovered
    )

    print(
        "Recovery Failed:",
        recovery_failed
    )

    print(
        "Revenue Recovered: ₹",
        revenue_recovered
    )

    print(
        "Recovery Rate:",
        round(recovery_rate, 2),
        "%"
    )

    print("====================================\n")


if __name__ == "__main__":

    run_recovery_simulation()