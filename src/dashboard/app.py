"""Streamlit dashboard for Organizational Network Analysis."""

from __future__ import annotations

from typing import Any

import streamlit as st
from loguru import logger

from src.analysis.runner import FullAnalysisResult, run_full_analysis
from src.config.settings import get_settings
from src.data.generator import ONADataGenerator
from src.network.centrality import CentralityAnalyzer
from src.network.graph_builder import OrgGraphBuilder

st.set_page_config(
    page_title="ONA Dashboard",
    layout="wide",
)


@st.cache_resource
def load_analysis() -> FullAnalysisResult:
    """Generate data and run full analysis pipeline (cached)."""
    settings = get_settings()
    logger.info("Loading analysis data for dashboard")

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

    return run_full_analysis(
        graph,
        betweenness_threshold=settings.analysis.bottleneck_betweenness_threshold,
        knowledge_risk_threshold=settings.analysis.knowledge_risk_threshold,
        community_resolution=settings.analysis.community_resolution,
    )


def main() -> None:
    """Render the Streamlit dashboard."""
    st.title("Organizational Network Analysis (ONA)")

    result = load_analysis()

    pages: dict[str, Any] = {
        "Overview": render_overview,
        "Centrality": render_centrality,
        "Bottlenecks": render_bottlenecks,
        "Communities": render_communities,
        "Recommendations": render_recommendations,
    }

    selection = st.sidebar.radio("Navigate", list(pages.keys()))
    pages[selection](result)


def render_overview(result: FullAnalysisResult) -> None:
    """Render the overview page with graph statistics."""
    st.header("Network Overview")

    stats = result.graph_stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodes", stats.n_nodes)
    col2.metric("Edges", stats.n_edges)
    col3.metric("Density", f"{stats.density:.4f}")
    col4.metric("Avg Clustering", f"{stats.avg_clustering:.4f}")

    col5, col6, col7 = st.columns(3)
    col5.metric("Connected Components", stats.n_connected_components)
    col6.metric("Avg Degree", f"{stats.avg_degree:.2f}")
    col7.metric("Diameter", stats.diameter if stats.diameter is not None else "N/A")

    st.subheader("Risk Score")
    risk = result.recommendations.risk_score
    st.progress(min(risk / 100, 1.0))
    st.write(f"**{risk}/100** - {result.recommendations.summary}")


def render_centrality(result: FullAnalysisResult) -> None:
    """Render the centrality analysis page."""
    st.header("Centrality Analysis")

    analyzer = CentralityAnalyzer()
    df = analyzer.get_centrality_dataframe(result.centrality)

    st.subheader("Top Connectors (Degree)")
    top_connectors = df.nlargest(10, "degree")[
        ["employee_id", "degree", "composite_score"]
    ]
    st.dataframe(top_connectors, use_container_width=True)

    st.subheader("Top Brokers (Betweenness)")
    top_brokers = df.nlargest(10, "betweenness")[
        ["employee_id", "betweenness", "composite_score"]
    ]
    st.dataframe(top_brokers, use_container_width=True)

    st.subheader("Top Influencers (Eigenvector)")
    top_influencers = df.nlargest(10, "eigenvector")[
        ["employee_id", "eigenvector", "composite_score"]
    ]
    st.dataframe(top_influencers, use_container_width=True)

    st.subheader("Centrality Distribution")
    st.bar_chart(df.set_index("employee_id")["composite_score"].nlargest(20))


def render_bottlenecks(result: FullAnalysisResult) -> None:
    """Render the bottleneck detection page."""
    st.header("Bottleneck Detection")

    bottlenecks = result.bottleneck.bottlenecks
    if bottlenecks:
        st.subheader(f"Detected Bottlenecks ({len(bottlenecks)})")
        rows = [
            {
                "Employee": b.employee_id,
                "Betweenness": b.betweenness,
                "Degree": b.degree,
                "Depts Connected": b.departments_connected,
                "Risk Level": b.risk_level.value.upper(),
                "Reason": b.reason,
            }
            for b in bottlenecks
        ]
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No significant bottlenecks detected.")

    st.subheader("Knowledge Risk Assessment")
    high_risk = [
        k for k in result.bottleneck.knowledge_risks
        if k.risk_level.value in ("critical", "high")
    ]
    if high_risk:
        st.write(f"**{len(high_risk)}** employees with high/critical knowledge risk")
        risk_rows = [
            {
                "Employee": k.employee_id,
                "Department": k.department,
                "Seniority": k.seniority,
                "Score": k.knowledge_score,
                "Risk": k.risk_level.value.upper(),
                "Replacement": k.replacement_difficulty,
            }
            for k in high_risk[:20]
        ]
        st.dataframe(risk_rows, use_container_width=True)
    else:
        st.info("No high knowledge risk employees detected.")

    st.subheader("Department Silos")
    silos = result.bottleneck.department_silos
    if silos:
        silo_rows = [
            {
                "Department": str(s["department"]),
                "Employees": s["n_employees"],
                "Internal Edges": s["internal_edges"],
                "External Edges": s["external_edges"],
                "Isolation Ratio": s["isolation_ratio"],
                "Is Silo": s["is_silo"],
            }
            for s in silos
        ]
        st.dataframe(silo_rows, use_container_width=True)


def render_communities(result: FullAnalysisResult) -> None:
    """Render the community detection page."""
    st.header("Community Detection")

    community = result.community
    col1, col2 = st.columns(2)
    col1.metric("Communities Detected", community.n_communities)
    col2.metric("Modularity", f"{community.modularity:.4f}")

    st.subheader("Community Details")
    for c in community.communities:
        label = f"Community {c.community_id} ({c.size} members)"
        with st.expander(label):
            st.write(f"**Dominant Department:** {c.dominant_department}")
            st.write(f"**Cross-Department:** {'Yes' if c.cross_department else 'No'}")
            st.write("**Department Breakdown:**")
            st.bar_chart(c.departments)
            st.write(f"**Members:** {', '.join(c.members[:30])}")
            if len(c.members) > 30:
                st.write(f"... and {len(c.members) - 30} more")


def render_recommendations(result: FullAnalysisResult) -> None:
    """Render the recommendations page."""
    st.header("Executive Recommendations")

    exec_report = result.recommendations
    st.subheader("Overall Risk Assessment")
    st.progress(min(exec_report.risk_score / 100, 1.0))
    st.write(exec_report.summary)

    st.subheader("Recommendations")
    for rec in exec_report.recommendations:
        priority_colors = {"high": "red", "medium": "orange", "low": "blue"}
        color = priority_colors.get(rec.priority.value, "gray")
        st.markdown(
            f"**[{rec.priority.value.upper()}]** :{color}[{rec.category}] "
            f"- {rec.title}"
        )
        st.write(rec.description)
        if rec.action_items:
            st.write("**Action Items:**")
            for item in rec.action_items:
                st.write(f"- {item}")
        st.divider()


if __name__ == "__main__":
    main()
