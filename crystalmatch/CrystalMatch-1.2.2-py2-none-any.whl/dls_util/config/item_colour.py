from CrystalMatch.dls_util.config.item import ConfigItem
from CrystalMatch.dls_util.imaging.color import Color


class ColorConfigItem(ConfigItem):
    # TODO: remove dependency on GUI layer (pyQT)
    """ Config item that stores a color. """
    DATA_TYPE = Color

    """ Config item that stores a color. """
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)
        self._acceptable_values = "Comma-separated RGBA values, e.g. '255,128,50,255'"

    def from_file_string(self, string):
        self._value = Color.from_string(string)