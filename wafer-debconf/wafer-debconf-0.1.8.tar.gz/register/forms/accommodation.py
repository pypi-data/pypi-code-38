from django import forms
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, HTML

from invoices.prices import ACCOMM_INVOICE_INFO
from register.dates import night_choices
from register.fields import NightSelectionField
from bursary.models import Bursary


class AccommodationForm(forms.Form):
    accomm = forms.BooleanField(
        label='I need conference-organised accommodation',
        widget=forms.Select(choices=(
            (False, 'No, I will find my own accommodation'),
            (True, 'Yes, I need accommodation'),
        )),
        required=False,
    )
    nights = forms.MultipleChoiceField(
        label="I'm requesting accommodation for these nights:",
        help_text='The "night of" is the date of the day before a night. '
                  'So accommodation on the night of 6 Aug ends on the '
                  'morning of the 7th.',
        choices=night_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    requirements = forms.CharField(
        label='Do you have any particular accommodation requirements?',
        help_text='Anything that you want us to consider for room attribution '
                  'should be listed here (ex. "I want to be with Joe Hill", '
                  '"I snore", "I go to bed early", "I need wheelchair access")',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    family_usernames = forms.CharField(
        label='Usernames of my family members, '
              'who have registered separately',
        help_text="One per line. This isn't validated.",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        attendee = kwargs.pop('attendee')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        try:
            self.bursary = attendee.user.bursary
        except Bursary.DoesNotExist:
            self.bursary = Bursary()

        if settings.DEBCONF_PAID_ACCOMMODATION:
            accomm_availability = HTML(
                '<p>The cost is {} USD/night for attendees who do not '
                'receive a bursary.</p>'.format(
                    ACCOMM_INVOICE_INFO['unit_price']))
        else:
            accomm_availability = HTML(
                '<p>Conference-organised accommodation is only available to '
                'attendees who receive an accommodation bursary. If you are '
                'paying for your own accommodation, see our '
                '<a href="/about/accommodation">list of nearby options</a>.')

        if (settings.DEBCONF_PAID_ACCOMMODATION
                or self.bursary.request_accommodation):
            self.helper.layout = Layout(
                accomm_availability,
                Field('accomm', id='accomm'),
                Fieldset(
                    'Accommodation Details',
                    NightSelectionField('nights'),
                    'requirements',
                    Field('family_usernames'),
                    css_id='accomm-details',
                )
            )
        else:
            self.helper.layout = Layout(accomm_availability)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('accomm'):
            if self.bursary.request_accommodation:
                self.add_error('accomm',
                    'Accommodation bursary was requested, but no accommodation '
                    'selected.')
            return cleaned_data

        if (not settings.DEBCONF_PAID_ACCOMMODATION and
                not self.bursary.request_accommodation):
            self.add_error(
                'accomm',
                'Accommodation is only available to attendees who receive an '
                'accommodation bursary.')

        if not cleaned_data.get('nights'):
            self.add_error(
                'accomm',
                'Please select the nights you require accommodation for.')

        return cleaned_data
