import io
from pathlib import Path

from PIL import Image, ImageCms, ImageEnhance


def load_image(path: str | Path) -> Image.Image:
    """
    Load an image with proper ICC profile handling.

    Converts the image to sRGB so vtracer receives color-accurate pixels.
    Without this step, photos with AdobeRGB / DisplayP3 / other profiles look
    desaturated or tinted because PIL treats all bytes as sRGB by default.
    """
    img = Image.open(str(path))

    if 'icc_profile' in img.info and img.info['icc_profile']:
        try:
            icc_bytes = img.info['icc_profile']
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
            dst_profile = ImageCms.createProfile('sRGB')

            if img.mode == 'RGBA':
                # Convert RGB channels; carry alpha separately
                r, g, b, a = img.split()
                rgb = Image.merge('RGB', (r, g, b))
                rgb = ImageCms.profileToProfile(rgb, src_profile, dst_profile)
                r2, g2, b2 = rgb.split()
                img = Image.merge('RGBA', (r2, g2, b2, a))
            elif img.mode == 'CMYK':
                img = ImageCms.profileToProfile(
                    img, src_profile, dst_profile, outputMode='RGB'
                )
            else:
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                img = ImageCms.profileToProfile(img, src_profile, dst_profile)
        except Exception:
            pass  # fall through with original pixels if ICC transform fails

    # Normalise to RGB or RGBA
    if img.mode == 'CMYK':
        img = img.convert('RGB')
    elif img.mode == 'P':
        img = img.convert('RGBA')
    elif img.mode == 'L':
        img = img.convert('RGB')
    elif img.mode == 'LA':
        img = img.convert('RGBA')
    elif img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    return img


def enhance_image(
    img: Image.Image,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0,
) -> Image.Image:
    """Apply perceptual adjustments before vectorization."""
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
    return img
