from kivy.uix.button import Button
from timedata.ui import box_layout, switch_button


class LooseButtons(box_layout.BoxLayout):
    def __init__(self, **kwds):
        super().__init__(orientation='vertical', **kwds)
        self.blackout = Button(text='BLACKOUT')
        self.left_right = switch_button.SwitchButton('Left', 'Right')
        self.down_up = switch_button.SwitchButton('Down', 'Up')

        self.add_all(
            self.blackout, 1 / 3, self.left_right, 1 / 3, self.down_up
        )
