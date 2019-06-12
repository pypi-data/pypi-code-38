from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from clarusui.layout import Element
from clarusui.layout import Dashboard

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

layout_template = env.get_template('tabs.html')

class Tabs(Element):
    def __init__(self, *childElements, **options):
        super(Tabs, self).__init__(None,**options)
        self._set_child_elements(childElements)
        style = options.pop('style', self._get_auto_style())
        if style is not None:
            self._set_style(style)
            
    def _set_style(self, style):
        self._fontColour = style.fontColour
        self._borderColour = style.borderColour
        self.set_bgcolour(style.backgroundColour)
        self.add_custom_css({'border-bottom-color':style.borderColour})
        for elements in self.childElements:
            elements._set_style(style)
                

    def _set_child_elements(self, childElements):
        self.childElements = []
        for element in childElements:
            self.childElements.append(element)
        
    def toDiv(self):
        return layout_template.render(tabs=self)