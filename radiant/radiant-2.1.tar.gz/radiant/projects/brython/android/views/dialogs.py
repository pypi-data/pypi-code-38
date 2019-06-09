from mdcframework.mdc import MDCTopAppBar, MDCDialog, MDCButton

from mdcframework.base import MDCView
from browser import html

########################################################################
class Dialogs(MDCView):
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
        self.topappbar = MDCTopAppBar('Dialogs')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
button = MDCButton('Show Dialog', raised=False, ripple=True)
container <= button

dialog1 = MDCDialog('Dialog', 'the content is here')
dialog1.mdc.add_footer_button('Accept', accept=True)
dialog1.mdc.add_footer_button('Decline', cancel=True)
dialog1.mdc.add_footer_button('Custom action', icon='favorite', action=True)
container <= dialog1

button.bind('click', lambda evt:dialog1.mdc.show())
        '''
        self.main.brython_code_sample('Dialog', code, container)

        code =  '''
button = MDCButton('Show Scrolable Dialog ', raised=False, ripple=True)
container <= button

list = html.UL(Class='mdc-list')
for label in ['None', 'Callisto', 'Ganymede', 'Luna', 'Marimba', 'Schwifty', 'Callisto', 'Ganymede', 'Luna', 'Marimba', 'Schwifty']:
    list <= html.LI(label, Class='mdc-list-item')

dialog2 = MDCDialog('Dialog', list.html, scrollable=True)
dialog2.mdc.add_footer_button('Accept', accept=True)
dialog2.mdc.add_footer_button('Decline', cancel=True)
container <= dialog2

button.bind('click', lambda evt:dialog2.mdc.show())
        '''
        self.main.brython_code_sample('Scrollable Dialog', code, container)



        return parent


