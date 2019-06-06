import clarusui as ui
from clarusui.layout import Element
from jinja2 import Environment, FileSystemLoader, select_autoescape
import clarusui.colours
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml']))

cardTemplate = env.get_template('card2.html')

#deprecated, use DetailCard
class Card2(Element):
    def __init__(self, **options):
        super(Card2, self).__init__(None, **options)
        self._icon = options.pop('icon', None)
        self._iconColour = options.pop('iconColour', None) 
        self._body = options.pop('body', '')
        
    @property
    def icon(self):
        return self._icon
    
    @property
    def iconColour(self):
        return self._iconColour
    
    @property
    def body(self):
        return self._body

    def toDiv(self):
        return cardTemplate.render(card=self)