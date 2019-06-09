from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from timedata.ui.switch_button import SwitchButton
from .dmx_levels import DMXLevels
from kiva.properties import StringProperty


class OneLaser(BoxLayout):
    StringProperty()
    OFF, ON = 'X', 'O'

    def __init__(self, **kwds):
        super().__init__(orientation='vertical', **kwds)
        self.enable = SwitchButton(self.OFF, self.ON)
        top_left = AnchorLayout(anchor_y='top', anchor_x='left')
        top_left.add_widget(self.enable)
        self.add_widget(top_left)

        label = Label()  # text=text
        top_right = AnchorLayout(anchor_y='top', anchor_x='right')
        top_right.add_widget(label)
        self.add_widget(top_right)

        self.levels = DMXLevels()
        bottom_center = AnchorLayout(anchor_y='bottom')
        bottom_center.add_widget(self.levels)
        self.add_widget(bottom_center)


LASER_DATA = """
<OneLaser>
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: .1
        Switch:
        Label:
            text: 'Your Big Label'
        Label:
            text: ''
    Button:
        text: 'The rest goes here'

OneLaser:

"""


def OneLaser2(*args):
    return Builder.load_string(LASER_DATA)


OneLaser = OneLaser if False else OneLaser2
