from mdcframework.mdc import MDCTopAppBar, MDCCard

from mdcframework.base import MDCView
from browser import html

########################################################################
class Cards(MDCView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        #self.toolbar.mdc['icon'].bind('click', lambda ev:self.main.drawer.mdc.open())


    #----------------------------------------------------------------------
    def build(self):
        """"""
        parent = html.DIV()
        self.topappbar = MDCTopAppBar('Cards')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container


        code = '''
card = html.DIV('This is simple card.', Class="mdc-card", style={'padding': '1em',})
container <= card
        '''
        self.main.brython_code_sample('Simple card', code, container)

        code =  '''
card = MDCCard(title='Card', subtitle='Hola mundo', content='Brython is awesome!', _16_9=True)

card.mdc.add_action_button('Action 1')
card.mdc.add_action_button('Action X', icon='start')
card.mdc.add_action_icontoggle('favorite', 'favorite_border')

container <= card
        '''
        self.main.brython_code_sample('16:9 Card', code, container)


        code =  '''
card = MDCCard(title='Card', subtitle='Hola mundo', content='Brython is awesome!', _16_9=True, outlined=True)
card.mdc.add_action_button('Action 1')
container <= card
        '''
        self.main.brython_code_sample('Outlined Card', code, container)


        code =  '''
card = MDCCard(title='Card', subtitle='Hola mundo', content='Brython is awesome!', _16_9=True, full_bleed=True)
card.mdc.add_action_button('Action 1', icon='arrow_forward', reversed=True)
container <= card
        '''
        self.main.brython_code_sample('Full bleed Card', code, container)


        code =  '''
card = MDCCard(title='Card', subtitle='Hola mundo', content='Brython is awesome!', square=True)
card.mdc.add_action_icon('more_vert')
container <= card
        '''
        self.main.brython_code_sample('Squared Card', code, container)






        return parent


