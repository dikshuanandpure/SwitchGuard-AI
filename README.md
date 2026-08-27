# SwitchGuard-AI

## AI-Powered Real-Time Payment Failure Detection and Revenue Recovery System

SwitchGuard-AI is an intelligent system designed to detect payment failures in real time, identify failure patterns, simulate incidents, and recommend or trigger recovery actions to reduce potential revenue loss.

## Features

- Real-time payment event monitoring
- Payment failure and outage detection
- Failure clustering and pattern identification
- Incident detection and analysis
- AI-based failure explanation
- Recovery action recommendations
- Automated recovery simulation
- Revenue loss analysis
- Real-time incident simulation
- Scenario-based testing

## Project Architecture

The project is organized into the following modules:

### Backend
Handles the core intelligence and recovery logic.

- `ai_explainer.py` – Explains detected failures
- `ai_recovery_agent.py` – Generates recovery recommendations
- `failure_cluster.py` – Groups similar failure events
- `incident_engine.py` – Detects and manages incidents
- `incidentSimulator.py` – Simulates incidents
- `outage_detector.py` – Detects possible outages
- `recovery_engine.py` – Executes recovery logic
- `recoverySimulator.py` – Simulates recovery actions

### Frontend

Provides the user interface for monitoring incidents and system activity.

- `index.html`
- `script.js`
- `style.css`

### Simulator

Generates and processes simulated payment events.

- `event_generator.py`
- `realtime_runner.py`
- `scenarios.py`

### Tests

- `test_recovery.py` – Tests recovery functionality

## Technology Stack

- Python
- Flask
- JavaScript
- HTML
- CSS

## How It Works

1. Payment events are generated or received by the system.
2. The system monitors events for failures or unusual patterns.
3. Failure events are clustered and analyzed.
4. The incident engine determines whether an incident or outage has occurred.
5. The AI components explain the failure and suggest recovery actions.
6. Recovery logic is executed or simulated.
7. Results can be monitored through the frontend.

## Running the Project

Clone the repository:

```bash
git clone <repository-url>
cd SwitchGuard-AI
