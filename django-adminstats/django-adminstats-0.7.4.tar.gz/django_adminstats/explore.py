import collections
import copy
import datetime
import weakref

import django
import django.db.models as db_models
import django.db.models.functions as db_functions
import django.utils.timezone as djtz
from dateutil.relativedelta import relativedelta
from django.contrib.admin import FieldListFilter, SimpleListFilter, \
    DateFieldListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.http import HttpRequest, QueryDict
from django.utils.formats import date_format


def to_default_timezone(dt):
    if djtz.is_aware(dt):
        return dt.astimezone(djtz.get_current_timezone())
    return dt


def dt_trunc_year(dt):
    return to_default_timezone(dt).replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def dt_trunc_month(dt):
    return to_default_timezone(dt).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)


def dt_trunc_day(dt):
    return to_default_timezone(dt).replace(
        hour=0, minute=0, second=0, microsecond=0)


def dt_trunc_hour(dt):
    return to_default_timezone(dt).replace(
        minute=0, second=0, microsecond=0)


def dt_trunc_minutes(dt):
    return to_default_timezone(dt).replace(second=0, microsecond=0)


# Scales used for zooming in on scalar axes
SCALES = {
    datetime.datetime: (
        (relativedelta(years=1), dt_trunc_year),
        (relativedelta(months=1), dt_trunc_month),
        (relativedelta(days=1), dt_trunc_day),
        (relativedelta(hours=1), dt_trunc_hour),
        (relativedelta(minutes=1), dt_trunc_minutes),
    ),

    datetime.date: (
        (relativedelta(years=1),
         lambda dt: dt.replace(month=1, day=1)),
        (relativedelta(months=1), lambda dt: dt.replace(month=1)),
        (relativedelta(days=1), lambda dt: dt),
    ),
}


def date_value(dt):
    """
    Returns a string representation of a date for C3

    This is like .isoformat, only we strip the timezone info and
    output the time portion (as 00:00) for dates to make it easy
    for C3 to parse.
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


class ChartTable(collections.OrderedDict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = []
        self.step = None
        self.periods = []

    def type(self):

        return 'area' if len(self.headers) > 1 else 'pie'

    def build_headers(self, periods, step, parent_query_dict, x_params):
        self.step = step
        self.periods = periods
        if not periods:
            self.headers = [
                ChartHeader(None, step, parent_query_dict, x_params)]
        else:
            self.headers = [
                ChartHeader(start, step, parent_query_dict, x_params)
                for (start, end) in periods]

    def display_items(self):
        for key, row in self.items():
            yield '—'.join(key), row

    def top_display(self):
        if self.periods:
            func = {
                relativedelta(years=1): lambda s: '',
                relativedelta(months=1): lambda s: s.year,
                relativedelta(days=1): lambda s: date_format(s, 'F'),
                relativedelta(hours=1): lambda s: date_format(s, 'M d'),
                relativedelta(minutes=1): lambda d: date_format(d, 'P'),
            }.get(self.step, str)
            return func(self.periods[0][0])
        else:
            return ''


class ChartRow(dict):
    def __init__(self, table, query_dict=None, **kwargs):
        super().__init__(**kwargs)
        self.table = weakref.ref(table)
        self.query_dict = query_dict

    def by_headers(self):
        for cell in self.table().headers:
            yield self[cell.index]

    def has_url(self):
        return self.query_dict is not None

    def url(self):
        return '?' + self.query_dict.urlencode()


class ChartHeader:
    def __init__(self, start, step, parent_query_dict, x_params):
        self.index = start
        self.step = step
        self.parent_query_dict = parent_query_dict
        self.x_params = x_params

    def value(self):
        if self.index is None:
            return ''
        func = {
            relativedelta(years=1): date_value,
            relativedelta(months=1): date_value,
            relativedelta(days=1): date_value,
            relativedelta(hours=1): date_value,
            relativedelta(minutes=1): date_value,
        }.get(self.step, str)
        return func(self.index)

    def display(self):
        if self.index is None:
            return ''
        func = {
            relativedelta(years=1): lambda d: d.year,
            relativedelta(months=1): lambda d: date_format(d, 'F'),
            relativedelta(days=1): lambda d: d.day,
            relativedelta(hours=1): lambda d: date_format(d, 'P'),
            relativedelta(minutes=1): lambda d: date_format(d, 'P'),
        }.get(self.step, str)
        return func(self.index)

    def has_url(self):
        return True

    def alter_query_dict(self, query_dict):
        if self.index is not None and self.step is not None:
            qd = copy.copy(query_dict)
            low_param, high_param = self.x_params
            qd[low_param] = self.index
            qd[high_param] = self.index + self.step
            return qd
        else:
            return query_dict

    def url(self):
        if self.step is None:
            return ''
        return '?' + self.alter_query_dict(self.parent_query_dict).urlencode()


class ChartCell:
    def __init__(self, idx, value, row):
        self.value = value
        self.row = weakref.ref(row)
        self.idx = idx

    def has_url(self):
        return self.row().query_dict is not None

    def url(self):
        qd = self.row().query_dict
        qd = self.row().table().headers[self.idx].alter_query_dict(qd)
        if qd is None:
            return ''
        else:
            return '?' + qd.urlencode()


class Choice:
    def __init__(self, selected, query_dict, label):
        self.selected = selected
        self.query_dict = query_dict
        self.label = label


class Filter:
    def __init__(self, list_filter,
                 changelist, un_grouped_query_dict, group_filters, x_field):
        self.list_filter = list_filter
        self.choices = []
        self.query_dict = None
        self.is_filtered = False
        self.default_label = ''
        self.x_field = x_field
        choices = self.list_filter.choices(changelist)
        try:
            first_choice = next(choices)
            self.default_label = first_choice['display']
            if not first_choice['selected']:
                params = QueryDict(first_choice['query_string'].lstrip('?'))
                self.query_dict = params
                self.is_filtered = True

        except StopIteration:
            pass
        for choice in choices:
            params = QueryDict(choice['query_string'].lstrip('?'))
            self.choices.append(Choice(
                choice['selected'], params, choice['display']))

        if isinstance(list_filter, FieldListFilter):
            self.id = list_filter.field_path
        else:
            assert isinstance(list_filter, SimpleListFilter)
            self.id = list_filter.parameter_name

        if self.query_dict is None:
            self.query_dict = un_grouped_query_dict
        self.group = group_filters
        self.in_group = self.id in self.group

    @property
    def is_axis(self):
        return self.id == self.x_field

    @property
    def is_scalar(self):
        return isinstance(self.list_filter, DateFieldListFilter)

    @property
    def url(self):
        return '?' + self.get_querystring().urlencode()

    @property
    def axis_url(self):
        qd = copy.copy(self.query_dict)
        qd.setlist('_group', self.group)
        if self.is_axis:
            qd.pop('_x', None)
        else:
            qd['_x'] = self.id
        return '?' + qd.urlencode()

    @property
    def title(self):
        return self.list_filter.title

    def get_querystring(self):
        query = copy.copy(self.query_dict)
        group = copy.copy(self.group)
        if self.id in group:
            group.remove(self.id)
        else:
            group.append(self.id)
        query.setlist('_group', group)
        return query

    def value(self):
        for choice in self.choices:
            if choice.selected:
                return str(choice.label)
        return ''

    def new_list_filter(self, request, query_dict, model_admin):
        model_cls = model_admin.model
        args = (request, query_dict, model_cls, model_admin)
        cls = self.list_filter.__class__
        if issubclass(cls, FieldListFilter):
            args = (self.list_filter.field, request,
                    query_dict.dict(), model_cls, model_admin,
                    self.list_filter.field_path)
        return cls(*args)

    def scalar_fields(self):
        return self.id + '__gte', self.id + '__lt'

    def get_scale(self, query_dict, queryset):
        start, end = self._parse_scalar_params(query_dict)
        if start is None or end is None:
            # we need to populate these values, so we do a prequery
            min_max = queryset.aggregate(
                min=db_models.Min(self.id),
                max=db_models.Max(self.id))
            if start is None:
                start = min_max['min']
            if end is None:
                end = min_max['max']
        if start is None or end is None:
            # we have an empty table, not much we can guess
            # just return something
            return 0, 0, 1

        # just make sure we're in the right order here:
        if start > end:
            start, end = end, start

        t_start = type(start)
        if t_start not in SCALES:
            raise RuntimeError(
                'Scale type ({}) not supported'.format(type(start)))
        scale = SCALES[t_start]

        for step, start_func in scale:
            if start + step < end:
                return start_func(start), end, step
        # if nothing matches, just use the last
        step, start_func = scale[-1]
        return start_func(start), end, step

    def _parse_scalar_params(self, query_dict):
        start = None
        end = None
        start_field, end_field = self.scalar_fields()
        field = self.list_filter.field
        if start_field in query_dict:
            try:
                start = field.to_python(query_dict[start_field])
            except ValidationError:
                pass
        if end_field in query_dict:
            try:
                end = field.to_python(query_dict[end_field])
            except ValidationError:
                pass
        return start, end


def mock_request(request, ignored_keys):
    result = HttpRequest()
    for key, value in request.GET.items():
        if key not in ignored_keys:
            result.GET[key] = value
    for attr in ('path', 'path_info', 'method', 'resolver_match',
                 '_post_parse_error', 'content_type', 'content_params',
                 'user', 'META'):
        if hasattr(request, attr):
            setattr(result, attr, getattr(request, attr))
    return result


def get_queryset(changelist, request):
    # First, we collect all the declared list filters.
    (changelist.filter_specs, changelist.has_filters, remaining_lookup_params,
     filters_use_distinct) = changelist.get_filters(request)

    # Then, we let every list filter modify the queryset to its liking.
    qs = changelist.root_queryset
    for filter_spec in changelist.filter_specs:
        new_qs = filter_spec.queryset(request, qs)
        if new_qs is not None:
            qs = new_qs
    # note: this code is copied from django
    try:
        qs = qs.filter(**remaining_lookup_params)
    except (django.SuspiciousOperation, django.ImproperlyConfigured):
        raise
    except Exception as e:
        raise IncorrectLookupParameters(e)

    if not qs.query.select_related:
        qs = changelist.apply_select_related(qs)

    # Note: we don't want to do ordering, because we want distinct values

    # Apply search results
    qs, search_use_distinct = changelist.model_admin.get_search_results(
        request, qs, changelist.query)

    # Remove duplicates from results, if necessary
    if filters_use_distinct | search_use_distinct:
        return qs.distinct()
    else:
        return qs


def generic_duple_range(start, end, step):
    """
    Sort of like range(), but it supports anything where you can check
    if start < end and do start += step.

    Also returns each value + the next value
    """
    while start < end:
        next = start + step
        yield start, next
        start = next


def get_group_annotations(group_filters, filters, model_admin, queryset):
    annotations = {}
    columns = {}
    if group_filters:
        # do regular grouping first
        for idx, path in enumerate(group_filters):
            if path in filters:
                filter_spec = filters[path]
                default_label = filter_spec.default_label
                case_args = []
                row_params = {}
                for choice in filters[path].choices:
                    qd = choice.query_dict
                    if qd:
                        new_list_filter = filter_spec.new_list_filter(
                            mock_request, qd, model_admin)
                        new_qs = new_list_filter.queryset(
                            mock_request, queryset)
                        case_args.append(
                            db_models.When(
                                id__in=new_qs.values('id'),
                                then=db_models.Value(str(choice.label))))
                        row_params[str(choice.label)] = qd
                case = db_models.Case(
                    *case_args, default=db_models.Value(str(default_label)),
                    output_field=db_models.CharField(blank=True))
                arg = 'adminstats_group{}'.format(idx)
                annotations[arg] = case
                columns[arg] = row_params
    return annotations, columns


class XQueryData:

    def __init__(self):
        self.step = None
        self.params = None, None
        self.periods = []
        self.annotations = collections.OrderedDict()

    def set_periods(self, start, end, step, low_param, high_param):
        self.step = step
        self.periods = list(generic_duple_range(start, end, step))
        self.params = low_param, high_param


def get_x_annotations(x_field, filters, query_dict, queryset):
    result = XQueryData()
    if x_field is not None:
        if x_field in filters and filters[x_field].is_scalar:

            filter_spec = filters[x_field]
            x_start_field, x_end_field = filter_spec.scalar_fields()
            start, end, step = filter_spec.get_scale(query_dict, queryset)
            result.set_periods(start, end, step, x_start_field, x_end_field)

            for idx, (p_start, p_end) in enumerate(result.periods):
                q = db_models.Q(**{x_start_field: p_start,
                                   x_end_field: p_end})
                result.annotations[
                    'adminstats_x{}'.format(idx)] = db_models.Count(
                    'id', filter=q)

    if not result.periods:
        result.annotations['adminstats_x'] = db_functions.Coalesce(
            db_models.Count('id'), 0)
    return result


def build_table(queryset, columns, xqd, row_query_dict, full_query_dict):
    table = ChartTable()
    for data in queryset:
        row_key = tuple(data[k] for k in data.keys()
                        if k.startswith('adminstats_group'))
        if row_key:
            query_dict = copy.copy(row_query_dict)
            for key, value in columns.items():
                result_value = data[key]
                if result_value in value:
                    query_dict.update(value[result_value])
        else:
            query_dict = row_query_dict

        row = ChartRow(table, query_dict)

        if xqd.periods:
            for idx, x_key in enumerate(xqd.annotations.keys()):
                row[xqd.periods[idx][0]] = ChartCell(
                    idx, data[x_key], row)
        else:
            row[None] = ChartCell(0, data.get('adminstats_x', 0), row)
        table[row_key] = row
    table.build_headers(xqd.periods, xqd.step, full_query_dict, xqd.params)
    return table
