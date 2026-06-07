from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock

from ui.fridge_ui import (
    Card, Divider, PillBadge, RoundedInput, RoundedButton,
    BG, BLUE, BLUE_LIGHT, BLUE_DARK, GREEN, GREEN_LIGHT,
    RED, RED_LIGHT, AMBER, AMBER_LIGHT,
    DARK, MID, MUTED, BORDER, CARD, CHIP_OFF,
)

# ── Page-local palette ────────────────────────────────────────────────────────
NAV_BG      = (0.91, 0.93, 0.96, 1)
NAV_TXT     = (0.35, 0.40, 0.47, 1)
EDIT_BG     = (0.88, 0.93, 0.99, 1)   # pencil button bg  (soft blue)
EDIT_TXT    = (0.15, 0.39, 0.66, 1)   # pencil icon colour
DEL_BG      = (0.99, 0.89, 0.89, 1)   # x button bg (soft red)
DEL_TXT     = (0.73, 0.11, 0.11, 1)   # x icon colour
GOAL_BAR_BG = (0.88, 0.90, 0.93, 1)

CAL_GOAL = 1700
PRO_GOAL = 130


# ── Goal progress bar ─────────────────────────────────────────────────────────

class GoalBar(Widget):
    def __init__(self, color, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", 6)
        super().__init__(**kwargs)
        self._color    = color
        self._progress = 0.0
        with self.canvas:
            Color(*GOAL_BAR_BG)
            self._track = RoundedRectangle(pos=self.pos, size=self.size, radius=[3])
            Color(*self._color)
            self._fill  = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[3])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._track.pos  = self.pos
        self._track.size = self.size
        fill_w = min(self.width, self.width * self._progress)
        self._fill.pos  = self.pos
        self._fill.size = (fill_w, self.height)

    def set_progress(self, value, goal):
        self._progress = (value / goal) if goal else 0
        self._upd()


# ── Icon button (tiny rounded square) ────────────────────────────────────────

class IconBtn(RoundedButton):
    """Small square icon button — pencil or X."""
    SIZE = 30

    def __init__(self, symbol, bg_color, text_color, **kwargs):
        super().__init__(
            text=symbol,
            bg_color=bg_color,
            text_color=text_color,
            radius=8,
            font_size=13,
            height=self.SIZE,
            **kwargs,
        )
        self.size_hint = (None, None)
        self.size      = (self.SIZE, self.SIZE)


# ── Ingredient row ────────────────────────────────────────────────────────────

class IngredientRow(BoxLayout):
    def __init__(self, update_callback, delete_callback, ingredient_names,
                 name="", amount="", **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None, height=44, spacing=8, **kwargs,
        )
        self.update_callback  = update_callback
        self.delete_callback  = delete_callback
        self.ingredient_names = ingredient_names
        self.dropdown         = DropDown()

        self.name_input   = RoundedInput("Ingredient", text=name)
        self.amount_input = RoundedInput("Amount", text=amount)
        self.amount_input.size_hint_x = None
        self.amount_input.width       = 80

        self.delete_btn = IconBtn("x", bg_color=DEL_BG, text_color=DEL_TXT)

        self.name_input.bind(text=self._on_name_text)
        self.amount_input.bind(text=lambda *_: self.update_callback())
        self.delete_btn.bind(on_press=lambda _: self.delete_callback(self))

        self.add_widget(self.name_input)
        self.add_widget(self.amount_input)
        self.add_widget(self.delete_btn)

    def _on_name_text(self, instance, value):
        self.update_callback()
        self.dropdown.dismiss()
        self.dropdown = DropDown()
        query = value.strip().lower()
        if not query:
            return
        matches = [n for n in self.ingredient_names if query in n.lower()][:5]
        if not matches:
            return
        for name in matches:
            btn = RoundedButton(name, bg_color=CARD, text_color=DARK,
                                height=38, font_size=13, radius=8)
            btn.bind(on_release=lambda b: self._select(b.text))
            self.dropdown.add_widget(btn)
        self.dropdown.open(self.name_input)

    def _select(self, name):
        self.name_input.text = name
        self.dropdown.dismiss()
        self.update_callback()

    def get_data(self):
        return {"name": self.name_input.text, "amount": self.amount_input.text}


# ── Active / edit meal card ───────────────────────────────────────────────────

class MealCard(Card):
    HEADER_H = 40
    BTN_ROW_H = 40
    ROW_H     = 44
    ROW_GAP   = 8
    V_PAD     = 24

    def __init__(self, calculate_callback, save_callback, meal_number,
                 ingredient_names, prefill_name="", prefill_ingredients=None, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None,
                         height=210, **kwargs)
        self.ingredient_names   = ingredient_names
        self.calculate_callback = calculate_callback
        self.save_callback      = save_callback
        self.meal_number        = meal_number
        self.rows               = []
        self.padding            = [14, 12, 14, 12]
        self.spacing            = 8
        self._build(prefill_name, prefill_ingredients or [])

    def _full_height(self):
        n = len(self.rows)
        return self.HEADER_H + n * self.ROW_H + max(0, n-1) * self.ROW_GAP + self.BTN_ROW_H + self.V_PAD + 16

    def _build(self, prefill_name, prefill_ingredients):
        # header
        header = BoxLayout(orientation="horizontal",
                           size_hint_y=None, height=self.HEADER_H, spacing=8)
        self.meal_name_input = RoundedInput(
            f"Meal {self.meal_number}", text=prefill_name)
        self.meal_name_input.height = self.HEADER_H
        self.total_label = Label(
            text="0 kcal  |  0g pro", color=MID, font_size=12, bold=True,
            halign="right", valign="middle", size_hint_x=None, width=110,
        )
        self.total_label.bind(size=self.total_label.setter("text_size"))
        header.add_widget(self.meal_name_input)
        header.add_widget(self.total_label)
        self.add_widget(header)

        # ingredient rows
        self.ingredients_box = BoxLayout(
            orientation="vertical", size_hint_y=None,
            height=self.ROW_H, spacing=self.ROW_GAP,
        )
        self.add_widget(self.ingredients_box)

        if prefill_ingredients:
            for item in prefill_ingredients:
                # item is either a dict {"name":..,"amount":..} or a display
                # string "Name: amountunit" — handle both
                if isinstance(item, dict):
                    self._add_row(name=item.get("name",""), amount=item.get("amount",""))
                else:
                    # parse "Chicken breast: 150g"
                    parts = item.split(":")
                    n = parts[0].strip() if parts else ""
                    a = parts[1].strip().rstrip("abcdefghijklmnopqrstuvwxyz ") if len(parts) > 1 else ""
                    self._add_row(name=n, amount=a)
        else:
            self._add_row()

        # buttons
        btn_row = BoxLayout(orientation="horizontal",
                            size_hint_y=None, height=self.BTN_ROW_H, spacing=8)
        add_btn = RoundedButton("+ Ingredient", bg_color=GREEN,
                                height=self.BTN_ROW_H, font_size=13, radius=10)
        add_btn.bind(on_press=lambda _: self._add_row())
        save_btn = RoundedButton("Save Meal", bg_color=BLUE,
                                 height=self.BTN_ROW_H, font_size=13, radius=10)
        save_btn.bind(on_press=lambda _: self._save())
        btn_row.add_widget(add_btn)
        btn_row.add_widget(save_btn)
        self.add_widget(btn_row)

        self._update_totals()

    def _add_row(self, name="", amount=""):
        row = IngredientRow(
            update_callback=self._update_totals,
            delete_callback=self._delete_row,
            ingredient_names=self.ingredient_names,
            name=name, amount=amount,
        )
        self.rows.append(row)
        self.ingredients_box.add_widget(row)
        self._resize()

    def _delete_row(self, row):
        if row in self.rows:
            self.rows.remove(row)
            self.ingredients_box.remove_widget(row)
        self._resize()
        self._update_totals()

    def _resize(self):
        n = len(self.rows)
        self.ingredients_box.height = n * self.ROW_H + max(0, n-1) * self.ROW_GAP
        self.height = self._full_height()

    def _update_totals(self):
        cal, pro = self.calculate_callback(self.get_ingredients())
        self.total_label.text = f"{cal:.0f} kcal  |  {pro:.0f}g pro"

    def _save(self):
        name = self.meal_name_input.text.strip() or f"Meal {self.meal_number}"
        self.save_callback(name, self.get_ingredients())

    def get_ingredients(self):
        return [r.get_data() for r in self.rows]


# ── Saved meal card ───────────────────────────────────────────────────────────

class SavedMealCard(Card):
    """
    Read-only display of a logged meal.
    Top-right corner has [pencil] [x] icon buttons.
    edit_callback(meal_name, meal_data) → called when pencil tapped
    delete_callback(meal_name)          → called when x tapped
    """

    LINE_H    = 22
    PILL_H    = 26
    HEADER_H  = 32
    DIVIDER_H = 9    # divider + spacing
    PAD_V     = 24

    def __init__(self, meal_name, meal_data,
                 edit_callback=None, delete_callback=None, **kwargs):
        n = len(meal_data["ingredients"])
        h = self.HEADER_H + self.DIVIDER_H + n * self.LINE_H + 8 + self.PILL_H + self.PAD_V
        super().__init__(orientation="vertical", size_hint_y=None, height=h, **kwargs)

        self.padding = [14, 12, 14, 12]
        self.spacing = 6

        # ── header: name + icon buttons ──
        header = BoxLayout(orientation="horizontal",
                           size_hint_y=None, height=self.HEADER_H, spacing=6)

        title = Label(
            text=f"[b]{meal_name}[/b]", markup=True, color=DARK, font_size=15,
            halign="left", valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        header.add_widget(title)

        if edit_callback:
            edit_btn = IconBtn("/ /", bg_color=EDIT_BG, text_color=EDIT_TXT)
            edit_btn.bind(on_press=lambda _: edit_callback(meal_name, meal_data))
            header.add_widget(edit_btn)

        if delete_callback:
            del_btn = IconBtn("x", bg_color=DEL_BG, text_color=DEL_TXT)
            del_btn.bind(on_press=lambda _: delete_callback(meal_name))
            header.add_widget(del_btn)

        self.add_widget(header)
        self.add_widget(Divider())

        # ── ingredient lines ──
        for line in meal_data["ingredients"]:
            # parse "Chicken breast: 150g" → bold name + muted amount
            parts = line.split(":", 1)
            if len(parts) == 2:
                display = f"[b]{parts[0].strip()}[/b]  [color=#849096]{parts[1].strip()}[/color]"
            else:
                display = line
            lbl = Label(
                text=display, markup=True, color=MID, font_size=13,
                halign="left", valign="middle", size_hint_y=None, height=self.LINE_H,
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)

        # ── macro pill row ──
        pill_row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=self.PILL_H, spacing=6)
        pill_row.add_widget(
            PillBadge(f"Cal {meal_data['calories']:.0f}",
                      bg_color=AMBER_LIGHT, text_color=AMBER, pill_w=80))
        pill_row.add_widget(
            PillBadge(f"Pro {meal_data['protein']:.0f}g",
                      bg_color=RED_LIGHT,   text_color=RED,   pill_w=80))
        pill_row.add_widget(Widget())
        self.add_widget(pill_row)


# ── Main daily tracker UI ─────────────────────────────────────────────────────

class DailyTrackerUI(BoxLayout):
    def __init__(self, date_text, calculate_callback, save_callback,
                 prev_day_callback, next_day_callback, ingredient_names,
                 delete_meal_callback=None, **kwargs):
        super().__init__(
            orientation="vertical", padding=[14, 18, 14, 14], spacing=12, **kwargs,
        )
        self.date_text            = date_text
        self.calculate_callback   = calculate_callback
        self.save_callback        = save_callback
        self.prev_day_callback    = prev_day_callback
        self.next_day_callback    = next_day_callback
        self.ingredient_names     = ingredient_names
        self.delete_meal_callback = delete_meal_callback
        self.meal_count           = 0
        self._toast_event         = None
        self._saved_meals_cache   = {}   # meal_name → meal_data, kept for edit

        with self.canvas.before:
            Color(*BG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        self._build_header()
        self._build_toast()
        self._build_summary()
        self._build_meal_area()

    def _upd_bg(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    # ── header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        title = Label(
            text="Daily Tracker", font_size=24, bold=True, color=DARK,
            size_hint_y=None, height=44, halign="left", valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        self.add_widget(title)

        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8)
        prev_btn = RoundedButton("<", bg_color=NAV_BG, text_color=NAV_TXT,
                                 height=44, font_size=16, radius=12)
        prev_btn.size_hint_x = None
        prev_btn.width       = 48
        prev_btn.bind(on_press=lambda _: self.prev_day_callback())

        self.date_label = Label(
            text=self.date_text, font_size=16, bold=True, color=DARK,
            halign="center", valign="middle",
        )
        self.date_label.bind(size=self.date_label.setter("text_size"))

        next_btn = RoundedButton(">", bg_color=NAV_BG, text_color=NAV_TXT,
                                 height=44, font_size=16, radius=12)
        next_btn.size_hint_x = None
        next_btn.width       = 48
        next_btn.bind(on_press=lambda _: self.next_day_callback())

        nav.add_widget(prev_btn)
        nav.add_widget(self.date_label)
        nav.add_widget(next_btn)
        self.add_widget(nav)

    # ── toast ─────────────────────────────────────────────────────────────────

    def _build_toast(self):
        self.toast = Label(
            text="", font_size=13, color=GREEN, bold=True,
            size_hint_y=None, height=0,
            halign="center", valign="middle", opacity=0,
        )
        self.toast.bind(size=self.toast.setter("text_size"))
        self.add_widget(self.toast)

    def set_message(self, text, error=False):
        self.toast.color   = RED if error else GREEN
        self.toast.text    = text
        self.toast.height  = 28
        self.toast.opacity = 1
        if self._toast_event:
            self._toast_event.cancel()
        self._toast_event = Clock.schedule_once(self._hide_toast, 3)

    def _hide_toast(self, *_):
        self.toast.opacity = 0
        self.toast.height  = 0
        self.toast.text    = ""

    # ── summary ───────────────────────────────────────────────────────────────

    def _build_summary(self):
        card = Card(orientation="vertical", size_hint_y=None, height=130)
        card.padding = [18, 14, 18, 14]
        card.spacing  = 8

        # stat row
        stat_row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=38, spacing=0)

        def stat_col(label):
            col = BoxLayout(orientation="vertical", spacing=2)
            val = Label(text="—", font_size=20, bold=True, color=DARK,
                        halign="center", valign="bottom", size_hint_y=None, height=26)
            val.bind(size=val.setter("text_size"))
            cap = Label(text=label, font_size=11, color=MUTED,
                        halign="center", valign="top", size_hint_y=None, height=16)
            cap.bind(size=cap.setter("text_size"))
            col.add_widget(val)
            col.add_widget(cap)
            return col, val

        def make_sep():
            s = Widget(size_hint_x=None, width=1)
            with s.canvas:
                Color(*BORDER)
                s._l = Line(points=[0, 0, 0, 36], width=1)
            return s

        self._s_cal_col,  self._cal_val     = stat_col("Calories today")
        self._s_pro_col,  self._protein_val = stat_col("Protein today")

        stat_row.add_widget(self._s_cal_col)
        stat_row.add_widget(make_sep())
        stat_row.add_widget(self._s_pro_col)
        card.add_widget(stat_row)

        # progress bars
        bar_row = BoxLayout(orientation="horizontal",
                            size_hint_y=None, height=20, spacing=12)

        cal_col = BoxLayout(orientation="vertical", spacing=3)
        self._cal_bar = GoalBar(color=AMBER)
        cal_cap = Label(text=f"Goal {CAL_GOAL} kcal", font_size=10,
                        color=MUTED, halign="left", valign="middle",
                        size_hint_y=None, height=13)
        cal_cap.bind(size=cal_cap.setter("text_size"))
        cal_col.add_widget(self._cal_bar)
        cal_col.add_widget(cal_cap)

        pro_col = BoxLayout(orientation="vertical", spacing=3)
        self._pro_bar = GoalBar(color=RED)
        pro_cap = Label(text=f"Goal {PRO_GOAL}g protein", font_size=10,
                        color=MUTED, halign="right", valign="middle",
                        size_hint_y=None, height=13)
        pro_cap.bind(size=pro_cap.setter("text_size"))
        pro_col.add_widget(self._pro_bar)
        pro_col.add_widget(pro_cap)

        bar_row.add_widget(cal_col)
        bar_row.add_widget(pro_col)
        card.add_widget(bar_row)

        # comment
        self._comment = Label(
            text="Log a meal to start the day.",
            font_size=13, color=MUTED,
            halign="center", valign="middle",
            size_hint_y=None, height=24,
        )
        self._comment.bind(size=self._comment.setter("text_size"))
        card.add_widget(self._comment)

        self.add_widget(card)

    def update_daily_summary(self, calories, protein):
        self._cal_val.text     = f"{calories:.0f} kcal"
        self._protein_val.text = f"{protein:.0f}g"
        self._cal_bar.set_progress(calories, CAL_GOAL)
        self._pro_bar.set_progress(protein, PRO_GOAL)
        self._comment.text     = self._daily_comment(calories, protein)

    @staticmethod
    def _daily_comment(calories, protein):
        if calories == 0 and protein == 0:
            return "Log a meal to start the day."
        if protein >= PRO_GOAL and calories <= CAL_GOAL:
            return "Protein hit, calories in check. Solid cut day."
        if protein < PRO_GOAL * 0.6:
            return "Protein is low. Feed the muscles."
        if calories > CAL_GOAL:
            return "Calories went over. Log it honestly, move on."
        if protein >= PRO_GOAL:
            return "Protein goal hit. Keep it up."
        if calories < CAL_GOAL * 0.6:
            return "Pretty low intake so far. Don't under-eat."
        return "Decent day. Keep logging."

    # ── meal area ─────────────────────────────────────────────────────────────

    def _build_meal_area(self):
        add_btn = RoundedButton("+ Add Meal", bg_color=BLUE,
                                height=48, font_size=15, radius=12)
        add_btn.bind(on_press=lambda _: self.add_meal_card())
        self.add_widget(add_btn)

        self.scroll   = ScrollView()
        self.meal_box = BoxLayout(orientation="vertical",
                                  size_hint_y=None, spacing=10)
        self.meal_box.bind(minimum_height=self.meal_box.setter("height"))
        self.scroll.add_widget(self.meal_box)
        self.add_widget(self.scroll)

    def add_meal_card(self):
        self.meal_count += 1
        card = MealCard(
            calculate_callback=self.calculate_callback,
            save_callback=self.save_callback,
            meal_number=self.meal_count,
            ingredient_names=self.ingredient_names,
        )
        self.meal_box.add_widget(card)

    # ── edit / delete handlers ────────────────────────────────────────────────

    def _on_edit_meal(self, meal_name, meal_data):
        """
        Replace every SavedMealCard for meal_name with an editable MealCard
        pre-filled with its ingredients.
        """
        # find the card widget to replace
        target = None
        for child in list(self.meal_box.children):
            if isinstance(child, SavedMealCard):
                # match by checking if meal_name label is in the card's first label
                # We stored meal_name on the widget for easy lookup
                if getattr(child, "_meal_name", None) == meal_name:
                    target = child
                    break

        self.meal_count += 1
        edit_card = MealCard(
            calculate_callback=self.calculate_callback,
            save_callback=self._on_save_edited_meal,
            meal_number=self.meal_count,
            ingredient_names=self.ingredient_names,
            prefill_name=meal_name,
            prefill_ingredients=meal_data["ingredients"],
        )
        edit_card._editing_meal_name = meal_name   # track which meal this replaces

        if target:
            idx = self.meal_box.children.index(target)
            self.meal_box.remove_widget(target)
            self.meal_box.add_widget(edit_card, index=idx)
        else:
            self.meal_box.add_widget(edit_card)

    def _on_save_edited_meal(self, meal_name, ingredients):
        """
        Called when the user saves an edited MealCard.
        The page-level save_callback handles DB write + refresh.
        """
        self.save_callback(meal_name, ingredients)

    def _on_delete_meal(self, meal_name):
        if self.delete_meal_callback:
            self.delete_meal_callback(meal_name)

    # ── public display ────────────────────────────────────────────────────────

    def display_saved_meals(self, meals):
        self.meal_box.clear_widgets()
        self.meal_count = 0
        self._saved_meals_cache = dict(meals)

        for meal_name, meal_data in meals.items():
            card = SavedMealCard(
                meal_name=meal_name,
                meal_data=meal_data,
                edit_callback=self._on_edit_meal,
                delete_callback=self._on_delete_meal,
            )
            card._meal_name = meal_name    # stash for lookup in _on_edit_meal
            self.meal_box.add_widget(card)

    def update_date(self, date_text):
        self.date_text       = date_text
        self.date_label.text = date_text