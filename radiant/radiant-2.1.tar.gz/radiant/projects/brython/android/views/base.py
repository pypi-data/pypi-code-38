from browser import document, window
from mdcframework.base import MDCBase
from mdcframework.mdc import *

from browser import html


########################################################################
class Base(MDCBase):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""

        self.rest = None
        self.load_styles([
            "styles.css",
            "theme.css",
        ])

        # self.load_scripts([

           # ])

        super().__init__(*args, **kwargs)

    # ----------------------------------------------------------------------

    def brython_code_sample(self, title, code, container, render=True, rest_ignore=None):
        """"""

        self.generate_rest_documentation(title, rest_ignore, code)

        title = html.H3(title)
        title.style = {
            'font-weight': 'normal',
        }
        container <= title

        display_code = html.PRE(code)
        display_code.style = {
            'overflow-x': 'scroll',
            'font-size': '13px',
            'margin': '0',
        }

        card = html.DIV(display_code, Class="mdc-card", style={'padding': '1em',
                                                               'margin': '1em 0px',
                                                               'background-color': 'rgba(77, 182, 172, 0.13)',
                                                               'color': '#3a3a3a',
                                                               })

        container <= card

        if render:
            eval(code, globals(), locals())

            divisor = html.DIV()
            divisor.style = {
                'height': '34px',
            }

            container <= divisor

    # ----------------------------------------------------------------------

    def generate_rest_documentation(self, title, rest_ignore, code):
        """"""
        if self.rest is None:
            return

        self.rest.append(title)
        self.rest.append('-' * len(title))
        self.rest.append('')
        self.rest.append('.. brython::')
        # self.rest.append('')

        if rest_ignore:
            # self.rest.append('\n')
            self.rest.append('')
            for line in rest_ignore.split('\n'):
                self.rest.append('    {}'.format(line))
            self.rest.append('    #!ignore')

        for line in code.split('\n'):
            self.rest.append('    {}'.format(line))

        self.rest.append('')


main = Base(**{'home': ['home.Home', 'Home', 'home'],
               'python': ['connectpython.Python', 'Python', 'code'],
               'buttons': ['buttons.Buttons', 'Buttons', 'add_circle_outline'],
               'cards': ['cards.Cards', 'Cards', 'picture_in_picture'],
               'chips': ['chips.Chips', 'ChipSet', 'label_outline'],
               'dialog': ['dialogs.Dialogs', 'Dialogs', 'announcement'],
               'elevations': ['elevations.Elevations', 'Elevations', 'filter_none'],
               'formfields': ['formfields.FormField', 'FormFields', 'text_fields'],
               'forms': ['forms.Forms', 'Forms', 'text_fields'],
               'gridlist': ['gridlist.GridLists', 'GridLists', 'view_week'],
               # 'imagelist': [ImageList, ['ImageList', 'view_quilt']],
               'layoutgrid': ['layoutgrid.LayoutGrid', 'LayoutGrid', 'view_quilt'],
               'linearprogress': ['linearprogress.LinearProgress', 'LinearProgress', 'more_horiz'],
               'lists': ['lists.Lists', 'Lists', 'list'],
               'menus': ['menus.Menus', 'Menus', 'more_vert'],
               'ripples': ['ripples.Ripples', 'Ripples', 'toll'],
               'shapes': ['shapes.Shapes', 'Shapes', 'format_shapes'],
               'snackbars': ['snackbars.Snackbars', 'Snackbars', 'call_to_action'],
               'tabs': ['tabs.Tabs', 'Tabs', 'tab'],
               'themes': ['themes.Themes', 'Themes', 'color_lens'],
               'topappbar': ['topappbar.TopAppBar', 'TopAppBar', 'featured_play_list'],
               'typography': ['typography.Typography', 'Typography', 'font_download'],
               })

# main.generate_drawer()
main.generate_drawer(mode='modal', theme='primary', item_theme='secondary', title='Radiant', subtitle='Python framework for Android apps development')


path = window.location.href.split('#')[-1].lower()
if path in main.register_class:
    main.view(path)
else:
    main.view('home')


try:
    document.select('.splash_loading')[0].remove()
except:
    pass

