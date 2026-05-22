import tempfile
from pathlib import Path

import vtracer

from .settings import ConversionSettings
from ..image.processor import load_image, enhance_image


def convert(src: Path, settings: ConversionSettings) -> str:
    """
    Convert a raster image to an SVG string.

    Pipeline:
      1. Load with ICC profile correction (preserves color accuracy).
      2. Apply user-requested contrast / saturation / sharpness.
      3. Save enhanced image to a temp PNG so vtracer can read it.
      4. Run vtracer's color-aware multi-layer tracer.
      5. Return the SVG string.

    Note: vtracer's in-memory API (convert_pixels_to_svg) segfaults on
    Python 3.14 due to ABI mismatch in the Rust binding (compiled cp310).
    Using convert_image_to_svg_py with temp files is the stable path.
    """
    img = load_image(src)
    img = enhance_image(img, settings.contrast, settings.saturation, settings.sharpness)

    # Ensure RGB for saving as PNG (vtracer handles transparency internally)
    if img.mode == 'RGBA':
        pass  # vtracer accepts RGBA PNGs fine
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    with tempfile.TemporaryDirectory() as tmp:
        tmp_in = Path(tmp) / "input.png"
        tmp_out = Path(tmp) / "output.svg"

        img.save(str(tmp_in), format='PNG')

        # Positional-only call: vtracer's PyO3 binding (cp310 ABI) crashes on
        # Python 3.14 when kwargs are used due to an incompatible C-API change.
        vtracer.convert_image_to_svg_py(
            str(tmp_in),
            str(tmp_out),
            settings.colormode,
            settings.hierarchical,
            settings.mode,
            settings.filter_speckle,
            settings.color_precision,
            settings.layer_difference,
            settings.corner_threshold,
            settings.length_threshold,
            settings.max_iterations,
            settings.splice_threshold,
            settings.path_precision,
        )

        return tmp_out.read_text(encoding='utf-8')


def convert_to_file(src: Path, dst: Path, settings: ConversionSettings) -> Path:
    """Convert image to SVG and write it to dst. Returns dst."""
    svg = convert(src, settings)
    dst.write_text(svg, encoding='utf-8')
    return dst
