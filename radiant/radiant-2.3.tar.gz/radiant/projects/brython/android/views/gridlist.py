
from mdcframework.mdc import MDCTopAppBar, MDCGridList

from mdcframework.base import MDCView
from browser import html

########################################################################
class GridLists(MDCView):
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
        self.topappbar = MDCTopAppBar('GridList')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
gridlist = MDCGridList()
gridlist.mdc.grid_tile("Title", img='/')
container <= gridlist
        '''
        self.main.brython_code_sample('GridList', code, container)


        code =  '''
gridlist = MDCGridList(icon_start=True)
gridlist.mdc.grid_tile("Title", img='/', icon='favorite')
container <= gridlist
        '''
        self.main.brython_code_sample('GridList with icon', code, container)


        code =  '''
gridlist = MDCGridList(icon_end=True, caption=True)
gridlist.mdc.grid_tile("Title", caption="A subtitle...", img='/', icon='favorite')
container <= gridlist
        '''
        self.main.brython_code_sample('GridList with icon and caption', code, container)


        code =  '''
gridlist = MDCGridList(aspect_ratio='16x9')
gridlist.mdc.grid_tile("Aspect Ratio = 16x9", img='/')
container <= gridlist

gridlist = MDCGridList(aspect_ratio='1x1')
gridlist.mdc.grid_tile("Aspect Ratio = 1x1", img='/')
container <= gridlist

gridlist = MDCGridList(aspect_ratio='2x3')
gridlist.mdc.grid_tile("Aspect Ratio = 2x3", img='/')
container <= gridlist

gridlist = MDCGridList(aspect_ratio='3x2')
gridlist.mdc.grid_tile("Aspect Ratio = 3x2", img='/')
container <= gridlist

gridlist = MDCGridList(aspect_ratio='4x3')
gridlist.mdc.grid_tile("Aspect Ratio = 4x3", img='/')
container <= gridlist

gridlist = MDCGridList(aspect_ratio='3x4')
gridlist.mdc.grid_tile("Aspect Ratio = 3x4", img='/')
container <= gridlist
        '''
        self.main.brython_code_sample('GridList Aspect Ratio', code, container)


        return parent


