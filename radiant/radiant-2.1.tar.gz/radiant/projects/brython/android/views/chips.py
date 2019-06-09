from mdcframework.mdc import MDCTopAppBar, MDCChipSet

from mdcframework.base import MDCView
from browser import html

########################################################################
class Chips(MDCView):
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
        self.topappbar = MDCTopAppBar('ChipSet')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
chips = MDCChipSet()

chips.mdc.add_chip('Hola')
chips.mdc.add_chip('Mundo', selected=True)
chips.mdc.add_chip('Add to calendar', leading='event')
chips.mdc.add_chip('Jane Smith', trailing='cancel')

container <= chips
        '''
        self.main.brython_code_sample('Chips', code, container)

        code = '''
    chips = MDCChipSet()
    container <= chips
    log = html.SPAN()
    container <= log

    for label in 'Uno Dos Tres Cuatro Cinco'.split():
        chip = chips.mdc.add_chip(label)
        chip.id = label
        chip.bind('click', self.select_chip(chip))
        chip.bind('click', lambda evt:setattr(log, 'text', chips.mdc['selected']))

    return container

#----------------------------------------------------------------------
def select_chip(self, chip):
    """"""
    return lambda evt:self.toggleclass(chip, 'mdc-chip--selected')
        '''


        self.main.brython_code_sample('Selectable Chips', code, container, render=False)


        chips = MDCChipSet()
        container <= chips
        log = html.SPAN()
        container <= log

        for label in 'Uno Dos Tres Cuatro Cinco'.split():
            chip = chips.mdc.add_chip(label)
            chip.id = label
            chip.bind('click', self.select_chip(chip))
            chip.bind('click', lambda evt:setattr(log, 'text', chips.mdc['selected']))

        return parent


    #----------------------------------------------------------------------
    def select_chip(self, chip):
        """"""
        return lambda evt:self.toggleclass(chip, 'mdc-chip--selected')
