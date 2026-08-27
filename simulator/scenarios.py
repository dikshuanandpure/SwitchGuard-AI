from simulator.event_generator import generate_payment


def normal_traffic(count=30):
    """
    Normal traffic.

    All transactions are successful so the dashboard
    clearly demonstrates a healthy system.
    """

    events = []

    for _ in range(count):

        event = generate_payment(
            status="SUCCESS",
            scenario="normal_traffic"
        )

        events.append(event)

    return events


def small_sample_anomaly():
    """
    Only 3 transactions fail.

    This should NOT automatically be treated
    as a systemic bank outage.
    """

    events = []

    for _ in range(3):

        event = generate_payment(
            status="FAILED",
            scenario="small_sample_anomaly"
        )

        event["bank"] = "Bank_S"
        event["error_code"] = "BANK_TIMEOUT"

        events.append(event)

    return events


def partial_bank_outage(count=30):
    """
    A significant percentage of transactions fail
    for one bank, creating a detectable partial outage.
    """

    events = []

    failed_count = 24

    for index in range(count):

        if index < failed_count:

            event = generate_payment(
                status="FAILED",
                scenario="partial_bank_outage"
            )

            event["bank"] = "Bank_P"
            event["error_code"] = "BANK_TIMEOUT"

        else:

            event = generate_payment(
                status="SUCCESS",
                scenario="partial_bank_outage"
            )

            event["bank"] = "Bank_P"

        events.append(event)

    return events


def full_bank_outage(count=30):
    """
    All transactions fail for one bank.

    This should produce a high-confidence outage.
    """

    events = []

    for _ in range(count):

        event = generate_payment(
            status="FAILED",
            scenario="full_bank_outage"
        )

        event["bank"] = "Bank_X"
        event["error_code"] = "BANK_TIMEOUT"

        events.append(event)

    return events


def mixed_failure_scenario(count=30):
    """
    All transactions fail, but the failures have
    different causes.

    This should demonstrate that high failure volume
    alone does not automatically mean a bank outage.
    """

    events = []

    error_codes = [

        "BANK_TIMEOUT",
        "INSUFFICIENT_FUNDS",
        "CARD_DECLINED",
        "UPI_TIMEOUT",
        "NETWORK_ERROR"

    ]

    banks = [

        "Bank_A",
        "Bank_B",
        "Bank_C",
        "Bank_D",
        "Bank_E"

    ]

    for index in range(count):

        event = generate_payment(
            status="FAILED",
            scenario="mixed_failures"
        )

        event["bank"] = (
            banks[index % len(banks)]
        )

        event["error_code"] = (
            error_codes[index % len(error_codes)]
        )

        events.append(event)

    return events