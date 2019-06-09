from mdcframework.mdc import MDCButton, MDCFab, MDCIconToggle, MDCTopAppBar, MDCDrawer

from mdcframework.base import MDCView
from browser import html

from radiant import AndroidMain
androidmain = AndroidMain()

########################################################################
class Buttons(MDCView):
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

        self.main.rest = []
        rest_ignore = 'from mdcframework.mdc import MDCButton'


        code =  '''
button = MDCButton('Button', raised=False)
container <= button
        '''
        self.main.brython_code_sample('Button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton('Raised Button', raised=True)
container <= button
        '''
        self.main.brython_code_sample('Raised button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton('Disabled button', raised=True, disabled=True)
container <= button
        '''
        self.main.brython_code_sample('Disabled button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton('Favorite', icon='favorite', raised=True)
container <= button
        '''
        self.main.brython_code_sample('Icon button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton('Favorite', icon='favorite', raised=True, reversed=True)
container <= button
        '''
        self.main.brython_code_sample('Icon button reversed', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton('Outlined Button', raised=False, outlined=True)
container <= button
        '''
        self.main.brython_code_sample('Outlined button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton('Unelevated Button', raised=False, unelevated=True)
container <= button
        '''
        self.main.brython_code_sample('Unelevated button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCButton(icon='favorite', raised=False)
container <= button
        '''
        self.main.brython_code_sample('Icon button ', code, container, rest_ignore=rest_ignore)


        androidmain.save_rest('MDCButton.rst', self.main.rest)
        self.main.rest = []
        rest_ignore = 'from mdcframework.mdc import MDCFab'


        code =  '''
button = MDCFab('favorite')
container <= button
        '''
        self.main.brython_code_sample('Floating action button', code, container, rest_ignore=rest_ignore)


        code =  '''
button = MDCFab('favorite', mini=True)
container <= button
        '''
        self.main.brython_code_sample('Floating action button mini', code, container, rest_ignore=rest_ignore)


        androidmain.save_rest('MDCFab.rst', self.main.rest)
        self.main.rest = []
        rest_ignore = 'from mdcframework.mdc import MDCIconToggle'


        code =  '''
button = MDCIconToggle('favorite', 'favorite_border')
container <= button

button = MDCIconToggle('star', 'star_border')
button.mdc.theme('primary')
container <= button

button = MDCIconToggle('bookmark', 'bookmark_border')
button.mdc.theme('secondary')
container <= button
        '''
        self.main.brython_code_sample('Icon toggle buttons ', code, container, rest_ignore=rest_ignore)


        androidmain.save_rest('MDCIconToggle.rst', self.main.rest)
        return parent


