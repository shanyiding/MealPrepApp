from kivy.config import Config

Config.set("graphics", "width", "390")
Config.set("graphics", "height", "844")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from database import init_db, seed_sample_data
from screens.fridge_page import FridgePage
from screens.daily_tracker_page import DailyTrackerPage
from screens.profile_page import ProfilePage
from screens.scan_page import ScanPage
from ui.fridge_ui import RoundedButton
from theme import theme


class RootPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.current_page = "fridge"

        self.nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=52,
            spacing=5,
            padding=[10, 10, 10, 0],
        )

        self.fridge_btn = RoundedButton("Fridge", bg_color=theme.BLUE, height=42, font_size=12)
        self.daily_btn = RoundedButton("Daily", bg_color=theme.CHIP_OFF, text_color=theme.MID, height=42, font_size=12)
        self.scan_btn = RoundedButton("Scan", bg_color=theme.CHIP_OFF, text_color=theme.MID, height=42, font_size=12)
        self.profile_btn = RoundedButton("Profile", bg_color=theme.CHIP_OFF, text_color=theme.MID, height=42, font_size=12)

        self.fridge_btn.bind(on_press=lambda _: self.show_fridge())
        self.daily_btn.bind(on_press=lambda _: self.show_daily())
        self.scan_btn.bind(on_press=lambda _: self.show_scan())
        self.profile_btn.bind(on_press=lambda _: self.show_profile())

        self.nav.add_widget(self.fridge_btn)
        self.nav.add_widget(self.daily_btn)
        self.nav.add_widget(self.scan_btn)
        self.nav.add_widget(self.profile_btn)

        self.content = BoxLayout(orientation="vertical")

        self.add_widget(self.nav)
        self.add_widget(self.content)

        theme.bind(on_theme_change=self._on_theme_change)

        self.show_fridge()

    def _set_active(self, active_btn):
        for btn in (self.fridge_btn, self.daily_btn, self.scan_btn, self.profile_btn):
            if btn is active_btn:
                btn.set_color(theme.BLUE)
                btn.color = (1, 1, 1, 1)
            else:
                btn.set_color(theme.CHIP_OFF)
                btn.color = theme.MID

    def _on_theme_change(self, *_):
        if self.current_page == "fridge":
            self.show_fridge()
        elif self.current_page == "daily":
            self.show_daily()
        elif self.current_page == "scan":
            self.show_scan()
        else:
            self.show_profile()

    def show_fridge(self):
        self.current_page = "fridge"
        self.content.clear_widgets()
        self._set_active(self.fridge_btn)
        self.content.add_widget(FridgePage())

    def show_daily(self):
        self.current_page = "daily"
        self.content.clear_widgets()
        self._set_active(self.daily_btn)
        self.content.add_widget(DailyTrackerPage())

    def show_scan(self):
        self.current_page = "scan"
        self.content.clear_widgets()
        self._set_active(self.scan_btn)
        self.content.add_widget(ScanPage())

    def show_profile(self):
        self.current_page = "profile"
        self.content.clear_widgets()
        self._set_active(self.profile_btn)
        self.content.add_widget(ProfilePage())


class MealPrepApp(App):
    def build(self):
        init_db()
        seed_sample_data()
        return RootPage()


if __name__ == "__main__":
    MealPrepApp().run()