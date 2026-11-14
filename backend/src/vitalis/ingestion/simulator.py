from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

from vitalis.domain.observations import HealthObservation


class ScenarioSimulator:
    """Deterministic illustrative data; values are not clinical thresholds or real telemetry."""

    scenario_id = "longitudinal-change-demo"
    crew_member_id = "crew-demo-01"

    def __init__(self, seed: int = 2026) -> None:
        self.seed = seed

    def generate(self) -> list[HealthObservation]:
        now = datetime.now(UTC).replace(hour=9, minute=0, second=0, microsecond=0)
        series: dict[str, tuple[str, list[float]]] = {
            "sleep_duration_hours": ("h", [7.4, 7.2, 7.5, 7.0, 6.8, 6.5, 6.3]),
            "fatigue_self_report_1_5": ("1–5 self-report scale", [2, 2, 2, 3, 3, 4, 4]),
            "workload_self_report_1_5": ("1–5 self-report scale", [2, 3, 2, 3, 3, 4, 4]),
            "mood_self_report_1_5": ("1–5 self-report scale", [4, 4, 4, 4, 3, 3, 3]),
            "exercise_duration_minutes": ("min", [40, 42, 38, 36, 32, 30, 28]),
        }
        observations: list[HealthObservation] = []
        for metric_id, (unit, values) in series.items():
            for day_index, value in enumerate(values):
                observed_at = now - timedelta(days=len(values) - day_index - 1)
                stable_id = uuid5(
                    NAMESPACE_URL,
                    f"vitalis:{self.scenario_id}:{self.seed}:{metric_id}:{day_index}",
                )
                observations.append(
                    HealthObservation(
                        id=stable_id,
                        crew_member_id=self.crew_member_id,
                        metric_id=metric_id,
                        value=value,
                        unit=unit,
                        observed_at=observed_at,
                        source="simulator",
                        synthetic=True,
                        context={
                            "scenario_id": self.scenario_id,
                            "scenario_label": "SYNTHETIC DEMO",
                            "mission_day": day_index + 1,
                            "note": "Illustrative data only; not a clinical threshold.",
                        },
                    )
                )
        return sorted(observations, key=lambda item: item.observed_at)
