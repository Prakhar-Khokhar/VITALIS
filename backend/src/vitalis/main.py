from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vitalis.api.routes import router
from vitalis.core.config import Settings
from vitalis.ingestion.simulator import ScenarioSimulator
from vitalis.storage.database import build_database, initialize_database
from vitalis.storage.repository import count_observations, replace_observations


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine, session_factory = build_database(app_settings.database_url)
        app.state.engine = engine
        app.state.session_factory = session_factory
        app.state.settings = app_settings
        await initialize_database(engine)
        if app_settings.demo_mode:
            async with session_factory() as session:
                if await count_observations(session) == 0:
                    scenario = ScenarioSimulator(seed=app_settings.demo_seed).generate()
                    await replace_observations(session, scenario)
        yield
        await engine.dispose()

    app = FastAPI(
        title="VITALIS API",
        description=(
            "Crew-health situational-awareness prototype. "
            "This API records observations; it does not diagnose or prescribe."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
