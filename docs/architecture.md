# VITALIS architecture decisions

## Product boundary
VITALIS is a crew-facing longitudinal health situational-awareness and asynchronous handover prototype. It records sparse observations, preserves provenance and context, supports review and follow-up, and prepares explicitly released handover information. It does not diagnose, prescribe treatment, or claim clinical validation. The prototype introduces no universal medical thresholds.

## Initial architecture
- FastAPI exposes a versioned `/api/v1` HTTP API.
- Pydantic validates incoming and outgoing observation contracts.
- Domain logic remains independent of transport and persistence.
- SQLAlchemy 2.x with SQLite provides initial persistence.
- Browser frontend uses HTTP polling initially.
- A deterministic simulator supplies labelled synthetic observations.
- Modular monolith; no microservices, Kubernetes, cloud dependency, or mandatory WebSockets in the MVP.

## Observation contract
Every source produces the same `HealthObservation`: ID, crew member ID, metric ID, value, unit, timezone-aware timestamp, source/provenance, synthetic flag, optional data-confidence metadata, and context. Environmental observations remain identifiable as environmental and are never silently assigned to a crew member.

The current Pydantic value union preserves exact boolean observations. The future baseline engine must explicitly exclude booleans from numeric calculations because Python treats `bool` as a subclass of `int`.

## Hardware integration
Hardware is not part of the MVP demonstration, but real Python transport adapters are included behind a common async source protocol:
- PySerial-AsyncIO: USB/UART streams, suitable for an ESP32 emitting newline-delimited JSON.
- Bleak: Bluetooth LE GATT notifications; address and characteristic UUID are configuration inputs.
- Paho MQTT: telemetry from a sensor gateway or broker.

These are optional dependencies and are not started automatically. No sensor-specific UUIDs, medical-device protocols, or ESP32 firmware are assumed. Device payloads must validate against the canonical observation contract.

## Persistence and growth
SQLite is the initial database. SQLAlchemy and a repository boundary keep domain logic independent of the database engine. As the product grows, keep raw observations, derived assessments/evidence, follow-up actions, handover packets/delivery state, and audit events separate. The initial scaffold persists observations only.

`Base.metadata.create_all()` is a bootstrap, not a migration mechanism, and does not alter existing columns. SQLite files created under the earlier foundation schema can retain a `NOT NULL` `crew_member_id` constraint and are not automatically compatible with environmental observations. A local database confirmed to contain only disposable synthetic demo data may be recreated; a database that may contain real user or crew-health data requires backup and a reviewed migration before reuse.

## Demo and privacy
The simulator produces reproducible, clearly labelled illustrative data, not medical thresholds or real astronaut telemetry. Crew-private notes must remain separate from information explicitly released in a handover. The MVP may demonstrate this behavior without claiming production-grade authentication or authorization.
