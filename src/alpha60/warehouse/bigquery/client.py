"""BigQuery client abstraction."""

from collections.abc import Iterable, Sequence
from typing import Any, Protocol


class BigQueryClient(Protocol):
    """Interface for interacting with BigQuery."""

    def load_rows(
        self,
        table_id: str,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Load rows into a BigQuery table.

        Returns the number of rows successfully loaded.
        """

    def query(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a SQL query and return rows as dictionaries."""