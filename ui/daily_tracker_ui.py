from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from ui.fridge_ui import (
    Card,
    RoundedInput,
    RoundedButton,
    BG,
    CARD,
    BLUE,
    GREEN,
    RED,
    DARK,
    MID,
    MUTED,
)


class IngredientRow(BoxLayout):
    def __init__(self, update_callback, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=8,
            **kwargs,
        )

        self.update_callback = update_callback

        self.name_input = RoundedInput("Ingredient")
        self.amount_input = RoundedInput("Amount")
        self.amount_input.size_hint_x = None
        self.amount_input.width = 90

        self.name_input.bind(text=lambda *_: self.update_callback())
        self.amount_input.bind(text=lambda *_: self.update_callback())

        self.add_widget(self.name_input)
        self.add_widget(self.amount_input)

    def get_data(self):
        return {
            "name": self.name_input.text,
            "amount": self.amount_input.text,
        }


class MealCard(Card):
    def __init__(self, calculate_callback, save_callback, meal_number, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=220,
            **kwargs,
        )

        self.calculate_callback = calculate_callback
        self.save_callback = save_callback
        self.meal_number = meal_number
        self.rows = []

        self.build_card()

    def build_card(self):
        top_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=36,
            spacing=8,
        )

        self.meal_name_input = RoundedInput(f"Meal {self.meal_number}")
        self.meal_name_input.height = 36

        self.total_label = Label(
            text="0 kcal | 0g protein",
            color=MID,
            font_size=12,
            halign="right",
            valign="middle",
            size_hint_x=None,
            width=130,
        )
        self.total_label.bind(size=self.total_label.setter("text_size"))

        top_row.add_widget(self.meal_name_input)
        top_row.add_widget(self.total_label)

        self.add_widget(top_row)

        self.ingredients_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        self.add_widget(self.ingredients_box)

        self.add_ingredient_row()

        button_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        add_ingredient_btn = RoundedButton(
            "+ Ingredient",
            bg_color=GREEN,
            height=42,
        )
        add_ingredient_btn.bind(on_press=lambda _: self.add_ingredient_row())

        save_btn = RoundedButton(
            "Save Meal",
            bg_color=BLUE,
            height=42,
        )
        save_btn.bind(on_press=lambda _: self.save_current_meal())

        button_row.add_widget(add_ingredient_btn)
        button_row.add_widget(save_btn)

        self.add_widget(button_row)

    def add_ingredient_row(self):
        row = IngredientRow(update_callback=self.update_totals)
        self.rows.append(row)

        self.ingredients_box.add_widget(row)

        self.ingredients_box.height = len(self.rows) * 52
        self.height = 36 + self.ingredients_box.height + 44 + 52

        self.update_totals()

    def get_ingredients(self):
        return [row.get_data() for row in self.rows]

    def update_totals(self):
        calories, protein = self.calculate_callback(self.get_ingredients())
        self.total_label.text = f"{calories:.0f} kcal | {protein:.0f}g protein"

    def save_current_meal(self):
        meal_name = self.meal_name_input.text.strip() or f"Meal {self.meal_number}"
        self.save_callback(meal_name, self.get_ingredients())


class DailyTrackerUI(BoxLayout):
    def __init__(self, date_text, calculate_callback, save_callback,
             prev_day_callback, next_day_callback, **kwargs):
        self.prev_day_callback = prev_day_callback
        self.next_day_callback = next_day_callback
        super().__init__(
            orientation="vertical",
            padding=[14, 18, 14, 14],
            spacing=12,
            **kwargs,
        )

        self.date_text = date_text
        self.calculate_callback = calculate_callback
        self.save_callback = save_callback
        self.meal_count = 0

        self.build_header()
        self.build_summary()
        self.build_meal_area()

    def update_date(self, date_text):
        self.date_text = date_text
        self.date_label.text = date_text

    def build_header(self):
        title = Label(
            text="Daily Tracker",
            font_size=24,
            bold=True,
            color=DARK,
            size_hint_y=None,
            height=36,
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        self.add_widget(title)

        date_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        prev_btn = RoundedButton(
            "<",
            bg_color=(0.93, 0.94, 0.96, 1),
            text_color=MID,
            height=40,
        )
        prev_btn.size_hint_x = None
        prev_btn.width = 48
        prev_btn.bind(on_press=lambda _: self.prev_day_callback())

        self.date_label = Label(
            text=self.date_text,
            font_size=16,
            bold=True,
            color=DARK,
            halign="center",
            valign="middle",
        )
        self.date_label.bind(size=self.date_label.setter("text_size"))

        next_btn = RoundedButton( ">",
            bg_color=(0.93, 0.94, 0.96, 1),
            text_color=MID,
            height=40,
        )
        next_btn.size_hint_x = None
        next_btn.width = 48
        next_btn.bind(on_press=lambda _: self.next_day_callback())

        date_row.add_widget(prev_btn)
        date_row.add_widget(self.date_label)
        date_row.add_widget(next_btn)

        self.add_widget(date_row)

        self.message = Label(
            text="",
            color=GREEN,
            font_size=13,
            size_hint_y=None,
            height=24,
        )
        self.add_widget(self.message)

    def build_summary(self):
        card = Card(
            orientation="horizontal",
            size_hint_y=None,
            height=78,
        )

        self.cal_label = Label(
            text="0 kcal",
            font_size=19,
            bold=True,
            color=DARK,
        )

        self.protein_label = Label(
            text="0g protein",
            font_size=19,
            bold=True,
            color=DARK,
        )

        card.add_widget(self.cal_label)
        card.add_widget(self.protein_label)

        self.add_widget(card)

    def build_meal_area(self):
        add_meal_btn = RoundedButton(
            "+ Add Meal",
            bg_color=BLUE,
            height=48,
        )
        add_meal_btn.bind(on_press=lambda _: self.add_meal_card())
        self.add_widget(add_meal_btn)

        self.scroll = ScrollView()

        self.meal_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=10,
        )
        self.meal_box.bind(minimum_height=self.meal_box.setter("height"))

        self.scroll.add_widget(self.meal_box)
        self.add_widget(self.scroll)

    def add_meal_card(self):
        self.meal_count += 1

        card = MealCard(
            calculate_callback=self.calculate_callback,
            save_callback=self.save_callback,
            meal_number=self.meal_count,
        )

        self.meal_box.add_widget(card)

    def update_daily_summary(self, calories, protein):
        self.cal_label.text = f"{calories:.0f} kcal"
        self.protein_label.text = f"{protein:.0f}g protein"

    def set_message(self, text):
        self.message.text = text