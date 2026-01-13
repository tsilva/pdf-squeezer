# pdf-compressor

[![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Ghostscript](https://img.shields.io/badge/Ghostscript-000000?logo=ghostscript&logoColor=white)](https://www.ghostscript.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-tsilva%2Fpdf--compressor-blue?logo=github)](https://github.com/tsilva/pdf-compressor)

A reliable PDF compression CLI tool that automatically selects the best compression strategy for each file.

## Overview

Different PDFs respond better to different compression methods. Some are already optimized, others are bloated with high-resolution images. This tool eliminates the guesswork by trying multiple compression strategies and keeping the smallest result.

The tool is fast, scriptable, and works great for batch processing. It supports single files, wildcards, custom output directories, and in-place replacement.

## Features

- **Smart compression** - Tries 3 strategies and picks the best result
- **Batch processing** - Compress multiple files with wildcards (`*.pdf`)
- **Flexible output** - Custom filenames, directories, or in-place replacement
- **Cross-platform** - Works on macOS and Linux
- **Scriptable** - Quiet mode for automation and pipelines

## Installation

### Dependencies

Install the required tools:

```bash
# macOS
brew install ghostscript qpdf

# Ubuntu/Debian
apt install ghostscript qpdf

# Fedora/RHEL
dnf install ghostscript qpdf
```

### Install compress-pdf

```bash
git clone https://github.com/tsilva/pdf-compressor.git
cd pdf-compressor
make install
```

Or manually copy to your PATH:

```bash
cp compress-pdf /usr/local/bin/
chmod +x /usr/local/bin/compress-pdf
```

To uninstall:

```bash
make uninstall
```

## Usage

```bash
# Compress a single file (creates document_compressed.pdf)
compress-pdf document.pdf

# Specify output filename
compress-pdf document.pdf -o small.pdf

# Batch compress multiple files
compress-pdf *.pdf

# Compress to a specific directory
compress-pdf *.pdf -d compressed/

# Replace original files (use with caution)
compress-pdf -i large.pdf

# Quiet mode (no output except errors)
compress-pdf -q document.pdf
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output <file>` | Output filename (single file mode only) |
| `-d, --output-dir <dir>` | Output directory for compressed files |
| `-i, --in-place` | Replace original files |
| `-q, --quiet` | Suppress output except errors |
| `-h, --help` | Show help message |
| `-v, --version` | Show version |

## How It Works

The tool tries three compression strategies and keeps the smallest result:

| Strategy | Method | Best For |
|----------|--------|----------|
| **qpdf** | Linearizes and optimizes PDF object streams | Already-optimized PDFs |
| **Ghostscript** | Aggressive 72 DPI image downsampling | Image-heavy PDFs |
| **Combined** | Ghostscript followed by qpdf optimization | Mixed content |

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
├── compress-pdf     # Main CLI script
├── Makefile         # Install/uninstall targets
├── LICENSE          # MIT License
└── README.md        # This file
```

## Reporting Issues

Found a bug or have a suggestion? Please open an issue:

[GitHub Issues](https://github.com/tsilva/pdf-compressor/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Tiago Silva** - [@tsilva](https://github.com/tsilva)
