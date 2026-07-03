"""Tests for the Google BigQuery client adapter."""

from unittest.mock import Mock, patch

from google.cloud import bigquery

from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.google_client import GoogleBigQueryClient


def test_google_bigquery_client_accepts_injected_client() -> None:
    """The adapter can use an injected BigQuery client."""
    client = Mock(spec=bigquery.Client)

    adapter = GoogleBigQueryClient(
        config=BigQueryConfig(project_id="alpha60-dev", dataset_id="raw"),
        client=client,
    )

    assert adapter is not None


def test_google_bigquery_client_creates_sdk_client_from_config() -> None:
    """The adapter creates a Google SDK client from config."""
    with patch("alpha60.warehouse.bigquery.google_client.bigquery.Client") as client_class:
        GoogleBigQueryClient(
            config=BigQueryConfig(
                project_id="alpha60-dev",
                dataset_id="raw",
                location="australia-southeast1",
            ),
        )

    client_class.assert_called_once_with(
        project="alpha60-dev",
        location="australia-southeast1",
    )


def test_google_bigquery_client_connection_passes_when_dataset_is_accessible() -> None:
    """Connection test passes when the configured dataset is accessible."""
    sdk_client = Mock(spec=bigquery.Client)

    client = GoogleBigQueryClient(
        config=BigQueryConfig(project_id="alpha60-dev", dataset_id="raw"),
        client=sdk_client,
    )

    result = client.test_connection()

    assert result is True
    sdk_client.get_dataset.assert_called_once_with("alpha60-dev.raw")


def test_google_bigquery_client_connection_fails_when_dataset_is_not_accessible() -> None:
    """Connection test fails when the configured dataset is not accessible."""
    sdk_client = Mock(spec=bigquery.Client)
    sdk_client.get_dataset.side_effect = RuntimeError("dataset unavailable")

    client = GoogleBigQueryClient(
        config=BigQueryConfig(project_id="alpha60-dev", dataset_id="raw"),
        client=sdk_client,
    )

    result = client.test_connection()

    assert result is False
    sdk_client.get_dataset.assert_called_once_with("alpha60-dev.raw")


def test_google_bigquery_client_loads_rows_with_load_job() -> None:
    """Rows are loaded into BigQuery using a load job."""
    sdk_client = Mock(spec=bigquery.Client)
    load_job = Mock()
    load_job.errors = None
    load_job.output_rows = 2
    sdk_client.load_table_from_json.return_value = load_job

    client = GoogleBigQueryClient(
        config=BigQueryConfig(project_id="alpha60-dev", dataset_id="raw"),
        client=sdk_client,
    )

    rows_loaded = client.load_rows(
        table_id="alpha60-dev.raw.shopify_products",
        rows=[
            {"record_id": "1"},
            {"record_id": "2"},
        ],
    )

    assert rows_loaded == 2
    load_job.result.assert_called_once()

    sdk_client.load_table_from_json.assert_called_once()
    _, kwargs = sdk_client.load_table_from_json.call_args

    assert kwargs["destination"] == "alpha60-dev.raw.shopify_products"
    assert kwargs["job_config"].write_disposition == bigquery.WriteDisposition.WRITE_APPEND


def test_google_bigquery_client_raises_when_load_job_has_errors() -> None:
    """A failed BigQuery load job raises a runtime error."""
    sdk_client = Mock(spec=bigquery.Client)
    load_job = Mock()
    load_job.errors = [{"message": "invalid row"}]
    load_job.output_rows = 0
    sdk_client.load_table_from_json.return_value = load_job

    client = GoogleBigQueryClient(
        config=BigQueryConfig(project_id="alpha60-dev", dataset_id="raw"),
        client=sdk_client,
    )

    try:
        client.load_rows(
            table_id="alpha60-dev.raw.shopify_products",
            rows=[{"record_id": "1"}],
        )
    except RuntimeError as exc:
        assert "BigQuery load failed" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")


def test_google_bigquery_client_runs_query_and_returns_rows() -> None:
    """Queries return BigQuery rows as dictionaries."""
    sdk_client = Mock(spec=bigquery.Client)

    row = Mock()
    row.items.return_value = [("job_name", "shopify-products")]
    query_job = Mock()
    query_job.result.return_value = [row]
    sdk_client.query.return_value = query_job

    client = GoogleBigQueryClient(
        config=BigQueryConfig(
            project_id="alpha60-dev",
            dataset_id="warehouse",
            location="australia-southeast1",
        ),
        client=sdk_client,
    )

    result = client.query("SELECT job_name FROM platform_state")

    assert result == [{"job_name": "shopify-products"}]
    sdk_client.query.assert_called_once()

    _, kwargs = sdk_client.query.call_args
    assert kwargs["location"] == "australia-southeast1"
    assert isinstance(kwargs["job_config"], bigquery.QueryJobConfig)


def test_google_bigquery_client_passes_query_parameters() -> None:
    """Query parameters are passed through to BigQuery."""
    sdk_client = Mock(spec=bigquery.Client)

    query_job = Mock()
    query_job.result.return_value = []
    sdk_client.query.return_value = query_job

    parameter = bigquery.ScalarQueryParameter(
        "job_name",
        "STRING",
        "shopify-products",
    )

    client = GoogleBigQueryClient(
        config=BigQueryConfig(project_id="alpha60-dev", dataset_id="warehouse"),
        client=sdk_client,
    )

    result = client.query(
        "SELECT * FROM platform_state WHERE job_name = @job_name",
        parameters=[parameter],
    )

    assert result == []
    sdk_client.query.assert_called_once()

    _, kwargs = sdk_client.query.call_args
    assert kwargs["job_config"].query_parameters == [parameter]