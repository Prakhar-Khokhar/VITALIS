# VITALIS
**Vital Intelligence and Tracking for Health Systems**

VITALIS is a crew-facing, longitudinal health situational-awareness and asynchronous handover prototype for long-duration space missions. It helps crew record observations, understand changes over time and in mission context, track follow-up, and prepare information for asynchronous medical handover. It is not a diagnostic or treatment system.

## Development status
- Python backend: FastAPI, Pydantic, SQLAlchemy, SQLite
- Hardware transports: PySerial-AsyncIO, Bleak, and Paho MQTT adapters
- Demo: reproducible, explicitly labelled synthetic observations; no hardware required
- Frontend: browser-based TypeScript workstream

## Safety and data integrity
- Synthetic data is never presented as real astronaut telemetry.
- No diagnosis, treatment advice, or invented clinical thresholds.
- Missing observations remain distinguishable from normal observations.
- Baselines and patterns must expose uncertainty and insufficient-data states.
- Environmental measurements are not individual crew measurements.

## Backend quick start
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn vitalis.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Install optional hardware transports with `python -m pip install -e ".[dev,hardware]"`.

See [backend/README.md](backend/README.md) and [docs/architecture.md](docs/architecture.md).
