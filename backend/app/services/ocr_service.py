from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


async def extract_text_with_tesseract(file_path: str) -> str:
    """Extract raw OCR text from a local PDF or image file using Tesseract."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        images = convert_from_path(file_path, dpi=300)
        pages = [_extract_best_text_from_image(image) for image in images]
        return "\n".join(page.strip() for page in pages if page.strip())
    image = Image.open(file_path)
    return _extract_best_text_from_image(image).strip()


def _extract_best_text_from_image(image: Image.Image) -> str:
    """Run OCR on several preprocessed variants and keep the best text candidate."""
    variants = _build_image_variants(image)
    candidates = []
    for variant in variants:
        text = pytesseract.image_to_string(variant, config="--oem 3 --psm 6").strip()
        score = len(text.split())
        candidates.append((score, text))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1] if candidates else ""


def _build_image_variants(image: Image.Image) -> list[Image.Image]:
    """Generate a few enhanced image variants to improve OCR quality on noisy inputs."""
    base = ImageOps.exif_transpose(image).convert("L")
    enlarged = base.resize((max(1, base.width * 2), max(1, base.height * 2)))
    contrast = ImageEnhance.Contrast(enlarged).enhance(2.0)
    sharpened = contrast.filter(ImageFilter.SHARPEN)
    threshold = sharpened.point(lambda pixel: 255 if pixel > 170 else 0)
    return [enlarged, contrast, sharpened, threshold]
