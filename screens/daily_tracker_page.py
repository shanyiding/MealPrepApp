from datetime import date, datetime, timedelta

from kivy.uix.boxlayout import BoxLayout

from database import (
    get_ingredient_by_name,
    save_meal_log,
    get_daily_totals,
)

from ui.daily_tracker_ui import DailyTrackerUI


class DailyTrackerPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.current_date = date.today()

        self.ui = DailyTrackerUI(
            date_text=str(self.current_date),
            calculate_callback=self.calculate_meal_totals,
            save_callback=self.save_meal,
            prev_day_callback=self.go_prev_day,
            next_day_callback=self.go_next_day,
        )

        self.add_widget(self.ui)
        self.refresh_daily_summary()

    def go_prev_day(self):
        self.current_date -= timedelta(days=1)
        self.refresh_date_page()

    def go_next_day(self):
        self.current_date += timedelta(days=1)
        self.refresh_date_page()

    def refresh_date_page(self):
        self.ui.update_date(str(self.current_date))
        self.refresh_daily_summary()

    def calculate_meal_totals(self, ingredients):
        total_calories = 0
        total_protein = 0

        for item in ingredients:
            name = item["name"].strip()
            amount_text = item["amount"].strip()

            if not name or not amount_text:
                continue

            try:
                amount = float(amount_text)
            except ValueError:
                continue

            ingredient = get_ingredient_by_name(name)

            if not ingredient:
                continue

            ingredient_id, food_name, unit, cal_per_unit, protein_per_unit = ingredient

            total_calories += amount * cal_per_unit
            total_protein += amount * protein_per_unit

        return total_calories, total_protein

    def save_meal(self, meal_name, ingredients):
        saved_count = save_meal_log(
            meal_name=meal_name,
            eaten_date=str(self.current_date),
            ingredients=ingredients,
        )

        if saved_count == 0:
            self.ui.set_message("No valid ingredients found.")
        else:
            self.ui.set_message(f"Saved {saved_count} ingredient(s).")
            self.refresh_daily_summary()

    def refresh_daily_summary(self):
        calories, protein = get_daily_totals(str(self.current_date))
        self.ui.update_daily_summary(calories, protein)