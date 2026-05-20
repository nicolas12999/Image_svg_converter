# image_svg_converter

Terminal application that converts PNG and JPG images to SVG using [potrace](http://potrace.sourceforge.net/) vector tracing.

## Requirements

- Python 3.11+
- `potrace` installed system-wide (`pacman -S potrace` on Arch)

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```bash
# Single file
.venv/bin/python convert.py image.png

# Multiple files
.venv/bin/python convert.py photo1.jpg logo.png -o out/

# Entire directory
.venv/bin/python convert.py images/ -o vectors/

# Black & white tracing
.venv/bin/python convert.py image.png --color-mode binary

# High color fidelity (more colors = larger SVG, slower)
.venv/bin/python convert.py photo.jpg --colors 16
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-o, --output DIR` | source dir | Output directory |
| `--color-mode` | `color` | `color` or `binary` (black & white) |
| `--colors N` | `8` | Colors for quantization (color mode, max 256) |
| `--turdsize N` | `2` | Discard patches smaller than N px² |
| `--opttolerance F` | `0.2` | Curve smoothing tolerance |
| `--threshold 0-255` | `128` | Grayscale threshold for binary mode |

## How it works

Color images are quantized to N colors (median-cut), then each color is traced separately using potrace to produce filled vector paths, layered from dark to light into a single SVG.
