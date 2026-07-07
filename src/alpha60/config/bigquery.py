"""BigQuery configuration models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BigQuerySettings:
    """Configuration required to connect to BigQuery."""

    project_id: str
    dataset_id: str
    staging_dataset_id: str = "stg"
    location: str = "australia-southeast1"
