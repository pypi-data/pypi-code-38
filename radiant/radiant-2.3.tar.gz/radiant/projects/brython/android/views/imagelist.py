from mdcframework.mdc import MDCTopAppBar, MDCImageList

from mdcframework.base import MDCView
from browser import html

########################################################################
class ImageList(MDCView):
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
        self.topappbar = MDCTopAppBar('ImageList')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
button = MDCImageList()
container <= button
        '''
        self.main.brython_code_sample('Button', code, container)


        return parent


