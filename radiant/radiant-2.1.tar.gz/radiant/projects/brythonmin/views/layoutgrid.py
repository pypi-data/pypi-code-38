from mdcframework.mdc import MDCTopAppBar, MDCLayoutGrid

from mdcframework.base import MDCView
from browser import html

########################################################################
class LayoutGrid(MDCView):
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
        self.topappbar = MDCTopAppBar('Layout Grid')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container


        code =  '''
layoutgrid = MDCLayoutGrid()

grid = layoutgrid.mdc.grid()

cell = grid.mdc.cell(C=1)
cell.style = {'background-color': 'red', 'height': '50px',}

cell = grid.mdc.cell(C=2)
cell.style = {'background-color': 'blue', 'height': '50px',}

cell = grid.mdc.cell(C=1)
cell.style = {'background-color': 'green', 'height': '50px',}

container <= layoutgrid
        '''
        self.main.brython_code_sample('Layout Grid', code, container)


        code =  '''
layoutgrid = MDCLayoutGrid()

grid = layoutgrid.mdc.grid(position='right')

cell = grid.mdc.cell(C=1)
cell.style = {'background-color': 'red', 'height': '50px',}

cell = grid.mdc.cell(C=1)
cell.style = {'background-color': 'blue', 'height': '50px',}

cell = grid.mdc.cell(C=1)
cell.style = {'background-color': 'green', 'height': '50px',}

container <= layoutgrid
        '''
        self.main.brython_code_sample('Layout Grid Right', code, container)



        code =  '''
layoutgrid = MDCLayoutGrid()

grid = layoutgrid.mdc.grid()

cell = grid.mdc.cell(C=1, position='top')
cell.style = {'background-color': 'red', 'height': '50px',}

cell = grid.mdc.cell(C=2, position='middle')
cell.style = {'background-color': 'blue', 'height': '140px',}

cell = grid.mdc.cell(C=1, position='bottom')
cell.style = {'background-color': 'green', 'height': '100px',}

container <= layoutgrid
        '''
        self.main.brython_code_sample('Layout Grid (Top - Middle - Bottom)', code, container)


        code =  '''
layoutgrid = MDCLayoutGrid()

grid = layoutgrid.mdc.grid()

cell = grid.mdc.cell(C=1, desktop=4, tablet=3, mobile=1)
cell.style = {'background-color': 'red', 'height': '50px',}

cell = grid.mdc.cell(C=2, desktop=4, tablet=3, mobile=2)
cell.style = {'background-color': 'blue', 'height': '50px',}

cell = grid.mdc.cell(C=1, desktop=4, tablet=3, mobile=1)
cell.style = {'background-color': 'green', 'height': '50px',}

container <= layoutgrid
        '''
        self.main.brython_code_sample('Layout Grid For Devices', code, container)




        return parent


