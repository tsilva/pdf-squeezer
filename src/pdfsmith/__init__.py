"""pdfsmith - PDF toolkit: compress, merge, and unlock PDF files."""

__version__ = "3.0.0"
__author__ = "Tiago Silva"

from pdfsmith.core.compressor import PDFCompressor, CompressionOutcome

__all__ = ["PDFCompressor", "CompressionOutcome", "__version__"]
