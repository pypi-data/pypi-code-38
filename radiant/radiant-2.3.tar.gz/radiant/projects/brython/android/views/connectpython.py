from browser import html

from mdcframework.mdc import MDCTopAppBar
from mdcframework.base import MDCView


# from radiant import PythonCore



########################################################################
class Python(MDCView):
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
        self.topappbar = MDCTopAppBar('Python')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
from radiant import AndroidMain
androidmain = AndroidMain()

# This functions are defined in android/code/main.py
# and can be accessed from here, that's awesome.

container <= html.SPAN(androidmain.local_ip())
container <= html.BR()
container <= html.SPAN(androidmain.my_python_function())
        '''
        self.main.brython_code_sample('', code, container)


        return parent


