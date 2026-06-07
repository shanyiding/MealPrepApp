from kivy.uix.boxlayout import BoxLayout

from database import (
    add_grocery,
    get_fridge_items,
    get_fridge_totals,
    deduct_inventory,
)
from ui.fridge_ui import FridgeUI


class FridgePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.ui = FridgeUI(
            add_callback=self.add_grocery_clicked,
            delete_callback=self.delete_portion_clicked,
        )

        self.add_widget(self.ui)
        self.refresh_inventory()

    def add_grocery_clicked(self, form_data):
        try:
            name = form_data["name"].strip()
            unit = form_data["unit"].strip()
            calories = float(form_data["calories"])
            protein = float(form_data["protein"])
            quantity = float(form_data["quantity"])
            date_bought = form_data["date_bought"].strip()

            if not name or not unit:
                self.ui.set_message("Food name and unit cannot be empty.")
                return

            add_grocery(name, unit, calories, protein, quantity, date_bought)
            self.ui.set_message(f"Added {quantity}{unit} of {name}.")
            self.ui.clear_add_form()
            self.refresh_inventory()

        except ValueError:
            self.ui.set_message("Calories, protein, and quantity must be numbers.")

    def delete_portion_clicked(self, form_data):
        name = form_data["name"].strip()
        amount_text = form_data["amount"].strip()

        try:
            amount = float(amount_text)
        except ValueError:
            self.ui.set_message("Amount must be a number.")
            return

        items = get_fridge_items()
        matched_item = None

        for item in items:
            ingredient_id, food_name, unit, cal, protein, qty, dates = item
            if food_name.lower() == name.lower():
                matched_item = item
                break

        if not matched_item:
            self.ui.set_message("Food not found in fridge.")
            return

        ingredient_id = matched_item[0]
        unit = matched_item[2]

        success = deduct_inventory(ingredient_id, amount)

        if success:
            self.ui.set_message(f"Removed {amount}{unit} of {name}.")
        else:
            self.ui.set_message(f"Not enough {name}. Removed what was available.")

        self.ui.clear_delete_form()
        self.refresh_inventory()

    def refresh_inventory(self):
        items = get_fridge_items()
        total_calories, total_protein, total_items = get_fridge_totals()

        self.ui.update_summary(total_calories, total_protein, total_items)
        self.ui.display_inventory(items)