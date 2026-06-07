from kivy.config import Config

Config.set("graphics", "width", "390")
Config.set("graphics", "height", "844")
Config.set("graphics", "resizable", "0")

from kivy.app import App

from database import init_db, seed_sample_data
from screens.fridge_page import FridgePage


class MealPrepApp(App):
    def build(self):
        init_db()
        seed_sample_data()
        return FridgePage()


if __name__ == "__main__":
    MealPrepApp().run()