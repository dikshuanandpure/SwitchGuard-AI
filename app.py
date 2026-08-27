from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

from backend.incident_engine import IncidentEngine

from backend.ai_explainer import (
    generate_ai_explanation
)

from simulator.scenarios import (
    normal_traffic,
    small_sample_anomaly,
    partial_bank_outage,
    full_bank_outage,
    mixed_failure_scenario
)


# ----------------------------------------
# CREATE FLASK APP
# ----------------------------------------

app = Flask(__name__)

CORS(app)


# ----------------------------------------
# GLOBAL SYSTEM DATA
# ----------------------------------------

engine = IncidentEngine()

processed_transactions = []

incident_history = []

recovery_history = []
# ----------------------------------------
# RECOVERY AUDIT TRAIL
# ----------------------------------------

recovery_audit_log = []
recovered_transactions = []

revenue_recovered = 0

current_scenario = "INITIAL_SYSTEM_DATA"


# ----------------------------------------
# PROCESS EVENTS
# ----------------------------------------
# ----------------------------------------
# RECOVERY SAFETY GUARDRAILS
# ----------------------------------------

MAX_RETRY_ATTEMPTS = 2
MAX_RECOVERY_ATTEMPTS = 3

PERMANENT_FAILURES = [
    "CARD_DECLINED",
    "INSUFFICIENT_FUNDS"
]


def get_guardrail_decision(
    error_code,
    recovery_action,
    retry_attempts=0
):

    # Permanent failures should not be retried
    if error_code in PERMANENT_FAILURES:

        return {
            "allowed": False,
            "reason":
                "Permanent payment failure - retry blocked"
        }


    # Prevent unlimited retries
    if (
        recovery_action == "RETRY NOW"
        and retry_attempts >= MAX_RETRY_ATTEMPTS
    ):

        return {
            "allowed": False,
            "reason":
                "Maximum retry limit reached"
        }


    # Critical outage should use rerouting
    if recovery_action == "SWITCH PAYMENT ROUTE":

        return {
            "allowed": True,
            "reason":
                "Critical outage detected - rerouting allowed"
        }


    return {
        "allowed": True,
        "reason":
            "Recovery action approved by safety guardrails"
    }
def process_events(new_events):

    global current_scenario
    global processed_transactions
    global incident_history
    global recovery_history
    global recovered_transactions
    global revenue_recovered

    for index, event in enumerate(
        new_events,
        start=len(processed_transactions) + 1
    ):

        # Process event through Incident Engine
        result = engine.process_event(event)


        # ------------------------------------
        # PREPARE TRANSACTION DATA
        # ------------------------------------

        error_code = event.get(
            "error_code",
            "-"
        )

        if event["status"] == "SUCCESS":

            error_code = "-"


        transaction = {

            "id":
                f"TXN-{index:05d}",

            "bank":
                event["bank"],

            "status":
                event["status"],

            "error":
                error_code,

            "amount":
                event.get(
                    "amount",
                    100 + (index * 137) % 5000
                ),

            "scenario":
                event.get(
                    "scenario",
                    "unknown",
                    
                ),"time":
             datetime.now().strftime("%H:%M:%S")

        }


        processed_transactions.append(
            transaction
        )
               # ------------------------------------
        # STORE RECOVERY RESULT
        # ------------------------------------

        recovery = result.get(
            "recovery"
        )


        if recovery is not None:

            recovery_history.append({

                "transaction_id":
                    transaction["id"],

                "bank":
                    event["bank"],

                "action":
                    recovery.get(
                        "action",
                        "NO_ACTION"
                    ),

                "reason":
                    recovery.get(
                        "reason",
                        "UNKNOWN"
                    ),

                "priority":
                    recovery.get(
                        "priority",
                        "UNKNOWN"
                    ),

                "result":
                    recovery.get(
                        "result",
                        "PENDING"
                    ),

                "recovered_amount":
                    recovery.get(
                        "recovered_amount",
                        0
                    ),

                "attempts":
                    recovery.get(
                        "attempts",
                        0
                    ),

                "stopped":
                    recovery.get(
                        "stopped",
                        False
                    )

            })

        # ------------------------------------
        # SAVE INCIDENT UPDATES
        # ------------------------------------

        for update in result["incident_updates"]:

            incident_history.append(
                update
            )


        # ------------------------------------
        # SAVE RECOVERY ACTION
        # ------------------------------------

        if result["recovery"] is not None:

            recovery = result["recovery"]
            
                
            recovery_history[:] = [
    item
    for item in recovery_history
    if item["bank"] != event["bank"]
]
            recovery_history.append({

                "transaction_id":
                    f"TXN-{index:05d}",

                "bank":
                    event["bank"],

                "action":
                    recovery["action"],

                "reason":
                    recovery["reason"],

                "priority":
                    recovery.get(
                        "priority",
                        "UNKNOWN"
                    )

            })


# ----------------------------------------
# RESET SYSTEM
# ----------------------------------------

# ----------------------------------------
# RESET SYSTEM
# ----------------------------------------

def reset_system():

    global engine
    global processed_transactions
    global incident_history
    global recovery_history
    global recovered_transactions
    global revenue_recovered

    engine = IncidentEngine()

    processed_transactions.clear()

    incident_history.clear()

    recovery_history.clear()

    recovered_transactions.clear()

    revenue_recovered = 0

    
# ----------------------------------------
# RUN SELECTED SCENARIO
# ----------------------------------------

def run_scenario(scenario_name):

    global current_scenario

    # Reset previous system
    reset_system()


    # ----------------------------------------
    # NORMAL TRAFFIC
    # ----------------------------------------

    if scenario_name == "normal":

        new_events = normal_traffic(30)

        current_scenario = "NORMAL TRAFFIC"


    # ----------------------------------------
    # SMALL SAMPLE ANOMALY
    # ----------------------------------------

    elif scenario_name == "small_sample":

        new_events = small_sample_anomaly()

        current_scenario = "SMALL SAMPLE ANOMALY"


    # ----------------------------------------
    # PARTIAL BANK OUTAGE
    # ----------------------------------------

    elif scenario_name == "partial_outage":

        new_events = partial_bank_outage(30)

        current_scenario = "PARTIAL BANK OUTAGE"


    # ----------------------------------------
    # FULL BANK OUTAGE
    # ----------------------------------------

    elif scenario_name == "full_outage":

        new_events = full_bank_outage(30)

        current_scenario = "FULL BANK OUTAGE"


    # ----------------------------------------
    # MIXED FAILURES
    # ----------------------------------------

    elif scenario_name == "mixed_failures":

        new_events = mixed_failure_scenario(30)

        current_scenario = "MIXED FAILURE SCENARIO"


    # ----------------------------------------
    # INVALID SCENARIO
    # ----------------------------------------

    else:

        return None


    # Process all generated events
    process_events(new_events)

    return new_events


# ----------------------------------------
# INITIAL SYSTEM DATA
# ----------------------------------------

# ----------------------------------------
# INITIAL SYSTEM STATE
# ----------------------------------------

# Do NOT process all scenarios at startup.
# Each dashboard simulation starts from a clean state.

current_scenario = "READY - SELECT A SCENARIO"

# ----------------------------------------
# HOME API
# ----------------------------------------

@app.route("/")
def home():

    return jsonify({

        "message":
            "SwitchGuard AI API is running successfully"

    })


# ----------------------------------------
# SCENARIO SIMULATION API
# ----------------------------------------

@app.route("/api/simulate/<scenario_name>")
def simulate_scenario(scenario_name):

    new_events = run_scenario(
        scenario_name
    )


    # Invalid scenario
    if new_events is None:

        return jsonify({

            "status":
                "ERROR",

            "message":
                "Invalid scenario"

        }), 400


    return jsonify({

        "status":
            "SUCCESS",

        "message":
            f"{current_scenario} simulation completed",

        "scenario":
            current_scenario,

        "events_generated":
            len(new_events),

        "total_events_processed":
            engine.get_total_events(),

        "active_incidents":
            engine.get_active_incidents()

    })


# ----------------------------------------
# RESET SYSTEM API
# ----------------------------------------

@app.route("/api/reset")
def reset_api():

    global current_scenario
    global processed_transactions
    global incident_history
    global recovery_history
    global recovery_audit_log
    reset_system()

    processed_transactions.clear()
    incident_history.clear()
    recovery_history.clear()
    recovery_audit_log.clear()
    current_scenario = "SYSTEM RESET"

    return jsonify({

        "status": "SUCCESS",

        "message":
            "SwitchGuard AI system reset successfully",

        "total_events_processed":
            engine.get_total_events(),

        "active_incidents":
            engine.get_active_incidents()

    })
@app.route("/api/simulate-recovery", methods=["POST"])
def simulate_recovery():

    global recovered_transactions
    global revenue_recovered

    recovered_transactions.clear()
    revenue_recovered = 0
    global recovery_audit_log
    # Recover failed transactions
    failed_transactions = [

        transaction

        for transaction in processed_transactions

        if transaction["status"] == "FAILED"

    ]

    # Recover approximately 60% of failed transactions
    recovery_count = int(
        len(failed_transactions) * 0.6
    )

    transactions_to_recover = failed_transactions[
        :recovery_count
    ]

    for transaction in transactions_to_recover:

     transaction["status"] = "RECOVERED"

    transaction["recovered"] = True

    recovered_transactions.append(
        transaction
    )

    revenue_recovered += transaction["amount"]
    return jsonify({

        "status": "SUCCESS",

        "message":
            "Recovery simulation completed",

        "recovered_transactions":
            len(recovered_transactions),

        "revenue_recovered":
            revenue_recovered

    })
# ----------------------------------------
# DASHBOARD API
# ----------------------------------------

@app.route("/api/dashboard")
def dashboard():

    # ------------------------------------
    # ACTIVE INCIDENTS
    # ------------------------------------

    active_incidents = (
        engine.get_active_incidents()
    )


    # ------------------------------------
    # BANK STATUS
    # ------------------------------------

    banks = {}

    for transaction in processed_transactions:

        bank = transaction["bank"]

        if bank not in banks:

            banks[bank] = "HEALTHY"


    # Update bank status from active incidents

    for incident in active_incidents:

        bank = incident["bank"]

        decision = incident["decision"]


        if decision == "HIGH_CONFIDENCE_OUTAGE":

            banks[bank] = "OUTAGE"


        elif decision == "POSSIBLE_OUTAGE_MONITOR":

            banks[bank] = "POSSIBLE OUTAGE"


    bank_status = []

    for bank, status in banks.items():

        bank_status.append({

            "bank":
                bank,

            "status":
                status

        })


    # ------------------------------------
    # FAILED TRANSACTION COUNT
    # ------------------------------------

    failed_transactions = sum(

        1

        for transaction
        in processed_transactions

        if transaction["status"]
        == "FAILED"

    )


    # ------------------------------------
    # SUCCESSFUL TRANSACTION COUNT
    # ------------------------------------

    successful_transactions = sum(

        1

        for transaction
        in processed_transactions

        if transaction["status"]
        == "SUCCESS"

    )
    # ------------------------------------
    # RECOVERY METRICS
    # ------------------------------------

    recovered_transactions = sum(

        1

        for transaction
        in processed_transactions

        if transaction.get(
            "recovered",
            False
        )

    )


    recovery_rate = 0


    if failed_transactions > 0:

        recovery_rate = round(

            (
                recovered_transactions
                / failed_transactions
            ) * 100,

            1

        )

    # ------------------------------------
    # HIGH CONFIDENCE OUTAGES
    # ------------------------------------

    high_confidence_outages = sum(

        1

        for incident
        in active_incidents

        if incident["decision"]
        == "HIGH_CONFIDENCE_OUTAGE"

    )


    # ------------------------------------
    # RETURN DASHBOARD DATA
    # ------------------------------------

    return jsonify({

        "current_scenario":
            current_scenario,

        "total_events":
            len(processed_transactions),

        "successful_transactions":
            successful_transactions,

        "failed_transactions":
            failed_transactions,

        "active_incidents":
            len(active_incidents),

        "high_confidence_outages":
            high_confidence_outages,
"revenue_at_risk":
    failed_transactions * 1000,

        "revenue_recovered":
            recovered_transactions * 1000,

        "recovery_rate":
            recovery_rate,
        "bank_status":
            bank_status,

        "incidents":
            active_incidents,

        "recovery_actions":
            recovery_history

    })


# ----------------------------------------
# AI INSIGHTS API
# ----------------------------------------

# ----------------------------------------
# AI INSIGHTS API
# ----------------------------------------

@app.route("/api/ai-insights")
def get_ai_insights():

    active_incidents = (
        engine.get_active_incidents()
    )


    insights = []


    # ----------------------------------------
    # ACTIVE INCIDENT INSIGHTS
    # ----------------------------------------

    for incident in active_incidents:

        result = {

            "failure_rate":
                incident.get(
                    "failure_rate",
                    0
                ),

            "failed_transactions":
                incident.get(
                    "failed_transactions",
                    0
                ),

            "dominant_error":
                incident.get(
                    "dominant_error",
                    None
                ),

            "error_concentration":
                incident.get(
                    "error_concentration",
                    0
                )

        }


        explanation = (
            generate_ai_explanation(

                result,

                incident.get(
                    "confidence",
                    0
                ),

                incident.get(
                    "decision",
                    ""
                )

            )
        )


        insights.append({

            "bank":
                incident.get(
                    "bank",
                    "UNKNOWN_BANK"
                ),

            "decision":
                incident.get(
                    "decision",
                    ""
                ),

            "confidence":
                incident.get(
                    "confidence",
                    0
                ),

            "ai_assessment":
                explanation

        })


    # ----------------------------------------
    # NO ACTIVE INCIDENT
    # ----------------------------------------

    if len(insights) == 0:

        scenario = current_scenario


        if scenario == "NORMAL TRAFFIC":

            explanation = {

                "risk_level":
                    "LOW",

                "confidence":
                    0,

                "reasons": [

                    "Transactions are completing normally",

                    "No abnormal failure concentration detected",

                    "No systemic bank outage detected"

                ],

                "recommendation":
                    "Continue normal monitoring."

            }


            decision = (
                "SYSTEM_HEALTHY"
            )


        elif scenario == "SMALL SAMPLE ANOMALY":

            explanation = {

                "risk_level":
                    "LOW",

                "confidence":
                    25,

                "reasons": [

                    "A small number of failures was detected",

                    "Failure volume is too low to confirm an outage",

                    "Additional events should be monitored before escalation"

                ],

                "recommendation":
                    "Continue monitoring and collect more evidence."

            }


            decision = (
                "INSUFFICIENT_EVIDENCE"
            )


        elif scenario == "MIXED FAILURE SCENARIO":

            explanation = {

                "risk_level":
                    "MEDIUM",

                "confidence":
                    45,

                "reasons": [

                    "Multiple failure types were detected",

                    "Failures are distributed across different causes",

                    "No single bank-wide outage pattern is confirmed"

                ],

                "recommendation":
                    "Investigate individual failures instead of declaring a systemic outage."

            }


            decision = (
                "MIXED_FAILURE_PATTERN"
            )


        elif scenario == "SYSTEM RESET":

            explanation = {

                "risk_level":
                    "LOW",

                "confidence":
                    0,

                "reasons": [

                    "System data has been cleared",

                    "No transactions are currently being monitored"

                ],

                "recommendation":
                    "Select a scenario to begin monitoring."

            }


            decision = (
                "SYSTEM_RESET"
            )


        else:

            explanation = {

                "risk_level":
                    "LOW",

                "confidence":
                    0,

                "reasons": [

                    "System is ready for monitoring",

                    "No scenario has been executed yet"

                ],

                "recommendation":
                    "Select and run a payment scenario."

            }


            decision = (
                "READY"
            )


        insights.append({

            "bank":
                "SYSTEM",

            "decision":
                decision,

            "confidence":
                explanation[
                    "confidence"
                ],

            "ai_assessment":
                explanation

        })


    return jsonify({

        "system":
            "SwitchGuard AI",

        "current_scenario":
            current_scenario,

        "insights":
            insights

    })

# ----------------------------------------
# TRANSACTIONS API
# ----------------------------------------

@app.route("/api/transactions")
def get_transactions():

    return jsonify({

        "transactions":
            processed_transactions

    })


# ----------------------------------------
# INCIDENT HISTORY API
# ----------------------------------------

@app.route("/api/incidents")
def get_incidents():

    return jsonify({

        "active_incidents":
            engine.get_active_incidents(),

        "incident_history":
            incident_history

    })


# ----------------------------------------
# RECOVERY ACTION API
# ----------------------------------------

@app.route("/api/recovery")
def get_recovery_actions():

    return jsonify({

        "recovery_actions":
            recovery_history

    })


# ----------------------------------------
# PROJECT STATUS API
# ----------------------------------------

@app.route("/api/status")
def get_status():

    return jsonify({

        "system":
            "SwitchGuard AI",

        "status":
            "RUNNING",

        "current_scenario":
            current_scenario,

        "total_events_processed":
            engine.get_total_events(),

        "active_incidents":
            len(
                engine.get_active_incidents()
            ),

        "total_recovery_actions":
            len(
                recovery_history
            )

    })


# ----------------------------------------
# START FLASK SERVER
# ----------------------------------------


if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )
    