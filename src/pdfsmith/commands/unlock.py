"""Unlock subcommand for pdfsmith (stub — full implementation in Task 6)."""

import typer


def register(app: typer.Typer) -> None:
    """Register the unlock subcommand."""
    app.command(name="unlock")(_placeholder)


def _placeholder() -> None:
    """Unlock encrypted PDF files. (Not yet implemented.)"""
    pass
