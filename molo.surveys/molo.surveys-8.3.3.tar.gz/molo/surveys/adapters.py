from collections import defaultdict
import datetime

from wagtail_personalisation.adapters import SessionSegmentsAdapter
from django.apps import apps
from django.db.models import Count
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from molo.core.models import ArticlePage, ArticlePageTags
from .rules import CombinationRule


def get_rule(rule_hash, data_structure):
    rule_type, order = rule_hash.split('_')
    return data_structure[rule_type][int(order)]


def index_rules_by_type(rules):
    '''
    Indexes a list of rules by type name,
    while maintaining rule order for each rule type

    Sample Input:
    [
        <TimeRule: Time Rule>,
        <TimeRule: Time Rule>,
        <UserIsLoggedInRule: Logged in Rule>
    ]

    Sample Output:
    {
        'TimeRule': [ <TimeRule: Time Rule>, <TimeRule: Time Rule> ],
        'UserIsLoggedInRule': [ <UserIsLoggedInRule: Logged in Rule> ]
    }
    '''
    indexed_rules = {}
    for rule in rules:
        type_name = type(rule).__name__
        if type_name in indexed_rules:
            indexed_rules[type_name].append(rule)
        else:
            indexed_rules[type_name] = [rule]
    return indexed_rules


def transform_into_boolean_list(stream_data, indexed_rules, request):
    '''
    Converts a stream field of strings and rules into a list
    of booleans (evaluated rule evaluations), strings and nested lists

    Sample Input:
    [
        {u'type': u'Rule', u'value': u'UserIsLoggedInRule_0'},
        {u'type': u'Operator', u'value': u'and'},
        {u'type': u'NestedLogic', u'value': {
            u'operator': u'or',
            u'rule_1': u'TimeRule_0',
            u'rule_2': u'TimeRule_1'}
        }
    ]

    Output:
    [True, 'and', [False, 'or', True]]
    '''
    return_value = []
    for block in stream_data:
        if block['type'] == 'Rule':
            rule = get_rule(block['value'], indexed_rules)
            return_value.append(rule.test_user(request))
        elif block['type'] == 'Operator':
            return_value.append(block['value'])
        elif block['type'] == 'NestedLogic':
            values = block['value']
            rule_1 = get_rule(values['rule_1'], indexed_rules)
            rule_2 = get_rule(values['rule_2'], indexed_rules)
            return_value.append([
                rule_1.test_user(request),
                values['operator'],
                rule_2.test_user(request)
            ])

    return return_value


def evaluate(list_):
    '''
    Function that evaluates a list of boolean values
    seperated by strings that represent boolean values
    i.e. 'and', 'or'

    Sample Input:

    '''
    if len(list_) == 1 and isinstance(list_[0], list):
        return evaluate(list_[0])
    elif len(list_) == 3:
        operator = list_[1]
        first = list_[0] if isinstance(list_[0], bool) else evaluate(list_[0])
        second = list_[2] if isinstance(list_[2], bool) else evaluate(list_[2])
        if operator == 'or':
            return first or second
        else:
            return first and second
    else:
        return evaluate([evaluate(list_[:3])] + list_[3:])


class SurveysSegmentsAdapter(SessionSegmentsAdapter):
    def add_page_visit(self, page):
        super(SurveysSegmentsAdapter, self).add_page_visit(page)
        tag_visits = self.request.session.setdefault(
            'tag_count',
            defaultdict(dict),
        )
        if isinstance(page.specific, ArticlePage):
            # Set the datetime based on UTC
            visit_time = datetime.datetime.now(timezone.utc).isoformat()
            for nav_tag in page.nav_tags.all():
                tag_visits.setdefault(str(nav_tag.tag.id), dict())
                tag_visits[str(nav_tag.tag.id)][page.path] = visit_time

    def get_tag_count(self, tag, date_from=None, date_to=None):
        """Return the number of visits on the given page"""
        if not date_from:
            date_from = timezone.make_aware(
                datetime.datetime.min,
                timezone.utc,
            )
        if not date_to:
            date_to = timezone.make_aware(
                datetime.datetime.max,
                timezone.utc,
            )

        tag_visits = self.request.session.setdefault(
            'tag_count',
            defaultdict(dict),
        )

        visits = tag_visits.get(str(tag.id), dict())
        valid_visits = [visit for visit in visits.values()
                        if date_from <= parse_datetime(visit) <= date_to]
        return len(valid_visits)

    def _test_rules(self, rules, request, match_any=False):
        if not rules:
            return False

        bool_rules = False
        bool_rules = [rule for rule in rules
                      if isinstance(rule, CombinationRule)]

        if not bool_rules:
            if match_any:
                return any(rule.test_user(request) for rule in rules)
            return all(rule.test_user(request) for rule in rules)
        else:
            # evaluates only 1 rule
            rule_combo = bool_rules[0]

            simple_rules = [rule for rule in rules
                            if not isinstance(rule, CombinationRule)]

            rules_indexed_by_type_name = index_rules_by_type(simple_rules)

            nested_list_of_booleans = transform_into_boolean_list(
                rule_combo.body.stream_data,
                rules_indexed_by_type_name,
                request
            )

            return evaluate(nested_list_of_booleans)


class PersistentSurveysSegmentsAdapter(SurveysSegmentsAdapter):
    '''
    Implements a segments adapter which includes support for persistence.

    Does not support requests without a user property or anonymous users to
    reduce unnecessary database writes and reads.

    self.request.user comes from Django's AuthenticationMiddleware - we defend
    against the middleware not being present or not working by returning early.

    Todo: currently only partially implemented so that we can start collecting
          data as quickly as possible.
    '''

    def add_page_visit(self, page):
        '''
        Persist pageview data in a model.
        '''
        super(PersistentSurveysSegmentsAdapter, self).add_page_visit(page)

        if not hasattr(self.request, 'user'):
            return

        if isinstance(page.specific, ArticlePage):
            MoloSurveyPageView = apps.get_model('surveys.MoloSurveyPageView')
            user = self.request.user

            if user.is_authenticated():
                pageview = MoloSurveyPageView.objects.create(
                    user=user,
                    page=page.specific,
                )
                pageview.save()

    def get_tag_count(self, tag, date_from=None, date_to=None):
        '''
        Fetch the number of times a user has viewed a given tag
        within the date period, grouped uniquely by article.
        '''
        if not hasattr(self.request, 'user'):
            return 0

        user = self.request.user

        if user.is_anonymous():
            return 0

        MoloSurveyPageView = apps.get_model('surveys.MoloSurveyPageView')

        page_ids = ArticlePageTags.objects.filter(tag=tag).values('page_id')

        query_parameters = {
            'user': user,
            'page_id__in': page_ids,
        }

        if date_from:
            query_parameters['visited_at__gte'] = date_from

        if date_to:
            query_parameters['visited_at__lte'] = date_to

        pageviews = MoloSurveyPageView.objects.filter(**query_parameters)
        unique_pages = pageviews.values('page_id').annotate(Count('page_id'))

        return unique_pages.count()

    def get_visit_count(self, page=None):
        if not hasattr(self.request, 'user'):
            return 0

        user = self.request.user

        if user.is_anonymous():
            return 0

        if page is None:
            return 0

        MoloSurveyPageView = apps.get_model('surveys.MoloSurveyPageView')

        query_parameters = {
            'user': user,
            'page_id': page.id,
        }

        return MoloSurveyPageView.objects.filter(**query_parameters).count()
