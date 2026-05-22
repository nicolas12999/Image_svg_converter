# image_svg_converter

Converts PNG/JPG images to SVG with high color fidelity.

Engine: **vtracer** — native multi-color vectorization with its own layer hierarchy.

Color pipeline: ICC profile correction → optional enhancements → RGBA → vtracer.

---

## Requirements

- Python 3.11+
- pip (to install dependencies)

---

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

---

## Graphical Interface (recommended)

```bash
.venv/bin/python main.py
```

Features:
- Drag & drop of images
- Side-by-side preview: original vs. SVG
- Independent zoom
- Presets: Photo, Logo, Illustration, High Quality, Draft, B&W
- Sliders for vectorization and image enhancement
- One-click SVG export
- **Language:** Spanish / English / Chinese (changes in real time, button ⚙)
- **Theme:** Dark (Catppuccin Mocha) / Light (Catppuccin Latte)

---

## CLI

```bash
# Single file
.venv/bin/python convert.py image.png

# Multiple files
.venv/bin/python convert.py photo.jpg logo.png -o output/

# Full directory with preset
.venv/bin/python convert.py images/ -o vectors/ --preset "High quality"

# Manual control
.venv/bin/python convert.py photo.jpg \
--color-precision 7 \
--layer-difference 8 \
--contrast 1.1 \
--saturation 1.15
```

### CLI Options

| Flag | Default | Description |

|------|---------|-------------|

`-o, --output DIR` | Source directory | Output directory |

`--preset NAME` | — | Predefined preset (overrides individual parameters) |

`--colormode` | `color` | `color` or `binary` |

`--hierarchical` | `stacked` | `stacked` (photo) or `cutout` (logo) |

`--mode` | `spline` | `spline`, `polygon`, or `none` |

`--color-precision 1-8` | `6` | Color depth per channel |

`--layer-difference 0-256` | `16` | Minimum difference between layers |

`--filter-speckle 1-32` | `4` | Removes speckles smaller than N px² |

`--corner-threshold 0-180` | `60` | Angle for detecting corners |

`--length-threshold 0-10` | `4.0` | Curve Simplification |

`--contrast 0.5-2.0` | `1.0` | Pre-vectorization Contrast |

`--saturation 0.0-2.0` | `1.0` | Pre-vectorization Saturation |

`--sharpness 0.5-2.0` | `1.0` | Pre-vectorization Sharpness |

--

## Presets

| Preset | Ideal Use |

|--------|-----------|

**Photo** | Photographs with gradients and shadows |

**Logo** | Logos with flat colors |

**Illustration** | Digital illustrations |

**High Quality** | Maximum fidelity, larger SVG file size |

**Draft** | Fast conversion, lower detail |

**B&W** | Grayscale / Black and White |

---

## Why vtracer instead of potrace

| | potrace (before) | vtracer (now) |

-|-----------------|-----------------|

| Colors | 8 by default, quantized MEDIANCUT | 64–256+ layers, perceptual quantization |

| Edges | Jagged (binary bitmap) | Smooth (native multi-layer) |

| Shadows | Lost in quantization | Preserved as gradient layers |

| Gamma | No correction | Correct internal color space |

| ICC profiles | Not applied | Applied before vectorizing |

---

## Architecture

```
image_svg_converter/
├── main.py ← GUI launcher
├── convert.py ← CLI
├── app/
│ ├── core/
│ │ ├── settings.py ← ConversionSettings dataclass
│ │ ├── presets.py ← predefined presets
│ │ └── converter.py ← conversion engine
│ ├── image/
│ │ └── processor.py ← ICC + enhancement
│ ├── ui/
│ │ ├── styles.py
│ │ ├── drop_zone.py
│ │ ├── controls_panel.py
│ │ ├── preview_panel.py
│ │ └── main_window.py
│ └── utils/
│ └── logger.py
├── requirements.txt
└── README.md
```
