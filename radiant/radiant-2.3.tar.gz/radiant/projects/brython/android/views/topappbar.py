from mdcframework.mdc import MDCTopAppBar, MDCButton

from mdcframework.base import MDCView
from browser import window, html

#from functools import wraps

########################################################################
class TopAppBar(MDCView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        #self.topappbar.mdc['icon'].bind('click', lambda ev:self.main.drawer.mdc.open())
        #self.topappbar.bind('MDCTopAppBar:nav', lambda ev:self.main.drawer.mdc.open())



    ##----------------------------------------------------------------------
    #def subview(view):
        #""""""
        #@wraps(view)
        #def wrapped(self, *args, **kwargs):
            #""""""
            #container = view(self)

            #self.container.clear()
            #self.container <= container

            #self.main.secure_load()

            ##self.main.container.clear()
            ##self.container.clear()
        #return wrapped



    #----------------------------------------------------------------------
    @MDCView.subview
    def normal(self):
        """"""
        container = html.DIV()

        topappbar = MDCTopAppBar('Normal Top App Bar')
        topappbar.mdc.add_item('file_download')
        topappbar.mdc.add_item('print')
        topappbar.mdc.add_item('bookmark')
        container <= topappbar

        content = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})

        code = """
topappbar = MDCTopAppBar('Normal Top App Bar')
topappbar.mdc.add_item('file_download')
topappbar.mdc.add_item('print')
topappbar.mdc.add_item('bookmark')

container <= topappbar
        """
        self.main.brython_code_sample('Normal Top App Bar', code, content, render=False)

        content <= self.build(False)
        container <= content
        return container



    #----------------------------------------------------------------------
    @MDCView.subview
    def prominent(self):
        """"""
        container = html.DIV()

        topappbar = MDCTopAppBar('Prominent Top App Bar', prominent=True)
        topappbar.mdc.add_item('file_download')
        topappbar.mdc.add_item('print')
        topappbar.mdc.add_item('bookmark')
        container <= topappbar

        content = html.DIV(style = {'padding': '15px', 'padding-top': '128px',})

        code = """
topappbar = MDCTopAppBar('Prominent Top App Bar', prominent=True)
topappbar.mdc.add_item('file_download')
topappbar.mdc.add_item('print')
topappbar.mdc.add_item('bookmark')

container <= topappbar
        """
        self.main.brython_code_sample('Top App Bar', code, content, render=False)

        content <= self.build(False)
        container <= content
        return container




    #----------------------------------------------------------------------
    @MDCView.subview
    def not_fixed(self):
        """"""
        container = html.DIV()

        topappbar = MDCTopAppBar('Fixed Top App Bar', fixed=False)
        topappbar.mdc.add_item('file_download')
        topappbar.mdc.add_item('print')
        topappbar.mdc.add_item('bookmark')
        container <= topappbar

        content = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})

        code = """
topappbar = MDCTopAppBar('Fixed Top App Bar', fixed=True)
topappbar.mdc.add_item('file_download')
topappbar.mdc.add_item('print')
topappbar.mdc.add_item('bookmark')

container <= topappbar
        """
        self.main.brython_code_sample('Fixed Top App Bar', code, content, render=False)

        content <= self.build(False)
        container <= content
        return container


    #----------------------------------------------------------------------
    @MDCView.subview
    def short(self):
        """"""
        container = html.DIV()

        topappbar = MDCTopAppBar('Short Top App Bar', short=True)
        topappbar.mdc.add_item('file_download')
        container <= topappbar

        content = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})

        code = """
topappbar = MDCTopAppBar('Short Top App Bar', short=True)
topappbar.mdc.add_item('file_download')

container <= topappbar
        """
        self.main.brython_code_sample('Fixed Top App Bar', code, content, render=False)

        content <= self.build(False)
        container <= content
        return container




    #----------------------------------------------------------------------
    def build(self, toolbar=True):
        """"""
        container = html.DIV()

        if toolbar:
            self.topappbar = MDCTopAppBar('Top App Bar')
            container <= self.topappbar
            container <= html.DIV(style = {'padding': '15px', 'padding-top': '56px',})

        content = html.DIV(style = {'padding': '15px',})

        button = MDCButton('Normal Top App Bar', raised=True)
        button.bind('click', self.normal)
        content <= button
        content <= html.DIV(style = {'padding-top': '15px',})

        button = MDCButton('Not Fixed Top App Bar', raised=True)
        button.bind('click', self.not_fixed)
        content <= button
        content <= html.DIV(style = {'padding-top': '15px',})

        button = MDCButton('Short Top App Bar', raised=True)
        button.bind('click', self.short)
        content <= button
        content <= html.DIV(style = {'padding-top': '15px',})

        button = MDCButton('Prominent Top App Bar', raised=True)
        button.bind('click', self.prominent)
        content <= button
        content <= html.DIV(style = {'padding-top': '15px',})


        content <= html.DIV(style={'height': '150vh',})

        container <= content
        return container


