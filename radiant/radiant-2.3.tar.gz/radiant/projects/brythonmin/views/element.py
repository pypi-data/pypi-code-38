from mdcframework.mdc import MDCTopAppBar

from mdcframework.base import MDCView
from browser import html

########################################################################
class LinearProgress(MDCView):
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
        self.topappbar = MDCTopAppBar('Buttons')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        #code =  '''
#button = MDCButton('Button', raised=False, ripple=True)
#container <= button
        #'''
        #self.main.brython_code_sample('Button', code, container)


        return parent


