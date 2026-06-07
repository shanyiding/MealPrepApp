"""
theme.py — central theme + user prefs store.

Usage:
    from theme import theme

    # read a colour
    bg = theme.BG

    # subscribe to changes (widget repaints itself)
    theme.bind(on_change=my_widget.apply_theme)

    # toggle dark mode
    theme.set_dark(True)

    # update goals
    theme.set_goals(cal=2000, protein=150)
"""

from kivy.event import EventDispatcher


# ── Light palette ─────────────────────────────────────────────────────────────
_LIGHT = dict(
    BG           = (0.94, 0.95, 0.96, 1),
    CARD         = (1.00, 1.00, 1.00, 1),
    CARD2        = (0.97, 0.98, 0.99, 1),   # subtle alt card (inputs, etc.)
    GREEN        = (0.09, 0.47, 0.32, 1),
    GREEN_LIGHT  = (0.86, 0.96, 0.91, 1),
    RED          = (0.73, 0.11, 0.11, 1),
    RED_LIGHT    = (0.99, 0.89, 0.89, 1),
    RED_BTN      = (0.69, 0.13, 0.13, 1),
    AMBER        = (0.85, 0.47, 0.04, 1),
    AMBER_LIGHT  = (0.99, 0.95, 0.85, 1),
    BLUE         = (0.15, 0.39, 0.66, 1),
    BLUE_DARK    = (0.10, 0.28, 0.50, 1),
    BLUE_LIGHT   = (0.85, 0.93, 0.99, 1),
    DARK         = (0.12, 0.16, 0.22, 1),
    MID          = (0.35, 0.40, 0.47, 1),
    MUTED        = (0.52, 0.57, 0.64, 1),
    BORDER       = (0.83, 0.85, 0.88, 1),
    INPUT_BG     = (0.97, 0.98, 0.99, 1),
    INPUT_BORDER = (0.74, 0.79, 0.86, 1),
    CHIP_OFF     = (0.88, 0.90, 0.93, 1),
    CHIP_OFF_TXT = (0.42, 0.47, 0.54, 1),
    TAB_OFF      = (0.91, 0.92, 0.94, 1),
    TAB_OFF_TXT  = (0.42, 0.47, 0.54, 1),
    TOGGLE_TRACK = (0.83, 0.85, 0.88, 1),
    TOGGLE_THUMB = (1.00, 1.00, 1.00, 1),
    SHADOW       = (0.70, 0.72, 0.76, 0.30),
)

# ── Dark palette ──────────────────────────────────────────────────────────────
_DARK = dict(
    BG           = (0.10, 0.11, 0.14, 1),
    CARD         = (0.16, 0.18, 0.22, 1),
    CARD2        = (0.13, 0.15, 0.18, 1),
    GREEN        = (0.20, 0.72, 0.52, 1),
    GREEN_LIGHT  = (0.08, 0.26, 0.18, 1),
    RED          = (0.90, 0.35, 0.35, 1),
    RED_LIGHT    = (0.30, 0.10, 0.10, 1),
    RED_BTN      = (0.75, 0.18, 0.18, 1),
    AMBER        = (0.95, 0.65, 0.15, 1),
    AMBER_LIGHT  = (0.28, 0.20, 0.06, 1),
    BLUE         = (0.30, 0.58, 0.90, 1),
    BLUE_DARK    = (0.20, 0.42, 0.70, 1),
    BLUE_LIGHT   = (0.10, 0.20, 0.35, 1),
    DARK         = (0.92, 0.93, 0.95, 1),   # flipped: text is light
    MID          = (0.65, 0.68, 0.72, 1),
    MUTED        = (0.42, 0.45, 0.50, 1),
    BORDER       = (0.24, 0.27, 0.32, 1),
    INPUT_BG     = (0.13, 0.15, 0.19, 1),
    INPUT_BORDER = (0.30, 0.34, 0.42, 1),
    CHIP_OFF     = (0.22, 0.25, 0.30, 1),
    CHIP_OFF_TXT = (0.55, 0.58, 0.64, 1),
    TAB_OFF      = (0.20, 0.22, 0.27, 1),
    TAB_OFF_TXT  = (0.55, 0.58, 0.64, 1),
    TOGGLE_TRACK = (0.22, 0.25, 0.30, 1),
    TOGGLE_THUMB = (0.92, 0.93, 0.95, 1),
    SHADOW       = (0.00, 0.00, 0.00, 0.40),
)


class ThemeManager(EventDispatcher):
    """Singleton. Holds all live colour values + user goals."""

    def __init__(self):
        self.register_event_type("on_theme_change")
        self.register_event_type("on_goals_change")
        super().__init__()

        self._dark = False
        self._apply_palette(_LIGHT)

        # user goals (can be updated from Profile page)
        self.cal_goal     = 1700
        self.protein_goal = 130

    # ── palette ───────────────────────────────────────────────────────────────

    def _apply_palette(self, p):
        for k, v in p.items():
            setattr(self, k, v)

    @property
    def dark(self):
        return self._dark

    def set_dark(self, value: bool):
        if value == self._dark:
            return
        self._dark = value
        self._apply_palette(_DARK if value else _LIGHT)
        self.dispatch("on_theme_change", self)

    def toggle_dark(self):
        self.set_dark(not self._dark)

    # ── goals ─────────────────────────────────────────────────────────────────

    def set_goals(self, cal: int, protein: int):
        self.cal_goal     = max(1, cal)
        self.protein_goal = max(1, protein)
        self.dispatch("on_goals_change", self)

    # ── required EventDispatcher stubs ────────────────────────────────────────

    def on_theme_change(self, *_):
        pass

    def on_goals_change(self, *_):
        pass


# singleton
theme = ThemeManager()