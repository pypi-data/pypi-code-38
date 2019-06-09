from mdcframework.mdc import MDCTopAppBar, MDCShape, MDCButton

from mdcframework.base import MDCView
from browser import html

########################################################################
class Shapes(MDCView):
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
        self.topappbar = MDCTopAppBar('Shapes')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
button = MDCButton('HOLA', raised=True, unelevated=True)
container <= button
container <= html.DIV(style={'margin': '15px'})

button_to_shape = MDCButton('HOLA', raised=False, unelevated=True)

shape = MDCShape(button_to_shape)
shape.mdc.set_corners(background_color='white', size='10px')
container <= shape
        '''
        self.main.brython_code_sample('Shape', code, container)


        code =  '''
button = MDCButton('HOLA', raised=False, outlined=True)
container <= button
container <= html.DIV(style={'margin': '15px'})

button_to_shape = MDCButton('HOLA', raised=False, outlined=True)

shape = MDCShape(button_to_shape)
shape.mdc.set_corners(outlined=True, outline_color='#4db6ac', size='10px', background_color='white')
container <= shape
        '''
        self.main.brython_code_sample('Shape Outlined', code, container)



        code =  '''
button = MDCButton('HOLA', raised=True, unelevated=True)
container <= button
container <= html.DIV(style={'margin': '15px'})

button_to_shape = MDCButton('HOLA', raised=False, unelevated=True)

shape = MDCShape(button_to_shape)
shape.mdc.set_corners(background_color='white', size=['10px', '0', '10px', '0'])
container <= shape
        '''
        self.main.brython_code_sample('Shape selected corners', code, container)



        return parent


