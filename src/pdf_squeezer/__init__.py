"""PDF Squeezer - Reliable PDF compression using multiple strategies."""

__version__ = "2.1.5"
__author__ = "Tiago Silva"

from pdf_squeezer.core.compressor import PDFCompressor, CompressionOutcome

__all__ = ["PDFCompressor", "CompressionOutcome", "__version__"]
