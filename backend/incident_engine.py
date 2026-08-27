from backend.failure_cluster import analyze_failures

from backend.outage_detector import (
    calculate_outage_confidence,
    get_outage_decision
)

from backend.recovery_engine import (
    choose_recovery_action
)

from backend.ai_explainer import (
    generate_ai_explanation
)


class IncidentEngine:
    """
    Processes payment events, tracks incident state changes,
    generates explainable AI assessments, and chooses
    recovery actions for failed payments.
    """

    def __init__(self):

        self.events = []

        # Stores the current active incident for each bank
        self.incidents = {}


    def process_event(self, event):
        """
        Process one incoming payment event.

        Returns:
        - Incident updates
        - Recovery action for failed payments
        """

        # Store incoming event
        self.events.append(event)


        # Analyze all events processed so far
        results = analyze_failures(
            self.events
        )


        incident_updates = []


        # ----------------------------------------
        # ANALYZE EACH BANK
        # ----------------------------------------

        for result in results:

            # Calculate outage confidence
            confidence = (
                calculate_outage_confidence(
                    result
                )
            )


            # Get outage decision
            decision = get_outage_decision(
                confidence,
                result
            )


            bank = result["bank"]


            # ----------------------------------------
            # CREATE OR UPDATE INCIDENT
            # ----------------------------------------

            if decision in [

                "POSSIBLE_OUTAGE_MONITOR",

                "HIGH_CONFIDENCE_OUTAGE"

            ]:

                # Generate explainable AI assessment
                ai_explanation = (
                    generate_ai_explanation(
                        result,
                        confidence,
                        decision
                    )
                )


                # Create incident object
                incident = {

                    "bank": bank,

                    "decision": decision,

                    "confidence": confidence,

                    "failure_rate":
                        result["failure_rate"],

                    "failed_transactions":
                        result["failed_transactions"],

                    "dominant_error":
                        result["dominant_error"],

                    "error_concentration":
                        result[
                            "error_concentration"
                        ],

                    # AI explanation
                    "ai_explanation":
                        ai_explanation

                }


                # ----------------------------------------
                # INCIDENT OPENED
                # ----------------------------------------

                if bank not in self.incidents:

                    self.incidents[bank] = (
                        incident
                    )


                    incident_updates.append({

                        "type":
                            "OPENED",

                        "incident":
                            incident

                    })


                else:

                    previous_incident = (
                        self.incidents[bank]
                    )


                    previous_decision = (
                        previous_incident[
                            "decision"
                        ]
                    )


                    # Update stored incident
                    self.incidents[bank] = (
                        incident
                    )


                    # ----------------------------------------
                    # INCIDENT ESCALATED
                    # ----------------------------------------

                    if (

                        previous_decision
                        == "POSSIBLE_OUTAGE_MONITOR"

                        and

                        decision
                        == "HIGH_CONFIDENCE_OUTAGE"

                    ):

                        incident_updates.append({

                            "type":
                                "ESCALATED",

                            "incident":
                                incident

                        })


            # ----------------------------------------
            # INCIDENT RESOLVED
            # ----------------------------------------

            else:

                if bank in self.incidents:

                    del self.incidents[bank]


                    incident_updates.append({

                        "type":
                            "RESOLVED",

                        "bank":
                            bank

                    })


        # ----------------------------------------
        # RECOVERY DECISION
        # ----------------------------------------

        recovery = None


        # Recovery is needed only for failed payments
        if event.get("status") == "FAILED":

            bank = event.get("bank")


            # Get active incident for this bank
            current_incident = (
                self.incidents.get(bank)
            )


            # Choose recovery action
            recovery = choose_recovery_action(

                event,

                current_incident

            )


        # ----------------------------------------
        # RETURN PROCESSING RESULT
        # ----------------------------------------

        return {

            "incident_updates":
                incident_updates,

            "recovery":
                recovery

        }


    def get_active_incidents(self):
        """
        Return all currently active incidents.
        """

        return list(
            self.incidents.values()
        )


    def get_total_events(self):
        """
        Return the number of processed events.
        """

        return len(
            self.events
        )