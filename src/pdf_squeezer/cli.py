"""Command-line interface for PDF compression."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, List, Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from pdf_squeezer import __version__
from pdf_squeezer.core.compressor import CompressionOutcome, PDFCompressor
from pdf_squeezer.parallel.executor import ParallelCompressor
from pdf_squeezer.utils.dependencies import check_dependencies, get_install_instructions
from pdf_squeezer.utils.filesize import format_size

app = typer.Typer(
    name="pdf-squeezer",
    help="Reliable PDF compression using multiple strategies.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"pdf-squeezer v{__version__}")
        raise typer.Exit()


def discover_pdf_files(files: Optional[List[Path]]) -> List[Path]:
    """Resolve file arguments, defaulting to *.pdf in CWD."""
    if files:
        # Validate provided files exist
        resolved = []
        for f in files:
            path = Path(f).resolve()
            if not path.exists():
                console.print(f"[red]Error:[/red] File not found: {f}")
                raise typer.Exit(1)
            if path.is_dir():
                console.print(f"[red]Error:[/red] Expected file, got directory: {f}")
                raise typer.Exit(1)
            resolved.append(path)
        return resolved

    # Default: find all PDFs in current directory
    cwd = Path.cwd()
    return sorted(cwd.glob("*.pdf"))


def confirm_operation(
    files: List[Path],
    output_dir: Optional[Path],
    in_place: bool,
) -> bool:
    """Show operation summary and ask for confirmation."""
    cwd = Path.cwd()

    console.print()
    console.print(f"[bold]Working directory:[/bold] {cwd}")
    console.print(f"[bold]Files to compress:[/bold] {len(files)}")

    # Show sample file names (up to 5)
    sample_count = min(5, len(files))
    for f in files[:sample_count]:
        console.print(f"  • {f.name}")
    if len(files) > sample_count:
        console.print(f"  ... and {len(files) - sample_count} more")

    # Show output destination
    if in_place:
        console.print("[bold]Output:[/bold] [yellow]Replacing original files[/yellow]")
    elif output_dir:
        console.print(f"[bold]Output:[/bold] {output_dir}/")
    else:
        console.print("[bold]Output:[/bold] Same directory as input (*.compressed.pdf)")

    console.print()
    return typer.confirm("Proceed with compression?")


@app.command()
def main(
    files: Annotated[
        Optional[List[Path]],
        typer.Argument(
            help="Input PDF file(s) to compress (default: *.pdf in current directory)",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "-o",
            "--output",
            help="Output filename (single file mode only)",
            dir_okay=False,
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "-d",
            "--output-dir",
            help="Output directory for compressed files",
            file_okay=False,
        ),
    ] = None,
    in_place: Annotated[
        bool,
        typer.Option(
            "-i",
            "--in-place",
            help="Replace original files (use with caution)",
        ),
    ] = False,
    quality: Annotated[
        str,
        typer.Option(
            "-Q",
            "--quality",
            help="Quality preset: screen (72dpi), ebook (150dpi), printer (300dpi), prepress",
            case_sensitive=False,
        ),
    ] = "ebook",
    jobs: Annotated[
        int,
        typer.Option(
            "-j",
            "--jobs",
            help="Number of parallel jobs (0 = auto)",
            min=0,
        ),
    ] = 0,
    quiet: Annotated[
        bool,
        typer.Option(
            "-q",
            "--quiet",
            help="Suppress output except errors",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "-n",
            "--dry-run",
            help="Simulate compression without saving output files",
        ),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "-v",
            "--version",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """
    Compress PDF files using multiple strategies, keeping the smallest result.

    [bold]Examples:[/bold]

        pdf-squeezer                               # Compress all *.pdf in current directory
        pdf-squeezer document.pdf                  # Creates document.compressed.pdf
        pdf-squeezer document.pdf -o small.pdf    # Creates small.pdf
        pdf-squeezer *.pdf -d compressed/         # Batch compress to directory
        pdf-squeezer -i *.pdf                     # Replace original files
        pdf-squeezer *.pdf -j 4                   # Use 4 parallel workers
        pdf-squeezer --dry-run                    # Preview compression without saving
    """
    # Resolve files (handles default *.pdf pattern)
    files = discover_pdf_files(files)

    if not files:
        console.print("[yellow]No PDF files found in current directory.[/yellow]")
        raise typer.Exit(0)

    if output and len(files) > 1:
        console.print("[red]Error:[/red] Cannot use -o with multiple files. Use -d instead.")
        raise typer.Exit(1)

    if output and in_place:
        console.print("[red]Error:[/red] Cannot use -o and -i together.")
        raise typer.Exit(1)

    if dry_run and (output or in_place):
        console.print("[red]Error:[/red] Cannot use --dry-run with -o or -i.")
        raise typer.Exit(1)

    # Validate quality preset
    valid_qualities = ["screen", "ebook", "printer", "prepress", "default"]
    if quality.lower() not in valid_qualities:
        console.print(
            f"[red]Error:[/red] Invalid quality '{quality}'. "
            f"Choose from: {', '.join(valid_qualities)}"
        )
        raise typer.Exit(1)

    # Check dependencies
    missing = check_dependencies()
    if missing:
        console.print(f"[red]Error:[/red] Missing dependencies: {', '.join(missing)}")
        console.print(get_install_instructions())
        raise typer.Exit(1)

    # Create output directory if needed
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Confirm operation (skip in dry-run or quiet mode)
    if not dry_run and not quiet:
        if not confirm_operation(files, output_dir, in_place):
            console.print("Operation cancelled.")
            raise typer.Exit(0)

    # Process files
    if dry_run:
        # Use temporary directory that auto-cleans on exit
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            if len(files) > 1 and jobs != 1:
                outcomes = process_parallel(files, temp_path, False, quality, jobs, quiet)
            else:
                outcomes = process_sequential(files, None, temp_path, False, quality, quiet)
            # Summary shown before temp dir cleanup
            if not quiet and len(outcomes) > 1:
                show_summary(outcomes)
    else:
        if len(files) > 1 and jobs != 1:
            # Parallel processing for multiple files
            outcomes = process_parallel(files, output_dir, in_place, quality, jobs, quiet)
        else:
            # Sequential processing
            outcomes = process_sequential(files, output, output_dir, in_place, quality, quiet)

        # Summary
        if not quiet and len(outcomes) > 1:
            show_summary(outcomes)

    # Exit with error if any compression failed completely
    if any(o.best_strategy == "error" for o in outcomes):
        raise typer.Exit(1)


def process_sequential(
    files: List[Path],
    output: Optional[Path],
    output_dir: Optional[Path],
    in_place: bool,
    quality: str,
    quiet: bool,
) -> List[CompressionOutcome]:
    """Process files sequentially with progress display."""
    outcomes = []
    compressor = PDFCompressor(quality=quality)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("Compressing...", total=len(files))

        for input_path in files:
            output_path = resolve_output_path(input_path, output, output_dir, in_place)

            progress.update(task, description=f"[cyan]{input_path.name}[/cyan]")
            outcome = compressor.compress(input_path, output_path)
            outcomes.append(outcome)

            if not quiet:
                show_result(outcome)

            progress.advance(task)

    return outcomes


def process_parallel(
    files: List[Path],
    output_dir: Optional[Path],
    in_place: bool,
    quality: str,
    jobs: int,
    quiet: bool,
) -> List[CompressionOutcome]:
    """Process files in parallel with progress display."""
    parallel_compressor = ParallelCompressor(
        quality=quality,
        max_workers=jobs if jobs > 0 else None,
    )

    # Prepare tasks
    tasks = []
    for input_path in files:
        output_path = resolve_output_path(input_path, None, output_dir, in_place)
        tasks.append((input_path, output_path))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        disable=quiet,
    ) as progress:
        task_id = progress.add_task("Compressing files...", total=len(tasks))

        def on_complete(outcome: CompressionOutcome) -> None:
            progress.advance(task_id)
            if not quiet:
                show_result(outcome)

        outcomes = parallel_compressor.compress_batch(tasks, on_complete)

    return outcomes


def resolve_output_path(
    input_path: Path,
    output: Optional[Path],
    output_dir: Optional[Path],
    in_place: bool,
) -> Path:
    """Determine output path based on options."""
    if output:
        return output
    if in_place:
        return input_path
    if output_dir:
        return output_dir / f"{input_path.stem}.compressed.pdf"
    return input_path.parent / f"{input_path.stem}.compressed.pdf"


def show_result(outcome: CompressionOutcome) -> None:
    """Display compression result for a single file."""
    name = outcome.input_path.name
    orig = format_size(outcome.original_size)
    final = format_size(outcome.final_size)

    if outcome.best_strategy == "error":
        console.print(f"  [bold]{name}[/bold] [red]ERROR[/red]")
    elif outcome.improved:
        console.print(
            f"  [bold]{name}[/bold] {orig} -> [green]{final}[/green] "
            f"([green]-{outcome.reduction_percent}%[/green]) via {outcome.best_strategy}"
        )
    else:
        console.print(f"  [bold]{name}[/bold] {orig} -> [yellow]{final}[/yellow] (no reduction)")


def show_summary(outcomes: List[CompressionOutcome]) -> None:
    """Display summary table for batch operations."""
    table = Table(title="Compression Summary")
    table.add_column("File", style="cyan")
    table.add_column("Original", justify="right")
    table.add_column("Compressed", justify="right")
    table.add_column("Reduction", justify="right")
    table.add_column("Strategy")

    total_original = 0
    total_final = 0

    for o in outcomes:
        total_original += o.original_size
        total_final += o.final_size

        if o.best_strategy == "error":
            table.add_row(o.input_path.name, format_size(o.original_size), "-", "[red]ERROR[/red]", "-")
        else:
            reduction = f"-{o.reduction_percent}%" if o.improved else "0%"
            style = "green" if o.improved else "yellow"

            table.add_row(
                o.input_path.name,
                format_size(o.original_size),
                format_size(o.final_size),
                f"[{style}]{reduction}[/{style}]",
                o.best_strategy,
            )

    # Total row
    total_reduction = int((1 - total_final / total_original) * 100) if total_original else 0
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{format_size(total_original)}[/bold]",
        f"[bold]{format_size(total_final)}[/bold]",
        f"[bold green]-{total_reduction}%[/bold green]",
        "",
    )

    console.print()
    console.print(table)


if __name__ == "__main__":
    app()
