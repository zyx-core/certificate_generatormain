from PIL import Image
import pytesseract

def extract_placeholders(image_path: str) -> list[str]:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return [word.strip("{}") for word in text.split() if word.startswith("{") and word.endswith("}")]
