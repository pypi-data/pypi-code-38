from clarusui.layout import Dashboard
from clarusui.detailcard import DetailCard

class MessagePanel(Dashboard):
    def __init__(self, **options):
        bgcolour = options.pop('bgcolour') #set this only for the card and stop cascading into the main dash background
        card = self._get_card(bgcolour=bgcolour, **options)
        super(MessagePanel, self).__init__(card, displayHeader=False, **options)
        
    def _get_card(self, **options):
        card = DetailCard(**options)
        return card
    

class ErrorPanel(MessagePanel):
    def __init__(self, **options):
        super(ErrorPanel, self).__init__(bgcolour='#d9534f', icon='fa-exclamation-circle', **options)
        
class InfoPanel(MessagePanel):
    def __init__(self, **options):
        super(InfoPanel, self).__init__(bgcolour='#2196F3', icon='fa-info-circle', **options)