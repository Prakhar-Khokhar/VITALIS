# VITALIS Python backend

Requires Python 3.11+. No hardware is needed for the simulator or API.

## Install and run
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn vitalis.main:app --reload
```

The API is at `http://127.0.0.1:8000`; interactive docs are at `/docs`. Demo mode is enabled by default and seeds a local `vitalis.db` SQLite database.

For optional hardware transports: `python -m pip install -e ".[dev,hardware]"`. This installs PySerial-AsyncIO (USB/UART), Bleak (Bluetooth LE), and Paho MQTT. They are not started automatically.

## Configuration
Copy `.env.example` to `.env`. Variables use the `VITALIS_` prefix.

## API
- `GET /api/v1/health`
- `GET /api/v1/observations`
- `POST /api/v1/observations`
- `POST /api/v1/demo/reset` (demo mode only)

## Device payload contract
Serial, BLE, and MQTT accept JSON objects matching the observation contract. Minimal example:
```json
{
  "crew_member_id": "crew-demo-01",
  "metric_id": "sleep_duration_hours",
  "value": 7.2,
  "unit": "h",
  "observed_at": "2026-11-14T09:00:00Z",
  "context": {"mission_day": 18}
}
```
Adapters set transport provenance and mark incoming device data non-synthetic. Device identity, metric mapping, and calibration must be configured before real hardware is connected. This is not a sensor specification or clinical protocol.
