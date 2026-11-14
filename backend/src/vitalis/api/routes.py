from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from vitalis.core.config import Settings
from vitalis.domain.observations import HealthObservation
from vitalis.ingestion.simulator import ScenarioSimulator
from vitalis.storage.database import session_dependency
from vitalis.storage.repository import add_observation, list_observations, replace_observations

router = APIRouter()


async def get_session(request: Request):
    async for session in session_dependency(request.app.state.session_factory):
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/health")
async def health(request: Request) -> dict[str, str | bool]:
    settings: Settings = request.app.state.settings
    return {"status": "ok", "project": "VITALIS", "demo_mode": settings.demo_mode}


@router.get("/observations", response_model=list[HealthObservation])
async def get_observations(
    session: SessionDep,
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[HealthObservation]:
    return await list_observations(session, limit=limit)


@router.post("/observations", response_model=HealthObservation, status_code=201)
async def create_observation(
    observation: HealthObservation,
    session: SessionDep,
) -> HealthObservation:
    return await add_observation(session, observation)


@router.post("/demo/reset", response_model=list[HealthObservation])
async def reset_demo(request: Request, session: SessionDep) -> list[HealthObservation]:
    settings: Settings = request.app.state.settings
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Demo mode is disabled")
    observations = ScenarioSimulator(seed=settings.demo_seed).generate()
    await replace_observations(session, observations)
    return observations
