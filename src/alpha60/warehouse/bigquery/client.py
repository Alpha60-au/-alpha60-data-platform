"""BigQuery client abstraction."""

from collections.abc import Iterable
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