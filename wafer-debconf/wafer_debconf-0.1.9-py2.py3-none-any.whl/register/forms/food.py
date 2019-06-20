from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout

from bursary.models import Bursary
from invoices.prices import MEAL_PRICES
from register.dates import conference_dinner_meal, meal_choices
from register.models.food import Food
from register.fields import MealSelectionField


def meal_price_string():
    entries = (
        ('breakfast', 'Breakfast {breakfast} USD'),
        ('lunch', 'Lunch {lunch} USD'),
        ('dinner', 'Dinner {dinner} USD'),
    )
    prices = MEAL_PRICES
    s = [e.format(**prices) for k, e in entries if prices[k]]
    return ', '.join(s) + '.'


class FoodForm(forms.Form):
    meals = forms.MultipleChoiceField(
        label='I want to eat catered food for these meals:',
        choices=meal_choices(),
        widget=forms.CheckboxSelectMultiple,
        help_text="If you don't have a food bursary, meal prices are: " + meal_price_string(),
        required=False,
    )
    conference_dinner = forms.BooleanField(
        label='I want to attend the conference dinner',
        help_text="If you don't have a food bursary, the conference dinner "
                  "will cost {conference_dinner} USD.".format(**MEAL_PRICES),
        required=False,
    )
    diet = forms.ChoiceField(
        label='My diet',
        choices=Food.DIETS.items(),
        required=False,
    )
    special_diet = forms.CharField(
        label='Details of my special dietary needs',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        attendee = kwargs.pop('attendee')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        conference_dinner = ()
        if conference_dinner_meal():
            conference_dinner = (Field('conference_dinner'),)
        self.helper.layout = Layout(
            MealSelectionField('meals', id='meals'),
            *conference_dinner,
            Field('diet', id='diet'),
            Field('special_diet', id='special_diet'),
        )

        try:
            self.bursary = attendee.user.bursary
        except Bursary.DoesNotExist:
            self.bursary = Bursary()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.pop('conference_dinner'):
            cleaned_data['meals'].append(conference_dinner_meal())

        if self.bursary.request_food and not cleaned_data.get('meals'):
            self.add_error(
                'meals', 'Food bursary was requested, but no meals selected.')

        if (cleaned_data.get('diet') == 'other' and
                not cleaned_data.get('special_diet')):
            self.add_error('special_diet', 'Required when diet is "other"')
