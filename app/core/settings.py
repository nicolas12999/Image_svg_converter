from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ConversionSettings:
    # vtracer — color engine
    colormode: Literal['color', 'binary'] = 'color'
    hierarchical: Literal['stacked', 'cutout'] = 'stacked'
    mode: Literal['spline', 'polygon', 'none'] = 'spline'
    filter_speckle: int = 4        # 1–32  — removes patches smaller than N px²
    color_precision: int = 6       # 1–8   — color quantization bit depth per channel
    layer_difference: int = 16     # 0–256 — min color distance between layers
    corner_threshold: int = 60     # 0–180 — angle (°) to detect corners
    length_threshold: float = 4.0  # 0–10  — curve simplification (higher = simpler)
    max_iterations: int = 10
    splice_threshold: int = 45
    path_precision: int = 8        # decimal places in path coordinates

    # image pre-processing (applied before vectorization)
    contrast: float = 1.0    # 0.5–2.0, 1.0 = no change
    saturation: float = 1.0  # 0.0–2.0, 1.0 = no change
    sharpness: float = 1.0   # 0.5–2.0, 1.0 = no change
