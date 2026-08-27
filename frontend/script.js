console.log("SwitchGuard AI Dashboard Started");


// ========================================
// API URLs
// ========================================

const DASHBOARD_API =
    "http://127.0.0.1:5000/api/dashboard";

const TRANSACTION_API =
    "http://127.0.0.1:5000/api/transactions";

const INCIDENT_API =
    "http://127.0.0.1:5000/api/incidents";

const RECOVERY_API =
    "http://127.0.0.1:5000/api/recovery";


// ========================================
// CHART VARIABLES
// ========================================

let failureChart = null;
async function loadTransactions() {

    try {

        const response =
            await fetch(
                TRANSACTION_API
            );


        if (!response.ok) {

            throw new Error(
                "Failed to fetch transactions"
            );

        }


        const data =
            await response.json();


        console.log(
            "Transactions:",
            data
        );


        const transactions =
            Array.isArray(data)
                ? data
                : (
                    data.transactions ||
                    data.events ||
                    []
                );


        updateFailureChart(
            transactions
        );
updateLiveTransactionMonitor(
    transactions
);
    }

    catch (error) {

        console.error(
            "Transaction Error:",
            error
        );

    }

}

// ========================================
// HELPER FUNCTION
// ========================================

function formatText(text) {

    return String(text || "")
        .replaceAll("_", " ");

}
// ========================================
// LIVE TRANSACTION MONITOR
// ========================================
function updateLiveTransactionMonitor(
    transactions
) {

    const totalElement =
        document.getElementById(
            "liveTotal"
        );

    const successElement =
        document.getElementById(
            "liveSuccess"
        );

    const failedElement =
        document.getElementById(
            "liveFailed"
        );

    const tableBody =
        document.getElementById(
            "transactionTable"
        );


    // Safety check
    if (
        !totalElement ||
        !successElement ||
        !failedElement ||
        !tableBody
    ) {

        console.warn(
            "Live transaction monitor elements not found"
        );

        return;

    }


    // Update total transactions
    totalElement.textContent =
        transactions.length;


    // Count successful transactions
    const successful =
        transactions.filter(
            transaction =>
                String(
                    transaction.status || ""
                ).toUpperCase() ===
                "SUCCESS"
        ).length;


    // Count failed transactions
    const failed =
        transactions.filter(
            transaction =>
                String(
                    transaction.status || ""
                ).toUpperCase() ===
                "FAILED"
        ).length;


    successElement.textContent =
        successful;

    failedElement.textContent =
        failed;


    // Clear previous rows
    tableBody.innerHTML = "";


    // Show latest 10 transactions
    transactions
        .slice(-10)
        .reverse()
        .forEach(
            transaction => {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

    <td>
        ${
            transaction.transaction_id ||
            transaction.id ||
            "-"
        }
    </td>

    <td>
        ${
            transaction.bank ||
            "-"
        }
    </td>

    <td>
        ₹${
            transaction.amount || 0
        }
    </td>

    <td>
        ${
            transaction.status ||
            "-"
        }
    </td>

    <td>
        ${
            transaction.error ||
            transaction.error_code ||
            "-"
        }
    </td>

    <td>
        ${
            transaction.time ||
            "-"
        }
    </td>

`;


                tableBody.appendChild(
                    row
                );

            }
        );

}
// ========================================
// LOAD DASHBOARD
// ========================================

async function loadDashboard() {

    try {

        const response =
            await fetch(DASHBOARD_API);

        if (!response.ok) {

            throw new Error(
                "Failed to fetch dashboard data"
            );

        }


        const data =
            await response.json();


        // ====================================
        // UPDATE STATISTICS
        // ====================================

        document.getElementById(
            "totalEvents"
        ).textContent =
            data.total_events ?? 0;


        document.getElementById(
            "failedTransactions"
        ).textContent =
            data.failed_transactions ?? 0;


        document.getElementById(
            "activeIncidents"
        ).textContent =
            data.active_incidents ?? 0;


        document.getElementById(
            "highOutages"
        ).textContent =
            data.high_confidence_outages ?? 0;
document.getElementById(
    "revenueAtRisk"
).textContent =
    "₹" +
    (data.revenue_at_risk ?? 0);


document.getElementById(
    "revenueRecovered"
).textContent =
    "₹" +
    (data.revenue_recovered ?? 0);


document.getElementById(
    "recoveryRate"
).textContent =
    (data.recovery_rate ?? 0) +
    "%";

        // ====================================
        // BANK STATUS
        // ====================================

        const bankList =
            document.getElementById(
                "bankStatusList"
            );

        bankList.innerHTML = "";


        const bankStatus =
            data.bank_status || [];


        bankStatus.forEach(
            function (bank) {

                let statusClass =
                    "healthy";


                if (
                    bank.status ===
                    "OUTAGE"
                ) {

                    statusClass =
                        "outage";

                }

                else if (
                    bank.status ===
                    "POSSIBLE OUTAGE"
                ) {

                    statusClass =
                        "warning-status";

                }


                bankList.innerHTML += `

                    <div class="bank">

                        <span>
                            🏦 ${bank.bank}
                        </span>

                        <span
                            class="
                                status
                                ${statusClass}
                            "
                        >

                            ${bank.status}

                        </span>

                    </div>

                `;

            }
        );


        // ====================================
        // ACTIVE INCIDENTS
        // ====================================

        const incidentList =
            document.getElementById(
                "incidentList"
            );

        incidentList.innerHTML = "";


        const incidents =
            data.incidents || [];


        if (
            incidents.length === 0
        ) {

            incidentList.innerHTML = `

                <p class="no-data">

                    ✅ No active incidents detected.

                </p>

            `;

        }


        incidents.forEach(
            function (incident) {

                let incidentClass =
                    "possible";


                let decisionText =
                    "Possible Outage";


                if (
                    incident.decision ===
                    "HIGH_CONFIDENCE_OUTAGE"
                ) {

                    incidentClass =
                        "critical";

                    decisionText =
                        "High Confidence Outage";

                }


                incidentList.innerHTML += `

                    <div
                        class="
                            incident
                            ${incidentClass}
                        "
                    >

                        <h3>
                            🚨 ${incident.bank}
                        </h3>

                        <p>
                            ${decisionText}
                        </p>

                        <div class="confidence">

                            Confidence:
                            ${Number(
                                incident.confidence
                            ).toFixed(1)}%

                        </div>

                        <small>

                            Failure Rate:
                            ${(
                                Number(
                                    incident.failure_rate
                                ) * 100
                            ).toFixed(1)}%

                        </small>

                    </div>

                `;

            }
        );


        // ====================================
        // RECOVERY ACTIONS
        // ====================================

        const recoveryList =
            document.getElementById(
                "recoveryList"
            );

        recoveryList.innerHTML = "";


        const recoveryActions =
            data.recovery_actions || [];


        if (
            recoveryActions.length === 0
        ) {

            recoveryList.innerHTML = `

                <p class="no-data">

                    No recovery actions required.

                </p>

            `;

        }


        // ====================================
// SHOW UNIQUE RECOVERY ACTIONS
// ====================================

// Multiple failed transactions can generate
// the same recovery recommendation.
// Keep only the latest recommendation
// for each bank + action.

const uniqueRecoveryActions = [];

const seenRecoveryActions = new Set();

recoveryActions
    .slice()
    .reverse()
    .forEach(
        function (recovery) {

            const key =
                `${recovery.bank}-${recovery.action}`;

            if (
                !seenRecoveryActions.has(key)
            ) {

                seenRecoveryActions.add(key);

                uniqueRecoveryActions.push(
                    recovery
                );

            }

        }
    );


// Show maximum 8 meaningful recommendations

uniqueRecoveryActions
    .slice(0, 8)
    .forEach(
        function (recovery) {

            const actionText =
                formatText(
                    recovery.action
                );

            const reasonText =
                formatText(
                    recovery.reason
                );

            const priority =
                recovery.priority ||
                "MEDIUM";


            recoveryList.innerHTML += `

                <div
                    class="recovery-card"
                >

                    <h3>
                        🔄 ${recovery.bank}
                    </h3>

                    <strong>

                        ${actionText}

                    </strong>

                    <p>

                        ${reasonText}

                    </p>

                    <small>

                        Priority:
                        <strong>
                            ${priority}
                        </strong>

                    </small>

                </div>

            `;

        }
    );


        // ====================================
        // AI DECISION EXPLANATION
        // ====================================

       

    }

    catch (error) {

        console.error(
            "Dashboard Error:",
            error
        );

    }

}


// ========================================
// AI DECISION INTELLIGENCE
// ========================================

function updateAIExplanation(
    incidents,
    recoveryActions
) {

    const aiExplanation =
        document.getElementById(
            "aiExplanation"
        );


    if (!aiExplanation) {

        return;

    }


    aiExplanation.innerHTML = "";


    if (
        incidents.length === 0
    ) {

        aiExplanation.innerHTML = `

            <div class="ai-card">

                <h3>
                    🟢 System Healthy
                </h3>

                <p>

                    SwitchGuard AI analyzed
                    transaction patterns and
                    currently found no active
                    outage requiring intervention.

                </p>

            </div>

        `;

        return;

    } 


    incidents.forEach(
        function (incident) {

            const confidence =
                Number(
                    incident.confidence
                ).toFixed(1);


            const failureRate =
                (
                    Number(
                        incident.failure_rate
                    ) * 100
                ).toFixed(1);


            const concentration =
                (
                    Number(
                        incident.error_concentration
                    ) * 100
                ).toFixed(1);


            let severity =
                "Possible service degradation";


            if (
                incident.decision ===
                "HIGH_CONFIDENCE_OUTAGE"
            ) {

                severity =
                    "High probability of bank outage";

            }


            const matchingRecovery =
                recoveryActions
                    .filter(
                        recovery =>
                            recovery.bank ===
                            incident.bank
                    )
                    .slice(-1)[0];


            let recoveryText =
                "Monitoring recommended";


            if (
                matchingRecovery
            ) {

                recoveryText =
                    `${formatText(
                        matchingRecovery.action
                    )} because ${formatText(
                        matchingRecovery.reason
                    )}`;

            }


            aiExplanation.innerHTML += `

                <div class="ai-card">

                    <h3>

                        🧠 ${incident.bank}

                    </h3>

                    <p>

                        <strong>
                            AI Assessment:
                        </strong>

                        ${severity}.

                    </p>

                    <p>

                        📉 Failure Rate:
                        ${failureRate}%

                    </p>

                    <p>

                        ⚠ Dominant Error:
                        ${formatText(
                            incident.dominant_error
                        )}

                    </p>

                    <p>

                        🎯 Error Pattern
                        Concentration:
                        ${concentration}%

                    </p>

                    <p>

                        🔥 Outage Confidence:
                        ${confidence}%

                    </p>

                    <p>

                        🔄 Recommended Recovery:
                        ${recoveryText}

                    </p>

                </div>

            `;

        }
    );

}


// ========================================
// INCIDENT TIMELINE
// ========================================

async function loadIncidentTimeline() {

    try {

        const response =
            await fetch(INCIDENT_API);


        if (!response.ok) {

            throw new Error(
                "Failed to fetch incident data"
            );

        }


        const data =
            await response.json();


        const timeline =
            document.getElementById(
                "incidentTimeline"
            );


        if (!timeline) {

            return;

        }


        timeline.innerHTML = "";


        const history =
            data.incident_history || [];


        if (
            history.length === 0
        ) {

            timeline.innerHTML = `

                <p class="no-data">

                    No incident activity detected yet.

                </p>

            `;

            return;

        }


        history
            .slice(-10)
            .reverse()
            .forEach(
                function (update) {

                    let icon = "⚠";
                    let typeClass = "opened";
                    let bank = "";
                    let details = "";


                    if (
                        update.type ===
                        "OPENED"
                    ) {

                        icon = "⚠";
                        typeClass =
                            "opened";

                        bank =
                            update.incident.bank;

                        details =
                            `Incident opened with
                            ${Number(
                                update.incident.confidence
                            ).toFixed(1)}%
                            confidence`;

                    }


                    else if (
                        update.type ===
                        "ESCALATED"
                    ) {

                        icon = "⬆";
                        typeClass =
                            "escalated";

                        bank =
                            update.incident.bank;

                        details =
                            `Escalated to
                            HIGH CONFIDENCE OUTAGE`;

                    }


                    else if (
                        update.type ===
                        "RESOLVED"
                    ) {

                        icon = "✅";
                        typeClass =
                            "resolved";

                        bank =
                            update.bank;

                        details =
                            "Incident resolved";

                    }


                    timeline.innerHTML += `

                        <div
                            class="
                                timeline-item
                                ${typeClass}
                            "
                        >

                            <div
                                class="timeline-icon"
                            >

                                ${icon}

                            </div>


                            <div
                                class="timeline-content"
                            >

                                <h3>

                                    ${formatText(
                                        update.type
                                    )}

                                    — ${bank}

                                </h3>

                                <p>

                                    ${details}

                                </p>

                            </div>

                        </div>

                    `;

                }
            );

    }

    catch (error) {

        console.error(
            "Incident Timeline Error:",
            error
        );

    }

}


// ========================================
// FAILURE ANALYTICS CHART
// ========================================

function updateFailureChart(events) {

    // =====================================
    // FIND OR CREATE CHART CONTAINER
    // =====================================

    let chartContainer =
        document.getElementById(
            "failureChartContainer"
        );


    if (!chartContainer) {

        const canvas =
            document.getElementById(
                "failureChart"
            );


        if (canvas) {

            chartContainer =
                canvas.parentElement;

            chartContainer.id =
                "failureChartContainer";

        }

    }


    if (!chartContainer) {

        console.error(
            "Failure chart container not found"
        );

        return;

    }


    // =====================================
    // DESTROY OLD CHART
    // =====================================

    if (failureChart) {

        failureChart.destroy();

        failureChart = null;

    }


    // =====================================
    // COUNT FAILED TRANSACTIONS
    // =====================================

    const bankFailures = {};


    events.forEach(event => {

        const status =
            String(
                event.status || ""
            ).trim().toUpperCase();


        if (
            status === "FAILED" ||
            status === "FAILURE" ||
            status === "ERROR"
        ) {

            const bank =
                event.bank ||
                "Unknown Bank";


            if (!bankFailures[bank]) {

                bankFailures[bank] = 0;

            }


            bankFailures[bank]++;

        }

    });


    const labels =
        Object.keys(
            bankFailures
        );


    const failureCounts =
        Object.values(
            bankFailures
        );


    // =====================================
    // NO FAILURES
    // =====================================

    if (labels.length === 0) {

        chartContainer.innerHTML = `

            <div class="no-failure-chart">

                <div class="success-icon">
                    ●
                </div>

                <h3>
                    No Failed Transactions
                </h3>

                <p>
                    All monitored banks are operating normally.
                </p>

            </div>

        `;

        return;

    }


    // =====================================
    // SHOW CANVAS AGAIN
    // =====================================

    chartContainer.innerHTML = `

        <canvas
            id="failureChart"
        ></canvas>

    `;


    const newCanvas =
        document.getElementById(
            "failureChart"
        );


    if (!newCanvas) {

        console.error(
            "Unable to create failure chart canvas"
        );

        return;

    }


    const context =
        newCanvas.getContext(
            "2d"
        );


    // =====================================
    // CREATE CHART
    // =====================================

    failureChart =
        new Chart(

            context,

            {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Failed Transactions",

                            data:
                                failureCounts,

                            backgroundColor:
                                "rgba(239, 68, 68, 0.65)",

                            borderColor:
                                "rgba(220, 38, 38, 1)",

                            borderWidth:
                                2,

                            borderRadius:
                                8

                        }

                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {

                            display:
                                true

                        },

                        title: {

                            display:
                                true,

                            text:
                                "Bank-wise Failed Transactions"

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {

                                precision:
                                    0,

                                stepSize:
                                    1

                            }

                        }

                    }

                }

            }

        );

}

// ========================================
// LOAD EVERYTHING
// ========================================

async function loadAllData() {

    await loadDashboard();

    await loadTransactions();

    await loadIncidentTimeline();
await loadAIInsights();
}


// ========================================
// FIRST LOAD
// ========================================

loadAllData();


// ========================================
// AUTO REFRESH
// ========================================

setInterval(
    loadAllData,
    5000
);
// ========================================
// SCENARIO SIMULATION CONTROLS
// ========================================

async function runScenario(scenario) {

    try {

        console.log(
            "Running scenario:",
            scenario
        );

        const response = await fetch(
         `http://127.0.0.1:5000/api/simulate/${scenario}`
      );

        if (!response.ok) {

            throw new Error(
                "Failed to run simulation"
            );

        }


        const data =
            await response.json();


        console.log(
            "Simulation Result:",
            data
        );


        // Scenario names for display

        const scenarioNames = {

            normal:
                "NORMAL TRAFFIC",

            small_sample:
                "SMALL SAMPLE ANOMALY",

            partial_outage:
                "PARTIAL BANK OUTAGE",

            full_outage:
                "FULL BANK OUTAGE",

            mixed_failures:
                "MIXED FAILURES"

        };


        // Update scenario text

        const scenarioElement =
            document.getElementById(
                "currentScenario"
            );


        if (scenarioElement) {

            scenarioElement.textContent =
                scenarioNames[scenario] ||
                scenario.toUpperCase();

        }


        // IMPORTANT:
        // Wait a little before loading
        // the updated backend data

        await new Promise(
            resolve =>
                setTimeout(
                    resolve,
                    300
                )
        );


        // Reload everything

        await loadAllData();


        console.log(
            "Dashboard updated successfully"
        );

    }

    catch (error) {

        console.error(
            "Simulation Error:",
            error
        );


        alert(
            "Unable to run simulation. " +
            "Check Flask server."
        );

    }

}


// ========================================
// RESET SYSTEM
// ========================================

async function resetSystem() {

    try {

        console.log(
            "Resetting SwitchGuard AI system"
        );


        const response = await fetch(

            "http://127.0.0.1:5000/api/reset"

        );


        if (!response.ok) {

            throw new Error(
                "Failed to reset system"
            );

        }


        const data =
            await response.json();


        console.log(
            "Reset Result:",
            data
        );


        // Update scenario text

        document.getElementById(
            "currentScenario"
        ).textContent =
            "SYSTEM RESET";


        // Reload dashboard

        await loadAllData();


        console.log(
            "System reset successfully"
        );

    }

    catch (error) {

        console.error(
            "Reset Error:",
            error
        );

        alert(
            "Unable to reset system. " +
            "Make sure Flask server is running."
        );

    }

}
// ========================================
// BACKEND AI INSIGHTS
// ========================================

async function loadAIInsights() {

    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/ai-insights"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to fetch AI insights"
            );

        }


        const data =
            await response.json();


        const aiExplanation =
            document.getElementById(
                "aiExplanation"
            );


        // If AI section does not exist,
        // stop safely

        if (!aiExplanation) {

            return;

        }


        aiExplanation.innerHTML = "";


        const insights =
            data.insights || [];


        // ------------------------------------
        // SYSTEM HEALTHY
        // ------------------------------------

        if (insights.length === 0) {

            aiExplanation.innerHTML = `

                <div class="ai-card">

                    <h3>
                        🟢 AI System Assessment
                    </h3>

                    <p>

                        No active systemic outage
                        detected.

                    </p>

                    <p>

                        SwitchGuard AI recommends
                        continuing normal monitoring.

                    </p>

                </div>

            `;

            return;
 
        }


        // ------------------------------------
        // SHOW AI INSIGHTS
        // ------------------------------------

        insights.forEach(
            function (insight) {

                const assessment =
                    insight.ai_assessment || {};


                const reasons =
                    assessment.reasons || [];


                let reasonsHTML = "";


                reasons.forEach(
                    function (reason) {

                        reasonsHTML += `

                            <li>
                                ${reason}
                            </li>

                        `;

                    }
                );


                aiExplanation.innerHTML += `

                    <div class="ai-card">

                        <h3>

                            🧠 ${insight.bank}

                        </h3>


                        <p>

                            <strong>
                                Risk Level:
                            </strong>

                            ${assessment.risk_level}

                        </p>


                        <p>

                            <strong>
                                Outage Confidence:
                            </strong>

                            ${Number(
                                insight.confidence
                            ).toFixed(1)}%

                        </p>


                        <p>

                            <strong>
                                AI Decision:
                            </strong>

                            ${formatText(
                                insight.decision
                            )}

                        </p>


                        <p>

                            <strong>
                                Why did AI make
                                this decision?
                            </strong>

                        </p>


                        <ul>

                            ${reasonsHTML}

                        </ul>


                        <p>

                            <strong>
                                Recommended Action:
                            </strong>

                            ${assessment.recommendation}

                        </p>

                    </div>

                `;

            }
        );

    }

    catch (error) {

        console.error(
            "AI Insights Error:",
            error
        );

    }

}
async function simulateRecovery() {
    try {
        const response = await fetch(
            "http://127.0.0.1:5000/api/simulate-recovery",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Recovery simulation failed."
            );
        }

        alert(
            `Recovery completed!\n\n` +
            `Recovered Transactions: ${data.recovered_transactions}\n` +
            `Revenue Recovered: ₹${data.revenue_recovered}`
        );

        loadDashboard();

    } catch (error) {
        console.error(
            "Recovery simulation failed:",
            error
        );

        alert(
            "Recovery simulation failed: " + error.message
        );
    }
}
document.addEventListener("DOMContentLoaded", function () {

    const buttons = document.querySelectorAll(".scenario-buttons button");

    buttons.forEach(function (button) {

        button.addEventListener("click", function () {

            // Sab buttons ko normal karo
            buttons.forEach(function (btn) {
                btn.classList.remove("active");
            });

            // Clicked button active
            this.classList.add("active");

        });

    });

});