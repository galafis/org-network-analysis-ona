"""Tests for application settings."""

from __future__ import annotations

from src.config.settings import AppSettings, get_settings


class TestSettings:
    """Test suite for AppSettings and get_settings."""

    def test_get_settings_returns_app_settings(self) -> None:
        """get_settings must return an AppSettings instance."""
        settings = get_settings()
        assert isinstance(settings, AppSettings)

    def test_singleton_same_object(self) -> None:
        """get_settings should return the same cached object each time."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_default_values(self) -> None:
        """Default settings must match expected baseline values."""
        settings = get_settings()
        assert settings.data.seed == 42
        assert settings.data.num_employees == 200
        assert settings.data.num_months == 6
        assert settings.analysis.bottleneck_betweenness_threshold == 0.15
        assert settings.analysis.community_resolution == 1.0
        assert settings.api.port == 8000

    def test_nested_settings_accessible(self) -> None:
        """Nested settings objects must be accessible with correct types."""
        settings = get_settings()
        assert isinstance(settings.data.slack_prob, float)
        assert isinstance(settings.analysis.key_person_percentile, int)
        assert isinstance(settings.api.title, str)
        assert len(settings.api.title) > 0

    def test_data_settings_probabilities(self) -> None:
        """Channel probabilities should be between 0 and 1."""
        settings = get_settings()
        assert 0.0 < settings.data.slack_prob < 1.0
        assert 0.0 < settings.data.email_prob < 1.0
        assert 0.0 < settings.data.meeting_prob < 1.0
