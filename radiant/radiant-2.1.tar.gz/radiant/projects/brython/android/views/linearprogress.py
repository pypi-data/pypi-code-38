from mdcframework.mdc import MDCTopAppBar, MDCLinearProgress, MDCButton

from mdcframework.base import MDCView
from browser import html

########################################################################
class LinearProgress(MDCView):
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
        self.topappbar = MDCTopAppBar('Linear Progress')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        progressbar = MDCLinearProgress()
        progressbar.style = {'margin-bottom': '20px', 'padding-top': '56px',}
        container <= progressbar

        progressbar.mdc.set_progress(0.5)  #50%

        code =  '''
progressbar = MDCLinearProgress()
progressbar.style = {'margin-bottom': '20px'}
container <= progressbar

progressbar.mdc.set_progress(0.5)  #50%
#progressbar.mdc.set_progress(0.5, buffer=0.6)  #50%
        '''
        self.main.brython_code_sample('Linear Progress', code, container, render=False)


        button = MDCButton('Set 0%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0))
        container <= button

        button = MDCButton('Set 10%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0.1))
        container <= button

        button = MDCButton('Set 50%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0.5))
        container <= button

        button = MDCButton('Set 100%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(1))
        container <= button



        button = MDCButton('Set 0%, Buffer=10%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0, 0.1))
        container <= button

        button = MDCButton('Set 10%, Buffer=20%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0.1, 0.2))
        container <= button

        button = MDCButton('Set 50%, Buffer=60%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0.5, 0.6))
        container <= button

        button = MDCButton('Set 70%, Buffer=80%', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_progress(0.7, 0.8))
        container <= button



        code =  '''
progressbar.mdc.close()
progressbar.mdc.open()
        '''
        self.main.brython_code_sample('Progress Bar Close-Open', code, container, render=False)

        button = MDCButton('Close', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.close())
        container <= button

        button = MDCButton('Open', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.open())
        container <= button


        code =  '''
progressbar.mdc.set_reverse(True)
progressbar.mdc.set_reverse(False)
        '''
        self.main.brython_code_sample('Progress Bar Reverse-Normal', code, container, render=False)

        button = MDCButton('Reverse', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_reverse(True))
        container <= button

        button = MDCButton('No Reverse', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_reverse(False))
        container <= button



        code =  '''
progressbar.mdc.set_determinate(True)
progressbar.mdc.set_determinate(False)
        '''
        self.main.brython_code_sample('Progress Bar Determinate-Indeterminate', code, container, render=False)

        button = MDCButton('Indeterminate', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_determinate(False))
        container <= button

        button = MDCButton('Determinate', raised=False, ripple=True)
        button.bind('click', lambda evt:progressbar.mdc.set_determinate(True))
        container <= button


        return parent


