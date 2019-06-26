class ProcessingTools:
    def __init__(self):
        self._fill_color = None

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, value):
        self._fill_color = value
