"""Simple Dashboard wrapping a single DetailCard.
Useful to display full screen message etc.

"""
from clarusui.layout import Dashboard
from clarusui.card import DetailCard

class MessagePanel(Dashboard):
    def __init__(self, **options):
        #set this only for the card and stop cascading into the main dash background
        bgcolour = options.pop('bgcolour')
        card = DetailCard(bgcolour=bgcolour, **options)
        super(MessagePanel, self).__init__(card, displayHeader=False, **options)

class ErrorPanel(MessagePanel):
    def __init__(self, **options):
        super(ErrorPanel, self).__init__(bgcolour='#d9534f',
                                         icon='fa-exclamation-circle', **options)

class InfoPanel(MessagePanel):
    def __init__(self, **options):
        super(InfoPanel, self).__init__(bgcolour='#2196F3',
                                        icon='fa-info-circle', **options)
