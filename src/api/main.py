"""FastAPI application with lifespan for ONA API."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.analysis.runner import run_full_analysis
from src.api.routes import router
from src.config.settings import get_settings
from src.data.generator import ONADataGenerator
from src.network.graph_builder import OrgGraphBuilder


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize data and run analysis on startup."""
    settings = get_settings()
    logger.info("Starting ONA API - generating data and running analysis")

    generator = ONADataGenerator(
        n_employees=settings.data.num_employees,
        n_months=settings.data.num_months,
        seed=settings.data.seed,
        slack_prob=settings.data.slack_prob,
        email_prob=settings.data.email_prob,
        meeting_prob=settings.data.meeting_prob,
    )
    employees_df = generator.generate_employees()
    interactions_df = generator.generate_interactions(employees_df)

    builder = OrgGraphBuilder()
    graph = builder.build_from_interactions(interactions_df, employees_df)

    result = run_full_analysis(
        graph,
        betweenness_threshold=settings.analysis.bottleneck_betweenness_threshold,
        knowledge_risk_threshold=settings.analysis.knowledge_risk_threshold,
        community_resolution=settings.analysis.community_resolution,
    )

    app.state.analysis = result
    logger.info("Analysis complete - API ready")

    yield

    logger.info("Shutting down ONA API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.api.title,
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
