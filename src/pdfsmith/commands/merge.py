"""Merge subcommand for pdfsmith (stub — full implementation in Task 4)."""

import typer


def register(app: typer.Typer) -> None:
    """Register the merge subcommand."""
    app.command(name="merge")(_placeholder)


def _placeholder() -> None:
    """Merge PDF files. (Not yet implemented.)"""
    pass
