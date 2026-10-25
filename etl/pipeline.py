import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "etl" / "output"

# Load database settings from backend/.env
load_dotenv(PROJECT_ROOT / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL was not found in backend/.env")


def extract_applications():
    """Extract application records from PostgreSQL."""
    engine = create_engine(DATABASE_URL)

    query = text("""
        SELECT
            id,
            company,
            job_title,
            job_url,
            location,
            source,
            application_date,
            status,
            resume_version,
            job_description,
            notes,
            created_at,
            updated_at
        FROM applications
        ORDER BY application_date DESC
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    engine.dispose()

    print(f"Extracted {len(df)} applications from PostgreSQL.")
    return df


def transform_applications(df):
    """Clean application data and calculate useful metrics."""
    if df.empty:
        return df

    df = df.copy()

    # Standardise text fields.
    text_columns = ["company", "job_title", "location", "source", "status"]

    for column in text_columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    # Convert dates to datetime values.
    df["application_date"] = pd.to_datetime(
        df["application_date"], errors="coerce"
    )

    # Remove records missing essential information.
    df = df.dropna(subset=["application_date"])
    df = df[
        (df["company"] != "")
        & (df["job_title"] != "")
    ]

    # Add useful time-based columns.
    df["application_month"] = (
        df["application_date"].dt.to_period("M").astype(str)
    )

    df["application_year"] = df["application_date"].dt.year

    # Add a numeric flag for applications that reached the interview stage.
    df["reached_interview"] = df["status"].isin(
        ["Interview", "Offer"]
    ).astype(int)

    print(f"Transformed data: {len(df)} valid applications.")
    return df

def generate_summaries(df):
    """Generate summary datasets for analytics."""

    # Applications grouped by status.
    status_summary = (
        df.groupby("status")
        .size()
        .reset_index(name="application_count")
        .sort_values("application_count", ascending=False)
    )

    status_file = OUTPUT_DIR / "status_summary.csv"
    status_summary.to_csv(status_file, index=False)

    print("\nApplications by status:")
    print(status_summary.to_string(index=False))

    # Applications grouped by month.
    monthly_summary = (
        df.groupby("application_month")
        .size()
        .reset_index(name="application_count")
        .sort_values("application_month")
    )

    monthly_file = OUTPUT_DIR / "monthly_summary.csv"
    monthly_summary.to_csv(monthly_file, index=False)

    print("\nApplications by month:")
    print(monthly_summary.to_string(index=False))

    print(f"\nExported status summary to: {status_file}")
    print(f"Exported monthly summary to: {monthly_file}")

def generate_performance_metrics(df):
    """Calculate overall job application performance metrics."""

    total = len(df)

    if total == 0:
        metrics = {
            "total_applications": 0,
            "interview_stage_count": 0,
            "interview_stage_rate": 0.0,
            "rejected_count": 0,
            "rejection_rate": 0.0,
            "offer_count": 0,
            "offer_rate": 0.0,
        }
    else:
        interview_stage_count = int(
            df["status"].isin(["Interview", "Offer"]).sum()
        )
        rejected_count = int((df["status"] == "Rejected").sum())
        offer_count = int((df["status"] == "Offer").sum())

        metrics = {
            "total_applications": total,
            "interview_stage_count": interview_stage_count,
            "interview_stage_rate": round(
                interview_stage_count / total * 100, 2
            ),
            "rejected_count": rejected_count,
            "rejection_rate": round(rejected_count / total * 100, 2),
            "offer_count": offer_count,
            "offer_rate": round(offer_count / total * 100, 2),
        }

    metrics_df = pd.DataFrame([metrics])

    metrics_file = OUTPUT_DIR / "performance_metrics.csv"
    metrics_df.to_csv(metrics_file, index=False)

    print("\nJob search performance metrics:")
    print(metrics_df.to_string(index=False))
    print(f"\nExported performance metrics to: {metrics_file}")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    applications = extract_applications()
    transformed = transform_applications(applications)

    output_file = OUTPUT_DIR / "applications_cleaned.csv"
    transformed.to_csv(output_file, index=False)

    print(f"Exported cleaned data to: {output_file}")
    
    generate_summaries(transformed)

    generate_performance_metrics(transformed)


if __name__ == "__main__":
    main()