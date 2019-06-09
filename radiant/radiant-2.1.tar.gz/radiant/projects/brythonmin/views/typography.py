from mdcframework.mdc import MDCTopAppBar, MDCComponent

from mdcframework.base import MDCView
from browser import html

########################################################################
class Typography(MDCView):
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
        self.topappbar = MDCTopAppBar('Typography')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
for i in range(1, 7):
    label = MDCComponent(html.SPAN('Headline{}'.format(i)))
    label.mdc.typography('headline{}'.format(i))
    container <= label
    container <= html.BR()

for i in range(1, 3):
    label = MDCComponent(html.SPAN('Subtitle{}'.format(i)))
    label.mdc.typography('subtitle{}'.format(i))
    container <= label
    container <= html.BR()

for i in range(1, 3):
    label = MDCComponent(html.SPAN('Body{}'.format(i)))
    label.mdc.typography('body{}'.format(i))
    container <= label
    container <= html.BR()

label = MDCComponent(html.SPAN('Caption'))
label.mdc.typography('caption')
container <= label
container <= html.BR()

label = MDCComponent(html.SPAN('Button'))
label.mdc.typography('button')
container <= label
container <= html.BR()

label = MDCComponent(html.SPAN('Overline'))
label.mdc.typography('overline')
container <= label
        '''
        self.main.brython_code_sample('Typography', code, container)


        return parent

