# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF compression CLI tool that tries multiple compression strategies (pikepdf, Ghostscript, combined) and keeps the smallest result. Uses Python with typer for CLI and rich for output formatting.

## Commands

```bash
# Install dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run the tool
compress-pdf document.pdf
compress-pdf *.pdf -j 4  # parallel processing

# Run tests
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```

## Architecture

**Strategy Pattern**: The core uses a strategy pattern where each compression method (`src/pdf_compressor/core/strategies/`) implements `CompressionStrategy`. The orchestrator (`PDFCompressor` in `compressor.py`) tries all strategies and picks the smallest successful output.

Three strategies:
- `PikepdfStrategy` - Lossless optimization via pikepdf (linearization, stream compression)
- `GhostscriptStrategy` - Lossy compression via subprocess to `gs`, uses quality presets (screen/ebook/printer/prepress)
- `CombinedStrategy` - Runs Ghostscript then pikepdf

**Parallel Processing**: `ParallelCompressor` in `parallel/executor.py` uses `ProcessPoolExecutor` (not threads) because Ghostscript subprocess calls and pikepdf C++ operations benefit from true parallelism.

**CLI Flow**: `cli.py` handles argument parsing via typer, resolves output paths, and dispatches to either sequential or parallel processing based on file count and `-j` flag.

## External Dependencies

Requires Ghostscript (`gs`) installed on system. The tool checks for this at runtime via `utils/dependencies.py`.
