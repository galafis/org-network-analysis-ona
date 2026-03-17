"""Synthetic organizational interaction data generator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

DEPARTMENTS = [
    "Engineering", "Product", "Sales", "Marketing",
    "HR", "Finance", "Operations", "Legal",
]
SENIORITY_LEVELS = ["Junior", "Mid", "Senior", "Lead", "Director", "VP"]
CHANNELS = ["slack", "email", "meeting"]


@dataclass
class EmployeeProfile:
    """Synthetic employee profile."""

    employee_id: str
    name: str
    department: str
    seniority: str
    tenure_years: float
    location: str


@dataclass
class Interaction:
    """A single interaction between two employees."""

    source_id: str
    target_id: str
    channel: str
    month: int
    weight: int = 1


class ONADataGenerator:
    """Generate synthetic organizational interaction data."""

    LOCATIONS = ["HQ-SP", "HQ-SP", "HQ-SP", "Remote-RJ", "Remote-BH", "Remote-CWB"]

    def __init__(
        self,
        n_employees: int = 200,
        n_months: int = 6,
        seed: int = 42,
        slack_prob: float = 0.15,
        email_prob: float = 0.10,
        meeting_prob: float = 0.08,
    ) -> None:
        self.n_employees = n_employees
        self.n_months = n_months
        self.seed = seed
        self.slack_prob = slack_prob
        self.email_prob = email_prob
        self.meeting_prob = meeting_prob
        self.rng = np.random.default_rng(seed)
        self.employees: list[EmployeeProfile] = []
        logger.info(
            "ONADataGenerator initialized: n={}, months={}, seed={}",
            n_employees, n_months, seed,
        )

    def generate_employees(self) -> pd.DataFrame:
        """Generate employee roster."""
        logger.info("Generating {} employee profiles", self.n_employees)
        first_names = [
            "Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda",
            "Gabriel", "Helena", "Igor", "Julia", "Lucas", "Mariana",
            "Nicolas", "Olivia", "Pedro", "Rafaela", "Samuel", "Tatiana",
            "Vitor", "Yasmin", "Andre", "Beatriz", "Caio", "Daniela",
        ]
        last_names = [
            "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira",
            "Costa", "Ferreira", "Rodrigues", "Almeida", "Nascimento",
            "Araujo", "Melo", "Barbosa", "Ribeiro", "Cardoso",
        ]

        dept_sizes = self._compute_dept_sizes()
        self.employees = []

        idx = 0
        for dept, size in dept_sizes.items():
            for _ in range(size):
                first = first_names[idx % len(first_names)]
                last = last_names[idx % len(last_names)]
                seniority = self.rng.choice(
                    SENIORITY_LEVELS,
                    p=[0.25, 0.30, 0.25, 0.12, 0.06, 0.02],
                )
                tenure = round(float(np.clip(self.rng.exponential(4.0), 0.3, 20.0)), 1)
                location = str(self.rng.choice(self.LOCATIONS))

                emp = EmployeeProfile(
                    employee_id=f"EMP-{idx + 1:04d}",
                    name=f"{first} {last}",
                    department=dept,
                    seniority=str(seniority),
                    tenure_years=tenure,
                    location=location,
                )
                self.employees.append(emp)
                idx += 1

        df = pd.DataFrame([
            {
                "employee_id": e.employee_id,
                "name": e.name,
                "department": e.department,
                "seniority": e.seniority,
                "tenure_years": e.tenure_years,
                "location": e.location,
            }
            for e in self.employees
        ])
        logger.info("Generated {} employees across {} departments", len(df), len(dept_sizes))
        return df

    def _compute_dept_sizes(self) -> dict[str, int]:
        """Compute department sizes ensuring they sum to n_employees."""
        weights = np.array([0.25, 0.12, 0.15, 0.10, 0.08, 0.10, 0.12, 0.08])
        raw = (weights * self.n_employees).astype(int)
        remainder = self.n_employees - raw.sum()
        for i in range(remainder):
            raw[i % len(raw)] += 1
        return dict(zip(DEPARTMENTS, raw.tolist(), strict=False))

    def generate_interactions(self, employees_df: pd.DataFrame) -> pd.DataFrame:
        """Generate interaction data across channels and months."""
        logger.info("Generating interactions for {} months", self.n_months)
        ids = employees_df["employee_id"].tolist()
        depts = dict(zip(
            employees_df["employee_id"], employees_df["department"],
            strict=False,
        ))
        seniorities = dict(zip(
            employees_df["employee_id"], employees_df["seniority"],
            strict=False,
        ))
        n = len(ids)
        interactions: list[dict[str, object]] = []

        for month in range(1, self.n_months + 1):
            for i in range(n):
                for j in range(i + 1, n):
                    src, tgt = ids[i], ids[j]
                    same_dept = depts[src] == depts[tgt]

                    # Higher interaction probability within department
                    dept_mult = 3.0 if same_dept else 1.0

                    # Seniority affects cross-dept connections
                    src_senior = seniorities[src] in ("Lead", "Director", "VP")
                    tgt_senior = seniorities[tgt] in ("Lead", "Director", "VP")
                    senior_mult = 1.5 if (src_senior or tgt_senior) and not same_dept else 1.0

                    for channel, base_prob in [
                        ("slack", self.slack_prob),
                        ("email", self.email_prob),
                        ("meeting", self.meeting_prob),
                    ]:
                        prob = min(base_prob * dept_mult * senior_mult, 0.95)
                        count = int(self.rng.poisson(prob * 5))
                        if count > 0:
                            interactions.append({
                                "source_id": src,
                                "target_id": tgt,
                                "channel": channel,
                                "month": month,
                                "weight": count,
                            })

        df = pd.DataFrame(interactions)
        logger.info("Generated {} interaction records", len(df))
        return df

    def save_all(self, output_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Generate and save all datasets."""
        if output_dir is None:
            output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)

        employees_df = self.generate_employees()
        interactions_df = self.generate_interactions(employees_df)

        employees_df.to_csv(output_dir / "employees.csv", index=False)
        interactions_df.to_csv(output_dir / "interactions.csv", index=False)
        logger.info("Data saved to {}", output_dir)
        return employees_df, interactions_df
