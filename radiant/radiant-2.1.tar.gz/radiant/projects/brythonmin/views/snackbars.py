from mdcframework.mdc import MDCTopAppBar, MDCSnackbar, MDCButton

from mdcframework.base import MDCView
from browser import html

########################################################################
class Snackbars(MDCView):
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
        self.topappbar = MDCTopAppBar('Snackbars')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container


        code =  '''
snackbar = ()
container <= snackbar

button = MDCButton('Show')
button.bind('click', lambda ev:snackbar.mdc.show('Hola'))
container <= button
        '''
        self.main.brython_code_sample('Snackbar', code, container)


        code =  '''
snackbar = MDCSnackbar()

container <= snackbar

button = MDCButton('Show')
button.bind('click', lambda ev:snackbar.mdc.show('Hola', action_text='action', action_handler=lambda :print('Check log')))
container <= button
        '''
        self.main.brython_code_sample('Snackbar with action', code, container)


        code =  '''
snackbar = MDCSnackbar()
container <= snackbar

button = MDCButton('Show')
button.bind('click', lambda ev:snackbar.mdc.show('Hola', action_text='action', timeout=500, action_handler=lambda :print('Check log')))
container <= button
        '''
        self.main.brython_code_sample('Snackbar with action', code, container)


        code =  '''
snackbar = MDCSnackbar()
container <= snackbar

button = MDCButton('Show')
button.bind('click', lambda ev:snackbar.mdc.show('Hola, this is a message really really  really  really  really  really  really long.', action_text='action', multiline=True, action_handler=lambda :print('Check log')))
container <= button
        '''
        self.main.brython_code_sample('Snackbar with long text', code, container)



        return parent


