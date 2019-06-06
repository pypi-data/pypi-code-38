import clarusui as ui
from clarusui.layout import Element
from jinja2 import Environment, FileSystemLoader, select_autoescape
import clarusui.colours
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml']))

cardTemplate = env.get_template('card.html')

#deprecated, use DetailCard
class Card(Element):
    def __init__(self, **options):
        super(self.__class__, self).__init__(None, **options)
        self._icon = options.pop('icon', None)
        # self._textalign = options.pop('textalign', 'center')
        self._title = options.pop('title', '')
        self._subtitle = options.pop('subtitle', '')
        self._body = options.pop('body', '')
        self._body2 = options.pop('body2', '')
        self._text_color = options.pop('textcolor', None)
        self._card_style = options.pop('cssClass', '')
        self._icon_size = options.pop('iconsize', None)
        self._icon_color = options.pop('iconcolor', None)
        self._width = options.pop('width', None)
        card_radius = options.pop('card_radius', '0')
        self.add_custom_css({'border-radius':card_radius})
        self._header_radius = options.pop('header_radius', None)
        self._fontsize = options.pop('fontsize', None)
        self._header_bgcolor = options.pop('header_bgcolor', None)
        self._header = options.pop('header', None)


    def _render(self):
        return cardTemplate.render(card=self, icon=self._icon, title=self._title,
                                   subtitle=self._subtitle, body=self._body, body2=self._body2,
                                   style=self._card_style, iconsize=self._icon_size, width=self._width,
                                   iconcolor=self._icon_color, textcolor=self._text_color,
                                   fontsize=self._fontsize, header_bgcolor=self._header_bgcolor,
                                   header=self._header, header_radius=self._header_radius)

    def toDiv(self):
        return self._render()
