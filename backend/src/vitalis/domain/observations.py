from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ObservationSourceKind = Literal[
    "simulator", "manual", "serial", "ble", "mqtt", "nasa_environment"
]


class HealthObservation(BaseModel):
    """A timestamped observation with explicit provenance; not a clinical assessment."""

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    crew_member_id: str | None = Field(default=None, min_length=1, max_length=80)
    metric_id: str = Field(min_length=1, max_length=100)
    value: float | str | bool
    unit: str = Field(max_length=40)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: ObservationSourceKind = "manual"
    synthetic: bool = False
    # Confidence describes source/data quality only, never clinical certainty.
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("observed_at")
    @classmethod
    def normalize_timestamp_to_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must include a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_observation_scope(self):
        if self.source == "nasa_environment" and self.crew_member_id is not None:
            raise ValueError("environmental observations must not be assigned to a crew member")
        if self.source != "nasa_environment" and self.crew_member_id is None:
            raise ValueError("crew_member_id is required for crew observations")
        if self.source == "simulator" and not self.synthetic:
            raise ValueError("simulator observations must be marked synthetic")
        return self
