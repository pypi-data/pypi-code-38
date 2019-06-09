from mdcframework.mdc import MDCTopAppBar, MDCTabBar, MDCTabScroller

from mdcframework.base import MDCView
from browser import html

########################################################################
class Tabs(MDCView):
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
        self.topappbar = MDCTopAppBar('Tabs')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
tabbar = MDCTabBar({'text': 'Text', 'id': 'one_', 'active': True},
                   {'text': 'only', 'id': 'two_'},
                   {'text': 'tabs', 'id': 'three_'},
                   )

tabbar.panel['one_'].html = 'This html element is a DIV element'
tabbar.panel['two_'].html = 'Can be accessed with the same id'
tabbar.panel['three_'].html = 'The panels must be added manually from tabbar.panels element'

container <= tabbar
container <= tabbar.panels
        '''
        self.main.brython_code_sample('Text only tabs', code, container)


        code =  '''
tabbar2 = MDCTabBar({'icon': 'favorite', 'id': 'one', 'active':True},
                   {'icon': 'phone', 'id': 'two'},
                   {'icon': 'person_pin', 'id': 'three'},
                   )

container <= tabbar2
        '''
        self.main.brython_code_sample('Icon only tabs', code, container)



        code =  '''
tabbar = MDCTabBar({'text': 'Favorite', 'icon': 'favorite', 'id': 'one', 'active':True},
                   {'text': 'Phone', 'icon': 'phone', 'id': 'two'},
                   {'text': 'Person_pin', 'icon': 'person_pin', 'id': 'three'},
                   )

container <= tabbar
        '''
        self.main.brython_code_sample('Text and icon tabs', code, container)




        code =  '''
tabbar = MDCTabScroller({'text': 'This', 'active':True, 'id':'a'},
                   {'text': 'is', 'id':'b'},
                   {'text': 'a', 'id':'c'},
                   {'text': 'long', 'id':'d'},
                   {'text': 'long', 'id':'e'},
                   {'text': 'tab', 'id':'f'},
                   {'text': 'list', 'id':'g'},
                   )

container <= tabbar
        '''
        self.main.brython_code_sample('Tabs Scroller', code, container)



        return parent


