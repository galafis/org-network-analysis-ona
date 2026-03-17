"""Tests for ONADataGenerator."""

from __future__ import annotations

import pandas as pd

from src.data.generator import CHANNELS, DEPARTMENTS, SENIORITY_LEVELS, ONADataGenerator


class TestONADataGenerator:
    """Test suite for the synthetic data generator."""

    def test_employees_shape(self, employees_df: pd.DataFrame) -> None:
        """Employee DataFrame must have exactly n_employees rows."""
        assert len(employees_df) == 50

    def test_interactions_non_empty(self, interactions_df: pd.DataFrame) -> None:
        """Interactions DataFrame must have at least one row."""
        assert len(interactions_df) > 0

    def test_employee_columns(self, employees_df: pd.DataFrame) -> None:
        """Employee DataFrame must contain the expected columns."""
        expected = {"employee_id", "name", "department", "seniority", "tenure_years", "location"}
        assert set(employees_df.columns) == expected

    def test_interaction_columns(self, interactions_df: pd.DataFrame) -> None:
        """Interaction DataFrame must contain the expected columns."""
        expected = {"source_id", "target_id", "channel", "month", "weight"}
        assert set(interactions_df.columns) == expected

    def test_employee_id_format(self, employees_df: pd.DataFrame) -> None:
        """All employee IDs must follow the EMP-XXXX format."""
        for eid in employees_df["employee_id"]:
            assert eid.startswith("EMP-")
            assert len(eid) == 8
            assert eid[4:].isdigit()

    def test_departments_valid(self, employees_df: pd.DataFrame) -> None:
        """All departments must come from the DEPARTMENTS constant."""
        for dept in employees_df["department"].unique():
            assert dept in DEPARTMENTS

    def test_seniority_valid(self, employees_df: pd.DataFrame) -> None:
        """All seniority values must come from SENIORITY_LEVELS."""
        for sen in employees_df["seniority"].unique():
            assert sen in SENIORITY_LEVELS

    def test_channels_valid(self, interactions_df: pd.DataFrame) -> None:
        """All channels must be slack, email, or meeting."""
        for ch in interactions_df["channel"].unique():
            assert ch in CHANNELS

    def test_months_in_range(self, interactions_df: pd.DataFrame) -> None:
        """Month values must be in range [1, n_months]."""
        months = interactions_df["month"].unique()
        for m in months:
            assert 1 <= m <= 2

    def test_weights_positive(self, interactions_df: pd.DataFrame) -> None:
        """All interaction weights must be positive integers."""
        assert (interactions_df["weight"] > 0).all()
        assert interactions_df["weight"].dtype in ("int64", "int32", "int")

    def test_reproducibility_same_seed(self) -> None:
        """Same seed must produce identical employee data."""
        gen_a = ONADataGenerator(n_employees=20, n_months=1, seed=77)
        gen_b = ONADataGenerator(n_employees=20, n_months=1, seed=77)
        df_a = gen_a.generate_employees()
        df_b = gen_b.generate_employees()
        pd.testing.assert_frame_equal(df_a, df_b)

    def test_different_seed_different_data(self) -> None:
        """Different seeds should produce different data."""
        gen_a = ONADataGenerator(n_employees=20, n_months=1, seed=10)
        gen_b = ONADataGenerator(n_employees=20, n_months=1, seed=11)
        df_a = gen_a.generate_employees()
        df_b = gen_b.generate_employees()
        # At least one column should differ (seniority is random)
        assert not df_a["seniority"].equals(df_b["seniority"])

    def test_save_all_writes_csvs(self, tmp_path) -> None:
        """save_all must write employees.csv and interactions.csv."""
        gen = ONADataGenerator(n_employees=10, n_months=1, seed=42)
        emp_df, int_df = gen.save_all(output_dir=tmp_path)
        assert (tmp_path / "employees.csv").exists()
        assert (tmp_path / "interactions.csv").exists()
        loaded_emp = pd.read_csv(tmp_path / "employees.csv")
        assert len(loaded_emp) == 10
