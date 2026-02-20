"""Compression strategy implementations."""

from pdfsmith.core.strategies.base import CompressionStrategy, CompressionResult
from pdfsmith.core.strategies.pikepdf_strategy import PikepdfStrategy
from pdfsmith.core.strategies.ghostscript_strategy import GhostscriptStrategy
from pdfsmith.core.strategies.combined_strategy import CombinedStrategy

__all__ = [
    "CompressionStrategy",
    "CompressionResult",
    "PikepdfStrategy",
    "GhostscriptStrategy",
    "CombinedStrategy",
]
