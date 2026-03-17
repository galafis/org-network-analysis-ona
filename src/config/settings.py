"""Application settings with Pydantic BaseSettings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Data generation settings."""

    seed: int = 42
    num_employees: int = 200
    num_months: int = 6
    slack_prob: float = 0.15
    email_prob: float = 0.10
    meeting_prob: float = 0.08

    model_config = {"env_prefix": "DATA_"}


class AnalysisSettings(BaseSettings):
    """Analysis thresholds."""

    key_person_percentile: int = 90
    bottleneck_betweenness_threshold: float = 0.15
    knowledge_risk_threshold: float = 0.70
    community_resolution: float = 1.0

    model_config = {"env_prefix": "ANALYSIS_"}


class APISettings(BaseSettings):
    """API configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    title: str = "ONA - Organizational Network Analysis"

    model_config = {"env_prefix": "API_"}


class AppSettings(BaseSettings):
    """Root application settings."""

    project_root: Path = Path(__file__).resolve().parent.parent.parent
    data: DataSettings = DataSettings()
    analysis: AnalysisSettings = AnalysisSettings()
    api: APISettings = APISettings()

    model_config = {"env_prefix": "APP_"}


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached singleton settings."""
    return AppSettings()
