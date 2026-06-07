from datetime import date, timedelta

from kivy.uix.boxlayout import BoxLayout

from database import (
    get_ingredient_by_name,
    save_meal_log,
    delete_meal_log,        # new — add this to database.py
    get_daily_totals,
    get_daily_meals,
    get_all_ingredient_names,
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
            ingredient_names=get_all_ingredient_names(),
            delete_meal_callback=self.delete_meal,   # wire up delete
        )

        self.add_widget(self.ui)
        self.refresh_daily_summary()

    # ── navigation ────────────────────────────────────────────────────────────

    def go_prev_day(self):
        self.current_date -= timedelta(days=1)
        self._refresh_date_page()

    def go_next_day(self):
        self.current_date += timedelta(days=1)
        self._refresh_date_page()

    def _refresh_date_page(self):
        self.ui.update_date(str(self.current_date))
        self.refresh_daily_summary()

    # ── calculate (no DB write) ───────────────────────────────────────────────

    def calculate_meal_totals(self, ingredients):
        total_cal = total_pro = 0.0
        for item in ingredients:
            name        = item["name"].strip()
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
            _, _, _, cal_per_unit, protein_per_unit = ingredient
            total_cal += amount * cal_per_unit
            total_pro += amount * protein_per_unit
        return total_cal, total_pro

    # ── save ──────────────────────────────────────────────────────────────────

    def save_meal(self, meal_name, ingredients):
        saved_count = save_meal_log(
            meal_name=meal_name,
            eaten_date=str(self.current_date),
            ingredients=ingredients,
        )
        if saved_count == 0:
            self.ui.set_message("No valid ingredients found.", error=True)
        else:
            self.ui.set_message(f"Saved {saved_count} ingredient(s).")
            self.refresh_daily_summary()

    # ── delete ────────────────────────────────────────────────────────────────

    def delete_meal(self, meal_name):
        """Delete all log entries for meal_name on the current date."""
        delete_meal_log(meal_name=meal_name, eaten_date=str(self.current_date))
        self.ui.set_message(f'"{meal_name}" deleted.')
        self.refresh_daily_summary()

    # ── refresh ───────────────────────────────────────────────────────────────

    def refresh_daily_summary(self):
        calories, protein = get_daily_totals(str(self.current_date))
        meals             = get_daily_meals(str(self.current_date))

        self.ui.update_daily_summary(calories, protein)
        self.ui.display_saved_meals(meals)