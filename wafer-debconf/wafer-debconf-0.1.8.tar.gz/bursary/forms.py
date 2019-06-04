import csv

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist, ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Fieldset, Layout, Submit

from bursary.models import Bursary


class BursaryRefereeAddForm(forms.Form):
    csv = forms.CharField(
        label='CSV input',
        help_text='Format: attendee_login,referee1_login,referee2_login',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(BursaryRefereeAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.add_input(Submit('submit', 'Create Referees'))

    def clean(self):
        cleaned_data = super(BursaryRefereeAddForm, self).clean()

        r = csv.reader(cleaned_data['csv'].splitlines())
        lines = {line[0]: set(line[1:]) for line in r}

        usernames = set(lines)
        referee_usernames = set().union(*lines.values())

        bursaries = {}
        missing_users = []

        referees = {}
        missing_referees = []

        for username in usernames:
            try:
                bursary = Bursary.objects.get(user__username=username)
            except Bursary.DoesNotExist:
                missing_users.append(username)
            else:
                bursaries[username] = bursary

        for username in referee_usernames:
            try:
                referee = User.objects.get(username=username)
            except User.DoesNotExist:
                missing_referees.append(username)
            else:
                if referee.has_perm('bursary.change_bursaryreferee'):
                    referees[username] = referee
                else:
                    missing_referees.append(username)

        errors = []

        if missing_users:
            errors.append(
                forms.ValidationError('no bursary request for users %s' %
                                      ', '.join(sorted(missing_users)))
            )

        if missing_referees:
            errors.append(
                forms.ValidationError('users %s are not referees' %
                                      ', '.join(sorted(missing_referees)))
            )

        if errors:
            raise forms.ValidationError(errors)

        cleaned_data['to_add'] = lines
        cleaned_data['bursaries'] = bursaries
        cleaned_data['referees'] = referees

        return cleaned_data


class BursaryMassUpdateForm(forms.Form):
    csv = forms.CharField(
        label='CSV input',
        help_text='add a header line',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(BursaryMassUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.add_input(Submit('submit', 'Update bursary requests'))

    def clean(self):
        cleaned_data = super(BursaryMassUpdateForm, self).clean()

        data = {}
        keys = set()
        r = csv.DictReader(cleaned_data['csv'].splitlines())
        for line in r:
            if 'user.username' not in line:
                raise forms.ValidationError(
                    'CSV data needs a `user.username` key'
                )
            data[line['user.username']] = line
            keys.update(line.keys())

        keys.remove('user.username')
        errors = []
        model_fields = {}
        for field in keys:
            try:
                model_fields[field] = Bursary._meta.get_field(field)
            except FieldDoesNotExist:
                errors.append(forms.ValidationError(
                    'Burary model has no %s field' % field
                ))
        if errors:
            raise forms.ValidationError(errors)

        bursaries = []
        notifies = []
        errors = []
        missing_users = []
        for username, updated_fields in data.items():
            try:
                bursary = Bursary.objects.get(user__username=username)
            except Bursary.DoesNotExist:
                missing_users.append(username)
                continue

            old_statuses = {
                'accommodation': bursary.accommodation_status,
                'food': bursary.food_status,
                'travel': bursary.travel_status,
            }

            for field, value in updated_fields.items():
                if field == 'user.username':
                    continue

                model_field = model_fields[field]
                if not value and model_field.null:
                    value = None

                try:
                    value = model_field.clean(value, bursary)
                except ValidationError as e:
                    errors.append(e)
                else:
                    setattr(bursary, field, value)

            try:
                bursary.full_clean()
            except ValidationError as e:
                errors.append(e)
                continue

            statuses = {
                'accommodation': bursary.accommodation_status,
                'food': bursary.food_status,
                'travel': bursary.travel_status,
            }
            if statuses != old_statuses:
                notifies.append(bursary)
            bursaries.append(bursary)

        if missing_users:
            errors.append(
                forms.ValidationError('no bursary request for users %s' %
                                      ', '.join(sorted(missing_users)))
            )

        if errors:
            raise forms.ValidationError(errors)

        cleaned_data['bursaries'] = bursaries
        cleaned_data['notifies'] = notifies

        return cleaned_data


class BursaryUpdateForm(forms.ModelForm):
    ALREADY_PROCESSED = 'Your reimbursement has already been processed'
    ONLY_DECREASE = ('You can only decrease the requested amount for your '
                     'travel bursrary')

    UPDATE_STATUS_CHOICES = (
        ('pending', 'Leave pending'),
        ('accepted', 'Accept'),
        ('canceled', 'Decline'),
    )

    class Meta:
        model = Bursary
        fields = ('accommodation_status', 'food_status', 'travel_status',
                  'travel_bursary')

    def __init__(self, *args, **kwargs):
        super(BursaryUpdateForm, self).__init__(*args, **kwargs)
        self.fields['accommodation_status'].choices = self.UPDATE_STATUS_CHOICES
        self.fields['accommodation_status'].label = 'Accommodation bursary'
        self.fields['food_status'].choices = self.UPDATE_STATUS_CHOICES
        self.fields['food_status'].label = 'Food bursary'
        self.fields['travel_status'].choices = self.UPDATE_STATUS_CHOICES
        self.fields['travel_status'].label = 'Travel bursary'
        self.fields['travel_bursary'].label = (
            'Final amount of my travel bursary request (in USD)'
        )
        self.fields['travel_bursary'].help_text = (
            'You can decrease the amount to that of your tickets once you '
            'know the final amount, so that more money is available for '
            'further rounds of bursaries. Food and accommodation are taken '
            'into account separately.'
        )

        acceptances = []
        for type_ in ('accommodation', 'food', 'travel'):
            field = '{}_status'.format(type_)
            if getattr(self.instance, field) == 'pending':
                acceptances.append(field)
            else:
                del self.fields[field]

        layout = []

        if acceptances:
            layout.append(
                Div(Fieldset('Accept or decline pending bursaries',
                             *acceptances),
                    css_class='alert alert-success')
            )

        if (self.instance.request_travel
                and self.instance.can_update('travel')
                and not self.instance.reimbursed_amount):
            layout.append(
                Fieldset('My travel bursary', 'travel_bursary')
            )
        else:
            del self.fields['travel_bursary']

        layout.append(ButtonHolder(Submit('submit', 'Update bursary status')))
        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout(*layout)

    def clean(self):
        cleaned_data = super(BursaryUpdateForm, self).clean()

        if (self.instance.request_travel and 'travel_bursary' in self.fields):

            if (self.instance.reimbursed_amount
                and (cleaned_data['travel_bursary']
                     != self.instance.travel_bursary)):
                raise forms.ValidationError(self.ALREADY_PROCESSED)

            if cleaned_data['travel_bursary'] > self.instance.travel_bursary:
                raise forms.ValidationError(self.ONLY_DECREASE)

        return cleaned_data
