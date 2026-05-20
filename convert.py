#!/usr/bin/env python3
"""PNG/JPG to SVG converter — terminal application using potrace."""

import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageFilter
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

console = Console()

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg"}


# ── Tracing helpers ──────────────────────────────────────────────────────────

def _run_potrace(bmp_path: str, turdsize: int, opttolerance: float) -> str:
    """Run potrace and return the full SVG string."""
    result = subprocess.run(
        [
            "potrace", "--svg",
            "--turdsize", str(turdsize),
            "--opttolerance", str(opttolerance),
            "--output", "-",
            bmp_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _extract_g_element(svg: str, fill_color: str) -> str:
    """Return the <g> element from a potrace SVG with the fill replaced."""
    match = re.search(r"(<g[^>]*>.*?</g>)", svg, re.DOTALL)
    if not match:
        return ""
    g = match.group(1)
    # Replace whatever fill potrace put in with our target color
    g = re.sub(r'fill="[^"]*"', f'fill="{fill_color}"', g)
    return g


def _extract_viewbox(svg: str) -> str:
    """Extract the viewBox attribute value from a potrace SVG."""
    match = re.search(r'viewBox="([^"]+)"', svg)
    return match.group(1) if match else "0 0 100 100"


def _extract_dimensions(svg: str) -> tuple[str, str]:
    """Extract width and height attribute values from a potrace SVG."""
    w = re.search(r'width="([^"]+)"', svg)
    h = re.search(r'height="([^"]+)"', svg)
    return (w.group(1) if w else "100pt"), (h.group(1) if h else "100pt")


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _image_to_bmp(img: Image.Image, tmp_dir: str) -> str:
    """Save a grayscale/binary PIL image as a BMP file potrace can read."""
    path = str(Path(tmp_dir) / "layer.bmp")
    img.save(path, format="BMP")
    return path


def convert_binary(
    src_img: Image.Image,
    tmp_dir: str,
    turdsize: int,
    opttolerance: float,
    threshold: int,
) -> str:
    """Produce a two-color (black on white) SVG via potrace."""
    gray = src_img.convert("L")
    bw = gray.point(lambda p: 0 if p < threshold else 255, "1")
    bmp = _image_to_bmp(bw.convert("L"), tmp_dir)
    svg = _run_potrace(bmp, turdsize, opttolerance)
    w, h = _extract_dimensions(svg)
    vb = _extract_viewbox(svg)
    g = _extract_g_element(svg, "#000000")
    return _build_svg(w, h, vb, "#ffffff", g)


def convert_color(
    src_img: Image.Image,
    tmp_dir: str,
    turdsize: int,
    opttolerance: float,
    num_colors: int,
) -> str:
    """Quantize to N colors, trace each color layer, merge into one SVG."""
    rgb = src_img.convert("RGB")
    quantized = rgb.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)

    # Pillow 12+ returns a compact palette with only the colors actually used.
    raw_palette = quantized.getpalette() or []
    num_palette_entries = len(raw_palette) // 3

    # Map palette index → RGB color, grouping duplicates.
    color_to_indices: dict[tuple[int, int, int], list[int]] = {}
    for i in range(num_palette_entries):
        c: tuple[int, int, int] = (raw_palette[i * 3], raw_palette[i * 3 + 1], raw_palette[i * 3 + 2])
        color_to_indices.setdefault(c, []).append(i)

    # Order colors by luminance (dark first so lighter colors paint on top).
    unique_colors = sorted(
        color_to_indices.keys(),
        key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2],
    )

    w_str = h_str = viewbox = ""
    all_groups: list[str] = []

    # Raw palette indices for every pixel — avoids the P→L palette-lookup bug.
    raw_indices = quantized.tobytes()

    for color in unique_colors:
        indices_set = set(color_to_indices[color])
        # 0 (black) = this color → potrace traces it; 255 (white) = everything else.
        mask_bytes = bytes(0 if b in indices_set else 255 for b in raw_indices)
        mask = Image.frombytes("L", rgb.size, mask_bytes)

        bmp_path = str(Path(tmp_dir) / f"layer_{_rgb_to_hex(color)[1:]}.bmp")
        mask.save(bmp_path, format="BMP")

        svg = _run_potrace(bmp_path, turdsize, opttolerance)

        if not w_str:
            w_str, h_str = _extract_dimensions(svg)
            viewbox = _extract_viewbox(svg)

        g = _extract_g_element(svg, _rgb_to_hex(color))
        if g:
            all_groups.append(g)

    bg_color = _rgb_to_hex(unique_colors[-1]) if unique_colors else "#ffffff"
    return _build_svg(w_str or "100pt", h_str or "100pt", viewbox or "0 0 100 100", bg_color, "\n".join(all_groups))


def _build_svg(width: str, height: str, viewbox: str, bg: str, body: str) -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'version="1.1" '
        f'width="{width}" height="{height}" '
        f'viewBox="{viewbox}" '
        f'preserveAspectRatio="xMidYMid meet">\n'
        f'<rect width="100%" height="100%" fill="{bg}"/>\n'
        f"{body}\n"
        f"</svg>\n"
    )


# ── Main conversion pipeline ─────────────────────────────────────────────────

def convert_image(
    src: Path,
    output_dir: Path,
    *,
    color_mode: str,
    num_colors: int,
    turdsize: int,
    opttolerance: float,
    threshold: int,
) -> tuple[bool, str]:
    try:
        img = Image.open(src)

        # Flatten transparency onto white
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode in ("RGBA", "LA"):
                if img.mode == "LA":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # JPEG compression artifacts create many near-identical colors that each
        # cover too few pixels for potrace to trace. A mild blur merges them.
        if src.suffix.lower() in (".jpg", ".jpeg") and color_mode == "color":
            img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

        svg_path = output_dir / (src.stem + ".svg")

        with tempfile.TemporaryDirectory() as tmp_dir:
            if color_mode == "binary":
                svg_content = convert_binary(img, tmp_dir, turdsize, opttolerance, threshold)
            else:
                svg_content = convert_color(img, tmp_dir, turdsize, opttolerance, num_colors)

        svg_path.write_text(svg_content, encoding="utf-8")
        size_kb = svg_path.stat().st_size / 1024
        return True, f"{svg_path.name} ({size_kb:.1f} KB)"

    except subprocess.CalledProcessError as exc:
        return False, f"potrace error: {exc.stderr.strip()}"
    except Exception as exc:
        return False, str(exc)


def collect_images(paths: list[str]) -> list[Path]:
    images: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for ext in SUPPORTED_FORMATS:
                images.extend(sorted(p.glob(f"*{ext}")))
                images.extend(sorted(p.glob(f"*{ext.upper()}")))
        elif p.is_file():
            if p.suffix.lower() not in SUPPORTED_FORMATS:
                console.print(f"[yellow]Skipped[/yellow] {p.name} — unsupported format")
            else:
                images.append(p)
        else:
            console.print(f"[red]Not found[/red]: {p}")
    return images


def build_summary_table(results: list[tuple[Path, bool, str]]) -> Table:
    table = Table(box=box.ROUNDED, expand=True)
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", no_wrap=True)
    table.add_column("Output / Error")
    for src, ok, msg in results:
        status = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
        table.add_row(src.name, status, msg)
    return table


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="convert",
        description="Convert PNG/JPG images to SVG via potrace vector tracing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python convert.py image.png
  python convert.py photo.jpg -o vectors/
  python convert.py img1.png img2.jpg --color-mode binary
  python convert.py images/ -o out/ --colors 16 --turdsize 6
""",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="FILE_OR_DIR",
        help="PNG/JPG files or directories to convert",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="DIR",
        default=None,
        help="Output directory (default: same directory as each source file)",
    )
    parser.add_argument(
        "--color-mode",
        choices=["color", "binary"],
        default="color",
        help="Tracing mode: 'color' (default) or 'binary' (black & white)",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=8,
        metavar="N",
        help="Number of colors for color mode quantization (default: 8, max: 256)",
    )
    parser.add_argument(
        "--turdsize",
        type=int,
        default=2,
        metavar="N",
        help="Discard speckles smaller than N px² (default: 2)",
    )
    parser.add_argument(
        "--opttolerance",
        type=float,
        default=0.2,
        metavar="F",
        help="Curve optimization tolerance (default: 0.2)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=128,
        metavar="0-255",
        help="Grayscale cut-off for binary mode (default: 128)",
    )

    args = parser.parse_args()

    console.print(Panel.fit("[bold]PNG / JPG → SVG Converter[/bold]", border_style="blue"))

    images = collect_images(args.inputs)
    if not images:
        console.print("[red]No supported images found.[/red]")
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
        task = progress.add_task("Converting…", total=len(images))
        for img_path in images:
            dest = output_dir if output_dir else img_path.parent
            progress.update(task, description=f"[cyan]{img_path.name}[/cyan]")
            ok, msg = convert_image(
                img_path,
                dest,
                color_mode=args.color_mode,
                num_colors=max(2, min(256, args.colors)),
                turdsize=args.turdsize,
                opttolerance=args.opttolerance,
                threshold=max(0, min(255, args.threshold)),
            )
            results.append((img_path, ok, msg))
            progress.advance(task)

    elapsed = time.perf_counter() - start
    console.print(build_summary_table(results))

    ok_count = sum(1 for _, ok, _ in results if ok)
    fail_count = len(results) - ok_count
    console.print(
        f"\n[bold]Done[/bold] in {elapsed:.2f}s — "
        f"[green]{ok_count} converted[/green]"
        + (f", [red]{fail_count} failed[/red]" if fail_count else "")
    )
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
