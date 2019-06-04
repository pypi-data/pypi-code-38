from django import forms
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout

from bursary.models import Bursary


BURSARIES_LINK = (
    '<a href="/about/bursaries/" target="blank">DebConf bursary instructions.'
    '</a>')


class BursaryForm(forms.Form):
    request_travel = forms.BooleanField(
        label='I want to apply for a travel bursary',
        required=False,
    )
    request_food = forms.BooleanField(
        label='I want to apply for a food bursary',
        required=False,
    )
    request_accommodation = forms.BooleanField(
        label='I want to apply for an accommodation bursary',
        required=False,
    )
    reason_contribution = forms.CharField(
        label='My contributions to Debian',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text='To help us evaluate your eligibility for a Debian bursary.',
    )
    reason_plans = forms.CharField(
        label='My plans for DebCamp or DebConf',
        help_text='To help us evaluate your eligibility for a Debian bursary.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    reason_diversity = forms.CharField(
        label='My eligibility for a diversity bursary',
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Diversity bursary applications only. Please consult the '
                  '<a href="/about/bursaries/#diversity-bursaries" '
                  'target="blank">diversity bursary instructions</a>.',
        required=False,
    )
    need = forms.ChoiceField(
        label='My level of need',
        choices=(
            ('', 'N/A (not requesting a travel bursary)'),
            ('unable', Bursary.BURSARY_NEEDS['unable']),
            ('sacrifice', Bursary.BURSARY_NEEDS['sacrifice']),
            ('inconvenient', Bursary.BURSARY_NEEDS['inconvenient']),
            ('non-financial', Bursary.BURSARY_NEEDS['non-financial']),
        ),
        required=False,
    )
    travel_bursary = forms.IntegerField(
        label='My travel expense claim (in USD)',
        help_text='Estimated amount required. ' + BURSARIES_LINK,
        min_value=0,
        max_value=10000,
        required=False,
    )
    travel_from = forms.CharField(
        label="I'm travelling from",
        help_text='Knowing where you need to travel from helps us evaluate '
                  'the amount you are claiming.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        readonly_attrs = {}
        if settings.BURSARIES_CLOSED:
            readonly_attrs['readonly'] = 'readonly'

        self.helper.layout = Layout(
            Fieldset(
                'Bursary Requests',
                Field('request_food', id='bursary-request-food'),
                Field('request_accommodation', id='bursary-request-accomm'),
                Field('request_travel', id='bursary-request-travel'),
                css_id='bursary-requests',
            ),
            Fieldset(
                'Bursary Details',
                HTML('<p>This is where you explain your needs, and '
                     'involvement in Debian, that justify a bursary. See the '
                     + BURSARIES_LINK + '.</p>'),
                Field(
                    'reason_contribution', **readonly_attrs),
                Field('reason_plans', **readonly_attrs),
                Field('reason_diversity', **readonly_attrs),
                css_id='bursary-details',
            ),
            Fieldset(
                'Travel Bursary Details',
                'travel_bursary',
                Field('travel_from', **readonly_attrs),
                Field('need', readonly=settings.BURSARIES_CLOSED),
                css_id='travel-details',
            )
        )
        if settings.BURSARIES_CLOSED:
            self.helper.layout.insert(0, HTML(
                '<div class="alert alert-warning">'
                '<strong>Bursaries are closed</strong> '
                'You can reduce or cancel your bursary request. '
                'But no other changes are possible any more.'
                '</div>'
            ))

    def clean_travel_bursary(self):
        travel_bursary = self.cleaned_data.get('travel_bursary')
        if travel_bursary == 0:
            return None
        return travel_bursary

    def clean(self):
        cleaned_data = super().clean()

        request_food = cleaned_data.get('request_food')
        request_accommodation = cleaned_data.get('request_accommodation')
        request_travel = cleaned_data.get('request_travel')
        if request_food or request_accommodation or request_travel:
            if not cleaned_data.get('reason_plans'):
                self.add_error(
                    'reason_plans',
                    'Please share your plans for the conference, when applying '
                    'for a bursary.')

            if (not cleaned_data.get('reason_contribution')
                    and not cleaned_data.get('reason_diversity')):
                for field in ('reason_contribution', 'reason_diversity'):
                    self.add_error(
                        field,
                        'Please describe your contributions and/or the '
                        'diversity of your background, when applying for a '
                        'bursary.')

        if request_travel:
            for field in ('travel_bursary', 'travel_from'):
                if not cleaned_data.get(field):
                    self.add_error(
                        field,
                        'Please share your travel details, when applying for '
                        'a travel bursary.'
                    )
            if not cleaned_data.get('need'):
                self.add_error(
                    'need',
                    'Please share your level of need, when applying for a '
                    'travel bursary.'
                )
        else:
            cleaned_data['travel_bursary'] = None
