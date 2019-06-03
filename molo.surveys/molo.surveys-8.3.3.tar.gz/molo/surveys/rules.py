from importlib import import_module
from operator import attrgetter

from django import forms
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.test.client import RequestFactory
from django.utils import six, timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from django.utils.six import text_type
from django.utils.text import slugify
from unidecode import unidecode

from wagtail.core.blocks.stream_block import StreamBlockValidationError
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail_personalisation.rules import AbstractBaseRule, VisitCountRule

from molo.core.models import ArticlePageTags

from .edit_handlers import TagPanel

from molo.surveys import blocks

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

# Filer the Visit Count Page only by articles
VisitCountRule._meta.verbose_name = 'Page Visit Count Rule'


# Add ordering to the base class
AbstractBaseRule.__old_subclasses__ = AbstractBaseRule.__subclasses__


def __ordered_subclasses__(cls):
    subclasses = cls.__old_subclasses__()
    for i, item in enumerate(subclasses):
        if not hasattr(item, 'order'):
            item.order = (i + 1) * 100

    return sorted(subclasses, key=attrgetter('order'))


AbstractBaseRule.__subclasses__ = classmethod(__ordered_subclasses__)


class FieldNameField(models.CharField):
    def value_from_object(self, obj):
        """ Returns the field label for rendering"""
        return obj.get_expected_field().label


class SurveySubmissionDataRule(AbstractBaseRule):
    static = True

    EQUALS = 'eq'
    CONTAINS = 'in'

    OPERATOR_CHOICES = (
        (EQUALS, _('equals')),
        (CONTAINS, _('contains')),
    )

    survey = models.ForeignKey('PersonalisableSurvey',
                               verbose_name=_('survey'),
                               on_delete=models.CASCADE)
    field_name = FieldNameField(
        _('field name'), max_length=255,
        help_text=_('Field\'s label. For possible choices '
                    'please input any text and save, '
                    'so it will be displayed in the '
                    'error messages below the '
                    'field.'))
    expected_response = models.CharField(
        _('expected response'), max_length=255,
        help_text=_('When comparing text values, please input text. Comparison'
                    ' on text is always case-insensitive. Multiple choice '
                    'values must be separated with commas.'))
    operator = models.CharField(
        _('operator'), max_length=3,
        choices=OPERATOR_CHOICES, default=CONTAINS,
        help_text=_('When using the "contains" operator'
                    ', "expected response" can '
                    'contain a small part of user\'s '
                    'response and it will be matched. '
                    '"Exact" would match responses '
                    'that are exactly the same as the '
                    '"expected response".'))

    panels = [
        PageChooserPanel('survey'),
        FieldPanel('field_name'),
        FieldPanel('operator'),
        FieldPanel('expected_response')
    ]

    class Meta:
        verbose_name = _('Survey submission rule')

    @cached_property
    def field_model(self):
        return apps.get_model('surveys', 'PersonalisableSurveyFormField')

    @property
    def survey_submission_model(self):
        from molo.surveys.models import MoloSurveySubmission

        return MoloSurveySubmission

    def get_expected_field(self):
        try:
            return self.survey.get_form().fields[self.field_name]
        except KeyError:
            raise self.field_model.DoesNotExist

    def get_expected_field_python_value(self, raise_exceptions=True):
        try:
            field = self.get_expected_field()
            self.expected_response = self.expected_response.strip()
            python_value = self.expected_response

            if isinstance(field, forms.MultipleChoiceField):
                # Eliminate duplicates, strip whitespaces,
                # eliminate empty values
                python_value = [v for v in {v.strip() for v in
                                            self.expected_response.split(',')}
                                if v]
                self.expected_response = ','.join(python_value)

                return python_value

            if isinstance(field, forms.BooleanField):
                if self.expected_response not in '01':
                    raise ValidationError({
                        'expected_response': [
                            _('Please use "0" or "1" on this field.')
                        ]
                    })
                return self.expected_response == '1'

            return python_value

        except (ValidationError, self.field_model.DoesNotExist):
            if raise_exceptions:
                raise

    def get_survey_submission_of_user(self, user):
        return self.survey_submission_model.objects.get(
            user=user, page_id=self.survey_id)

    def clean(self):
        # Do not call clean() if we have no survey set.
        if not self.survey_id:
            return

        # Make sure field name is in correct format
        self.field_name = str(slugify(text_type(unidecode(self.field_name))))

        # Make sure field name is a valid name
        field_names = [f.clean_name for f in self.survey.get_form_fields()]

        if self.field_name not in field_names:
            field_labels = [f.label for f in self.survey.get_form_fields()]
            raise ValidationError({
                'field_name': [_('You need to choose valid field name out '
                                 'of: "%s".') % '", "'.join(field_labels)]
            })

        # Convert value from the rule into Python value.
        python_value = self.get_expected_field_python_value()

        # Get this particular's field instance from the survey's form
        # so we can do validation on the value.
        try:
            self.get_expected_field().clean(python_value)
        except ValidationError as error:
            raise ValidationError({
                'expected_response': error
            })

    def test_user(self, request, user=None):
        if request:
            # When testing a request they must be logged-in to use this rule
            if not request.user.is_authenticated():
                return False
            user = request.user

        if not user:
            return False

        try:
            survey_submission = self.get_survey_submission_of_user(user)
        except self.survey_submission_model.DoesNotExist:
            # No survey found so return false
            return False
        except self.survey_submission_model.MultipleObjectsReturned:
            # There should not be two survey submissions, but just in case
            # let's return false since we don't want to be guessing what user
            # meant in their response.
            return False

        # Get dict with user's survey submission to a particular question
        user_response = survey_submission.get_data().get(self.field_name)

        if not user_response:
            return False

        python_value = self.get_expected_field_python_value()

        # Compare user's response
        try:
            # Convert lists to sets for easy comparison
            if isinstance(python_value, list) \
                    and isinstance(user_response, list):
                if self.operator == self.CONTAINS:
                    return set(python_value).issubset(user_response)

                if self.operator == self.EQUALS:
                    return set(python_value) == set(user_response)
            if isinstance(python_value, list) \
                    and isinstance(user_response, six.string_types):
                user_response = user_response.split(u', ')
                if self.operator == self.CONTAINS:
                    return set(python_value).issubset(user_response)
                if self.operator == self.EQUALS:
                    return set(python_value) == set(user_response)
            if isinstance(python_value, six.string_types) \
                    and isinstance(user_response, six.string_types):
                if self.operator == self.CONTAINS:
                    return python_value.lower() in user_response.lower()

                return python_value.lower() == user_response.lower()

            return python_value == user_response
        except ValidationError:
            # In case survey has been modified and we cannot obtain Python
            # value, we want to return false.
            return False
        except self.field_model.DoesNotExist:
            # In case field does not longer exist on the survey
            # return false. We cannot compare its value if
            # we do not know its type (hence it needs to be on the survey).
            return False

    def description(self):
        try:
            field_name = self.get_expected_field().label
        except self.field_model.DoesNotExist:
            field_name = self.field_name

        return {
            'title': _('Based on survey submission of users'),
            'value': _('%s - %s  "%s"') % (
                self.survey,
                field_name,
                self.expected_response
            )
        }

    def get_column_header(self):
        try:
            field_name = self.get_expected_field().label
        except self.field_model.DoesNotExist:
            field_name = self.field_name

        return '%s - %s' % (self.survey, field_name)

    def get_user_info_string(self, user):
        try:
            survey_submission = self.get_survey_submission_of_user(user)
        except self.survey_submission_model.DoesNotExist:
            # No survey found so return false
            return "No submission"
        except self.survey_submission_model.MultipleObjectsReturned:
            # There should not be two survey submissions, but just in case
            # let's return false since we don't want to be guessing what user
            # meant in their response.
            return "Too many submissions"

        user_response = survey_submission.get_data().get(self.field_name)
        if not user_response:
            return "Not answered"
        if isinstance(user_response, list):
            user_response = ", ".join(user_response)
        return str(user_response)


class SurveyResponseRule(AbstractBaseRule):
    static = True

    survey = models.ForeignKey('MoloSurveyPage',
                               verbose_name=_('survey'),
                               on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('survey')
    ]

    class Meta:
        verbose_name = _('Survey response rule')

    def test_user(self, request, user=None):
        if request:
            if not request.user.is_authenticated():
                return False
            user = request.user
        if not user:
            return False

        # Django formsets don't honour 'required' fields so check rule is valid
        try:
            submission_class = self.survey.get_submission_class()
        except ObjectDoesNotExist:
            return False

        return submission_class.objects.filter(
            user=user,
            page=self.survey,
        ).exists()

    def description(self):
        return {
            'title': _('Based on responses to surveys.'),
            'value': _('Have responsed to: %s') % (
                self.survey,
            )
        }

    def get_column_header(self):
        return self.survey.title

    def get_user_info_string(self, user):
        submission_class = self.survey.get_submission_class()
        submission = submission_class.objects.filter(
            user=user,
            page=self.survey,
        ).last()
        if not submission:
            return "No submission"
        response_date = submission.created_at
        if timezone.is_naive(response_date):
            response_date = timezone.make_aware(response_date)
        return response_date.strftime("%Y-%m-%d %H:%M")


class GroupMembershipRule(AbstractBaseRule):
    """wagtail-personalisation rule based on user's group membership."""
    static = True

    group = models.ForeignKey('surveys.segmentusergroup')

    panels = [
        FieldPanel('group')
    ]

    class Meta:
        verbose_name = _('Group membership rule')

    def description(self):
        return {
            'title': _('Based on survey group memberships of users'),
            'value': _('Member of: "%s"') % self.group
        }

    def test_user(self, request, user=None):
        if request:
            # Ignore not-logged in users when testing requests
            if not request.user.is_authenticated():
                return False
            user = request.user
        if not user:
            return False

        # Check whether user is part of a group
        return user.segment_groups.filter(id=self.group_id).exists()

    def get_column_header(self):
        return self.group.name

    def get_user_info_string(self, user):
        return str(user.segment_groups.filter(id=self.group_id).exists())


class ArticleTagRule(AbstractBaseRule):
    static = True

    order = 410
    EQUALS = 'eq'
    GREATER_THAN = 'gt'
    LESS_THAN = 'lt'

    OPERATORS = {
        EQUALS: lambda a, b: a == b,
        GREATER_THAN: lambda a, b: a > b,
        LESS_THAN: lambda a, b: a < b,
    }

    OPERATOR_CHOICES = (
        (GREATER_THAN, _('more than')),
        (LESS_THAN, _('less than')),
        (EQUALS, _('equal to')),
    )

    tag = models.ForeignKey(
        'core.Tag',
        on_delete=models.CASCADE,
        help_text=_(
            'The number in the bracket indicates the number of articles '
            'that have the tag.'
        )
    )

    operator = models.CharField(
        _('operator'),
        max_length=3,
        choices=OPERATOR_CHOICES,
        default=GREATER_THAN,
    )
    count = models.PositiveIntegerField()

    # Naive datetimes as we are not storing the datetime based on the users
    # timezone.
    date_from = models.DateTimeField(blank=True, null=True)
    date_to = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_(
            'All times are UTC. Leave both fields blank to search all time.'
        ),
    )

    panels = [
        TagPanel('tag'),
        FieldRowPanel(
            [
                FieldPanel('operator'),
                FieldPanel('count'),
            ]
        ),
        FieldPanel('date_from'),
        FieldPanel('date_to'),
    ]

    class Meta:
        verbose_name = _('Article tag rule')

    def clean(self):
        super(ArticleTagRule, self).clean()
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(
                    {
                        'date_from': [_('Date from must be before date to.')],
                        'date_to': [_('Date from must be before date to.')],
                    }
                )

        if hasattr(self, 'tag'):
            if self.count > ArticlePageTags.objects.filter(
                    tag=self.tag
            ).count():
                raise ValidationError(
                    {
                        'count': [_(
                            'Count can not exceed the number of articles.'
                        )],
                    }
                )

    def test_user(self, request, user=None):
        if user:
            # Create a fake request so we can use the adapter
            request = RequestFactory().get('/')
            request.session = SessionStore()
            request.user = user
        elif not request:
            # Return false if we don't have a user or a request
            return False

        # Django formsets don't honour 'required' fields so check rule is valid
        try:
            self.tag
        except ObjectDoesNotExist:
            return False

        from wagtail_personalisation.adapters import get_segment_adapter
        operator = self.OPERATORS[self.operator]
        adapter = get_segment_adapter(request)
        visit_count = adapter.get_tag_count(
            self.tag,
            self.date_from,
            self.date_to,
        )

        return operator(visit_count, self.count)

    def description(self):
        return {
            'title': _('These users visited {}').format(
                self.tag
            ),
            'value': _('{} {} times').format(
                self.get_operator_display(),
                self.count
            ),
        }

    def get_column_header(self):
        return 'Article Tag = %s' % self.tag.title

    def get_user_info_string(self, user):
        # Create a fake request so we can use the adapter
        request = RequestFactory().get('/')
        request.session = SessionStore()
        request.user = user

        from wagtail_personalisation.adapters import get_segment_adapter
        adapter = get_segment_adapter(request)
        visit_count = adapter.get_tag_count(
            self.tag,
            self.date_from,
            self.date_to,
        )
        return str(visit_count)


class CombinationRule(AbstractBaseRule):
    body = blocks.StreamField([
        ('Rule', blocks.RuleSelectBlock()),
        ('Operator', blocks.AndOrBlock()),
        ('NestedLogic', blocks.LogicBlock())
    ])

    panels = [
        StreamFieldPanel('body'),
    ]

    def description(self):
        return {
            'title': _(
                'Based on whether they satisfy a '
                'particular combination of rules'),
        }

    def clean(self):
        super(CombinationRule, self).clean()
        if len(self.body.stream_data) > 0:
            if isinstance(self.body.stream_data[0], dict):
                newData = [block['type'] for block in self.body.stream_data]
            elif isinstance(self.body.stream_data[0], tuple):
                newData = [block[0] for block in self.body.stream_data]

            if (len(newData) - 1) % 2 != 0:
                raise StreamBlockValidationError(non_block_errors=[_(
                    'Rule Combination must follow the <Rule/NestedLogic>'
                    '<Operator> <Rule/NestedLogic> pattern.')])

            if len(newData) == 1:
                if newData[0] == 'NestedLogic':
                    pass
                else:
                    raise StreamBlockValidationError(non_block_errors=[_(
                        'Rule Combination must follow the <Rule/NestedLogic> '
                        '<Operator> <Rule/NestedLogic> pattern.')])
            else:
                iterations = (len(newData) - 1) / 2
                for i in range(iterations):
                    first_rule_index = i * 2
                    operator_index = (i * 2) + 1
                    second_rule_index = (i * 2) + 2

                    if not (
                        (newData[first_rule_index] == 'Rule' or
                         newData[first_rule_index] == 'NestedLogic') and
                        (newData[operator_index] == 'Operator') and
                        (newData[second_rule_index] == 'Rule' or
                            newData[second_rule_index] == 'NestedLogic')):
                        raise StreamBlockValidationError(non_block_errors=[_(
                            'Rule Combination must follow the '
                            '<Rule/NestedLogic> '
                            '<Operator> <Rule/NestedLogic> pattern.')])
        else:
            raise StreamBlockValidationError(non_block_errors=[_(
                'Rule Combination must follow the <Rule/NestedLogic>'
                '<Operator> <Rule/NestedLogic> pattern.')])

    class Meta:
        verbose_name = _('Rule Combination')
