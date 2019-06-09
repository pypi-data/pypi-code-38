from browser import window
from mdcframework.mdc import MDCTopAppBar, MDCComponent
# from mdcframework.MyImporter import MDCTopAppBar

#from pythoncore import PythonCore
#Piton = PythonCore()

from radiant import AndroidMain
androidmain = AndroidMain()

from mdcframework.base import MDCView

from browser import html


########################################################################
class Home(MDCView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        super().__init__(parent)

        #self.toolbar.mdc['icon'].bind('click', lambda ev:self.main.drawer.mdc.open())
        #self.icon_button.bind('click', lambda ev:self.main.drawer.mdc.open())


    #----------------------------------------------------------------------
    def build(self):
        """"""
        parent = html.DIV()
        topappbar = MDCTopAppBar('Radiant Framework')
        # topappbar.mdc.add_item('info')
        # topappbar.mdc.add_item('print')
        # topappbar.mdc.add_item('bookmark')
        parent <= topappbar
        container = html.DIV(Class='', style = {'padding': '15px',
                                                   'padding-top': 'calc(56px + 15px)',
                                                    # 'background-color': '#4db6ac',
                                                    # 'color': 'white',
                                                    'height': '-webkit-fill-available',
                                                    'width': '-webkit-fill-available',
                                                   # 'background-color': '#4db6ac',
                                                   })
        parent <= container

        title = MDCComponent(html.H2('A Python Framework for Android Apps Development'), style={'color': '#00867C'})
        title.mdc.typography('headline6')
        container <= title


        content = html.P('''
        This APP was made with <a class='my_link' target='_blank' href='http://brython.info/index.html'>Brython</a> and <a class='my_link' target='_blank' href='https://material.io/develop/web/'>Material Design Components</a>
        through <a class='my_link' target='_blank' href='https://radiantforandroid.bitbucket.io/'>Radiant Framework</a>.
        ''')

        body = MDCComponent(content)
        body.mdc.typography('body1')
        container <= body


        code =  '''
$ pip install radiant

$ radiant startproject brython MyProject 'My APP Name'
$ cd MyProject
$ python manage.py androidcreate --clean
$ python manage.py androidapk --brython_test
$ python manage.py androidapk --debug
        '''
        self.main.brython_code_sample('', code, container, render=False)



        for link in content.select("a.my_link"):
            # print(link.href)
            link.bind('click', self.open_link(link))



        return parent





    #----------------------------------------------------------------------
    def open_link(self, link):
        """"""
        def inset(event):
            event.preventDefault()
            androidmain.open_url(link.href)
        return inset
