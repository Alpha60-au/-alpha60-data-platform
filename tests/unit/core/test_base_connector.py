# tests/test_base_connector.py

from datetime import UTC, datetime

from alpha60.core.connectors.base import BaseConnector
from alpha60.core.models.record import Record


class DummyConnector(BaseConnector):
    def test_connection(self) -> None:
        return None

    def extract(self, **kwargs: object) -> list[Record]:
        return [
            Record(
                source="dummy",
                entity="test",
                record_id="1",
                extracted_at=datetime.now(UTC),
                payload={"ok": True},
            )
        ]

    def health(self) -> dict[str, str]:
        return {"status": "ok"}


def test_dummy_connector_can_be_instantiated() -> None:
    connector = DummyConnector()

    connector.test_connection()

    records = connector.extract()

    assert len(records) == 1
    assert records[0].source == "dummy"
    assert connector.health() == {"status": "ok"}