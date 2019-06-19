"""HTML Iframe to display from a URL."""
from clarusui.layout import Element
from clarusui import templates as tmp

class IFrame(Element):
    def __init__(self, response, **options):
        super(IFrame, self).__init__(response, **options)

        if response is None:
            raise ValueError("IFrame needs a content source URL")
        self.add_custom_css({'height':'90vh', 'overflow':'hidden'})

    def toDiv(self):
        return tmp.IFRAME_TEMPLATE.render(element=self)
