from src.cli import handle_ingest, handle_interactive


def run_pipeline() -> None:
    """Retrofits the legacy pipeline script as a backward-compatible wrapper.

    This delegates directly to the decoupled CLI ingestion and interactive loop
    to prevent any logic duplication or startup indexing overhead.
    """
    handle_ingest()
    handle_interactive()


if __name__ == "__main__":
    run_pipeline()
