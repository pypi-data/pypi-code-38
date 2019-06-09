from mdcframework.mdc import MDCTopAppBar, MDCComponent

from mdcframework.base import MDCView
from browser import html

########################################################################
class Themes(MDCView):
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
        self.topappbar = MDCTopAppBar('Themes')
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

frame1 = html.DIV('Primary')
frame1.style = style
frame1 = MDCComponent(frame1)
frame1.mdc.theme('primary')

frame2 = html.DIV('Secondary')
frame2.style = style
frame2 = MDCComponent(frame2)
frame2.mdc.theme('secondary')

frame3 = html.DIV('Background')
frame3.style = style
frame3 = MDCComponent(frame3)
frame3.mdc.theme('background')


parent = html.DIV(style={'display': 'inline-flex', })

parent <= frame1
parent <= frame2
parent <= frame3

container <= parent
        '''
        self.main.brython_code_sample('Primary and Secondary', code, container)


        code =  '''
frame1 = html.DIV('Primary-Bg')
frame1.style = style
frame1 = MDCComponent(frame1)
frame1.mdc.theme('on-primary')
frame1.mdc.theme('primary-bg')

frame2 = html.DIV('Secondary-Bg')
frame2.style = style
frame2 = MDCComponent(frame2)
frame2.mdc.theme('on-secondary')
frame2.mdc.theme('secondary-bg')


parent = html.DIV(style={'display': 'inline-flex', })

parent <= frame1
parent <= frame2

container <= parent
        '''
        self.main.brython_code_sample('Backgrounds', code, container)


        code =  '''
frame1 = html.DIV('text-hint')
frame1.style = style
frame1 = MDCComponent(frame1)
frame1.mdc.theme('text-hint', on='light')

frame2 = html.DIV('text-disabled')
frame2.style = style
frame2 = MDCComponent(frame2)
frame2.mdc.theme('text-disabled', on='light')

frame3 = html.DIV('text-icon')
frame3.style = style
frame3 = MDCComponent(frame3)
frame3.mdc.theme('text-icon', on='light')


parent = html.DIV(style={'display': 'inline-flex', })

parent <= frame1
parent <= frame2
parent <= frame3

container <= parent
        '''
        self.main.brython_code_sample('Texts', code, container)



        return parent


