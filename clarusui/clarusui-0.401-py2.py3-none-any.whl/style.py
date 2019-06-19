"""Contains top level style parameters for Dashboards."""
from six import string_types
from clarusui import utils

class Style(object):
    def __init__(self, **options):
        self._colours = None
        self.colours = options.pop('colours', None)
        self._bg_colour = options.pop('backgroundColour')
        self._fg_colour = options.pop('foregroundColour')
        self._font_colour = options.pop('fontColour')
        self._font_family = options.pop('fontFamily', 'Roboto,sans-serif')
        self._border_colour = options.pop('borderColour')
        self._chart_theme = options.pop('chartTheme', None)
        self._table_css_class = options.pop('tableCssClass', '')

    @property
    def background_colour(self):
        return self._bg_colour

    @property
    def foreground_colour(self):
        return self._fg_colour

    @property
    def font_colour(self):
        return self._font_colour

    @property
    def border_colour(self):
        return self._border_colour

    @property
    def font_family(self):
        return self._font_family

    @property
    def chart_theme(self):
        return self._chart_theme

    @property
    def table_css_class(self):
        return self._table_css_class

    @property
    def colours(self):
        return self._colours

    @colours.setter
    def colours(self, colours):
        if isinstance(colours, string_types):
            decoded = utils.get_colour_set(colours)
            if decoded is None:
                raise ValueError('Specify a list of colours or one of: '+ str(list(utils.COLOURS)))
            self._colours = decoded
        if isinstance(colours, list):
            self._colours = colours

class DarkStyle(Style):
    def __init__(self, backgroundColour='#000000', foregroundColour='#111111',
                 fontColour='white', borderColour='#3E3E3E',
                 tableCssClass='table-inverse', **options):
        super(DarkStyle, self).__init__(backgroundColour=backgroundColour,
                                        foregroundColour=foregroundColour,
                                        fontColour=fontColour, borderColour=borderColour,
                                        tableCssClass=tableCssClass, **options)

class DarkBlueStyle(Style):
    def __init__(self, backgroundColour='#252830', foregroundColour='#111111',
                 fontColour='white', borderColour='#434857',
                 tableCssClass='table-inverse', **options):
        super(DarkBlueStyle, self).__init__(backgroundColour=backgroundColour,
                                            foregroundColour=foregroundColour,
                                            fontColour=fontColour, borderColour=borderColour,
                                            tableCssClass=tableCssClass, **options)

class LightStyle(Style):
    def __init__(self, backgroundColour='white', foregroundColour='white',
                 fontColour='black', borderColour='#e9ecef', **options):
        super(LightStyle, self).__init__(backgroundColour=backgroundColour,
                                         foregroundColour=foregroundColour,
                                         fontColour=fontColour, borderColour=borderColour,
                                         **options)

def get_auto_style(event, colours):
    if event is None or event.get('__theme') != 'default':
        return DarkStyle(colours=colours)
    return LightStyle(colours=colours)
