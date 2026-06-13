import requests


HEADERS = {
    "User-Agent": "MealPrepApp/1.0 (Personal Android food tracker; contact: shanyiding@gmail.com)"
}


def lookup_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    print("\n========== OPEN FOOD FACTS REQUEST ==========")
    print("URL:", url)
    print("Headers:", HEADERS)

    res = requests.get(url, headers=HEADERS, timeout=8)

    print("HTTP status:", res.status_code)
    print("============================================\n")

    res.raise_for_status()
    data = res.json()

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    nutriments = product.get("nutriments", {})

    name = product.get("product_name") or product.get("generic_name") or ""

    calories_100g = nutriments.get("energy-kcal_100g")
    protein_100g = nutriments.get("proteins_100g")
    carbs_100g = nutriments.get("carbohydrates_100g")
    fiber_100g = nutriments.get("fiber_100g")

    calories_per_g = float(calories_100g) / 100 if calories_100g is not None else ""
    protein_per_g = float(protein_100g) / 100 if protein_100g is not None else ""

    tag = "others"
    if protein_100g is not None and float(protein_100g) >= 8:
        tag = "protein"
    elif fiber_100g is not None and float(fiber_100g) >= 3:
        tag = "fibre"
    elif carbs_100g is not None and float(carbs_100g) >= 10:
        tag = "carbs"

    print("\n========== OPEN FOOD FACTS PRODUCT ==========")
    print("Name:", name)
    print("Calories/100g:", calories_100g)
    print("Protein/100g:", protein_100g)
    print("Tag:", tag)
    print("============================================\n")

    return {
        "name": name,
        "quantity": "",
        "unit": "g",
        "calories": calories_per_g,
        "protein": protein_per_g,
        "tag": tag,
        "source": "Open Food Facts",
    }