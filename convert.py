#!/usr/bin/env python3
"""
PNG/JPG → SVG converter — CLI interface.

Uses vtracer for color-accurate vectorization with proper ICC profile handling.
Run  main.py  instead to open the graphical interface.
"""

import argparse
import sys
import time
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from app.core.converter import convert_to_file
from app.core.settings import ConversionSettings

console = Console()
SUPPORTED = {".png", ".jpg", ".jpeg"}


def collect_images(inputs: list[str]) -> list[Path]:
    images: list[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            for ext in SUPPORTED:
                images.extend(sorted(p.glob(f"*{ext}")))
                images.extend(sorted(p.glob(f"*{ext.upper()}")))
        elif p.is_file():
            if p.suffix.lower() not in SUPPORTED:
                console.print(f"[yellow]Saltado[/yellow] {p.name} — formato no soportado")
            else:
                images.append(p)
        else:
            console.print(f"[red]No encontrado[/red]: {p}")
    return images


def _run_one(src: Path, dest_dir: Path, settings: ConversionSettings) -> tuple[bool, str]:
    try:
        out = convert_to_file(src, dest_dir / (src.stem + ".svg"), settings)
        size_kb = out.stat().st_size / 1024
        return True, f"{out.name} ({size_kb:.1f} KB)"
    except Exception as exc:
        return False, str(exc)


def build_table(results: list[tuple[Path, bool, str]]) -> Table:
    t = Table(box=box.ROUNDED, expand=True)
    t.add_column("Origen", style="cyan", no_wrap=True)
    t.add_column("Estado", justify="center", no_wrap=True)
    t.add_column("Resultado / Error")
    for src, ok, msg in results:
        t.add_row(src.name, "[green]OK[/green]" if ok else "[red]FALLO[/red]", msg)
    return t


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="convert",
        description="Convierte imágenes PNG/JPG a SVG con vtracer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ejemplos:
  python convert.py imagen.png
  python convert.py foto.jpg -o vectores/
  python convert.py imagenes/ -o salida/ --preset "Alta calidad"
  python convert.py logo.png --colormode binary --contrast 1.2
""",
    )
    parser.add_argument("inputs", nargs="+", metavar="ARCHIVO_O_DIR")
    parser.add_argument("-o", "--output", metavar="DIR", default=None)

    # preset shortcut
    parser.add_argument(
        "--preset",
        choices=["Foto", "Logo", "Ilustración", "Alta calidad", "Borrador", "B&N"],
        default=None,
        help="Preset de configuración (anula los parámetros individuales si se especifica)",
    )

    # vtracer params
    parser.add_argument("--colormode", choices=["color", "binary"], default="color")
    parser.add_argument("--hierarchical", choices=["stacked", "cutout"], default="stacked")
    parser.add_argument("--mode", choices=["spline", "polygon", "none"], default="spline")
    parser.add_argument("--color-precision", type=int, default=6, metavar="1-8")
    parser.add_argument("--layer-difference", type=int, default=16, metavar="0-256")
    parser.add_argument("--filter-speckle", type=int, default=4, metavar="1-32")
    parser.add_argument("--corner-threshold", type=int, default=60, metavar="0-180")
    parser.add_argument("--length-threshold", type=float, default=4.0, metavar="0-10")

    # enhancement
    parser.add_argument("--contrast", type=float, default=1.0, metavar="0.5-2.0")
    parser.add_argument("--saturation", type=float, default=1.0, metavar="0.0-2.0")
    parser.add_argument("--sharpness", type=float, default=1.0, metavar="0.5-2.0")

    args = parser.parse_args()

    console.print(Panel.fit("[bold]PNG / JPG → SVG Converter[/bold]", border_style="blue"))

    if args.preset:
        from app.core.presets import PRESETS
        settings = PRESETS[args.preset]
        console.print(f"[dim]Usando preset:[/dim] {args.preset}")
    else:
        settings = ConversionSettings(
            colormode=args.colormode,
            hierarchical=args.hierarchical,
            mode=args.mode,
            color_precision=max(1, min(8, args.color_precision)),
            layer_difference=max(0, min(256, args.layer_difference)),
            filter_speckle=max(1, min(32, args.filter_speckle)),
            corner_threshold=max(0, min(180, args.corner_threshold)),
            length_threshold=max(0.0, min(10.0, args.length_threshold)),
            contrast=max(0.5, min(2.0, args.contrast)),
            saturation=max(0.0, min(2.0, args.saturation)),
            sharpness=max(0.5, min(2.0, args.sharpness)),
        )

    images = collect_images(args.inputs)
    if not images:
        console.print("[red]No se encontraron imágenes soportadas.[/red]")
        return 1

    output_dir: Path | None = None
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[Path, bool, str]] = []
    start = time.perf_counter()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Convirtiendo…", total=len(images))
        for img_path in images:
            dest = output_dir or img_path.parent
            progress.update(task, description=f"[cyan]{img_path.name}[/cyan]")
            ok, msg = _run_one(img_path, dest, settings)
            results.append((img_path, ok, msg))
            progress.advance(task)

    elapsed = time.perf_counter() - start
    console.print(build_table(results))

    ok_count = sum(1 for _, ok, _ in results if ok)
    fail_count = len(results) - ok_count
    console.print(
        f"\n[bold]Listo[/bold] en {elapsed:.2f}s — "
        f"[green]{ok_count} convertidos[/green]"
        + (f", [red]{fail_count} fallidos[/red]" if fail_count else "")
    )
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
