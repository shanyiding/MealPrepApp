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

        self.fridge_btn  = RoundedButton("My Fridge",      bg_color=BLUE,     height=42)
        self.daily_btn   = RoundedButton("Daily Tracker",  bg_color=CHIP_OFF, text_color=MID, height=42)
        self.profile_btn = RoundedButton("Profile",        bg_color=CHIP_OFF, text_color=MID, height=42)

        self.fridge_btn.bind (on_press=lambda _: self.show_fridge())
        self.daily_btn.bind  (on_press=lambda _: self.show_daily())
        self.profile_btn.bind(on_press=lambda _: self.show_profile())

        self.nav.add_widget(self.fridge_btn)
        self.nav.add_widget(self.daily_btn)
        self.nav.add_widget(self.profile_btn)

        self.content = BoxLayout(orientation="vertical")

        self.add_widget(self.nav)
        self.add_widget(self.content)

        self.show_fridge()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _set_active(self, active_btn):
        """Highlight active_btn blue, reset all others to grey."""
        for btn in (self.fridge_btn, self.daily_btn, self.profile_btn):
            if btn is active_btn:
                btn.set_color(BLUE)
                btn.color = (1, 1, 1, 1)
            else:
                btn.set_color(CHIP_OFF)
                btn.color = MID

    # ── pages ─────────────────────────────────────────────────────────────────

    def show_fridge(self):
        self.content.clear_widgets()
        self._set_active(self.fridge_btn)
        self.content.add_widget(FridgePage())

    def show_daily(self):
        self.content.clear_widgets()
        self._set_active(self.daily_btn)
        self.content.add_widget(DailyTrackerPage())

    def show_profile(self):
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