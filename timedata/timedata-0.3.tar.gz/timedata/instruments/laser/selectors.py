from timedata.ui import selector, box_layout
from . import constants


class ColorSelector(selector.Selector):
    def __init__(self, **kwds):
        super().__init__(constants.Colors, **kwds)

    def on_enum(self, _, e):
        color_name = 'white' if e is constants.Colors.ALL else e.name.lower()
        self.background_normal = self.background_selected = color_name
        self.background_down = color_name


class Selectors(box_layout.BoxLayout):
    def __init__(self, orientation='vertical', **kwds):
        super().__init__(**kwds)
        self.colors = ColorSelector()
        self.patterns = selector.Selector(constants.Patterns)

        self.add_all(self.colors, 0.5, self.patterns, other=0.20)
