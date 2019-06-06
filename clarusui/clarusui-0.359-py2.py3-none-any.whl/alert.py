import clarusui as ui
from clarusui.layout import Element
from jinja2 import Environment, FileSystemLoader, select_autoescape
import clarusui.colours
import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml']))

alertTemplate = env.get_template('alert.html')


class Alert(Element):
    def __init__(self, **options):
        super(self.__class__, self).__init__(None, **options)
        self._style = options.pop('cssClass','alert-info')
        self._message = options.pop('message', '')
        self._title = options.pop('title','')
        self._icon = options.pop('icon','')
        self._iconsize = options.pop('iconsize', 'lg')
        self._iconColour = options.pop('iconColour', 'white')
        #border_color = options.pop('border_color', '')
        #self.add_custom_css({'border-color':border_color})
        borderwidth = options.pop('borderwidth', '1')
        self.add_custom_css({'border-width':borderwidth})
        self.add_custom_css({'font-size':'1em'})
        self.add_custom_css({'width':'100%'})
        self.add_custom_css({'text-align':'right'})
        self.add_custom_css({'padding-left':'15px'})
        self.add_custom_css({'display':'inline-flex'})



    def _render(self):
        return alertTemplate.render(alert=self, title=self._title, style=self._style, message=self._message, icon=self._icon, iconsize=self._iconsize, iconColour=self._iconColour)

    def toDiv(self):
        return self._render()
