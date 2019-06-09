"""
Brython MDCFramework: Base
==========================



"""


from browser import document, window, html, timer, load

from .mdc.MDCDrawer import MDCDrawer

#from .core import MDC

# from functools import wraps
# from importlib import import_module


########################################################################
class MDCBase:
    """
    BASE

    """

    # ----------------------------------------------------------------------
    def __init__(self, preload=False, preload_timeout=5000, save_static=False, *args, **kwargs):
        """"""
        self.__last_view__ = None

        self.save_static = save_static

        self.close_drawer_on_view = True

        self.registered_views = {}
        # self.all_views = []
        self.register_class = kwargs
        # self.

        self.build()

        # t = Thread(target=self.timeout_preload)
        if preload:
            timer.set_timeout(self.__timeout_preload__, preload_timeout)
        # t.start()

    # ----------------------------------------------------------------------
    def generate_drawer(self, **kwargs):
        """"""
        self.drawer = MDCDrawer(**kwargs)

        if kwargs.get('mode', 'modal') == 'modal':
            self.__drawer_placeholder__.after(html.DIV(Class="mdc-drawer-scrim"))
            self.__drawer_placeholder__.after(self.drawer)
            self.drawer.attach()
        else:
            self.__drawer_placeholder__.after(self.drawer)

        for key in self.register_class:
            _, name, icon = self.register_class[key]
            item = self.drawer.mdc.add_item(name, icon, id=key, link='{}.html'.format(key), ignore_link=True)
            item.bind('click', self.__set_view__(key, item))

        self.drawer.mdc['items'][0].class_name += ' mdc-list-item--activated'
        [item.bind('click', self.__set_focus__) for item in document.select('.mdc-list-item')]

    # ----------------------------------------------------------------------

    def __set_view__(self, key, item):
        """"""
        def inset(evt):
            self.view(key)
        return inset

    # ----------------------------------------------------------------------

    def __set_focus__(self, element):
        """"""
        for item in document.select('.mdc-list-item'):
            item.class_name = item.class_name.replace('mdc-list-item--activated', '')
        try:
            element.target.class_name += ' mdc-list-item--activated'
        except:
            element.class_name += ' mdc-list-item--activated'

    # ----------------------------------------------------------------------

    @classmethod
    def load_styles(self, styles_list):
        """"""
        document.select('head')[0] <= [html.LINK(href='/static/{}'.format(style), type='text/css', rel='stylesheet') for style in styles_list]
        # [load('/static/{}'.format(style)) for style in styles_list]

    # ----------------------------------------------------------------------

    @classmethod
    def load_scripts(self, scripts_list):
        """"""
        # document.select('head')[0] <= [html.SCRIPT(src='/static/{}'.format(script), type='text/javascript') for script in scripts_list]
        # [load('/static/{}'.format(script)) for script in scripts_list]
        for script in scripts_list:
            if script.startswith('http'):
                load(script)
            else:
                load('/static/{}'.format(script))

    # ----------------------------------------------------------------------

    def build(self):
        """"""
        body = html.DIV(Class='radiant-main', style={'display': 'inline-flex', 'width': '100%', 'height': '100%', })

        self.__drawer_placeholder__ = html.SPAN()
        body <= self.__drawer_placeholder__

        self.container = html.DIV(Class="mdc-drawer-app-content", style={'width': '100vw'})
        body <= self.container

        document <= body

    # #----------------------------------------------------------------------
    # def register(self, class_, icon, name):
        # """"""
        # self.register_class[name] = (class_, icon)

    # ----------------------------------------------------------------------
    def remove_parent(self, element):
        """"""
        new_parent = element.parent
        new = element.child[0]

    # ----------------------------------------------------------------------
    def __timeout_preload__(self):
        """"""
        # print(self.register_class)
        for view in self.register_class:
            self.preload(view)

    # ----------------------------------------------------------------------
    # @coroutine

    def preload(self, name):
        """"""
        if name in self.registered_views:
            # print('already loaded')
            return

        else:
            #view = eval(name)
            view, _, _ = self.register_class[name]
            mod, class_ = view.split('.')
            mod = __import__(mod)
            view = getattr(mod, class_)
            view = view(self, preload=True)
            # view.onload()
            # self.container.clear()
            # self.container <= view.container
            self.registered_views[name] = view

    # ----------------------------------------------------------------------

    def view(self, name, fn=None, kwargs={}):
        """"""
        if self.__last_view__:
            self.registered_views[self.__last_view__].onchange()
            self.registered_views[self.__last_view__].onchange_()

        # print(name)
        if name in self.registered_views:
            self.container.clear()
            self.container <= self.registered_views[name].container
            if fn:
                getattr(self.registered_views[name], fn)(**kwargs)
            self.registered_views[name].onload()
            self.registered_views[name].onload_()
            self.registered_views[name].apply_styles()
            # self.registered_views[name].loaded()
            self.registered_views[name].firstload()

        else:
            #view = eval(name)
            view, _, _ = self.register_class[name]
            mod, class_ = view.split('.')
            mod = __import__(mod)
            view = getattr(mod, class_)
            view = view(self)
            view.name__ = name
            view.onload()
            view.onload_()
            view.apply_styles()
            self.container.clear()
            self.container <= view.container
            self.registered_views[name] = view
            # view.loaded()

        self.__last_view__ = name
        self.secure_load()
        self.secure_styles()

        self.__set_focus__(document.select('.mdc-list-item#{}'.format(name))[-1])

        if self.save_static:
            from radiant import Exporter
            html_code = document.select('html')[-1].html
            ex = Exporter()
            ex.export('{}.html'.format(name), html_code)

    # ----------------------------------------------------------------------

    def secure_load(self):
        """"""
        try:
            topappbar = window.mdc.topAppBar.MDCTopAppBar.attachTo(document.querySelector('.mdc-top-app-bar'))
            if hasattr(self, 'drawer') and document.querySelector('.mdc-top-app-bar').autodrawer:
                # document.select('.mdc-top-app-bar')[0].unbind('MDCTopAppBar:nav')
                # document.select('.mdc-top-app-bar')[0].bind('MDCTopAppBar:nav', lambda ev:self.drawer.mdc.toggle())
                document.select('.mdc-top-app-bar .mdc-top-app-bar__navigation-icon')[0].unbind()
                document.select('.mdc-top-app-bar .mdc-top-app-bar__navigation-icon')[0].bind('click', lambda ev: self.drawer.mdc.toggle())

        except:
            pass

        # [window.mdc.ripple.MDCRipple.attachTo(ripple) for ripple in document.select('[data-mdc-auto-init=MDCRipple]')]
        # [window.mdc.ripple.MDCRipple.attachTo(surface) for surface in document.select('.mdc-button')]
        # [window.mdc.ripple.MDCRipple.attachTo(surface) for surface in document.select('.mdc-ripple-surface')]

        try:
            [window.mdc.slider.MDCSlider.attachTo(slider) for slider in document.select('.mdc-slider')]
        except:
            pass

        # try:
            # [window.mdc.floatingLabel.MDCFloatingLabel.attachTo(label) for label in document.select('.mdc-floating-label')]
        # except:
            # pass
        # try:
            # [window.mdc.helperText.MDCTextFieldHelperText.attachTo(label) for label in document.select('.mdc-text-field-helper-text')]
        # except:
            # pass

        # try:
            # [window.mdc.lineRipple.MDCLineRipple.attachTo(label) for label in document.select('.mdc-line-ripple')]
        # except:
            # pass

        # try:
            # [window.mdc.textField.MDCTextField.attachTo(label) for label in document.select('.mdc-text-field')]
        # except:
            # pass

        if hasattr(self, 'drawer') and self.close_drawer_on_view:
            self.drawer.mdc.close()

    # ----------------------------------------------------------------------

    def secure_styles(self):
        """"""

        # document <= html.STYLE('.mdc-text-field__input {height: unset;}')


    #----------------------------------------------------------------------
    def hide(self):
        """"""
        document.select_one('.radiant-main').style = {'display': None,}


    #----------------------------------------------------------------------
    def show(self, mode="inline-flex"):
        """"""
        document.select_one('.radiant-main').style = {'display': mode,}


########################################################################
class MDCView:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, preload=False):
        """Constructor"""

        self.main = parent

        if not preload:
            # self.main.mdc_drawer.mdc.close()
            self.main.container.clear()

        self.container = self.build()
            # self.connect()

    # ----------------------------------------------------------------------
    def firstload(self):
        """"""

    # ----------------------------------------------------------------------
    def onreloaded(self):
        """"""

    # ----------------------------------------------------------------------
    def onload(self):
        """"""

    # ----------------------------------------------------------------------
    def onchange(self):
        """"""

    # ----------------------------------------------------------------------
    def onchange_(self):
        """"""
        for e in document.select(f'.emtp-show-on-{self.name__}'):
            e.style = {'display': None, }

    # ----------------------------------------------------------------------
    def onload_(self):
        """"""
        for e in document.select(f'.emtp-show-on-{self.name__}'):
            e.style = {'display': 'flex', }

    # ----------------------------------------------------------------------
    def apply_styles(self):
        """"""
        styles = self.styles()
        for k in styles:
            for component in self.container.select(k):
                component.style = styles[k]

    # ----------------------------------------------------------------------
    def reloadview(self, event=None):
        """"""
        self.main.container.clear()
        self.container = self.build()
        self.onload()
        self.main.container <= self.container
        self.main.secure_load()
        self.onreloaded()

        # if fn:
            # fn(kwargs)

    # ----------------------------------------------------------------------

    def toggleclass(self, chip, class_):
        """"""
        if class_ in chip.class_name:
            chip.class_name = chip.class_name.replace(class_, '')
        else:
            chip.class_name += ' {}'.format(class_)

    # ----------------------------------------------------------------------
    @classmethod
    def subview(cls, view):
        """"""
        from functools import wraps

        @wraps(view)
        def wrapped(self, *args, **kwargs):
            """"""
            container = view(self)

            self.container.clear()
            self.container <= container

            self.main.secure_load()

            # self.main.container.clear()
            # self.container.clear()
        return wrapped

    # ----------------------------------------------------------------------
    def styles(self):
        """"""
        return {}


    # ----------------------------------------------------------------------
    def set_title(self, title):
        """"""
        document.select_one('body title').text = title


    # #----------------------------------------------------------------------
    # def open_link(self, link):
        # """"""
        # def inset(event):
            # event.preventDefault()
            # androidmain.open_url(link.href)
        # return inset


#########################################################################
# class htmlElement:
    # """"""

    # ----------------------------------------------------------------------
    # def __new__(self, element):
        # """"""
        #element.__getattr__ = self.__getattr__
        # return element

    # ----------------------------------------------------------------------
    # def __getattr__(self, attr):
        # """"""
        #name = self.getAttribute('mdc-name')

        # if attr is 'mdc':
            # return MDC.__mdc__(name, element=self)

        # elif attr is 'Foundation':
            # return MDC.__mdc__(name, element=self).mdc.foundation_


