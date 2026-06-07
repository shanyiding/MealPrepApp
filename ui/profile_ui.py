"""
profile_ui.py — Profile & Settings page UI.

Exports: ProfileUI
"""
import json
import os
from datetime import date

from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from theme import theme
from ui.fridge_ui import RoundedButton, RoundedInput, Divider

STATS_FILE = "body_stats.json"


def load_body_stats():
    if not os.path.exists(STATS_FILE):
        return []
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_body_stats(data):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class StatsGraph(Widget):
    def __init__(self, stats, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats
        self.bind(pos=self._draw, size=self._draw)

    def set_stats(self, stats):
        self.stats = stats
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()

        with self.canvas:
            Color(*theme.CARD2)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

            if len(self.stats) < 2:
                Color(*theme.MUTED)
                Line(
                    points=[
                        self.x + 20, self.center_y,
                        self.right - 20, self.center_y
                    ],
                    width=1
                )
                return

            weights = [float(s["weight"]) for s in self.stats if s.get("weight")]
            waists = [float(s["waist"]) for s in self.stats if s.get("waist")]

            all_values = weights + waists
            if not all_values:
                return

            min_v = min(all_values)
            max_v = max(all_values)

            if min_v == max_v:
                min_v -= 1
                max_v += 1

            pad_x = 24
            pad_y = 20
            usable_w = self.width - pad_x * 2
            usable_h = self.height - pad_y * 2

            # weight line
            weight_points = []
            for i, stat in enumerate(self.stats):
                if not stat.get("weight"):
                    continue

                value = float(stat["weight"])
                x = self.x + pad_x + usable_w * (i / max(1, len(self.stats) - 1))
                y = self.y + pad_y + usable_h * ((value - min_v) / (max_v - min_v))
                weight_points.extend([x, y])

            if len(weight_points) >= 4:
                Color(*theme.BLUE)
                Line(points=weight_points, width=2)

            for i in range(0, len(weight_points), 2):
                Color(*theme.BLUE)
                RoundedRectangle(
                    pos=(weight_points[i] - 3, weight_points[i + 1] - 3),
                    size=(6, 6),
                    radius=[3],
                )

            # waist line
            waist_points = []
            for i, stat in enumerate(self.stats):
                if not stat.get("waist"):
                    continue

                value = float(stat["waist"])
                x = self.x + pad_x + usable_w * (i / max(1, len(self.stats) - 1))
                y = self.y + pad_y + usable_h * ((value - min_v) / (max_v - min_v))
                waist_points.extend([x, y])

            if len(waist_points) >= 4:
                Color(*theme.AMBER)
                Line(points=waist_points, width=2)

            for i in range(0, len(waist_points), 2):
                Color(*theme.AMBER)
                RoundedRectangle(
                    pos=(waist_points[i] - 3, waist_points[i + 1] - 3),
                    size=(6, 6),
                    radius=[3],
                )
# ── Toggle switch widget ──────────────────────────────────────────────────────

class ToggleSwitch(Widget):
    """
    An iOS-style toggle switch.  Tapping fires on_toggle(is_on).
    """
    W, H, R = 52, 28, 14     # width, height, corner radius
    THUMB_R  = 11

    def __init__(self, is_on=False, on_toggle=None, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (self.W, self.H))
        super().__init__(**kwargs)
        self._on        = is_on
        self._callback  = on_toggle
        self._draw()
        self.bind(pos=self._redraw, size=self._redraw)

    def _draw(self):
        self.canvas.clear()
        track_c = theme.BLUE  if self._on else theme.TOGGLE_TRACK
        thumb_x = self.x + self.W - self.THUMB_R * 2 - 3 if self._on \
                  else self.x + 3
        with self.canvas:
            # track
            Color(*track_c)
            RoundedRectangle(pos=self.pos, size=(self.W, self.H), radius=[self.R])
            # thumb
            Color(*theme.TOGGLE_THUMB)
            RoundedRectangle(
                pos=(thumb_x, self.y + (self.H - self.THUMB_R * 2) // 2),
                size=(self.THUMB_R * 2, self.THUMB_R * 2),
                radius=[self.THUMB_R],
            )

    def _redraw(self, *_):
        self._draw()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._on = not self._on
            self._draw()
            if self._callback:
                self._callback(self._on)
            return True
        return super().on_touch_down(touch)

    def set_state(self, val: bool):
        self._on = val
        self._draw()


# ── Section header inside the page ────────────────────────────────────────────

def _section_lbl(text):
    lbl = Label(
        text=text, font_size=10, bold=True,
        color=theme.MUTED,
        size_hint_y=None, height=18,
        halign="left", valign="middle",
    )
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


# ── Setting row (label left, widget right) ────────────────────────────────────

class SettingRow(BoxLayout):
    def __init__(self, label_text, right_widget, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None, height=44,
            **kwargs,
        )
        lbl = Label(
            text=label_text,
            font_size=14,
            color=theme.DARK,
            halign="left", valign="middle",
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.add_widget(lbl)
        self.add_widget(right_widget)


# ── Card wrapper (replicates fridge_ui.Card without importing it to avoid
#    circular theme issues — reads from theme singleton directly) ──────────────

class ProfileCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = [16, 14, 16, 14]
        self.spacing  = 10
        self._radius  = 14
        with self.canvas.before:
            self._shadow_c = Color(*theme.SHADOW)
            self._shadow   = RoundedRectangle(
                pos=(self.x+1, self.y-2), size=self.size, radius=[self._radius])
            self._fill_c   = Color(*theme.CARD)
            self._fill     = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self._radius])
            self._border_c = Color(*theme.BORDER)
            self._border   = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self._radius),
                width=1)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._fill.pos    = self.pos
        self._fill.size   = self.size
        self._shadow.pos  = (self.x+1, self.y-2)
        self._shadow.size = self.size
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, self._radius)

    def apply_theme(self):
        self._shadow_c.rgba = theme.SHADOW
        self._fill_c.rgba   = theme.CARD
        self._border_c.rgba = theme.BORDER
        self._upd()


# ── Main Profile UI ───────────────────────────────────────────────────────────

class ProfileUI(BoxLayout):
    """
    Full-page profile / settings screen.

    Callbacks:
        on_goals_saved(cal_goal, protein_goal)
        on_dark_toggle(is_dark)
    """

    def __init__(self, on_goals_saved=None, on_dark_toggle=None, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[14, 20, 14, 14],
            spacing=14,
            **kwargs,
        )
        self._on_goals_saved = on_goals_saved
        self._on_dark_toggle = on_dark_toggle
        self._toast_event    = None

        self._draw_bg()
        self.bind(pos=self._upd_bg, size=self._upd_bg)
        
        self._body_stats = load_body_stats()
        self._build_header()
        self._build_goals_card()
        self._build_body_stats_card()
        self._build_appearance_card()
        self._build_toast()
        self.add_widget(Widget())   # flex spacer pushes content up

        # subscribe so dark-mode flip repaints this page too
        theme.bind(on_theme_change=self._on_theme_change)

    def _stats_summary_text(self):
        if not self._body_stats:
            return "No body stats saved yet."

        latest = self._body_stats[-1]
        text = f"Latest: {latest['weight']}kg"
        if latest.get("height"):
            text += f" | {latest['height']}cm"
        if latest.get("waist"):
            text += f" | waist {latest['waist']}cm"
        text += f" | {latest['date']}"
        return text


    def _save_body_stats(self, *_):
        height = self._height_input.text.strip()
        weight = self._weight_input.text.strip()
        waist = self._waist_input.text.strip()
        recorded_date = self._date_input.text.strip() or str(date.today())

        if not weight:
            self._show_toast("Weight is required.", error=True)
            return

        try:
            float(weight)
            if height:
                float(height)
            if waist:
                float(waist)
        except ValueError:
            self._show_toast("Stats must be numbers.", error=True)
            return

        entry = {
            "date": recorded_date,
            "height": height,
            "weight": weight,
            "waist": waist,
        }

        self._body_stats.append(entry)
        self._body_stats.sort(key=lambda x: x["date"])
        save_body_stats(self._body_stats)

        self._latest_stats.text = self._stats_summary_text()
        self._stats_graph.set_stats(self._body_stats)

        self._show_toast("Body stats saved.")

    # ── background ────────────────────────────────────────────────────────────

    def _draw_bg(self):
        with self.canvas.before:
            self._bg_c  = Color(*theme.BG)
            self._bg_rr = RoundedRectangle(pos=self.pos, size=self.size)

    def _upd_bg(self, *_):
        self._bg_rr.pos  = self.pos
        self._bg_rr.size = self.size

    # ── header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        self._title = Label(
            text="Profile & Settings",
            font_size=24, bold=True,
            color=theme.DARK,
            size_hint_y=None, height=46,
            halign="left", valign="middle",
        )
        self._title.bind(size=self._title.setter("text_size"))
        self.add_widget(self._title)

    # ── goals card ────────────────────────────────────────────────────────────
    def _build_goals_card(self):
        self.add_widget(_section_lbl("DAILY GOALS"))

        card = ProfileCard(orientation="vertical", size_hint_y=None, height=218)
        self._goals_card = card

        desc = Label(
            text="Set your daily targets. The tracker bars and comments update automatically.",
            font_size=12,
            color=theme.MUTED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=32,
            text_size=(340, None),
        )
        desc.bind(size=desc.setter("text_size"))
        card.add_widget(desc)

        card.add_widget(Divider())

        cal_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=10,
        )

        cal_lbl = Label(
            text="Calories (kcal)",
            font_size=14,
            color=theme.DARK,
            halign="left",
            valign="middle",
        )
        cal_lbl.bind(size=cal_lbl.setter("text_size"))

        self._cal_input = RoundedInput("e.g. 1700", text=str(theme.cal_goal))
        self._cal_input.size_hint_x = None
        self._cal_input.width = 110
        self._cal_input.input_filter = "int"

        cal_row.add_widget(cal_lbl)
        cal_row.add_widget(self._cal_input)
        card.add_widget(cal_row)

        pro_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=10,
        )

        pro_lbl = Label(
            text="Protein (g)",
            font_size=14,
            color=theme.DARK,
            halign="left",
            valign="middle",
        )
        pro_lbl.bind(size=pro_lbl.setter("text_size"))

        self._pro_input = RoundedInput("e.g. 130", text=str(theme.protein_goal))
        self._pro_input.size_hint_x = None
        self._pro_input.width = 110
        self._pro_input.input_filter = "int"

        pro_row.add_widget(pro_lbl)
        pro_row.add_widget(self._pro_input)
        card.add_widget(pro_row)

        save_btn = RoundedButton(
            "Save Goals",
            bg_color=theme.BLUE,
            height=44,
            font_size=14,
            radius=12,
        )
        save_btn.bind(on_press=self._save_goals)
        self._save_btn = save_btn
        card.add_widget(save_btn)

        self.add_widget(card)

    def _build_body_stats_card(self):
        self.add_widget(_section_lbl("BODY STATS"))

        card = ProfileCard(orientation="vertical", size_hint_y=None, height=310)
        self._stats_card = card

        desc = Label(
            text="Track your cut over time. Weight is graphed so you can see the trend.",
            font_size=12,
            color=theme.MUTED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=32,
            text_size=(340, None),
        )
        desc.bind(size=desc.setter("text_size"))
        self._stats_desc = desc
        card.add_widget(desc)

        card.add_widget(Divider())

        grid = GridLayout(cols=2, spacing=8, size_hint_y=None, height=96)

        self._height_input = RoundedInput("Height cm")
        self._weight_input = RoundedInput("Weight kg")
        self._waist_input = RoundedInput("Waist cm")
        self._date_input = RoundedInput("Date", text=str(date.today()))

        grid.add_widget(self._height_input)
        grid.add_widget(self._weight_input)
        grid.add_widget(self._waist_input)
        grid.add_widget(self._date_input)

        card.add_widget(grid)

        save_btn = RoundedButton(
            "Save Body Stats",
            bg_color=theme.BLUE,
            height=42,
            font_size=14,
            radius=12,
        )
        save_btn.bind(on_press=self._save_body_stats)
        self._save_stats_btn = save_btn
        card.add_widget(save_btn)

        self._latest_stats = Label(
            text=self._stats_summary_text(),
            font_size=12,
            color=theme.MUTED,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=28,
        )
        self._latest_stats.bind(size=self._latest_stats.setter("text_size"))
        card.add_widget(self._latest_stats)

        legend = Label(
            text="[color=4D93E6]■[/color] Weight    [color=E6A53A]■[/color] Waist",
            markup=True,
            font_size=11,
            color=theme.MUTED,
            size_hint_y=None,
            height=18,
            halign="center",
            valign="middle",
        )
        legend.bind(size=legend.setter("text_size"))
        self._stats_legend = legend
        card.add_widget(legend)

        self._stats_graph = StatsGraph(
            self._body_stats,
            size_hint_y=None,
            height=80,
        )
        card.add_widget(self._stats_graph)
        self.add_widget(card)

    # ── appearance card ───────────────────────────────────────────────────────

    def _build_appearance_card(self):
        self.add_widget(_section_lbl("APPEARANCE"))

        card = ProfileCard(orientation="vertical", size_hint_y=None, height=78)
        self._appearance_card = card

        row = BoxLayout(orientation="horizontal",
                        size_hint_y=None, height=44, spacing=10)

        lbl = Label(
            text="Dark Mode",
            font_size=14, color=theme.DARK,
            halign="left", valign="middle",
        )
        lbl.bind(size=lbl.setter("text_size"))
        self._dark_label = lbl

        self._toggle = ToggleSwitch(
            is_on=theme.dark,
            on_toggle=self._on_dark_toggled,
        )
        self._toggle.size_hint_x = None
        self._toggle.width       = ToggleSwitch.W

        row.add_widget(lbl)
        row.add_widget(self._toggle)
        card.add_widget(row)

        self.add_widget(card)

    # ── toast ─────────────────────────────────────────────────────────────────

    def _build_toast(self):
        self._toast = Label(
            text="", font_size=13, bold=True,
            color=theme.GREEN,
            size_hint_y=None, height=0,
            halign="center", valign="middle", opacity=0,
        )
        self._toast.bind(size=self._toast.setter("text_size"))
        self.add_widget(self._toast)

    def _show_toast(self, text, error=False):
        self._toast.color   = theme.RED if error else theme.GREEN
        self._toast.text    = text
        self._toast.height  = 28
        self._toast.opacity = 1
        if self._toast_event:
            self._toast_event.cancel()
        self._toast_event = Clock.schedule_once(self._hide_toast, 2.5)

    def _hide_toast(self, *_):
        self._toast.opacity = 0
        self._toast.height  = 0
        self._toast.text    = ""

    # ── handlers ──────────────────────────────────────────────────────────────

    def _save_goals(self, *_):
        try:
            cal     = int(self._cal_input.text.strip() or "0")
            protein = int(self._pro_input.text.strip() or "0")
        except ValueError:
            self._show_toast("Please enter whole numbers.", error=True)
            return

        if cal < 100 or protein < 10:
            self._show_toast("Goals seem too low — check the values.", error=True)
            return

        theme.set_goals(cal, protein)
        self._show_toast("Goals saved.")

        if self._on_goals_saved:
            self._on_goals_saved(cal, protein)

    def _on_dark_toggled(self, is_on: bool):
        theme.set_dark(is_on)
        if self._on_dark_toggle:
            self._on_dark_toggle(is_on)

    # ── theme change repaint ──────────────────────────────────────────────────

    def _on_theme_change(self, *_):
        # repaint background
        self._bg_c.rgba = theme.BG
        self._stats_legend.color = theme.MUTED
        # labels
        self._title.color     = theme.DARK
        self._dark_label.color = theme.DARK
        self._toast.color     = theme.GREEN

        # cards
        self._goals_card.apply_theme()
        self._appearance_card.apply_theme()

        # save button colour
        self._save_btn.set_color(theme.BLUE)

        # toggle sync (in case set_dark was called externally)
        self._toggle.set_state(theme.dark)
        self._stats_card.apply_theme()

        self._stats_desc.color = theme.MUTED
        self._latest_stats.color = theme.MUTED
        self._save_stats_btn.set_color(theme.BLUE)
        self._stats_graph._draw()