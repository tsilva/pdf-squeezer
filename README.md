# pdf-compressor

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ghostscript](https://img.shields.io/badge/Ghostscript-000000?logo=ghostscript&logoColor=white)](https://www.ghostscript.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-tsilva%2Fpdf--compressor-blue?logo=github)](https://github.com/tsilva/pdf-compressor)

A reliable PDF compression CLI tool that automatically selects the best compression strategy for each file.

## Overview

Different PDFs respond better to different compression methods. Some are already optimized, others are bloated with high-resolution images. This tool eliminates the guesswork by trying multiple compression strategies and keeping the smallest result.

The tool is fast, scriptable, and works great for batch processing. It supports single files, wildcards, custom output directories, in-place replacement, and parallel processing.

## Features

- **Smart compression** - Tries 3 strategies and picks the best result
- **Batch processing** - Compress multiple files with wildcards (`*.pdf`)
- **Parallel processing** - Compress multiple files concurrently for faster batch operations
- **Flexible output** - Custom filenames, directories, or in-place replacement
- **Quality presets** - Choose between screen, ebook, printer, or prepress quality
- **Cross-platform** - Works on macOS and Linux
- **Scriptable** - Quiet mode for automation and pipelines

## Installation

### Prerequisites

Install Ghostscript:

```bash
# macOS
brew install ghostscript

# Ubuntu/Debian
apt install ghostscript

# Fedora/RHEL
dnf install ghostscript
```

### Install as global tool (recommended)

```bash
uv tool install git+https://github.com/tsilva/pdf-compressor.git
```

This installs `pdf-compressor` as a globally available command in an isolated environment. To upgrade later:

```bash
uv tool upgrade pdf-compressor
```

### Install with pip

```bash
pip install git+https://github.com/tsilva/pdf-compressor.git
```

### Install from source

```bash
git clone https://github.com/tsilva/pdf-compressor.git
cd pdf-compressor
uv tool install -e .
```

## Usage

```bash
# Compress a single file (creates document_compressed.pdf)
pdf-compressor document.pdf

# Specify output filename
pdf-compressor document.pdf -o small.pdf

# Batch compress multiple files
pdf-compressor *.pdf

# Compress to a specific directory
pdf-compressor *.pdf -d compressed/

# Replace original files (use with caution)
pdf-compressor -i large.pdf

# Use 4 parallel workers for batch compression
pdf-compressor *.pdf -j 4

# Use ebook quality (150 DPI) instead of screen (72 DPI)
pdf-compressor document.pdf -Q ebook

# Quiet mode (no output except errors)
pdf-compressor -q document.pdf
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output <file>` | Output filename (single file mode only) |
| `-d, --output-dir <dir>` | Output directory for compressed files |
| `-i, --in-place` | Replace original files |
| `-Q, --quality <preset>` | Quality preset: screen, ebook, printer, prepress |
| `-j, --jobs <n>` | Number of parallel jobs (0 = auto) |
| `-q, --quiet` | Suppress output except errors |
| `-v, --version` | Show version |

### Quality Presets

| Preset | DPI | Use Case |
|--------|-----|----------|
| `screen` | 72 | Web viewing, smallest size |
| `ebook` | 150 | E-readers and tablets (default) |
| `printer` | 300 | Office printing |
| `prepress` | 300 | Professional printing |

## How It Works

The tool tries three compression strategies and keeps the smallest result:

| Strategy | Method | Best For |
|----------|--------|----------|
| **pikepdf** | Linearizes and optimizes PDF object streams | Already-optimized PDFs |
| **Ghostscript** | Aggressive image downsampling | Image-heavy PDFs |
| **Combined** | Ghostscript followed by pikepdf optimization | Mixed content |

If none of the strategies produce a smaller file, the original is preserved.

## Example Results

| PDF Type | Original | Compressed | Reduction |
|----------|----------|------------|-----------|
| Scanned document | 434 KB | 38 KB | 91% |
| Digital form | 164 KB | 96 KB | 41% |
| Invoice | 32 KB | 21 KB | 33% |

Results vary depending on PDF content. Image-heavy PDFs typically see the largest reductions.

## Repository Structure

```
pdf-compressor/
├── pyproject.toml              # Project configuration
├── src/
│   └── pdf_compressor/
│       ├── cli.py              # CLI interface
│       ├── core/
│       │   ├── compressor.py   # Main orchestrator
│       │   └── strategies/     # Compression strategies
│       ├── parallel/           # Parallel processing
│       └── utils/              # Utilities
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## Reporting Issues

Found a bug or have a suggestion? Please open an issue:

[GitHub Issues](https://github.com/tsilva/pdf-compressor/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Tiago Silva** - [@tsilva](https://github.com/tsilva)
