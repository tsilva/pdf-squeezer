#!/bin/bash
# compress-pdf - Reliable PDF compression using multiple strategies
# https://github.com/tsilva/pdf-compressor

set -e

VERSION="1.0.0"

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BOLD='' NC=''
fi

# Default options
QUIET=false
IN_PLACE=false
OUTPUT_DIR=""

usage() {
    cat << EOF
${BOLD}compress-pdf${NC} v${VERSION} - Reliable PDF compression

${BOLD}USAGE${NC}
    compress-pdf [OPTIONS] <input.pdf> [input2.pdf ...]
    compress-pdf [OPTIONS] <input.pdf> -o <output.pdf>

${BOLD}OPTIONS${NC}
    -o, --output <file>    Output filename (single file mode only)
    -d, --output-dir <dir> Output directory for compressed files
    -i, --in-place         Replace original files (use with caution)
    -q, --quiet            Suppress output except errors
    -h, --help             Show this help message
    -v, --version          Show version

${BOLD}EXAMPLES${NC}
    compress-pdf document.pdf                    # Creates document_compressed.pdf
    compress-pdf document.pdf -o small.pdf       # Creates small.pdf
    compress-pdf *.pdf -d compressed/            # Batch compress to directory
    compress-pdf -i large.pdf                    # Replace original

${BOLD}HOW IT WORKS${NC}
    Tries three compression strategies and keeps the smallest result:
    1. qpdf - Linearizes and optimizes PDF structure
    2. Ghostscript /screen - Aggressive image downsampling (72 DPI)
    3. Combined - Ghostscript followed by qpdf optimization

${BOLD}DEPENDENCIES${NC}
    - ghostscript (gs)
    - qpdf

    Install on macOS: brew install ghostscript qpdf
    Install on Ubuntu: apt install ghostscript qpdf

EOF
}

log() {
    if [ "$QUIET" = false ]; then
        echo -e "$@"
    fi
}

error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

# Check dependencies
check_deps() {
    local missing=()
    command -v gs >/dev/null 2>&1 || missing+=("ghostscript")
    command -v qpdf >/dev/null 2>&1 || missing+=("qpdf")

    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        echo "Install with: brew install ${missing[*]}" >&2
        exit 1
    fi
}

# Get file size (cross-platform)
get_size() {
    stat -f%z "$1" 2>/dev/null || stat -c%s "$1" 2>/dev/null
}

# Format bytes to human readable
format_size() {
    local bytes=$1
    if command -v numfmt >/dev/null 2>&1; then
        numfmt --to=iec "$bytes"
    else
        # Fallback for macOS without coreutils
        if [ "$bytes" -ge 1048576 ]; then
            echo "$((bytes / 1048576))M"
        elif [ "$bytes" -ge 1024 ]; then
            echo "$((bytes / 1024))K"
        else
            echo "${bytes}B"
        fi
    fi
}

# Compress a single PDF
compress_pdf() {
    local input="$1"
    local output="$2"

    if [ ! -f "$input" ]; then
        error "File not found: $input"
        return 1
    fi

    local orig_size
    orig_size=$(get_size "$input")

    local tmpdir
    tmpdir=$(mktemp -d)
    trap "rm -rf '$tmpdir'" RETURN

    log "${BOLD}$(basename "$input")${NC} ($(format_size "$orig_size"))"

    # Strategy 1: qpdf only
    local size1=999999999
    if qpdf --linearize --compress-streams=y --object-streams=generate "$input" "$tmpdir/qpdf.pdf" 2>/dev/null; then
        size1=$(get_size "$tmpdir/qpdf.pdf")
        log "  qpdf:      $(format_size "$size1")"
    else
        log "  qpdf:      ${YELLOW}failed${NC}"
    fi

    # Strategy 2: Ghostscript /screen
    local size2=999999999
    if gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen \
        -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$tmpdir/gs.pdf" "$input" 2>/dev/null; then
        size2=$(get_size "$tmpdir/gs.pdf")
        log "  gs:        $(format_size "$size2")"
    else
        log "  gs:        ${YELLOW}failed${NC}"
    fi

    # Strategy 3: Combined
    local size3=999999999
    if [ -f "$tmpdir/gs.pdf" ] && qpdf --linearize --compress-streams=y --object-streams=generate \
        "$tmpdir/gs.pdf" "$tmpdir/combined.pdf" 2>/dev/null; then
        size3=$(get_size "$tmpdir/combined.pdf")
        log "  gs+qpdf:   $(format_size "$size3")"
    else
        log "  gs+qpdf:   ${YELLOW}failed${NC}"
    fi

    # Find best result
    local best_size=$orig_size
    local best_file=""
    local best_method="none"

    if [ "$size1" -lt "$best_size" ]; then
        best_size=$size1
        best_file="$tmpdir/qpdf.pdf"
        best_method="qpdf"
    fi

    if [ "$size2" -lt "$best_size" ]; then
        best_size=$size2
        best_file="$tmpdir/gs.pdf"
        best_method="gs"
    fi

    if [ "$size3" -lt "$best_size" ]; then
        best_size=$size3
        best_file="$tmpdir/combined.pdf"
        best_method="gs+qpdf"
    fi

    # Save result
    if [ -n "$best_file" ]; then
        cp "$best_file" "$output"
        local reduction
        reduction=$(echo "scale=0; (1 - $best_size/$orig_size) * 100" | bc)
        log "  ${GREEN}→ $(format_size "$best_size") (-${reduction}%) via ${best_method}${NC}"
        log "  Saved: $output"
    else
        cp "$input" "$output"
        log "  ${YELLOW}→ No reduction possible, copied original${NC}"
    fi

    echo ""
}

# Parse arguments
INPUTS=()
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--version)
            echo "compress-pdf v${VERSION}"
            exit 0
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -i|--in-place)
            IN_PLACE=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -d|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -*)
            error "Unknown option: $1"
            exit 1
            ;;
        *)
            INPUTS+=("$1")
            shift
            ;;
    esac
done

# Validate arguments
if [ ${#INPUTS[@]} -eq 0 ]; then
    usage
    exit 1
fi

if [ -n "$OUTPUT_FILE" ] && [ ${#INPUTS[@]} -gt 1 ]; then
    error "Cannot use -o with multiple input files. Use -d instead."
    exit 1
fi

if [ -n "$OUTPUT_FILE" ] && [ "$IN_PLACE" = true ]; then
    error "Cannot use -o and -i together."
    exit 1
fi

# Check dependencies
check_deps

# Create output directory if specified
if [ -n "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
fi

# Process files
for input in "${INPUTS[@]}"; do
    if [ ! -f "$input" ]; then
        error "File not found: $input"
        continue
    fi

    # Determine output filename
    if [ -n "$OUTPUT_FILE" ]; then
        output="$OUTPUT_FILE"
    elif [ "$IN_PLACE" = true ]; then
        output="$input"
    elif [ -n "$OUTPUT_DIR" ]; then
        basename="${input##*/}"
        name="${basename%.pdf}"
        output="${OUTPUT_DIR}/${name}_compressed.pdf"
    else
        dir=$(dirname "$input")
        basename="${input##*/}"
        name="${basename%.pdf}"
        output="${dir}/${name}_compressed.pdf"
    fi

    compress_pdf "$input" "$output"
done
