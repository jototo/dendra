"""Dendra CLI — generate mathematically-driven SVG tree silhouettes."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from dendra.color import PALETTES, accent_color, parse_color_config
from dendra.species import SPECIES

# ---------------------------------------------------------------------------
# Rich theme — Ozark-palette terminal aesthetic
# ---------------------------------------------------------------------------

OZARK_THEME = Theme({
    "heading":         "bold white on dark_green",
    "species.name":    "bold green",
    "species.sci":     "italic dim",
    "math.value":      "italic cyan",
    "path.out":        "dim cyan",
    "param.label":     "dim white",
    "param.value":     "bold white",
    "success":         "bold green",
    "error.header":    "bold red",
    "warning":         "bold yellow",
    "palette.swatch":  "bold",
    "stage.done":      "dim green",
})

console = Console(theme=OZARK_THEME)
app = typer.Typer(
    name="dendra",
    help="Generate SVG silhouettes of NW Arkansas native trees using L-systems, wave math, and fractals.",
    add_completion=False,
    rich_markup_mode="rich",
)

OUTPUT_DIR = Path("output")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _swatch(hex_color: str, label: str = "") -> str:
    """Rich markup for a colored block swatch."""
    return f"[{hex_color}]██[/{hex_color}] {label}"


def _palette_swatch(palette_name: str) -> str:
    p = PALETTES[palette_name]
    return (
        f"[{p.trunk}]█[/{p.trunk}]"
        f"[{p.canopy}]█[/{p.canopy}]"
        f"[{p.canopy_accent}]█[/{p.canopy_accent}]"
        f" {p.display}"
    )


def _file_size(path: Path) -> str:
    size = path.stat().st_size
    if size < 1024:
        return f"{size} B"
    return f"{size / 1024:.1f} KB"


def _error(msg: str) -> None:
    console.print(Panel(
        f"[white]{msg}[/white]",
        title="[error.header]Generation Failed[/error.header]",
        border_style="red",
        padding=(0, 2),
    ))
    raise typer.Exit(1)


# ---------------------------------------------------------------------------
# list command
# ---------------------------------------------------------------------------

@app.command("list", help="List all available tree species.")
def list_species() -> None:
    table = Table(
        box=box.ROUNDED,
        border_style="dark_green",
        header_style="bold white on dark_green",
        show_lines=False,
        padding=(0, 1),
        title="[bold white]NW Arkansas Native Trees[/bold white]",
        title_style="bold white",
        caption="[dim]Use [bold]dendra generate <species>[/bold] to render[/dim]",
    )

    table.add_column("Species", style="species.name", min_width=22)
    table.add_column("Scientific Name", style="species.sci", min_width=22)
    table.add_column("Silhouette", min_width=36)
    table.add_column("Engine", style="math.value", min_width=18)
    table.add_column("Palette", min_width=24)
    table.add_column("Note", justify="center", min_width=6)

    for slug, spec in SPECIES.items():
        table.add_row(
            f"[bold]{spec.display_name}[/bold]\n[dim]{slug}[/dim]",
            spec.scientific_name,
            spec.silhouette,
            spec.math_engine.split("+")[0].strip(),
            _palette_swatch(spec.default_palette),
            f"[bold cyan]{spec.default_note}[/bold cyan]",
        )

    console.print()
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# generate command
# ---------------------------------------------------------------------------

@app.command("generate", help="Render a single tree species to SVG.")
def generate(
    species: str = typer.Argument(..., help="Species slug (see [bold]dendra list[/bold])"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output SVG path"),
    iterations: Optional[int] = typer.Option(None, "--iterations", "-i", help="L-system iterations"),
    note: Optional[str] = typer.Option(None, "--note", "-n", help="Musical note e.g. A3, C#4"),
    harmonic_depth: Optional[int] = typer.Option(None, "--harmonic-depth", help="Number of harmonics"),
    seed: int = typer.Option(0, "--seed", "-s", help="Random seed for variation"),
    palette: Optional[str] = typer.Option(None, "--palette", "-p", help="Named palette"),
    color: Optional[str] = typer.Option(None, "--color", "-c", help="Flat hex color e.g. #2d4a38"),
    gradient: Optional[str] = typer.Option(None, "--gradient", "-g", help="Gradient e.g. '#1a3a2a:#8fb8a0:vertical'"),
    width: int = typer.Option(600, "--width", "-W", help="Canvas width in px"),
    height: int = typer.Option(700, "--height", "-H", help="Canvas height in px"),
    trunk_height: Optional[float] = typer.Option(None, "--trunk-height", help="Trunk height as fraction of canvas height (0.0–1.0)"),
    style: str = typer.Option("lsystem", "--style", help="Render style: lsystem or waveform"),
    preview: bool = typer.Option(False, "--preview", help="Open SVG in browser after generation"),
    debug: bool = typer.Option(False, "--debug", help="Show full tracebacks on error"),
) -> None:
    from dendra.renderer import render, write_svg
    from dendra.math.wave import note_to_freq

    # --- Resolve species ---
    slug = species.lower()
    if slug not in SPECIES:
        available = ", ".join(SPECIES.keys())
        _error(f"Unknown species [bold]{slug!r}[/bold].\nAvailable: {available}")

    spec = SPECIES[slug]

    # --- Resolve color ---
    try:
        color_cfg = parse_color_config(palette, color, gradient)
    except ValueError as e:
        if debug:
            raise
        _error(str(e))

    # --- Output path ---
    out_path = output or (OUTPUT_DIR / f"{slug}.svg")

    # --- Resolve display params ---
    note_str = note or spec.default_note
    try:
        freq = note_to_freq(note_str)
    except ValueError as e:
        if debug:
            raise
        _error(str(e))

    n_iter = iterations or spec.lsystem.iterations
    n_harm = harmonic_depth or spec.wave.n_harmonics
    accent = accent_color(color_cfg)

    console.print()

    # --- Validate style ---
    if style not in ("lsystem", "waveform"):
        _error(f"Unknown style {style!r}. Available: lsystem, waveform")

    # --- Progress pipeline ---
    stages = (
        ["Expanding L-system", "Applying wave modulation", "Building SVG paths", "Writing file"]
        if style == "lsystem" else
        ["Sampling harmonic wave", "Building waveform polygon", "Writing file"]
    )

    svg_element = None

    with Progress(
        SpinnerColumn(style=f"{accent}"),
        TextColumn("[bold]{task.description}[/bold]", style="white"),
        BarColumn(bar_width=28, style=accent, complete_style=f"bold {accent}"),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(stages[0], total=len(stages))

        try:
            progress.update(task, description=stages[0], completed=0)

            if style == "waveform":
                from dendra.wave_renderer import render_waveform
                svg_element = render_waveform(
                    spec=spec,
                    color=color_cfg,
                    note=note_str,
                    harmonic_depth=n_harm,
                    seed=seed,
                    canvas_width=width,
                    canvas_height=height,
                    trunk_height=trunk_height,
                )
                progress.update(task, description=stages[1], completed=1)
            else:
                svg_element = render(
                    spec=spec,
                    color=color_cfg,
                    iterations=n_iter,
                    note=note_str,
                    harmonic_depth=n_harm,
                    seed=seed,
                    canvas_width=width,
                    canvas_height=height,
                    trunk_height=trunk_height,
                )
                progress.update(task, description=stages[1], completed=1)
                progress.update(task, description=stages[2], completed=2)

            write_svg(svg_element, out_path)
            progress.update(task, completed=len(stages))

        except Exception as e:
            if debug:
                raise
            _error(str(e))

    # --- Summary panel ---
    from rich.table import Table as RTable

    summary = RTable.grid(padding=(0, 2))
    summary.add_column(style="param.label", justify="right")
    summary.add_column(style="param.value")

    summary.add_row("Species",    f"[species.name]{spec.display_name}[/species.name]  [species.sci]{spec.scientific_name}[/species.sci]")
    summary.add_row("Style",      f"[math.value]{style}[/math.value]")
    summary.add_row("Output",     f"[path.out]{out_path}[/path.out]  [dim]({_file_size(out_path)})[/dim]")
    if style == "lsystem":
        summary.add_row("Iterations", f"[math.value]{n_iter}[/math.value]")
    summary.add_row("Note",       f"[math.value]{note_str}[/math.value]  [dim]→  {freq:.1f} Hz[/dim]")
    summary.add_row("Harmonics",  f"[math.value]{n_harm}[/math.value]")
    summary.add_row("Seed",       f"[math.value]{seed}[/math.value]")
    if trunk_height is not None:
        summary.add_row("Trunk H",    f"[math.value]{trunk_height:.2f}[/math.value]")

    if color_cfg.mode == "palette":
        summary.add_row("Palette", _palette_swatch(color_cfg.palette.name))
    elif color_cfg.mode == "flat":
        summary.add_row("Color", _swatch(color_cfg.flat_color, color_cfg.flat_color))
    else:
        summary.add_row("Gradient",
            f"{_swatch(color_cfg.gradient_start)} → {_swatch(color_cfg.gradient_end)}  "
            f"[dim]{color_cfg.gradient_direction}[/dim]"
        )

    console.print(Panel(
        summary,
        title=f"[bold white]{out_path.name}[/bold white]",
        border_style=accent,
        padding=(1, 2),
    ))
    console.print()

    if preview:
        _open_preview(out_path)


# ---------------------------------------------------------------------------
# batch command
# ---------------------------------------------------------------------------

@app.command("batch", help="Render all species with shared color options.")
def batch(
    output_dir: Path = typer.Option(OUTPUT_DIR, "--output-dir", "-d", help="Directory for output SVGs"),
    iterations: Optional[int] = typer.Option(None, "--iterations", "-i"),
    note: Optional[str] = typer.Option(None, "--note", "-n"),
    harmonic_depth: Optional[int] = typer.Option(None, "--harmonic-depth"),
    seed: int = typer.Option(0, "--seed", "-s"),
    palette: Optional[str] = typer.Option(None, "--palette", "-p"),
    color: Optional[str] = typer.Option(None, "--color", "-c"),
    gradient: Optional[str] = typer.Option(None, "--gradient", "-g"),
    width: int = typer.Option(600, "--width", "-W"),
    height: int = typer.Option(700, "--height", "-H"),
    trunk_height: Optional[float] = typer.Option(None, "--trunk-height"),
    style: str = typer.Option("lsystem", "--style"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    from dendra.renderer import render, write_svg
    from rich.live import Live
    from rich.table import Table as RTable

    try:
        color_cfg = parse_color_config(palette, color, gradient)
    except ValueError as e:
        if debug:
            raise
        _error(str(e))

    console.print()
    results: list[tuple[str, Path, str, bool]] = []   # (display, path, size, ok)

    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold white]{task.description}[/bold white]"),
        BarColumn(bar_width=24, style="dark_green", complete_style="bold green"),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[status]}[/dim]"),
        console=console,
    ) as progress:
        overall = progress.add_task(
            f"[bold]Batch rendering {len(SPECIES)} species[/bold]",
            total=len(SPECIES),
            status="",
        )

        for slug, spec in SPECIES.items():
            progress.update(overall, status=f"{spec.display_name}…")
            out_path = output_dir / f"{slug}.svg"
            ok = True
            try:
                if style == "waveform":
                    from dendra.wave_renderer import render_waveform
                    svg_el = render_waveform(
                        spec=spec,
                        color=color_cfg,
                        note=note or spec.default_note,
                        harmonic_depth=harmonic_depth or spec.wave.n_harmonics,
                        seed=seed,
                        canvas_width=width,
                        canvas_height=height,
                        trunk_height=trunk_height,
                    )
                else:
                    svg_el = render(
                        spec=spec,
                        color=color_cfg,
                        iterations=iterations or spec.lsystem.iterations,
                        note=note or spec.default_note,
                        harmonic_depth=harmonic_depth or spec.wave.n_harmonics,
                        seed=seed,
                        canvas_width=width,
                        canvas_height=height,
                        trunk_height=trunk_height,
                    )
                write_svg(svg_el, out_path)
                size = _file_size(out_path)
            except Exception as e:
                if debug:
                    raise
                size = str(e)
                ok = False

            results.append((spec.display_name, out_path, size, ok))
            progress.advance(overall)

        progress.update(overall, status="[bold green]done[/bold green]")

    # --- Results table ---
    table = Table(box=box.SIMPLE, border_style="dark_green", show_header=True,
                  header_style="bold white")
    table.add_column("Species", style="species.name")
    table.add_column("Output", style="path.out")
    table.add_column("Size", justify="right", style="math.value")
    table.add_column("", justify="center")

    for display, path, size, ok in results:
        status = "[bold green]✓[/bold green]" if ok else "[bold red]✗[/bold red]"
        table.add_row(display, str(path), size, status)

    n_ok = sum(1 for *_, ok in results if ok)
    console.print(Panel(
        table,
        title=f"[bold white]Batch Complete — {n_ok}/{len(SPECIES)} rendered[/bold white]",
        border_style="dark_green",
        padding=(0, 1),
    ))
    console.print()


# ---------------------------------------------------------------------------
# Preview helper
# ---------------------------------------------------------------------------

def _open_preview(path: Path) -> None:
    """Open SVG in the default browser."""
    import webbrowser
    webbrowser.open(path.resolve().as_uri())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
