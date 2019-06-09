from mdcframework.mdc import MDCTopAppBar, MDCMenu, MDCButton

from mdcframework.base import MDCView
from browser import html

########################################################################
class Menus(MDCView):
    """"""

    NAME = 'menu', 'MDCMenu'

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        #self.toolbar.mdc['icon'].bind('click', lambda ev:self.main.drawer.mdc.open())


    #----------------------------------------------------------------------
    def build(self):
        """"""
        parent = html.DIV()
        self.topappbar = MDCTopAppBar('Menus')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
parent = html.DIV(Class='mdc-menu-anchor')

menu = MDCMenu()
menu.mdc.add_item('menu item')
menu.mdc.add_item('menu item', disable=True)
menu.mdc.add_item('menu item')
menu.mdc.add_divider()
menu.mdc.add_item('menu item')
menu.mdc.add_item('menu item')

button = MDCButton('Open Menu')
button.bind('click', lambda evt:menu.mdc.toggle(corner='BOTTOM_LEFT'))
# options are 'BOTTOM_START', 'BOTTOM_LEFT', 'BOTTOM_RIGHT', 'BOTTOM_END', 'TOP_START', 'TOP_LEFT', 'TOP_RIGHT', 'TOP_END'.

parent <= button
parent <= menu

container <= parent
        '''
        self.main.brython_code_sample('Menu', code, container)


        return parent


