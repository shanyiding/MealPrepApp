import re
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Could not read image.")

    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    gray = cv2.convertScaleAbs(gray, alpha=1.4, beta=15)

    return gray

def ocr_image(image_path):
    processed = preprocess_image(image_path)

    texts = []

    for psm in [6, 11, 4, 3]:
        config = f"--psm {psm}"
        text = pytesseract.image_to_string(processed, config=config)
        texts.append(text)

    return "\n".join(texts)


def find_number_after(label, text):
    pattern = rf"{label}\s*[^0-9a-zA-Z]*(\d+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return ""

def guess_tag(protein, calories):
    try:
        protein = float(protein)
        calories = float(calories)
    except Exception:
        return "others"

    if protein >= 8:
        return "protein"
    if calories >= 180 and protein < 8:
        return "carbs"
    return "others"

def extract_nutrition(image_path):
    raw_text = ocr_image(image_path)

    print("\n========== RAW OCR TEXT ==========")
    print(raw_text)
    print("==================================\n")

    calories = find_number_after("calories", raw_text)
    protein = find_number_after("protein", raw_text)
    carbs = find_number_after("total carbohydrate", raw_text)
    fibre = find_number_after("dietary fiber", raw_text)

    tag = "others"
    if protein != "" and protein >= 8:
        tag = "protein"
    elif carbs != "" and carbs >= 10:
        tag = "carbs"
    elif fibre != "" and fibre >= 3:
        tag = "fibre"

    return {
        "name": "",
        "quantity": "",
        "unit": "g",
        "calories": calories,
        "protein": protein,
        "tag": tag,
        "raw_text": raw_text,
    }