import cv2


def scan_barcode_from_image(image_path):
    print("\n========== BARCODE SCAN ==========")
    print("Image path:", image_path)

    img = cv2.imread(image_path)

    if img is None:
        print("Could not read image.")
        print("==================================\n")
        raise ValueError("Could not read image.")

    print("Image shape:", img.shape)

    detector = cv2.barcode.BarcodeDetector()
    result = detector.detectAndDecode(img)

    print("Raw result:", result)

    decoded_info = None

    if len(result) == 4:
        ok, decoded_info, decoded_type, points = result
        print("OK:", ok)
        print("Decoded type:", decoded_type)
        print("Points:", points)

    elif len(result) == 3:
        decoded_info, decoded_type, points = result
        print("Decoded type:", decoded_type)
        print("Points:", points)

    print("Decoded info:", decoded_info)
    print("==================================\n")

    if not decoded_info:
        return None

    if isinstance(decoded_info, str):
        return decoded_info if decoded_info.strip() else None

    for code in decoded_info:
        if code:
            return code

    return None