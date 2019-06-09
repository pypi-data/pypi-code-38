from kivy.uix import togglebutton


class SwitchButton(togglebutton.ToggleButton):
    def __init__(self, off, on='', **kwds):
        super().__init__(text=off, **kwds)
        self.texts = off, on

    def on_state(self, _, value):
        self.text = self.texts[value == 'down']
