from kivy.config import Config

Config.set("graphics", "width", "390")
Config.set("graphics", "height", "844")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from database import init_db, seed_sample_data
from screens.fridge_page import FridgePage
from screens.daily_tracker_page import DailyTrackerPage
from ui.fridge_ui import RoundedButton, BLUE, CHIP_OFF, MID


class RootPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=52,
            spacing=6,
            padding=[14, 10, 14, 0],
        )

        self.fridge_btn = RoundedButton("My Fridge", bg_color=BLUE, height=42)
        self.daily_btn = RoundedButton("Daily Tracker", bg_color=CHIP_OFF, text_color=MID, height=42)

        self.fridge_btn.bind(on_press=lambda _: self.show_fridge())
        self.daily_btn.bind(on_press=lambda _: self.show_daily())

        self.nav.add_widget(self.fridge_btn)
        self.nav.add_widget(self.daily_btn)

        self.content = BoxLayout(orientation="vertical")

        self.add_widget(self.nav)
        self.add_widget(self.content)

        self.show_fridge()

    def clear_content(self):
        self.content.clear_widgets()

    def show_fridge(self):
        self.clear_content()

        self.fridge_btn.set_color(BLUE)
        self.fridge_btn.color = (1, 1, 1, 1)

        self.daily_btn.set_color(CHIP_OFF)
        self.daily_btn.color = MID

        self.content.add_widget(FridgePage())

    def show_daily(self):
        self.clear_content()

        self.daily_btn.set_color(BLUE)
        self.daily_btn.color = (1, 1, 1, 1)

        self.fridge_btn.set_color(CHIP_OFF)
        self.fridge_btn.color = MID

        self.content.add_widget(DailyTrackerPage())


class MealPrepApp(App):
    def build(self):
        init_db()
        seed_sample_data()
        return RootPage()


if __name__ == "__main__":
    MealPrepApp().run()