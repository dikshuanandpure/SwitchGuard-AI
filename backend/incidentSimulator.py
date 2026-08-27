from backend.incident_engine import IncidentEngine


def create_event(
    bank,
    status,
    error_code=None
):

    return {
        "bank": bank,
        "status": status,
        "error_code": error_code
    }


def run_incident_simulation():

    engine = IncidentEngine()

    print("\n======================================")
    print(" SWITCHGUARD AI INCIDENT SIMULATION")
    print("======================================\n")


    # ----------------------------------
    # SCENARIO 1
    # NORMAL TRAFFIC
    # ----------------------------------

    print("SCENARIO 1: Normal Traffic\n")

    for _ in range(10):

        event = create_event(
            bank="Bank_A",
            status="SUCCESS"
        )

        result = engine.process_event(event)

    print(
        "Active Incidents:",
        engine.get_active_incidents()
    )


    # ----------------------------------
    # SCENARIO 2
    # POSSIBLE OUTAGE
    # ----------------------------------

    print("\nSCENARIO 2: Possible Bank Failure\n")

    for _ in range(6):

        event = create_event(
            bank="Bank_Test",
            status="FAILED",
            error_code="BANK_TIMEOUT"
        )

        result = engine.process_event(event)

        for update in result["incident_updates"]:

            print(
                "Incident Update:",
                update["type"]
            )

        print(
            "Recovery:",
            result["recovery"]
        )


    # ----------------------------------
    # SCENARIO 3
    # HIGH CONFIDENCE OUTAGE
    # ----------------------------------

    print("\nSCENARIO 3: Escalating Failure\n")

    for _ in range(50):

        event = create_event(
            bank="Bank_Test",
            status="FAILED",
            error_code="BANK_TIMEOUT"
        )

        result = engine.process_event(event)

        for update in result["incident_updates"]:

            print(
                "Incident Update:",
                update["type"]
            )


    # ----------------------------------
    # FINAL STATUS
    # ----------------------------------

    print("\n======================================")
    print(" FINAL ACTIVE INCIDENTS")
    print("======================================\n")

    for incident in engine.get_active_incidents():

        print("Bank:", incident["bank"])

        print(
            "Decision:",
            incident["decision"]
        )

        print(
            "Confidence:",
            incident["confidence"]
        )

        print(
            "Failure Rate:",
            incident["failure_rate"]
        )

        print("-" * 35)


    print(
        "\nTotal Events Processed:",
        engine.get_total_events()
    )

    print("\nSIMULATION COMPLETED\n")


if __name__ == "__main__":

    run_incident_simulation()