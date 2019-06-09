from timedata.ui import switch_button, int_slider, box_layout


class AbsLfoFader(box_layout.BoxLayout):
    def __init__(self, label, **kwds):
        super().__init__(orientation='vertical', **kwds)
        self.slider = int_slider.IntSlider(label, 0, 127)
        self.button = switch_button.SwitchButton('abs', 'LFO')
        self.add_all(self.slider, 0.9, self.button)
