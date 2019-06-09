from mdcframework.mdc import MDCTopAppBar, MDCForm, MDCFormField

from mdcframework.base import MDCView
from browser import html

########################################################################
class Forms(MDCView):
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
        self.topappbar = MDCTopAppBar('Forms')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container


        code =  '''
form = MDCForm()

form.mdc.TextField('Name', helper_text='Will be visible for everyone')
form.mdc.TextField('Email')
form.mdc.TextField('Password', type='password')

form.mdc.Radio('Science', name='n0', checked=True)
form.mdc.Radio('Arts', name='n0')
form.mdc.Radio('Humanities', name='n0')

form.mdc.Checkbox('I want to receive emails about cats', checked=True)

form.mdc.TextAreaField('Comments', helper_text='Please, be nice', cols='20', rows='3')

container <= form
        '''
        self.main.brython_code_sample('Forms', code, container)


        code =  '''
form = MDCForm()

form.mdc.TextField('Name', helper_text='Will be visible for everyone', fullwidth=True)
form.mdc.TextField('Email', fullwidth=True)


form.mdc.TextAreaField('Comments', fullwidth=True)


container <= form
        '''
        self.main.brython_code_sample('Fullwidth Forms', code, container)




        # code =  '''
# ff = MDCFormField()
# ff.style = {'width': '100%',
            # 'min-height': '40px'}

# form = MDCForm(formfield=ff)
# form.mdc.Checkbox('My Checkbox')
# form.mdc.Checkbox('My Checkbox')
# form.mdc.Radio('My Radio')
# container <= form
        # '''
        # self.main.brython_code_sample('Forms with custom FormField', code, container)


        # code =  '''
# ff = MDCFormField()
# ff.style = {'width': '100%',
            # 'min-height': '40px'}
# ss = html.HR()

# form = MDCForm(formfield=ff, separator=ss)
# form.mdc.Checkbox('My Checkbox')
# form.mdc.Checkbox('My Checkbox')
# form.mdc.Radio('My Radio')
# container <= form
        # '''
        # self.main.brython_code_sample('Forms with separators', code, container)




        return parent


