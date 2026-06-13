from datetime import date

from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock

from theme import theme
from ui.fridge_ui import Card, RoundedButton, RoundedInput, Divider


class ScanUI(BoxLayout):
    def __init__(self, label_callback, add_callback, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[14, 18, 14, 14],
            spacing=12,
            **kwargs,
        )

        self.label_callback = label_callback
        self.add_callback = add_callback
        self._toast_event = None
        self.last_image_path = "scanned_item.png"

        with self.canvas.before:
            self._bg_color = Color(*theme.BG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._upd_bg, size=self._upd_bg)

        self._build_header()
        self._build_toast()
        self._build_camera_card()
        self._build_form_card()

        theme.bind(on_theme_change=self._on_theme_change)

    def _upd_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _on_theme_change(self, *_):
        self._bg_color.rgba = theme.BG

    def _build_header(self):
        title = Label(
            text="Nutrition Scanner",
            font_size=24,
            bold=True,
            color=theme.DARK,
            size_hint_y=None,
            height=44,
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        self.add_widget(title)

    def _build_toast(self):
        self.toast = Label(
            text="",
            font_size=13,
            color=theme.GREEN,
            bold=True,
            size_hint_y=None,
            height=0,
            halign="center",
            valign="middle",
            opacity=0,
        )
        self.toast.bind(size=self.toast.setter("text_size"))
        self.add_widget(self.toast)

    def set_message(self, text, error=False):
        self.toast.color = theme.RED if error else theme.GREEN
        self.toast.text = text
        self.toast.height = 28
        self.toast.opacity = 1

        if self._toast_event:
            self._toast_event.cancel()

        self._toast_event = Clock.schedule_once(self._hide_toast, 3)

    def _hide_toast(self, *_):
        self.toast.opacity = 0
        self.toast.height = 0
        self.toast.text = ""

    def _build_camera_card(self):
        card = Card(orientation="vertical", size_hint_y=None, height=350)
        card.padding = [14, 14, 14, 14]
        card.spacing = 10

        desc = Label(
            text="Point the camera at the nutrition label. Fill the label as much as possible.",
            font_size=12,
            color=theme.MUTED,
            size_hint_y=None,
            height=30,
            halign="left",
            valign="middle",
        )
        desc.bind(size=desc.setter("text_size"))
        card.add_widget(desc)

        self.camera = Camera(
            play=True,
            resolution=(1280, 720),
            size_hint_y=None,
            height=220,
        )
        card.add_widget(self.camera)

        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        scan_btn = RoundedButton(
            "Scan Nutrition Label",
            bg_color=theme.BLUE,
            height=44,
            radius=12,
            font_size=13,
        )
        scan_btn.bind(on_press=lambda _: self.capture_and_scan())

        btn_row.add_widget(scan_btn)
        card.add_widget(btn_row)

        self.add_widget(card)

    def _build_form_card(self):
        card = Card(orientation="vertical", size_hint_y=None, height=260)
        card.padding = [14, 14, 14, 14]
        card.spacing = 10

        desc = Label(
            text="Check the extracted info before adding it to your fridge.",
            font_size=12,
            color=theme.MUTED,
            size_hint_y=None,
            height=24,
            halign="left",
            valign="middle",
        )
        desc.bind(size=desc.setter("text_size"))
        card.add_widget(desc)

        card.add_widget(Divider())

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

        self.unit_input = RoundedInput("Unit", text="g")
        self.unit_input.size_hint_x = None
        self.unit_input.width = 66

        row1.add_widget(self.name_input)
        row1.add_widget(self.quantity_input)
        row1.add_widget(self.unit_input)

        row2 = GridLayout(
            cols=4,
            size_hint_y=None,
            height=44,
            spacing=8,
        )

        self.cal_input = RoundedInput("Calories")
        self.protein_input = RoundedInput("Protein")

        self.tag_input = Spinner(
            text="protein",
            values=("protein", "fibre", "carbs", "others"),
            size_hint_y=None,
            height=44,
            background_normal="",
            background_color=theme.INPUT_BG,
            color=theme.DARK,
            font_size=13,
        )

        self.date_input = RoundedInput("Date", text=str(date.today()))

        row2.add_widget(self.cal_input)
        row2.add_widget(self.protein_input)
        row2.add_widget(self.tag_input)
        row2.add_widget(self.date_input)

        add_btn = RoundedButton(
            "Add to Fridge",
            bg_color=theme.GREEN,
            height=44,
            radius=12,
        )
        add_btn.bind(on_press=lambda _: self.add_callback(self.get_form_data()))

        card.add_widget(row1)
        card.add_widget(row2)
        card.add_widget(add_btn)

        self.add_widget(card)

    def capture_and_scan(self):
        try:
            self.camera.export_to_png(self.last_image_path)
            self.set_message("Captured image. Reading nutrition label...")
            self.label_callback(self.last_image_path)

        except Exception as e:
            self.set_message(f"Camera capture failed: {e}", error=True)

    def populate_fields(self, data):
        self.name_input.text = str(data.get("name", ""))
        self.quantity_input.text = str(data.get("quantity", ""))
        self.unit_input.text = str(data.get("unit", "g"))
        self.cal_input.text = str(data.get("calories", ""))
        self.protein_input.text = str(data.get("protein", ""))
        self.tag_input.text = str(data.get("tag", "protein"))
        self.date_input.text = str(data.get("date_bought", str(date.today())))

    def get_form_data(self):
        return {
            "name": self.name_input.text,
            "quantity": self.quantity_input.text,
            "unit": self.unit_input.text,
            "calories": self.cal_input.text,
            "protein": self.protein_input.text,
            "tag": self.tag_input.text.strip().lower(),
            "date_bought": self.date_input.text,
        }