from directory_components import forms, fields, widgets


class PrefixIdMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(auto_id='demo-%s', *args, **kwargs)


class TextBoxForm(PrefixIdMixin, forms.Form):
    text_field1 = fields.CharField(
        label='Q1: Simple text field',
        help_text='Some help text'
    )
    url_field = fields.URLField(
        label='Q2: URL field',
        help_text='Some help text'
    )
    email_field = fields.EmailField(
        label='Q3: Email field',
        help_text='Some email field help text',
    )
    choice_field = fields.ChoiceField(
        label='Q4: select field',
        help_text='Some help text',
        choices=[
            ('red', 'Red'),
            ('green', 'Green'),
            ('blue', 'Blue'),
        ]
    )


class CheckboxForm(PrefixIdMixin, forms.Form):
    checkbox1 = fields.BooleanField(
        label='Q1: Label text',
        help_text=(
            'This is some help text. This help text is very long so '
            'you can see how it wraps next to the form elements. Very very '
            'long boring text that doesn\'t say anything. Why are you '
            'reading this?'
        ),
        widget=widgets.CheckboxWithInlineLabel(
            attrs={'id': 'checkbox-one'}
        )
    )
    checkbox2 = fields.BooleanField(
        label='Q2: Label text with no help text',
        widget=widgets.CheckboxWithInlineLabel(
            attrs={'id': 'checkbox-two'}
        )
    )


class MultipleChoiceForm(PrefixIdMixin, forms.Form):
    multiple_choice = fields.MultipleChoiceField(
        label='Q1: Multiple choice checkboxes',
        help_text='This is some help text.',
        widget=widgets.CheckboxSelectInlineLabelMultiple(
            attrs={'id': 'checkbox-multiple'},
            use_nice_ids=True,
        ),
        choices=(
            ('red', 'Red'),
            ('green', 'Green'),
            ('blue', 'Blue'),
        ),
    )


class RadioForm(PrefixIdMixin, forms.Form):
    radio = fields.ChoiceField(
        label='Q1: Radio select',
        label_suffix='',
        help_text='Some help text.',
        widget=widgets.RadioSelect(
            use_nice_ids=True,
            attrs={'id': 'radio-one'}
        ),
        choices=(
            (True, 'Yes'),
            (False, 'No'),
        )
    )
    radio_group = fields.ChoiceField(
        label='Q2: Radio select with option groups',
        label_suffix='',
        help_text='Some help text.',
        widget=widgets.RadioSelect(
            use_nice_ids=True,
            attrs={'id': 'radio-two'}
        ),
        choices=(
            ('Colours',
                (
                    ('red', 'Red'),
                    ('green', 'Green'),
                    ('blue', 'Blue'),
                )),
            ('Numbers',
                (
                    ('4', 'Four'),
                    ('5', 'Five'),
                    ('6', 'Six'),
                )),
        )
    )


class DemoFormErrors(PrefixIdMixin, forms.Form):

    text_field1 = fields.CharField(
        label='Simple text field',
        help_text='Some help text',
        required=True
    )
    checkbox1 = fields.BooleanField(
        label='Label text',
        required=True,
        help_text=(
            'Some help text.'
        ),
        widget=widgets.CheckboxWithInlineLabel(
            attrs={'id': 'checkbox-one'}
        )
    )
    multiple_choice = fields.MultipleChoiceField(
        label='Multiple choice checkboxes',
        required=True,
        help_text='Some help text.',
        widget=widgets.CheckboxSelectInlineLabelMultiple(
            attrs={'id': 'checkbox-multiple'},
            use_nice_ids=True,
        ),
        choices=(
            ('red', 'Red'),
            ('green', 'Green'),
            ('blue', 'Blue'),
        ),
    )

    radio = fields.ChoiceField(
        label='Radio select',
        required=True,
        label_suffix='',
        help_text='Some help text.',
        widget=widgets.RadioSelect(
            use_nice_ids=True,
            attrs={'id': 'radio-one'}
        ),
        choices=(
            (True, 'Yes'),
            (False, 'No'),
        )
    )
