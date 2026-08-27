import time

from backend.incident_engine import IncidentEngine

from simulator.scenarios import (
    normal_traffic,
    small_sample_anomaly,
    partial_bank_outage,
    full_bank_outage,
    mixed_failure_scenario
)


def print_incident_update(update):
    """
    Display incident state changes.
    """

    update_type = update["type"]

    if update_type == "RESOLVED":

        print("\n✅ INCIDENT RESOLVED")
        print(f"Bank: {update['bank']}")
        print("-" * 45)

        return

    incident = update["incident"]

    if update_type == "OPENED":
        print("\n⚠ INCIDENT OPENED")

    elif update_type == "ESCALATED":
        print("\n⬆ INCIDENT ESCALATED")

    print(f"Bank: {incident['bank']}")
    print(f"Decision: {incident['decision']}")
    print(f"Confidence: {incident['confidence']}%")
    print(
        f"Failure Rate: "
        f"{incident['failure_rate'] * 100}%"
    )
    print(
        f"Failed Transactions: "
        f"{incident['failed_transactions']}"
    )
    print(
        f"Dominant Error: "
        f"{incident['dominant_error']}"
    )
    print(
        f"Error Concentration: "
        f"{incident['error_concentration'] * 100}%"
    )

    print("-" * 45)


def print_recovery_action(recovery):
    """
    Display the recovery action selected
    for a failed payment.
    """

    if recovery is None:
        return

    print("\n🔄 RECOVERY ACTION")

    print(
        f"Action: "
        f"{recovery['action']}"
    )

    print(
        f"Reason: "
        f"{recovery['reason']}"
    )

    print("-" * 45)


def run_realtime_simulation():

    print("\n=== SWITCHGUARD REAL-TIME SIMULATION ===\n")

    engine = IncidentEngine()

    events = (
        normal_traffic(30)
        + small_sample_anomaly()
        + partial_bank_outage(30)
        + full_bank_outage(30)
        + mixed_failure_scenario(30)
    )

    # Process events one by one
    for index, event in enumerate(events, start=1):

        result = engine.process_event(event)

        incident_updates = result["incident_updates"]
        recovery = result["recovery"]

        print(
            f"Event {index} | "
            f"Bank: {event['bank']} | "
            f"Status: {event['status']} | "
            f"Scenario: {event['scenario']}"
        )

        # Display incident state changes
        for update in incident_updates:

            print_incident_update(update)

        # Display recovery action for failed payments
        if event["status"] == "FAILED":

            print_recovery_action(recovery)

        time.sleep(0.05)

    print("\n=== SIMULATION COMPLETE ===")

    print(
        f"Total Events Processed: "
        f"{engine.get_total_events()}"
    )

    print("\n=== ACTIVE INCIDENTS ===\n")

    active_incidents = engine.get_active_incidents()

    if not active_incidents:

        print("No active incidents detected.")

    else:

        for incident in active_incidents:

            print(
                f"{incident['bank']} → "
                f"{incident['decision']} "
                f"({incident['confidence']}%)"
            )


if __name__ == "__main__":
    run_realtime_simulation()