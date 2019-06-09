from mdcframework.mdc import MDCTopAppBar, MDCForm, MDCFormField

from mdcframework.base import MDCView
from browser import html

########################################################################
class FormField(MDCView):
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
        self.topappbar = MDCTopAppBar('FormFields')
        parent <= self.topappbar
        container = html.DIV(style = {'padding': '15px', 'padding-top': '56px',})
        parent <= container


        code =  '''
ff = MDCFormField()
ff.style = {'width': '100%'}

form = MDCForm(formfield=ff)
form.mdc.Checkbox('My Checkbox')
form.mdc.Checkbox('My Checkbox', checked=True)
form.mdc.Checkbox('My Checkbox', disabled=True)
container <= form
        '''
        self.main.brython_code_sample('Checkbox', code, container)



        code =  '''
ff = MDCFormField()
ff.style = {'width': '100%'}

form = MDCForm(formfield=ff)
form.mdc.Radio('My Radio', name='n0')
form.mdc.Radio('My Radio', name='n0', checked=True)
form.mdc.Radio('My Radio', name='n0', disabled=True)
container <= form
        '''
        self.main.brython_code_sample('Radio', code, container)



        code =  '''
ff = MDCFormField()
ff.style = {'width': '100%'}

form = MDCForm(formfield=ff)

form.mdc.Select('Select', options=[('A', 'a'), ('B', 'b'), ('C', 'c'), ('D', 'd')])
form.mdc.Select('Preselected', options=[('A', 'a'), ('B', 'b'), ('C', 'c'), ('D', 'd')], selected='b')


container <= form
        '''
        self.main.brython_code_sample('Select', code, container)



        code =  '''
ff = MDCFormField()
ff.style = {'width': '100%'}

form = MDCForm(formfield=ff)

form.mdc.Slider('Slider', min=0, max=100, step=1, valuenow=10, continuous=True)
form.mdc.Slider('Slider', min=10, max=90, step=2, valuenow=20, discrete=True)
form.mdc.Slider('Slider', min=20, max=80, step=3, valuenow=30, discrete=True, markers=True)


container <= form
        '''
        self.main.brython_code_sample('Slider', code, container)



        code =  '''
ff = MDCFormField()
ff.style = {'width': '100%', 'height': '40px'}

form = MDCForm(formfield=ff)

form.mdc.Switch('Switch')
form.mdc.Switch('Switch', disabled=True)

container <= form
        '''
        self.main.brython_code_sample('Switch', code, container)


        code =  '''
ff = MDCFormField()
ff.style = {'width': '100%',
            'min-height': '40px',
            'display': 'flow-root'}

form = MDCForm(formfield=ff)

form.mdc.TextField('TextField')
form.mdc.TextField('TextField Fullwidth', fullwidth=True)

container <= form
        '''
        self.main.brython_code_sample('TextField', code, container)


        code =  '''
form = MDCForm(formfield=ff.clone())

form.mdc.TextField('Helper Text', helper_text='Helper text')
form.mdc.TextField('Not Persistent Helper Text', helper_text='Helper text', helper_text_persistent=False)
form.mdc.TextField('Helper Text', outlined=True, helper_text='Helper text')
form.mdc.TextField('Helper Text', box=True, helper_text='Helper text')

container <= form
        '''
        self.main.brython_code_sample('TextField With Helper Text', code, container)


        code =  '''
form = MDCForm(formfield=ff.clone())

form.mdc.TextField('TextField', value='Default Value')
form.mdc.TextField('TextField Outlined', outlined=True)
form.mdc.TextField('TextField Boxed', box=True)

container <= form
        '''
        self.main.brython_code_sample('TextField Variants', code, container)


        code =  '''
form = MDCForm(formfield=ff.clone())

form.mdc.TextField('Leading Icon', outlined=True, leading_icon='favorite')
form.mdc.TextField('Leading Icon', box=True, leading_icon='event')

form.mdc.TextField('Trailing Icon', outlined=True, trailing_icon='delete')
form.mdc.TextField('Trailing Icon', box=True, trailing_icon='favorite')

container <= form
        '''
        self.main.brython_code_sample('TextField with icons', code, container)


        code =  '''
form = MDCForm(formfield=ff.clone())

form.mdc.TextAreaField('Comments', cols='20', rows='3')
form.mdc.TextAreaField('Comments', fullwidth=True, helper_text='Be nice')

container <= form
        '''
        self.main.brython_code_sample('TextArea', code, container)





        return parent







