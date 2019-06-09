from mdcframework.mdc import MDCTopAppBar, MDCList, MDCListGroup

from mdcframework.base import MDCView
from browser import html

########################################################################
class Lists(MDCView):
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
        self.topappbar = MDCTopAppBar('Lists')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container

        code =  '''
list_ = MDCList()

list_.mdc.add_item('Suzuka Nakamoto', 'Su-metal')
list_.mdc.add_item('Yui Mizuno', 'Yuimetal')
list_.mdc.add_item('Moa Kikuchi', 'Moametal')

container <= list_
        '''
        self.main.brython_code_sample('List with secondary text', code, container)


        code =  '''
list_ = MDCList(dense=True)

list_.mdc.add_item('Luke Hemmings')
list_.mdc.add_item('Calum Hood')
list_.mdc.add_item('Ashton Irwin')
list_.mdc.add_item('Michael Clifford')

container <= list_
        '''
        self.main.brython_code_sample('List dense', code, container)


        code =  '''
list_ = MDCList()

list_.mdc.add_item('Wi-Fi', icon='network_wifi')
list_.mdc.add_item('Bluetooth', icon='bluetooth')
list_.mdc.add_item('Data Usage', icon='data_usage')

container <= list_
        '''
        self.main.brython_code_sample('List with icons', code, container)



        code =  '''
list_ = MDCList()

list_.mdc.add_item('Wi-Fi', meta='network_wifi')
list_.mdc.add_item('Bluetooth', meta='bluetooth')
list_.mdc.add_item('Data Usage', meta='data_usage')

container <= list_
        '''
        self.main.brython_code_sample('List with metal label', code, container)




        code =  '''
list_ = MDCList(avatar=True)

list_.mdc.add_item('Red', avatar='favorite', avatar_background_color='red', avatar_color='white')
list_.mdc.add_item('Green', avatar='favorite', avatar_background_color='green', avatar_color='white')
list_.mdc.add_item('Blue', avatar='favorite', avatar_background_color='blue', avatar_color='white')
list_.mdc.add_item('gray', avatar='favorite')

container <= list_
        '''
        self.main.brython_code_sample('List with avatar', code, container)



        code =  '''
list_ = MDCList()

list_.mdc.add_item('Single-line item ', placeholder=True)
list_.mdc.add_item('Single-line item ', placeholder=True)

container <= list_
        '''
        self.main.brython_code_sample('List with placeholder', code, container)


        code =  '''
list_ = MDCList()

list_.mdc.add_item('Suzuka Nakamoto', icon_meta='favorite', meta_color='red')
list_.mdc.add_item('Aya Hirano', icon_meta='favorite')
list_.mdc.add_item('MISA', 'Band-Maid', icon_meta='favorite')

container <= list_
        '''
        self.main.brython_code_sample('List with icon in meta', code, container)



        code =  '''
list_ = MDCList()

list_.mdc.add_check_item('Undergraduate', checked=True)
list_.mdc.add_check_item('Master', checked=True)
list_.mdc.add_check_item('Doctorate')
list_.mdc.add_check_item('Postdoctoral')

container <= list_
        '''
        self.main.brython_code_sample('List with check item', code, container)


        code =  '''
list1 = MDCList()
list1.mdc.add_item('Suzuka Nakamoto', 'Su-metal', placeholder=True)
list1.mdc.add_item('Yui Mizuno', 'Yuimetal', placeholder=True)
list1.mdc.add_item('Moa Kikuchi', 'Moametal', placeholder=True)

list2 = MDCList()
list2.mdc.add_item('Saiki Atsumi', placeholder=True)
list2.mdc.add_item('Miku Kobato', placeholder=True)
list2.mdc.add_item('Akane Hirose', placeholder=True)
list2.mdc.add_item('Kanami Tōno', placeholder=True)
list2.mdc.add_item('MISA', placeholder=True)


listgroup = MDCListGroup()
listgroup.mdc.add_list('Babymetal', list1)
listgroup.mdc.add_list('Band-Maid', list2)


container <= listgroup
        '''
        self.main.brython_code_sample('List groups', code, container)


        code =  '''
list_ = MDCList()

list_.mdc.add_item('Suzuka Nakamoto', 'Su-metal', placeholder=True)
list_.mdc.add_item('Yui Mizuno', 'Yuimetal', placeholder=True)
list_.mdc.add_item('Moa Kikuchi', 'Moametal', placeholder=True)
list_.mdc.add_divider()
list_.mdc.add_item('Saiki Atsumi', placeholder=True)
list_.mdc.add_item('Miku Kobato', placeholder=True)
list_.mdc.add_item('Akane Hirose', placeholder=True)
list_.mdc.add_item('Kanami Tōno', placeholder=True)
list_.mdc.add_item('MISA', placeholder=True)
list_.mdc.add_divider(inset=True)
list_.mdc.add_item('Kanako Momota', placeholder=True)
list_.mdc.add_item('Shiori Tamai', placeholder=True)
list_.mdc.add_item('Ayaka Sasaki', placeholder=True)
list_.mdc.add_item('Reni Takagi', placeholder=True)

container <= list_
        '''
        self.main.brython_code_sample('List with separators', code, container)




        return parent


