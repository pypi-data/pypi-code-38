from clarusui.layout import Dashboard
from clarusui.card2 import Card2

class ErrorPanel(Dashboard):
    def __init__(self, **options):
        icon = options.pop('icon', 'fa-exclamation-circle')
        iconColour = options.pop('iconColour', None) 
        body = options.pop('body', '')
        header = options.get('header', 'Oops!')
        card = self._get_error_card(icon, iconColour, header, body)
        super(self.__class__, self).__init__(card, displayHeader=False, **options)
        
    def _get_error_card(self, icon, iconColour, header, body):
        card = Card2(icon=icon, iconColour=iconColour, 
                     header=header, body=body, bgcolour='#d9534f')
        card.add_custom_css({'color':'white'})
        return card