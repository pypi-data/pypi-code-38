import itertools

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.fields import MultiValueField
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _

from votebase.core.utils.widgets import Matrix, MatrixMultiple


class MatrixField(MultiValueField):
    empty_row_enabled = True
    unique_answers = False

    default_error_messages = {
        'required_all_rows': _(u'All rows are required.'),
        'unique_answers': _(u'Values have to be unique.'),
    }

    def __init__(self, rows=None, columns=None, required=True, widget=Matrix,
                 label=None, initial=None, help_text=None, unique_answers=False, empty_row_enabled=True, *args, **kwargs):
        self.fields = []
        self.empty_row_enabled = empty_row_enabled
        self.unique_answers = unique_answers
        self.widget = widget(rows=rows, columns=columns)

        self.choice_field = forms.ChoiceField
        if widget == MatrixMultiple:
            self.choice_field = forms.MultipleChoiceField

        for row in rows:
            # self.fields.append(self.choice_field(choices=columns, initial=40))  # TODO: why 40 ???
            self.fields.append(self.choice_field(choices=columns))

        super(MatrixField, self).__init__(self.fields, initial=initial, help_text=help_text, required=required, label=label, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) is 0:
            return u''
        if self.choice_field == forms.ChoiceField:
            return '-'.join(data_list)

        items = []
        for item in data_list:
            items.append('|'.join(item))
        return '-'.join(items)

    def clean(self, value):
        """
        Validates every value in the given list. A value is validated against
        the corresponding Field in self.fields.

        For example, if this MultiValueField was instantiated with
        fields=(DateField(), TimeField()), clean() would call
        DateField.clean(value[0]) and TimeField.clean(value[1]).
        """
        clean_data = []
        errors = ErrorList()

        # EMPTY MATRIX
        if not value or isinstance(value, (list, tuple)):
            if not value or not [v for v in value if
                                 v not in validators.EMPTY_VALUES]:
                if self.required:
                    raise ValidationError(self.error_messages['required'])
                else:
                    return self.compress([])
        else:
            raise ValidationError(self.error_messages['invalid'])

        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None

            # EMPTY ROW
            if self.required and field_value in validators.EMPTY_VALUES:
                if not self.empty_row_enabled:
                    raise ValidationError(self.error_messages['required_all_rows'])

            try:
                clean_data.append(field.clean(field_value))
            except ValidationError, e:
                # Collect all validation errors in a single list, which we'll
                # raise at the end of clean(), rather than raising a single
                # exception for the first error we encounter.
                errors.extend(e.messages)

        # uniqueness
        if self.unique_answers:
            value_groups = [(g[0], len(list(g[1]))) for g in itertools.groupby(sorted(value))]
            for group in value_groups:
                count = group[1]
                if count > 1:
                    raise ValidationError(self.error_messages['unique_answers'])

        if errors:
            raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out
