"""A simple alert (box with text/icon)"""
#TODO clean up to bring into line with rest of the elements
from clarusui.layout import Element
from clarusui import templates as tmp

class Alert(Element):
    def __init__(self, **options):
        super(Alert, self).__init__(None, **options)
        #self._style = options.pop('cssClass','alert-info')
        self._message = options.pop('message', '')
        self._title = options.pop('title', '')
        self._icon = options.pop('icon', '')
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



#    def _render(self):
#        return tmp.ALERT_TEMPLATE.render(alert=self, title=self._title, message=self._message, icon=self._icon, iconsize=self._iconsize, iconColour=self._iconColour)

    def toDiv(self):
        return tmp.ALERT_TEMPLATE.render(alert=self, title=self._title, message=self._message, icon=self._icon, iconsize=self._iconsize, iconColour=self._iconColour)
