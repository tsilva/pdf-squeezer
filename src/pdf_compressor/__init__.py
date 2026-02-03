"""PDF Compressor - Reliable PDF compression using multiple strategies."""

__version__ = "2.1.3"
__author__ = "Tiago Silva"

from pdf_compressor.core.compressor import PDFCompressor, CompressionOutcome

__all__ = ["PDFCompressor", "CompressionOutcome", "__version__"]
