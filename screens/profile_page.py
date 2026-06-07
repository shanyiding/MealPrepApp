from kivy.uix.boxlayout import BoxLayout

from theme import theme
from ui.profile_ui import ProfileUI


class ProfilePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.ui = ProfileUI(
            on_goals_saved=self._on_goals_saved,
            on_dark_toggle=self._on_dark_toggle,
        )
        self.add_widget(self.ui)

    def _on_goals_saved(self, cal, protein):
        # theme.set_goals already fired on_goals_change —
        # DailyTrackerPage listens to that and updates its bars.
        pass

    def _on_dark_toggle(self, is_dark):
        # theme.set_dark already fired on_theme_change —
        # all subscribed pages repaint themselves.
        pass