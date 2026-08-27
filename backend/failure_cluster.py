from collections import defaultdict


def analyze_failures(events):
    """
    Analyze payment events and detect failure patterns
    for each bank.
    """

    # ----------------------------------------
    # STORE BANK-WISE STATISTICS
    # ----------------------------------------

    bank_stats = defaultdict(
        lambda: {
            "total": 0,
            "failed": 0,
            "successful": 0,
            "error_codes": defaultdict(int)
        }
    )


    # ----------------------------------------
    # COLLECT EVENT STATISTICS
    # ----------------------------------------

    for event in events:

        bank = event.get(
            "bank",
            "UNKNOWN_BANK"
        )

        status = event.get(
            "status",
            "UNKNOWN"
        )


        # Count total transactions

        bank_stats[bank]["total"] += 1


        # ----------------------------------------
        # FAILED TRANSACTION
        # ----------------------------------------

        if status == "FAILED":

            bank_stats[bank]["failed"] += 1


            error_code = event.get(
                "error_code",
                "UNKNOWN_ERROR"
            )


            if error_code:

                bank_stats[bank]["error_codes"][
                    error_code
                ] += 1


        # ----------------------------------------
        # SUCCESSFUL TRANSACTION
        # ----------------------------------------

        elif status == "SUCCESS":

            bank_stats[bank]["successful"] += 1


    # ----------------------------------------
    # ANALYZE EACH BANK
    # ----------------------------------------

    results = []


    for bank, stats in bank_stats.items():

        total = stats["total"]

        failed = stats["failed"]

        successful = stats["successful"]


        # ----------------------------------------
        # FAILURE RATE
        # ----------------------------------------

        if total > 0:

            failure_rate = failed / total

        else:

            failure_rate = 0


        # ----------------------------------------
        # SUCCESS RATE
        # ----------------------------------------

        if total > 0:

            success_rate = successful / total

        else:

            success_rate = 0


        # ----------------------------------------
        # DEFAULT ERROR VALUES
        # ----------------------------------------

        dominant_error = None

        dominant_error_count = 0

        error_concentration = 0


        # ----------------------------------------
        # FIND MOST COMMON ERROR
        # ----------------------------------------

        if stats["error_codes"]:

            dominant_error = max(

                stats["error_codes"],

                key=stats["error_codes"].get

            )


            dominant_error_count = (

                stats["error_codes"][
                    dominant_error
                ]

            )


            # ----------------------------------------
            # ERROR CONCENTRATION
            # ----------------------------------------

            if failed > 0:

                error_concentration = (

                    dominant_error_count
                    / failed

                )


        # ----------------------------------------
        # POSSIBLE OUTAGE SIGNAL
        # ----------------------------------------

        possible_outage = (

            total >= 3

            and failed >= 3

            and failure_rate >= 0.70

        )


        # ----------------------------------------
        # ADD BANK ANALYSIS RESULT
        # ----------------------------------------

        results.append({

            "bank": bank,

            "total_transactions":
                total,

            "successful_transactions":
                successful,

            "failed_transactions":
                failed,

            "failure_rate":
                round(
                    failure_rate,
                    2
                ),

            "success_rate":
                round(
                    success_rate,
                    2
                ),

            "dominant_error":
                dominant_error,

            "dominant_error_count":
                dominant_error_count,

            "error_concentration":
                round(
                    error_concentration,
                    2
                ),

            "possible_outage":
                possible_outage

        })


    # ----------------------------------------
    # SORT BANKS BY FAILURE RATE
    # ----------------------------------------

    results.sort(

        key=lambda result:
            result["failure_rate"],

        reverse=True

    )


    return results