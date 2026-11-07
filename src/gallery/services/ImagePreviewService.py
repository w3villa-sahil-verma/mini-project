from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

PREVIEW_MAX_DIMENSION = 960
PREVIEW_MAX_PIXELS = 25_000_000
CONTENT_TYPE_FORMATS = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}


def create_gallery_preview(
    image_bytes: bytes,
    content_type: str,
    *,
    watermark: bool,
) -> bytes:
    expected_format = CONTENT_TYPE_FORMATS.get(content_type)
    if expected_format is None:
        raise ValueError("Unsupported gallery image type.")

    try:
        with Image.open(BytesIO(image_bytes)) as source:
            if source.format != expected_format:
                raise ValueError("Uploaded image content does not match its file type.")
            if source.width * source.height > PREVIEW_MAX_PIXELS:
                raise ValueError("Uploaded image dimensions are too large.")

            source.load()
            preview = ImageOps.exif_transpose(source)
            preview.thumbnail(
                (PREVIEW_MAX_DIMENSION, PREVIEW_MAX_DIMENSION),
                Image.Resampling.LANCZOS,
            )
            preview = _flatten_to_rgb(preview)

            if watermark:
                _apply_watermark(preview)

            output = BytesIO()
            preview.save(output, format="WEBP", quality=76, method=5)
            return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValueError("Uploaded file is not a valid image.") from error


def _flatten_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image.copy()
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, "white")
    return Image.alpha_composite(background, rgba).convert("RGB")


def _apply_watermark(image: Image.Image) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default(size=32)
    text = "PREVIEW"
    text_bounds = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    text_width = int(text_bounds[2] - text_bounds[0])
    text_height = int(text_bounds[3] - text_bounds[1])
    step_x = max(text_width * 2, 180)
    step_y = max(text_height * 4, 100)

    for y in range(-text_height, image.height + step_y, step_y):
        for x in range(-text_width, image.width + step_x, step_x):
            position = (x + y // 2, y)
            draw.text(
                position,
                text,
                font=font,
                fill=(255, 255, 255, 150),
                stroke_width=2,
                stroke_fill=(0, 0, 0, 150),
            )

    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"))
