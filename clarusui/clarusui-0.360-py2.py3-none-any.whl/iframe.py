from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from clarusui.layout import Element

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

iframeTemplate = env.get_template('iframe.html')

class IFrame(Element):
    def __init__(self, response, **options):
        super(self.__class__, self).__init__(response,**options)
        
        if response is None:
            raise ValueError("IFrame needs a content source URL")
        self.add_custom_css({'height': '90vh','overflow':'hidden'})
    
    def toDiv(self):
        return iframeTemplate.render(element=self)
    