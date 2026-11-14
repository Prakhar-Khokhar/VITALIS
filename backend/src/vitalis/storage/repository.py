from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from vitalis.domain.observations import HealthObservation
from vitalis.storage.models import ObservationRecord


def to_record(observation: HealthObservation) -> ObservationRecord:
    return ObservationRecord(
        id=str(observation.id),
        crew_member_id=observation.crew_member_id,
        metric_id=observation.metric_id,
        value=observation.value,
        unit=observation.unit,
        observed_at=observation.observed_at.isoformat(),
        source=observation.source,
        synthetic=observation.synthetic,
        confidence=observation.confidence,
        context=observation.context,
    )


def to_observation(record: ObservationRecord) -> HealthObservation:
    return HealthObservation(
        id=record.id,
        crew_member_id=record.crew_member_id,
        metric_id=record.metric_id,
        value=record.value,
        unit=record.unit,
        observed_at=record.observed_at,
        source=record.source,
        synthetic=record.synthetic,
        confidence=record.confidence,
        context=record.context,
    )


async def add_observation(
    session: AsyncSession,
    observation: HealthObservation,
) -> HealthObservation:
    record = to_record(observation)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return to_observation(record)


async def list_observations(
    session: AsyncSession,
    limit: int = 200,
) -> list[HealthObservation]:
    result = await session.execute(
        select(ObservationRecord)
        .order_by(ObservationRecord.observed_at.desc())
        .limit(limit)
    )
    return [to_observation(record) for record in result.scalars()]


async def replace_observations(
    session: AsyncSession,
    observations: list[HealthObservation],
) -> None:
    await session.execute(delete(ObservationRecord))
    session.add_all(to_record(item) for item in observations)
    await session.commit()


async def count_observations(session: AsyncSession) -> int:
    from sqlalchemy import func

    result = await session.execute(select(func.count()).select_from(ObservationRecord))
    return int(result.scalar_one())
