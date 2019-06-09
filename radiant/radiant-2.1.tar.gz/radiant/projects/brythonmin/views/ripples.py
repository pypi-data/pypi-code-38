from mdcframework.mdc import MDCTopAppBar, MDCComponent

from mdcframework.base import MDCView
from browser import html

########################################################################
class Ripples(MDCView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        #self.toolbar.mdc['icon'].bind('click', lambda ev:self.main.drawer.mdc.open())


    #----------------------------------------------------------------------
    def build(self):
        parent = html.DIV()
        self.topappbar = MDCTopAppBar('Ripples')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
style = {'width': 'calc(30vw - 10px)',
         'height': '100px',
         'border': '1px solid lightgray',
         'border-radius': '10%',
         'align-items': 'center',
         'justify-content': 'center',
         'display': 'flex',
         'margin': '0 1.5vw',
         }


frame1 = html.DIV('Ripple')
frame1.style = style
frame1 = MDCComponent(frame1)
frame1.mdc.ripple()

frame2 = html.DIV('Ripple<br>Primary')
frame2.style = style
frame2 = MDCComponent(frame2)
frame2.mdc.ripple(theme='primary')

frame3 = html.DIV('Ripple<br>Accent')
frame3.style = style
frame3 = MDCComponent(frame3)
frame3.mdc.ripple(theme='accent')


parent = html.DIV(style={'display': 'inline-flex', })

parent <= frame1
parent <= frame2
parent <= frame3

container <= parent
        '''
        self.main.brython_code_sample('Ripple', code, container)


        return parent


