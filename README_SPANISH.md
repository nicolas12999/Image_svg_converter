# image_svg_converter

Convierte imágenes PNG/JPG a SVG con alta fidelidad de color.

Motor: **vtracer** — vectorización nativa multi-color con jerarquía de capas propia.  
Pipeline de color: corrección de perfil ICC → mejoras opcionales → RGBA → vtracer.

---

## Requisitos

- Python 3.11+
- pip (para instalar dependencias)

---

## Instalación

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

---

## Interfaz gráfica (recomendada)

```bash
.venv/bin/python main.py
```

Características:
- Drag & drop de imágenes
- Preview lado a lado: original vs SVG
- Zoom independiente
- Presets: Foto, Logo, Ilustración, Alta calidad, Borrador, B&N
- Sliders de vectorización y mejora de imagen
- Exportar SVG con un clic
- **Idioma:** Español / English / 中文 (cambia en tiempo real, botón ⚙)
- **Tema:** Oscuro (Catppuccin Mocha) / Claro (Catppuccin Latte)

---

## CLI

```bash
# Archivo único
.venv/bin/python convert.py imagen.png

# Varios archivos
.venv/bin/python convert.py foto.jpg logo.png -o salida/

# Directorio completo con preset
.venv/bin/python convert.py imagenes/ -o vectores/ --preset "Alta calidad"

# Control manual
.venv/bin/python convert.py foto.jpg \
  --color-precision 7 \
  --layer-difference 8 \
  --contrast 1.1 \
  --saturation 1.15
```

### Opciones CLI

| Flag | Defecto | Descripción |
|------|---------|-------------|
| `-o, --output DIR` | directorio origen | Directorio de salida |
| `--preset NOMBRE` | — | Preset predefinido (anula parámetros individuales) |
| `--colormode` | `color` | `color` o `binary` |
| `--hierarchical` | `stacked` | `stacked` (foto) o `cutout` (logo) |
| `--mode` | `spline` | `spline`, `polygon`, o `none` |
| `--color-precision 1-8` | `6` | Profundidad de color por canal |
| `--layer-difference 0-256` | `16` | Diferencia mínima entre capas |
| `--filter-speckle 1-32` | `4` | Elimina manchas menores de N px² |
| `--corner-threshold 0-180` | `60` | Ángulo para detectar esquinas |
| `--length-threshold 0-10` | `4.0` | Simplificación de curvas |
| `--contrast 0.5-2.0` | `1.0` | Contraste pre-vectorización |
| `--saturation 0.0-2.0` | `1.0` | Saturación pre-vectorización |
| `--sharpness 0.5-2.0` | `1.0` | Nitidez pre-vectorización |

---

## Presets

| Preset | Uso ideal |
|--------|-----------|
| **Foto** | Fotografías con gradientes y sombras |
| **Logo** | Logotipos con colores planos |
| **Ilustración** | Ilustraciones digitales |
| **Alta calidad** | Máxima fidelidad, SVG más pesado |
| **Borrador** | Conversión rápida, menor detalle |
| **B&N** | Escala de grises / blanco y negro |

---

## Por qué vtracer en lugar de potrace

| | potrace (antes) | vtracer (ahora) |
|-|-----------------|-----------------|
| Colores | 8 por defecto, cuantizado MEDIANCUT | 64–256+ capas, cuantización perceptual |
| Bordes | Jagged (bitmap binario) | Suaves (multi-layer nativo) |
| Sombras | Se pierden en la cuantización | Preservadas como capas de gradiente |
| Gamma | Sin corrección | Espacio de color interno correcto |
| ICC profiles | No aplicado | Aplicado antes de vectorizar |

---

## Arquitectura

```
image_svg_converter/
├── main.py              ← lanzador GUI
├── convert.py           ← CLI
├── app/
│   ├── core/
│   │   ├── settings.py  ← ConversionSettings dataclass
│   │   ├── presets.py   ← presets predefinidos
│   │   └── converter.py ← motor de conversión
│   ├── image/
│   │   └── processor.py ← ICC + enhancement
│   ├── ui/
│   │   ├── styles.py
│   │   ├── drop_zone.py
│   │   ├── controls_panel.py
│   │   ├── preview_panel.py
│   │   └── main_window.py
│   └── utils/
│       └── logger.py
├── requirements.txt
└── README.md
```
