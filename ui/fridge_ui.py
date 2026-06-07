from datetime import date

from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


BG = (0.96, 0.94, 0.90, 1)
CARD = (1, 1, 1, 1)
GREEN = (0.35, 0.55, 0.38, 1)
RED = (0.65, 0.35, 0.32, 1)
DARK = (0.13, 0.15, 0.13, 1)
MUTED = (0.42, 0.42, 0.42, 1)


class Card(BoxLayout):
    def __init__(self, bg_color=CARD, radius=18, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.padding = 14
        self.spacing = 8

        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class FridgeUI(BoxLayout):
    def __init__(self, add_callback, delete_callback, **kwargs):
        super().__init__(orientation="vertical", padding=16, spacing=12, **kwargs)

        self.add_callback = add_callback
        self.delete_callback = delete_callback

        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        self.build_title()
        self.build_summary()
        self.build_add_card()
        self.build_delete_card()
        self.build_inventory_list()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def make_input(self, hint, text=""):
        return TextInput(
            text=text,
            hint_text=hint,
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=DARK,
            hint_text_color=MUTED,
            padding=[10, 10, 10, 10],
            size_hint_y=None,
            height=42,
        )

    def make_button(self, text, bg_color=GREEN):
        return Button(
            text=text,
            size_hint_y=None,
            height=46,
            background_normal="",
            background_color=bg_color,
            color=(1, 1, 1, 1),
            bold=True,
        )

    def make_foldable_card(self, title, expanded_height):
        outer = Card(orientation="vertical", size_hint_y=None, height=expanded_height)
        outer.expanded_height = expanded_height
        outer.collapsed_height = 58
        outer.is_open = True

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=34)

        title_label = Label(
            text=title,
            font_size=20,
            bold=True,
            color=DARK,
            halign="left",
            valign="middle",
        )
        title_label.bind(size=title_label.setter("text_size"))

        toggle_btn = Button(
            text="Hide",
            size_hint_x=None,
            width=70,
            background_normal="",
            background_color=(0.82, 0.82, 0.76, 1),
            color=DARK,
            bold=True,
        )

        header.add_widget(title_label)
        header.add_widget(toggle_btn)

        content = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None,
            height=expanded_height - 70,
        )

        outer.add_widget(header)
        outer.add_widget(content)

        def toggle(instance):
            if outer.is_open:
                outer.remove_widget(content)
                outer.height = outer.collapsed_height
                toggle_btn.text = "Show"
                outer.is_open = False
            else:
                outer.add_widget(content)
                outer.height = outer.expanded_height
                toggle_btn.text = "Hide"
                outer.is_open = True

        toggle_btn.bind(on_press=toggle)

        return outer, content

        def toggle(instance):
            if outer.is_open:
                content.opacity = 0
                content.disabled = True
                content.height = 0
                outer.height = outer.collapsed_height
                toggle_btn.text = "Show"
                outer.is_open = False
            else:
                content.opacity = 1
                content.disabled = False
                outer.height = outer.expanded_height
                toggle_btn.text = "Hide"
                outer.is_open = True

        toggle_btn.bind(on_press=toggle)

        outer.add_widget(header)
        outer.add_widget(content)

        return outer, content

    def build_title(self):
        self.add_widget(Label(
            text="MealPrep Fridge",
            font_size=30,
            bold=True,
            color=DARK,
            size_hint_y=None,
            height=44,
        ))

        self.message = Label(
            text="Track what you have before your fridge becomes a crime scene.",
            color=MUTED,
            size_hint_y=None,
            height=34,
        )
        self.add_widget(self.message)

    def build_summary(self):
        card = Card(orientation="vertical", size_hint_y=None, height=115)

        self.summary_label = Label(
            text="",
            markup=True,
            color=DARK,
            font_size=18,
            halign="left",
            valign="middle",
        )
        self.summary_label.bind(size=self.summary_label.setter("text_size"))

        card.add_widget(self.summary_label)
        self.add_widget(card)

    def build_add_card(self):
        card, content = self.make_foldable_card("Add Grocery", expanded_height=340)

        form = GridLayout(cols=2, spacing=8, size_hint_y=None, height=235)

        self.name_input = self.make_input("Eggs / beef / broccoli")
        self.unit_input = self.make_input("g / piece / ml")
        self.cal_input = self.make_input("Calories per unit")
        self.protein_input = self.make_input("Protein per unit")
        self.quantity_input = self.make_input("Quantity bought")
        self.date_input = self.make_input("YYYY-MM-DD", str(date.today()))

        fields = [
            ("Food", self.name_input),
            ("Unit", self.unit_input),
            ("Calories", self.cal_input),
            ("Protein", self.protein_input),
            ("Quantity", self.quantity_input),
            ("Bought date", self.date_input),
        ]

        for label_text, input_widget in fields:
            form.add_widget(Label(text=label_text, color=DARK, size_hint_y=None, height=42))
            form.add_widget(input_widget)

        add_button = self.make_button("Add to Fridge")
        add_button.bind(on_press=lambda instance: self.add_callback(self.get_add_form_data()))

        content.add_widget(form)
        content.add_widget(add_button)

        self.add_widget(card)

    def build_delete_card(self):
        card, content = self.make_foldable_card("Remove / Throw Out", expanded_height=200)

        form = GridLayout(cols=2, spacing=8, size_hint_y=None, height=90)

        self.delete_name_input = self.make_input("Food name")
        self.delete_amount_input = self.make_input("Amount")

        form.add_widget(Label(text="Food", color=DARK, size_hint_y=None, height=42))
        form.add_widget(self.delete_name_input)

        form.add_widget(Label(text="Amount", color=DARK, size_hint_y=None, height=42))
        form.add_widget(self.delete_amount_input)

        delete_button = self.make_button("Remove Portion", bg_color=RED)
        delete_button.bind(on_press=lambda instance: self.delete_callback(self.get_delete_form_data()))

        content.add_widget(form)
        content.add_widget(delete_button)

        self.add_widget(card)

    def build_inventory_list(self):
        self.scroll = ScrollView()

        self.inventory_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=10,
        )

        self.inventory_box.bind(minimum_height=self.inventory_box.setter("height"))
        self.scroll.add_widget(self.inventory_box)
        self.add_widget(self.scroll)

    def update_summary(self, calories, protein, items):
        self.summary_label.text = (
            f"[b]Fridge Summary[/b]\n"
            f"🔥 Total Calories: {calories:.0f} kcal\n"
            f"💪 Total Protein: {protein:.0f} g\n"
            f"📦 Foods: {items}"
        )

    def get_add_form_data(self):
        return {
            "name": self.name_input.text,
            "unit": self.unit_input.text,
            "calories": self.cal_input.text,
            "protein": self.protein_input.text,
            "quantity": self.quantity_input.text,
            "date_bought": self.date_input.text,
        }

    def get_delete_form_data(self):
        return {
            "name": self.delete_name_input.text,
            "amount": self.delete_amount_input.text,
        }

    def clear_add_form(self):
        self.name_input.text = ""
        self.unit_input.text = ""
        self.cal_input.text = ""
        self.protein_input.text = ""
        self.quantity_input.text = ""
        self.date_input.text = str(date.today())

    def clear_delete_form(self):
        self.delete_name_input.text = ""
        self.delete_amount_input.text = ""

    def set_message(self, text):
        self.message.text = text

    def display_inventory(self, items):
        self.inventory_box.clear_widgets()

        if not items:
            self.inventory_box.add_widget(Label(
                text="Fridge is empty.",
                color=DARK,
                size_hint_y=None,
                height=40,
            ))
            return

        for ingredient_id, name, unit, cal, protein, qty, dates in items:
            total_calories = qty * cal
            total_protein = qty * protein

            card = Card(orientation="vertical", size_hint_y=None, height=155)

            title = Label(
                text=f"[b]{name}[/b]",
                markup=True,
                font_size=20,
                color=DARK,
                size_hint_y=None,
                height=28,
                halign="left",
            )
            title.bind(size=title.setter("text_size"))

            details = Label(
                text=(
                    f"Amount: {qty:.1f} {unit}\n"
                    f"Calories stored: {total_calories:.1f} kcal\n"
                    f"Protein stored: {total_protein:.1f} g\n"
                    f"Batches: {dates}"
                ),
                color=MUTED,
                size_hint_y=None,
                height=105,
                halign="left",
                valign="top",
            )
            details.bind(size=details.setter("text_size"))

            card.add_widget(title)
            card.add_widget(details)

            self.inventory_box.add_widget(card)