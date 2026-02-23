"""
Initialize SQLite database from vcus.csv with computed metrics for Momentum and Velocity.

Tables created:
- vcus: Raw carbon credit data
- project_summary: Per-project aggregations
- project_activity_90d: 90-day and prior 90-day retirement counts
- project_metrics: Momentum, Velocity, and quadrant classification
- retirement_beneficiaries: Intermediary analysis
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "verra.db"
CSV_PATH = Path(__file__).parent.parent / "vcus.csv"


def clean_numeric_column(val):
    """Remove commas from numeric strings."""
    if pd.isna(val) or val == "":
        return None
    if isinstance(val, str):
        return float(val.replace(",", ""))
    return float(val)


def load_and_clean_csv() -> pd.DataFrame:
    """Load CSV and clean data."""
    print(f"Loading CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)

    # Clean numeric columns
    for col in ["Total Vintage Quantity", "Quantity Issued"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric_column)

    # Parse date columns
    date_cols = [
        "Issuance Date",
        "Vintage Start",
        "Vintage End",
        "Retirement/Cancellation Date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Sanitize column names for SQL (replace spaces, slashes, etc. with underscores)
    df.columns = (
        df.columns.str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
        .str.replace("&", "and")
    )

    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def init_database(df: pd.DataFrame):
    """Initialize SQLite database with tables and computed metrics."""
    print(f"Creating database at {DB_PATH}...")

    # Remove existing DB if it exists
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create vcus table from CSV
    print("Creating vcus table...")
    df.to_sql("vcus", conn, if_exists="replace", index=False)

    # Create indexes for performance
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_vcus_country ON vcus(Country_Area)")
    cursor.execute("CREATE INDEX idx_vcus_project_type ON vcus(Project_Type)")
    cursor.execute("CREATE INDEX idx_vcus_id ON vcus(ID)")
    cursor.execute("CREATE INDEX idx_vcus_issuance_date ON vcus(Issuance_Date)")
    cursor.execute("CREATE INDEX idx_vcus_retirement_date ON vcus(Retirement_Cancellation_Date)")

    # 2. Create project_summary table
    print("Creating project_summary table...")
    cursor.execute(
        """
    CREATE TABLE project_summary AS
    SELECT
        ID,
        Name,
        Country_Area,
        Project_Type,
        Methodology,
        COUNT(*) as num_issuances,
        SUM(CASE WHEN Retirement_Cancellation_Date IS NOT NULL THEN 1 ELSE 0 END) as num_retirements,
        SUM(Total_Vintage_Quantity) as total_vintage_quantity,
        SUM(Quantity_Issued) as total_quantity_issued,
        SUM(CASE WHEN Retirement_Cancellation_Date IS NOT NULL THEN Quantity_Issued ELSE 0 END) as total_retired,
        MIN(Issuance_Date) as first_issuance_date,
        MAX(Issuance_Date) as last_issuance_date,
        COUNT(DISTINCT Retirement_Beneficiary) as unique_retirement_beneficiaries
    FROM vcus
    GROUP BY ID, Name, Country_Area, Project_Type, Methodology
    """
    )

    # 3. Create project_activity_90d table
    print("Creating project_activity_90d table...")
    cursor.execute(
        """
    CREATE TABLE project_activity_90d AS
    SELECT
        ID,
        SUM(CASE WHEN Retirement_Cancellation_Date >= date('now', '-90 days')
                  THEN 1 ELSE 0 END) as recent_90d_count,
        SUM(CASE WHEN Retirement_Cancellation_Date >= date('now', '-180 days')
                  AND Retirement_Cancellation_Date < date('now', '-90 days')
                  THEN 1 ELSE 0 END) as prior_90d_count
    FROM vcus
    WHERE Retirement_Cancellation_Date IS NOT NULL
    GROUP BY ID
    """
    )

    # 4. Create project_metrics table with Momentum and Velocity
    print("Creating project_metrics table with computed metrics...")

    # First, get all activity data
    cursor.execute(
        """
    SELECT ID, recent_90d_count, prior_90d_count
    FROM project_activity_90d
    """
    )
    activity_data = cursor.fetchall()

    # Calculate z-scores
    recent_counts = [row[1] for row in activity_data]
    delta_values = [row[1] - row[2] for row in activity_data]

    recent_mean = np.mean(recent_counts) if recent_counts else 0
    recent_std = np.std(recent_counts) if recent_counts and np.std(recent_counts) > 0 else 1

    delta_mean = np.mean(delta_values) if delta_values else 0
    delta_std = np.std(delta_values) if delta_values and np.std(delta_values) > 0 else 1

    # Calculate z-scores for each project
    z_score_map = {}
    for row in activity_data:
        project_id = row[0]
        recent_90z = (row[1] - recent_mean) / recent_std if recent_std > 0 else 0
        delta_z = ((row[1] - row[2]) - delta_mean) / delta_std if delta_std > 0 else 0
        z_score_map[project_id] = (recent_90z, delta_z)

    # Create the metrics table
    cursor.execute(
        """
    CREATE TABLE project_metrics (
        ID INTEGER PRIMARY KEY,
        recent_90d_count INTEGER,
        prior_90d_count INTEGER,
        recent_90z REAL,
        delta_z REAL,
        velocity REAL,
        quadrant TEXT
    )
    """
    )

    # Populate metrics
    cursor.execute("SELECT ID, total_quantity_issued FROM project_summary")
    for project_id, total_qty in cursor.fetchall():
        if total_qty is None or total_qty == 0:
            total_qty = 1  # Avoid division by zero

        if project_id in z_score_map:
            recent_90z, delta_z = z_score_map[project_id]
            recent_90d_count, prior_90d_count = [
                row[1:3] for row in activity_data if row[0] == project_id
            ][0]

            # Velocity = (recent_90 / total_qty) * 10,000
            velocity = (recent_90d_count / total_qty) * 10000

            # Quadrant classification
            # High momentum = delta_z > 0, High velocity = velocity > median
            velocity_median = np.median([
                (row[1] / total_qty) * 10000
                for row in activity_data
                if row[0] in z_score_map
            ])

            high_momentum = delta_z > 0
            high_velocity = velocity > velocity_median

            if high_momentum and high_velocity:
                quadrant = "Hot"
            elif high_momentum and not high_velocity:
                quadrant = "Emerging"
            elif not high_momentum and high_velocity:
                quadrant = "Stable"
            else:
                quadrant = "Dormant"

            cursor.execute(
                """
            INSERT INTO project_metrics
            (ID, recent_90d_count, prior_90d_count, recent_90z, delta_z, velocity, quadrant)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (project_id, recent_90d_count, prior_90d_count, recent_90z, delta_z, velocity, quadrant),
            )

    # 5. Create retirement_beneficiaries table for intermediary analysis
    print("Creating retirement_beneficiaries table...")
    cursor.execute(
        """
    CREATE TABLE retirement_beneficiaries AS
    SELECT
        ID,
        Retirement_Beneficiary,
        COUNT(*) as retirement_count,
        SUM(Quantity_Issued) as quantity_retired
    FROM vcus
    WHERE Retirement_Cancellation_Date IS NOT NULL
      AND Retirement_Beneficiary IS NOT NULL
      AND Retirement_Beneficiary != ''
    GROUP BY ID, Retirement_Beneficiary
    ORDER BY ID, retirement_count DESC
    """
    )

    # Commit all changes
    conn.commit()

    # Print summary statistics
    cursor.execute("SELECT COUNT(*) FROM project_summary")
    num_projects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT Country_Area) FROM project_summary")
    num_countries = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_quantity_issued) FROM project_summary")
    total_credits = cursor.fetchone()[0]

    print(f"\nDatabase initialized successfully!")
    print(f"  - {num_projects} unique projects")
    print(f"  - {num_countries} countries")
    print(f"  - {total_credits:,.0f} total credits issued")

    # Quadrant distribution
    cursor.execute("SELECT quadrant, COUNT(*) FROM project_metrics GROUP BY quadrant")
    print("\nQuadrant Distribution:")
    for quadrant, count in cursor.fetchall():
        print(f"  - {quadrant}: {count} projects")

    conn.close()


if __name__ == "__main__":
    df = load_and_clean_csv()
    init_database(df)
    print(f"\nDatabase ready at {DB_PATH}")
