from datetime import date, datetime

from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.clock import Clock
from theme import theme

# ── Palette — Slate & Stone ───────────────────────────────────────────────────
BG = theme.BG
CARD = theme.CARD
GREEN = theme.GREEN
GREEN_LIGHT = theme.GREEN_LIGHT
RED = theme.RED
RED_LIGHT = theme.RED_LIGHT
RED_BTN = theme.RED_BTN
AMBER = theme.AMBER
AMBER_LIGHT = theme.AMBER_LIGHT
BLUE = theme.BLUE
BLUE_DARK = theme.BLUE_DARK
BLUE_LIGHT = theme.BLUE_LIGHT
DARK = theme.DARK
MID = theme.MID
MUTED = theme.MUTED
BORDER = theme.BORDER
INPUT_BG = theme.INPUT_BG
INPUT_BORDER = theme.INPUT_BORDER
CHIP_OFF = theme.CHIP_OFF
CHIP_OFF_TXT = theme.CHIP_OFF_TXT
TAB_OFF = theme.TAB_OFF
TAB_OFF_TXT = theme.TAB_OFF_TXT

TAG_COLORS = {
    "protein": ((0.55, 0.12, 0.12, 1), (0.98, 0.86, 0.86, 1)),
    "fibre":   ((0.09, 0.47, 0.32, 1), (0.86, 0.96, 0.91, 1)),
    "carbs":   ((0.48, 0.28, 0.72, 1), (0.93, 0.88, 0.99, 1)),
    "others":  ((0.52, 0.57, 0.64, 1), (0.88, 0.90, 0.93, 1)),
}
ALL_TAGS = list(TAG_COLORS.keys())


SORT_OPTIONS = [
    ("A-Z", lambda i: i[1].lower()),
    ("Date", lambda i: i[6].split(",")[0].strip()),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def days_since(date_str):
    try:
        # Example input:
        # "2026-06-01: 10piece, 2026-06-06: 100piece"

        first_batch = date_str.split(",")[0].strip()
        date_part = first_batch.split(":")[0].strip()

        bought = datetime.strptime(date_part, "%Y-%m-%d").date()
        return (date.today() - bought).days

    except Exception:
        return -1


def freshness_color(days):
    if days < 0:  return MUTED
    if days <= 3: return GREEN
    if days <= 6: return AMBER
    return RED


def freshness_label(days):
    if days < 0:
        return "Unknown"
    if days == 0:
        return "Today"
    if days == 1:
        return "1 day old"
    return f"{days} days old"

def build_pills(total_cal, total_protein, tag):
    pills = []
    pills.append((f"Cal {total_cal:.0f}", AMBER, AMBER_LIGHT))
    if total_protein > 0:
        pills.append((f"Pro {total_protein:.0f}g", RED, RED_LIGHT))
    skip_type = tag.lower() in ("meat", "fish", "other", "")
    if not skip_type and len(pills) < 3:
        colors = TAG_COLORS.get(tag.lower(), TAG_COLORS["other"])
        pills.append((tag.capitalize(), colors[0], colors[1]))
    return pills[:3]


# ── Widgets ───────────────────────────────────────────────────────────────────

class Card(BoxLayout):
    def __init__(self, bg_color=None, radius=14, border_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or theme.CARD
        self.radius = radius
        self.border_color = border_color or theme.BORDER
        self.padding = [12, 12, 12, 12]
        self.spacing = 6

        with self.canvas.before:
            self._shadow_c = Color(*theme.SHADOW)
            self.shadow = RoundedRectangle(pos=(self.x + 1, self.y - 2), size=self.size, radius=[self.radius])
            self._fill_c = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_c = Color(*self.border_color)
            self.border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                width=1,
            )

        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.shadow.pos = (self.x + 1, self.y - 2)
        self.shadow.size = self.size
        self.border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, self.radius
        )

class RoundedButton(Button):
    """
    Button whose visible background is a RoundedRectangle drawn on canvas.
    Kivy's default Button draws a plain rect regardless of border_radius,
    so we suppress it (background_normal="", background_color transparent)
    and paint our own rounded fill instead.
    """
    def __init__(self, text, bg_color=BLUE, text_color=(1,1,1,1),
                 radius=12, font_size=14, height=48, **kwargs):
        super().__init__(
            text=text,
            background_normal="",
            background_color=(0, 0, 0, 0),   # fully transparent — we draw our own
            color=text_color,
            bold=True,
            font_size=font_size,
            size_hint_y=None,
            height=height,
            **kwargs,
        )
        self._bg_color = bg_color
        self._radius   = radius
        with self.canvas.before:
            self._ci = Color(*self._bg_color)
            self._rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rr.pos  = self.pos
        self._rr.size = self.size

    def set_color(self, c):
        self._bg_color = c
        self._ci.rgba  = c


class RoundedInput(TextInput):
    def __init__(self, hint, text="", **kwargs):
        super().__init__(
            text=text,
            hint_text=hint,
            multiline=False,
            background_normal="",
            background_active="",
            background_color=theme.INPUT_BG,
            foreground_color=theme.DARK,
            hint_text_color=theme.MUTED,
            cursor_color=theme.BLUE,
            padding=[12, 11, 12, 11],
            font_size=14,
            size_hint_y=None,
            height=44,
            write_tab=False,
            **kwargs,
        )


class PillBadge(Label):
    def __init__(self, text, bg_color=GREEN_LIGHT, text_color=GREEN, pill_w=None, **kwargs):
        w = pill_w or max(56, len(text) * 7 + 14)
        super().__init__(
            text=text, color=text_color, font_size=11, bold=True,
            size_hint=(None, None), size=(w, 22),
            halign="center", valign="middle", **kwargs,
        )
        self.text_size = self.size
        with self.canvas.before:
            Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[11])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rect.pos  = self.pos
        self._rect.size = self.size
        self.text_size  = self.size


class ToggleChip(Button):
    def __init__(self, label, on_toggle=None, active=False, chip_w=68, **kwargs):
        super().__init__(
            text=label,
            size_hint=(None, None), size=(chip_w, 28),
            background_normal="", background_color=(0,0,0,0),
            color=(1,1,1,1) if active else CHIP_OFF_TXT,
            bold=True, font_size=11, **kwargs,
        )
        self.active    = active
        self._callback = on_toggle
        with self.canvas.before:
            self._ci = Color(*(BLUE if active else CHIP_OFF))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
        self.bind(pos=self._upd_bg, size=self._upd_bg, on_press=self._toggle)

    def _upd_bg(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def _toggle(self, *_):
        self.active = not self.active
        self._set_state(self.active)
        if self._callback:
            self._callback(self.text, self.active)

    def set_active(self, val):
        self.active = val
        self._set_state(val)

    def _set_state(self, val):
        c = BLUE if val else CHIP_OFF
        self.color = (1,1,1,1) if val else CHIP_OFF_TXT
        self.canvas.before.clear()
        with self.canvas.before:
            self._ci = Color(*c)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])


class Divider(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", 1)
        super().__init__(**kwargs)
        with self.canvas:
            self._line_c = Color(*theme.BORDER)
            self.line = Line(points=[self.x, self.y, self.right, self.y], width=1)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self.line.points = [self.x, self.y, self.right, self.y]

# ── Main UI ───────────────────────────────────────────────────────────────────

class FridgeUI(BoxLayout):
    def __init__(self, add_callback, delete_callback, **kwargs):
        super().__init__(orientation="vertical", padding=[14, 18, 14, 14], spacing=12, **kwargs)
        self.add_callback    = add_callback
        self.delete_callback = delete_callback
        self._toast_event    = None
        self._all_items      = []
        self._search_text    = ""
        self._active_tags    = set()
        self._sort_index     = 0

        with self.canvas.before:
            self._bg_color = Color(*theme.BG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._upd_bg, size=self._upd_bg)

        self._build_header()
        self._build_toast()
        self._build_summary()
        self._build_form_tabs()
        self._build_inventory()

        theme.bind(on_theme_change=self._on_theme_change)

    def _upd_bg(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        
    def _on_theme_change(self, *_):
        self._bg_color.rgba = theme.BG
        
    # ── helpers ───────────────────────────────────────────────────────────────

    def _section_label(self, text):
        lbl = Label(
            text=text, font_size=10, bold=True, color=MUTED,
            size_hint_y=None, height=18, halign="left", valign="middle",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    # ── header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)
        title = Label(
            text="My Fridge", font_size=24, bold=True, color=DARK,
            halign="left", valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        today_lbl = Label(
            text=str(date.today()), font_size=12, color=MUTED,
            halign="right", valign="middle", size_hint_x=None, width=100,
        )
        today_lbl.bind(size=today_lbl.setter("text_size"))
        row.add_widget(title)
        row.add_widget(today_lbl)
        self.add_widget(row)

    # ── toast ─────────────────────────────────────────────────────────────────

    def _build_toast(self):
        self.toast = Label(
            text="", font_size=13, color=GREEN, bold=True,
            size_hint_y=None, height=0, halign="center", valign="middle", opacity=0,
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
        self.add_widget(self._section_label("TOTAL IN FRIDGE"))
        card = Card(orientation="horizontal", size_hint_y=None, height=78)
        card.padding = [16, 10, 16, 10]
        card.spacing = 0

        def stat_col(prefix, label):
            col = BoxLayout(orientation="vertical", spacing=2)
            val = Label(text="—", font_size=19, bold=True, color=DARK,
                        halign="center", valign="bottom", size_hint_y=None, height=28)
            val.bind(size=val.setter("text_size"))
            cap = Label(text=f"{prefix} {label}", font_size=11, color=MUTED,
                        halign="center", valign="top", size_hint_y=None, height=18)
            cap.bind(size=cap.setter("text_size"))
            col.add_widget(val)
            col.add_widget(cap)
            return col, val

        self._s_cal_col,  self._cal_val     = stat_col("Cal.", "Calories")
        self._s_pro_col,  self._protein_val = stat_col("Pro.", "Protein")
        self._s_item_col, self._items_val   = stat_col("#",    "Foods")

        def make_sep():
            s = Widget(size_hint_x=None, width=1)
            with s.canvas:
                Color(*BORDER)
                s._l = Line(points=[0, 0, 0, 48], width=1)
            return s

        card.add_widget(self._s_cal_col)
        card.add_widget(make_sep())
        card.add_widget(self._s_pro_col)
        card.add_widget(make_sep())
        card.add_widget(self._s_item_col)
        self.add_widget(card)

    def update_summary(self, calories, protein, items):
        self._cal_val.text     = f"{calories:.0f} kcal"
        self._protein_val.text = f"{protein:.0f} g"
        self._items_val.text   = str(items)

    # ── tab system (Add / Remove) ─────────────────────────────────────────────

    def _build_form_tabs(self):
        """
        Two tabs side-by-side at the top of a single card.
        Only one panel is visible at a time. The card height expands / contracts.
        """
        COLLAPSED_H = 52          # just the tab bar, nothing open
        ADD_CONTENT_H  = self._add_content_height()
        DEL_CONTENT_H = 44 + 12 + 48 + 20

        # outer container card
        self._tab_card = Card(orientation="vertical",
                              size_hint_y=None, height=COLLAPSED_H)
        self._tab_card.padding = [0, 0, 0, 0]
        self._tab_card.spacing = 0
        self._tab_card._collapsed_h   = COLLAPSED_H
        self._tab_card._add_open_h    = COLLAPSED_H + ADD_CONTENT_H + 16
        self._tab_card._del_open_h    = COLLAPSED_H + DEL_CONTENT_H + 16

        # ── tab bar row ──
        tab_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=COLLAPSED_H)

        self._tab_add_btn = self._make_tab_btn("+ Add Grocery", active=False)
        self._tab_del_btn = self._make_tab_btn("- Remove",      active=False)
        self._tab_add_btn.bind(on_press=lambda _: self._switch_tab("add"))
        self._tab_del_btn.bind(on_press=lambda _: self._switch_tab("del"))

        tab_bar.add_widget(self._tab_add_btn)
        tab_bar.add_widget(self._tab_del_btn)
        self._tab_card.add_widget(tab_bar)

        # ── add panel ──
        self._add_panel = self._build_add_panel(ADD_CONTENT_H)

        # ── delete panel ──
        self._del_panel = self._build_del_panel(DEL_CONTENT_H)

        self._tab_divider = Divider()
        self._active_tab  = None     # neither open yet

        self.add_widget(self._tab_card)

    def _make_tab_btn(self, text, active):
        btn = Button(
            text=text,
            background_normal="",
            background_color=(0,0,0,0),
            color=DARK if active else TAB_OFF_TXT,
            bold=active,
            font_size=14,
            size_hint_y=None,
            height=52,
        )
        # draw rounded top corners only via a full rounded rect —
        # visually they blend into card so this is fine
        with btn.canvas.before:
            btn._tab_ci = Color(*(CARD if active else TAB_OFF))
            btn._tab_rr = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[12])
        btn.bind(pos=lambda w,_: self._upd_tab_btn(w),
                 size=lambda w,_: self._upd_tab_btn(w))
        return btn

    def _upd_tab_btn(self, btn):
        btn._tab_rr.pos  = btn.pos
        btn._tab_rr.size = btn.size

    def _set_tab_active(self, btn, active):
        btn.bold  = active
        btn.color = DARK if active else TAB_OFF_TXT
        btn.canvas.before.clear()
        with btn.canvas.before:
            btn._tab_ci = Color(*(CARD if active else TAB_OFF))
            btn._tab_rr = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[12])

    def _switch_tab(self, which):
        # toggling the same tab collapses it
        if self._active_tab == which:
            self._close_tab()
            return

        # remove whatever panel is open
        if self._active_tab is not None:
            panel = self._add_panel if self._active_tab == "add" else self._del_panel
            self._tab_card.remove_widget(self._tab_divider)
            self._tab_card.remove_widget(panel)

        self._active_tab = which
        panel = self._add_panel if which == "add" else self._del_panel

        self._tab_card.add_widget(self._tab_divider)
        self._tab_card.add_widget(panel)

        self._tab_card.height = (self._tab_card._add_open_h
                                 if which == "add"
                                 else self._tab_card._del_open_h)

        self._set_tab_active(self._tab_add_btn, which == "add")
        self._set_tab_active(self._tab_del_btn, which == "del")

    def _close_tab(self):
        if self._active_tab is None:
            return
        panel = self._add_panel if self._active_tab == "add" else self._del_panel
        self._tab_card.remove_widget(self._tab_divider)
        self._tab_card.remove_widget(panel)
        self._tab_card.height = self._tab_card._collapsed_h
        self._set_tab_active(self._tab_add_btn, False)
        self._set_tab_active(self._tab_del_btn, False)
        self._active_tab = None

    # ── add panel content ─────────────────────────────────────────────────────

    def _add_content_height(self):
        return 44 + 8 + 44 + 12 + 48 + 20

    def _build_add_panel(self, content_h):
        panel = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
            height=content_h,
            padding=[14, 16, 14, 14],
        )

        # Row 1: food name, quantity, unit
        row1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        self.name_input = RoundedInput("Food name")
        self.quantity_input = RoundedInput("Qty")
        self.quantity_input.size_hint_x = None
        self.quantity_input.width = 76

        self.unit_input = RoundedInput("Unit")
        self.unit_input.size_hint_x = None
        self.unit_input.width = 66

        row1.add_widget(self.name_input)
        row1.add_widget(self.quantity_input)
        row1.add_widget(self.unit_input)

        # Row 2: calories, protein, tag, date
        row2 = GridLayout(
            cols=4,
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        self.cal_input = RoundedInput("Calories")
        self.protein_input = RoundedInput("Protein")

        self.tag_input = Spinner(
            text="Tag",
            values=("protein", "fibre", "carbs", "others"),
            size_hint_y=None,
            height=44,
            background_normal="",
            background_color=INPUT_BG,
            color=DARK,
            font_size=13,
        )

        # Default to today
        self.date_input = RoundedInput(
            "Date",
            str(date.today())
        )

        row2.add_widget(self.cal_input)
        row2.add_widget(self.protein_input)
        row2.add_widget(self.tag_input)
        row2.add_widget(self.date_input)

        add_btn = RoundedButton(
            "Add to Fridge",
            bg_color=BLUE,
            radius=12,
            height=48,
        )
        add_btn.bind(on_press=lambda _: self.add_callback(self.get_add_form_data()))

        panel.add_widget(row1)
        panel.add_widget(row2)
        panel.add_widget(add_btn)

        return panel

    # ── delete panel content ──────────────────────────────────────────────────

    def _build_del_panel(self, content_h):
        panel = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
            height=content_h,
            padding=[14, 16, 14, 14],
        )

        # Single row inputs
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        self.delete_name_input = RoundedInput("Food name")

        self.delete_amount_input = RoundedInput("Amount")
        self.delete_amount_input.size_hint_x = None
        self.delete_amount_input.width = 100

        row.add_widget(self.delete_name_input)
        row.add_widget(self.delete_amount_input)

        delete_btn = RoundedButton(
            "Remove Portion",
            bg_color=RED_BTN,
            radius=12,
            height=48,
        )

        delete_btn.bind(
            on_press=lambda _: self.delete_callback(
                self.get_delete_form_data()
            )
        )

        panel.add_widget(row)
        panel.add_widget(delete_btn)

        return panel

    # ── inventory ─────────────────────────────────────────────────────────────
    def _build_inventory(self):
        self.add_widget(self._section_label("WHAT'S IN THE FRIDGE"))

        control_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=72,
            spacing=6,
        )

        # SORT — 20%
        sort_col = BoxLayout(
            orientation="vertical",
            spacing=3,
            size_hint_x=0.25,
        )
        sort_col.add_widget(self._section_label("SORT"))

        sort_chip_row = GridLayout(
            cols=2,
            size_hint_y=None,
            height=30,
            spacing=4,
        )

        self._sort_chips = []

        for idx, (label, _) in enumerate(SORT_OPTIONS):
            chip = ToggleChip(
                label=label,
                active=(idx == 0),
                chip_w=1,  # ignored because of size_hint_x
                on_toggle=lambda lbl, act, i=idx: self._on_sort_chip(i),
            )

            chip.size_hint_x = 1
            chip.font_size = 12

            self._sort_chips.append(chip)
            sort_chip_row.add_widget(chip)

        sort_col.add_widget(sort_chip_row)

        # FILTER — 45%
        filter_col = BoxLayout(
            orientation="vertical",
            spacing=3,
            size_hint_x=0.5,
        )
        filter_col.add_widget(self._section_label("FILTER"))

        tag_row = GridLayout(
            cols=4,
            size_hint_y=None,
            height=30,
            spacing=4,
        )

        self._tag_chips = {}

        for tag in ALL_TAGS:
            chip = ToggleChip(
                label=tag.capitalize(),
                active=False,
                chip_w=1,
                on_toggle=lambda lbl, act, t=tag: self._on_tag_chip(t, act),
            )
            chip.size_hint_x = 1
            chip.font_size = 12
            self._tag_chips[tag] = chip
            tag_row.add_widget(chip)

        filter_col.add_widget(tag_row)

        # SEARCH — 35%, but actual input is shorter
        search_col = BoxLayout(
            orientation="vertical",
            spacing=3,
            size_hint_x=0.25,
        )
        search_col.add_widget(self._section_label("SEARCH"))

        search_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=30,
            spacing=0,
        )

        self._search_input = RoundedInput("Search")
        self._search_input.height = 30
        self._search_input.font_size = 11
        self._search_input.padding = [8, 7, 4, 7]
        self._search_input.size_hint_x = None
        self._search_input.width = 110
        self._search_input.bind(text=self._on_search_text)

        clear_btn = RoundedButton(
            "x",
            bg_color=INPUT_BG,
            text_color=MID,
            radius=10,
            height=30,
        )
        clear_btn.width = 24
        clear_btn.size_hint_x = None
        clear_btn.font_size = 12
        clear_btn.bind(on_press=lambda _: setattr(self._search_input, "text", ""))

        search_row.add_widget(self._search_input)
        search_row.add_widget(clear_btn)
        search_row.add_widget(Widget())

        search_col.add_widget(search_row)

        control_row.add_widget(sort_col)
        control_row.add_widget(filter_col)
        control_row.add_widget(search_col)

        self.add_widget(control_row)

        self.scroll = ScrollView()
        self.inv_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8,
        )
        self.inv_box.bind(minimum_height=self.inv_box.setter("height"))
        self.scroll.add_widget(self.inv_box)
        self.add_widget(self.scroll)

    # ── filter / sort handlers ────────────────────────────────────────────────

    def _on_search_text(self, instance, value):
        self._search_text = value.strip().lower()
        self._render_inventory()

    def _on_sort_chip(self, idx):
        self._sort_index = idx
        for i, chip in enumerate(self._sort_chips):
            chip.set_active(i == idx)
        self._render_inventory()

    def _on_tag_chip(self, tag, active):
        if active:
            self._active_tags.add(tag)
        else:
            self._active_tags.discard(tag)
        self._render_inventory()

    # ── render inventory ──────────────────────────────────────────────────────

    def display_inventory(self, items):
        normalised = []
        for row in items:
            normalised.append(tuple(row) if len(row) >= 8 else tuple(row) + ("other",))
        self._all_items = normalised
        self._render_inventory()

    def _render_inventory(self):
        items = list(self._all_items)
        if self._search_text:
            items = [i for i in items if self._search_text in i[1].lower()]
        if self._active_tags:
            items = [i for i in items if i[7].lower() in self._active_tags]
        try:
            items.sort(key=SORT_OPTIONS[self._sort_index][1])
        except Exception:
            pass

        self.inv_box.clear_widgets()

        if not items:
            msg = ("No items match." if (self._search_text or self._active_tags)
                   else "Your fridge is empty — add something above.")
            empty = Label(text=msg, color=MUTED, font_size=13,
                          size_hint_y=None, height=48, halign="center")
            empty.bind(size=empty.setter("text_size"))
            self.inv_box.add_widget(empty)
            return

        CARD_H = 140
        for i in range(0, len(items), 2):
            row_box = BoxLayout(orientation="horizontal",
                                size_hint_y=None, height=CARD_H, spacing=8)
            row_box.add_widget(self._make_item_card(items[i], CARD_H))
            if i + 1 < len(items):
                row_box.add_widget(self._make_item_card(items[i+1], CARD_H))
            else:
                row_box.add_widget(Widget())
            self.inv_box.add_widget(row_box)

    def _make_item_card(self, row, height):
        ingredient_id, name, unit, cal, protein, qty, dates, tag = row

        total_cal = qty * cal
        total_protein = qty * protein
        days = days_since(dates)
        f_label = freshness_label(days) or "Unknown"

        date_text = dates.replace(", ", "\n")

        card = Card(orientation="vertical", size_hint_y=None, height=135)
        card.padding = [12, 9, 12, 9]
        card.spacing = 4

        # Top: name left, age + dates right
        top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=6)

        name_lbl = Label(
            text=f"[b]{name}[/b]",
            markup=True,
            font_size=13,
            color=DARK,
            halign="left",
            valign="top",
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        right_col = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=95,
            spacing=2,
        )

        right_col.add_widget(
            PillBadge(
                text=f_label,
                bg_color=(0.91, 0.92, 0.94, 1),
                text_color=(0.35, 0.40, 0.47, 1),
                pill_w=90,
            )
        )

        date_lbl = Label(
            text=date_text,
            font_size=8,
            color=MUTED,
            size_hint_y=None,
            height=18,
            halign="center",
            valign="top",
        )
        date_lbl.bind(size=date_lbl.setter("text_size"))
        right_col.add_widget(date_lbl)

        top_row.add_widget(name_lbl)
        top_row.add_widget(right_col)
        card.add_widget(top_row)

        # Amount
        amount_lbl = Label(
            text=f"{qty:.0f}{unit} remaining",
            font_size=12,
            bold=True,
            color=(0.42, 0.47, 0.56, 1),
            size_hint_y=None,
            height=22,
            halign="left",
            valign="middle",
        )
        amount_lbl.bind(size=amount_lbl.setter("text_size"))
        card.add_widget(amount_lbl)

        # Pills
        pill_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=24,
            spacing=5,
        )

        pill_row.add_widget(PillBadge(
            text=f"Cal {total_cal:.0f}",
            bg_color=(1.0, 0.94, 0.76, 1),
            text_color=(0.60, 0.32, 0.05, 1),
            pill_w=59,
        ))

        pill_row.add_widget(PillBadge(
            text=f"Pro {total_protein:.0f}g",
            bg_color=(0.84, 0.89, 1.0, 1),
            text_color=(0.16, 0.30, 0.68, 1),
            pill_w=65,
        ))

        tag_text = tag.capitalize() if tag else "Others"
        if len(tag_text) > 7:
            tag_text = tag_text[:7]

        tag_colors = TAG_COLORS.get(tag.lower(), TAG_COLORS["others"])

        pill_row.add_widget(PillBadge(
            text=tag_text,
            bg_color=tag_colors[1],
            text_color=tag_colors[0],
            pill_w=64,
        ))

        card.add_widget(pill_row)

        return card

    # ── form accessors ────────────────────────────────────────────────────────

    def get_add_form_data(self):
        return {
            "name":        self.name_input.text,
            "unit":        self.unit_input.text,
            "calories":    self.cal_input.text,
            "protein":     self.protein_input.text,
            "quantity":    self.quantity_input.text,
            "date_bought": self.date_input.text,
            "tag": self.tag_input.text.strip().lower() if self.tag_input.text != "Tag" else "others",
        }

    def get_delete_form_data(self):
        return {
            "name":   self.delete_name_input.text,
            "amount": self.delete_amount_input.text,
        }

    def clear_add_form(self):
        self.name_input.text     = ""
        self.unit_input.text     = ""
        self.cal_input.text      = ""
        self.protein_input.text  = ""
        self.quantity_input.text = ""
        self.date_input.text     = str(date.today())
        self.tag_input.text      = ""

    def clear_delete_form(self):
        self.delete_name_input.text   = ""
        self.delete_amount_input.text = ""