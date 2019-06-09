from mdcframework.mdc import MDCButton, MDCTopAppBar

from mdcframework.base import MDCView
from browser import html

########################################################################
class Elevations(MDCView):
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

        code =  '''

button = MDCButton('Button elevation', raised=False, ripple=True)
button.mdc.elevation(Z=5)
container <= button

        '''
        self.main.brython_code_sample('', code, container, render=False)


        buttons_container = html.DIV()
        buttons_container.style = {'text-align': 'center',}

        for i in range (1, 25):
            button = MDCButton('Z={}'.format(i), raised=True, ripple=True)
            button.style = {'margin': '20px',}
            button.mdc.elevation(Z=i)
            buttons_container <= button
            #button = MDCButton('Z={}'.format(25-i), raised=True, ripple=True)
            #button.style = {'margin': '10px',}
            #button.mdc.set_elevation(25-i)
            #buttons_container <= button

            #buttons_container <= html.DIV('<br>')

        container <= buttons_container
        return parent


