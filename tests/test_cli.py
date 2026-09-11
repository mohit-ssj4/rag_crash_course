import sys

from src import cli


def test_cli_parser_ingest(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["src/cli.py", "ingest"])
    # Stub CLI handlers to test parsing
    called = []
    monkeypatch.setattr(cli, "handle_ingest", lambda: called.append("ingest"))
    cli.main()
    assert "ingest" in called


def test_cli_parser_query(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["src/cli.py", "query", "my test query"])
    called = []
    monkeypatch.setattr(cli, "handle_query", lambda text: called.append(text))
    cli.main()
    assert "my test query" in called


def test_cli_parser_interactive(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["src/cli.py", "interactive"])
    called = []
    monkeypatch.setattr(cli, "handle_interactive", lambda: called.append("interactive"))
    cli.main()
    assert "interactive" in called


def test_cli_empty_state_warning(caplog, monkeypatch):
    # Mock VectorStore inside handle_query to return empty collection
    monkeypatch.setattr(
        "src.vector_store.chromadb.PersistentClient", lambda *args, **kwargs: None
    )

    # Force collection count to be 0
    class MockCollection:
        def count(self):
            return 0

    def mock_init_store(self):
        self.client = None
        self.collection = MockCollection()

    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", mock_init_store
    )

    with caplog.at_level("WARNING"):
        cli.handle_query("test query")

    # Assert on captured logging records
    assert any(
        "Database empty. Please run ingestion first" in record.message
        for record in caplog.records
    )
