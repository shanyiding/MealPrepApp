from kivy.uix.boxlayout import BoxLayout

from database import add_grocery
from ui.scan_ui import ScanUI
from services.nutrition_ocr import extract_nutrition


class ScanPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.ui = ScanUI(
            label_callback=self.scan_label,
            add_callback=self.add_to_fridge,
        )

        self.add_widget(self.ui)

    def scan_label(self, image_path):
        try:
            result = extract_nutrition(image_path)
            self.ui.populate_fields(result)
            self.ui.set_message("Nutrition label extracted.")
        except Exception as e:
            self.ui.set_message(f"Label scan failed: {e}", error=True)

    def add_to_fridge(self, form_data):
        try:
            name = form_data["name"].strip()
            unit = form_data["unit"].strip()
            calories = float(form_data["calories"])
            protein = float(form_data["protein"])
            quantity = float(form_data["quantity"])
            date_bought = form_data["date_bought"].strip()

            if not name or not unit:
                self.ui.set_message("Food name and unit cannot be empty.", error=True)
                return

            add_grocery(name, unit, calories, protein, quantity, date_bought)
            self.ui.set_message(f"Added {quantity:g}{unit} of {name}.")

        except ValueError:
            self.ui.set_message("Calories, protein, and quantity must be numbers.", error=True)