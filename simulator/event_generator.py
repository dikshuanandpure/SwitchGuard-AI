import random
import uuid
from datetime import datetime


def generate_payment(status="SUCCESS", scenario="normal"):
    """Generate one synthetic payment event."""

    payment_methods = ["UPI", "CARD", "NETBANKING"]
    banks = ["Bank_A", "Bank_B", "Bank_C", "Bank_D"]

    amount = random.randint(100, 50000)

    payment = {
        "payment_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "amount": amount,
        "method": random.choice(payment_methods),
        "bank": random.choice(banks),
        "status": status,
        "error_code": None,
        "scenario": scenario
    }

    if status == "FAILED":
        payment["error_code"] = random.choice([
            "BANK_TIMEOUT",
            "INSUFFICIENT_FUNDS",
            "CARD_DECLINED",
            "UPI_TIMEOUT",
            "NETWORK_ERROR"
        ])

    return payment


def generate_normal_events(count=100):
    """Generate mostly successful normal payment events."""

    events = []

    for _ in range(count):

        if random.random() < 0.95:
            event = generate_payment(
                status="SUCCESS",
                scenario="normal"
            )
        else:
            event = generate_payment(
                status="FAILED",
                scenario="random_failure"
            )

        events.append(event)

    return events


def generate_bank_outage_events(count=50):
    """Generate failures concentrated on one bank."""

    events = []

    for _ in range(count):

        event = generate_payment(
            status="FAILED",
            scenario="bank_outage"
        )

        event["bank"] = "Bank_X"
        event["error_code"] = "BANK_TIMEOUT"

        events.append(event)

    return events


if __name__ == "__main__":

    from backend.failure_cluster import analyze_failures

    from backend.outage_detector import (
        calculate_outage_confidence,
        get_outage_decision
    )

    from simulator.scenarios import (
        normal_traffic,
        small_sample_anomaly,
        partial_bank_outage,
        full_bank_outage,
        mixed_failure_scenario
    )

    # Generate different payment scenarios
    normal_events = normal_traffic(100)

    small_sample_events = small_sample_anomaly()

    partial_outage_events = partial_bank_outage(50)

    full_outage_events = full_bank_outage(50)

    mixed_failure_events = mixed_failure_scenario(50)

    # Combine all events
    all_events = (
        normal_events
        + small_sample_events
        + partial_outage_events
        + full_outage_events
        + mixed_failure_events
    )

    # Analyze failures
    results = analyze_failures(all_events)

    print("\n--- SWITCHGUARD FAILURE ANALYSIS ---\n")

    for result in results:

        confidence = calculate_outage_confidence(result)

        # Pass both confidence and result
        decision = get_outage_decision(
            confidence,
            result
        )

        print(f"Bank: {result['bank']}")

        print(
            f"Total Transactions: "
            f"{result['total_transactions']}"
        )

        print(
            f"Failed Transactions: "
            f"{result['failed_transactions']}"
        )

        print(
            f"Failure Rate: "
            f"{result['failure_rate'] * 100}%"
        )

        print(
            f"Dominant Error: "
            f"{result['dominant_error']}"
        )

        print(
            f"Dominant Error Count: "
            f"{result['dominant_error_count']}"
        )

        print(
            f"Error Concentration: "
            f"{result['error_concentration'] * 100}%"
        )

        print(
            f"Outage Confidence: "
            f"{confidence}%"
        )

        print(
            f"Decision: "
            f"{decision}"
        )

        print("-" * 40)