"""
Metrics computation for Momentum and Velocity analysis.

Momentum = f(recent_90z, delta_z)
- recent_90z: z-score of recent 90-day retirement activity
- delta_z: z-score of change in activity between prior and recent 90-day windows

Velocity = (recent_90 / qty_issued) * 10,000
- Normalized activity metric to compare projects fairly
"""

import sqlite3
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional

DB_PATH = Path(__file__).parent.parent / "verra.db"


def get_project_metrics(project_id: int) -> Optional[Dict]:
    """Get computed metrics for a single project."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT
        ID,
        recent_90d_count,
        prior_90d_count,
        recent_90z,
        delta_z,
        velocity,
        quadrant
    FROM project_metrics
    WHERE ID = ?
    """,
        (project_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "project_id": row[0],
        "recent_90d_count": row[1],
        "prior_90d_count": row[2],
        "recent_90z": row[3],
        "delta_z": row[4],
        "velocity": row[5],
        "quadrant": row[6],
    }


def get_quadrant_projects(quadrant: str) -> list:
    """Get all projects in a specific quadrant."""
    valid_quadrants = ["Hot", "Emerging", "Stable", "Dormant"]
    if quadrant not in valid_quadrants:
        raise ValueError(f"Quadrant must be one of {valid_quadrants}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT m.ID, p.Name, p.Country_Area, m.velocity, m.delta_z, m.quadrant
    FROM project_metrics m
    JOIN project_summary p ON m.ID = p.ID
    WHERE m.quadrant = ?
    ORDER BY m.velocity DESC
    """,
        (quadrant,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "project_id": row[0],
            "name": row[1],
            "country": row[2],
            "velocity": row[3],
            "momentum": row[4],
            "quadrant": row[5],
        }
        for row in rows
    ]


def get_hot_projects(limit: int = 10) -> list:
    """Get top projects by velocity in the Hot quadrant."""
    return get_quadrant_projects("Hot")[:limit]


def get_emerging_projects(limit: int = 10) -> list:
    """Get emerging projects (high momentum, low velocity) - pre-trade positioning."""
    return get_quadrant_projects("Emerging")[:limit]


def get_slowing_projects(limit: int = 10) -> list:
    """Get projects with negative momentum (slowing down)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT m.ID, p.Name, p.Country_Area, m.velocity, m.delta_z, m.quadrant
    FROM project_metrics m
    JOIN project_summary p ON m.ID = p.ID
    WHERE m.delta_z < 0
    ORDER BY m.delta_z ASC
    LIMIT ?
    """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "project_id": row[0],
            "name": row[1],
            "country": row[2],
            "velocity": row[3],
            "momentum": row[4],
            "quadrant": row[5],
        }
        for row in rows
    ]


def get_retirement_beneficiaries(project_id: int) -> list:
    """Get intermediaries/beneficiaries retiring credits for a project."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT Retirement_Beneficiary, retirement_count, quantity_retired
    FROM retirement_beneficiaries
    WHERE ID = ?
    ORDER BY retirement_count DESC
    """,
        (project_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "beneficiary": row[0],
            "retirement_count": row[1],
            "quantity_retired": row[2],
        }
        for row in rows
    ]


def get_metrics_summary() -> Dict:
    """Get overall metrics summary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total projects in each quadrant
    cursor.execute(
        "SELECT quadrant, COUNT(*) FROM project_metrics GROUP BY quadrant"
    )
    quadrant_counts = {row[0]: row[1] for row in cursor.fetchall()}

    # Velocity stats
    cursor.execute("SELECT AVG(velocity), MAX(velocity), MIN(velocity) FROM project_metrics")
    avg_velocity, max_velocity, min_velocity = cursor.fetchone()

    # Delta_z (momentum) stats
    cursor.execute(
        "SELECT AVG(delta_z), MAX(delta_z), MIN(delta_z) FROM project_metrics"
    )
    avg_momentum, max_momentum, min_momentum = cursor.fetchone()

    # Project count
    cursor.execute("SELECT COUNT(*) FROM project_summary")
    total_projects = cursor.fetchone()[0]

    # Country count
    cursor.execute("SELECT COUNT(DISTINCT Country_Area) FROM project_summary")
    total_countries = cursor.fetchone()[0]

    # Total credits issued
    cursor.execute("SELECT SUM(total_quantity_issued) FROM project_summary")
    total_credits_issued = cursor.fetchone()[0]

    # Total credits retired
    cursor.execute("SELECT SUM(total_retired) FROM project_summary")
    total_credits_retired = cursor.fetchone()[0]

    conn.close()

    return {
        "quadrant_distribution": quadrant_counts,
        "velocity": {
            "average": avg_velocity,
            "max": max_velocity,
            "min": min_velocity,
        },
        "momentum": {
            "average": avg_momentum,
            "max": max_momentum,
            "min": min_momentum,
        },
        "total_projects": total_projects,
        "total_countries": total_countries,
        "total_credits_issued": total_credits_issued,
        "total_credits_retired": total_credits_retired,
    }


if __name__ == "__main__":
    # Example usage
    summary = get_metrics_summary()
    print("Metrics Summary:")
    print(f"  Projects: {summary['total_projects']}")
    print(f"  Countries: {summary['total_countries']}")
    print(f"  Credits Issued: {summary['total_credits_issued']:,.0f}")
    print(f"\nQuadrant Distribution: {summary['quadrant_distribution']}")
    print(f"\nTop Hot Projects:")
    for proj in get_hot_projects(5):
        print(
            f"  - {proj['name']} ({proj['country']}): Velocity={proj['velocity']:.1f}, Momentum={proj['momentum']:.2f}"
        )
