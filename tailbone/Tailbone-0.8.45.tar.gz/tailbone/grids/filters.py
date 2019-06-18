# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Grid Filters
"""

from __future__ import unicode_literals, absolute_import

import re
import datetime
import logging

import six
import sqlalchemy as sa

from rattail.gpc import GPC
from rattail.util import OrderedDict
from rattail.core import UNSPECIFIED
from rattail.time import localtime, make_utc
from rattail.util import prettify

import colander
from webhelpers2.html import HTML, tags

from tailbone import forms


log = logging.getLogger(__name__)


class FilterValueRenderer(object):
    """
    Base class for all filter renderers.
    """
    data_type = 'string'

    @property
    def name(self):
        return self.filter.key

    def render(self, value=None, **kwargs):
        """
        Render the filter input element(s) as HTML.  Default implementation
        uses a simple text input.
        """
        return tags.text(self.name, value=value, **kwargs)


class DefaultValueRenderer(FilterValueRenderer):
    """
    Default / fallback renderer.
    """


class NumericValueRenderer(FilterValueRenderer):
    """
    Input renderer for numeric values.
    """
    # TODO
    # data_type = 'number'

    def render(self, value=None, **kwargs):
        kwargs.setdefault('step', '0.001')
        return tags.text(self.name, value=value, type='number', **kwargs)


class DateValueRenderer(FilterValueRenderer):
    """
    Input renderer for date values.
    """
    data_type = 'date'

    def render(self, value=None, **kwargs):
        kwargs['data-datepicker'] = 'true'
        return tags.text(self.name, value=value, **kwargs)


class ChoiceValueRenderer(FilterValueRenderer):
    """
    Renders value input as a dropdown/selectmenu of available choices.
    """
    data_type = 'choice'

    def __init__(self, options):
        self.options = options

    def render(self, value=None, **kwargs):
        return tags.select(self.name, [value], self.options, **kwargs)


class EnumValueRenderer(ChoiceValueRenderer):
    """
    Renders value input as a dropdown/selectmenu of available choices.
    """

    def __init__(self, enum):
        if isinstance(enum, OrderedDict):
            sorted_keys = list(enum.keys())
        else:
            sorted_keys = sorted(enum, key=lambda k: enum[k].lower())
        self.options = [tags.Option(enum[k], six.text_type(k)) for k in sorted_keys]


class GridFilter(object):
    """
    Represents a filter available to a grid.  This is used to construct the
    'filters' section when rendering the index page template.
    """
    verb_labels = {
        'is_any':               "is any",
        'equal':                "equal to",
        'not_equal':            "not equal to",
        'greater_than':         "greater than",
        'greater_equal':        "greater than or equal to",
        'less_than':            "less than",
        'less_equal':           "less than or equal to",
        'is_null':              "is null",
        'is_not_null':          "is not null",
        'is_true':              "is true",
        'is_false':             "is false",
        'contains':             "contains",
        'does_not_contain':     "does not contain",
        'is_me':                "is me",
        'is_not_me':            "is not me",
    }

    valueless_verbs = ['is_any', 'is_null', 'is_not_null', 'is_true', 'is_false',
                       'is_me', 'is_not_me']

    value_renderer_factory = DefaultValueRenderer
    data_type = 'string'        # default, but will be set from value renderer

    def __init__(self, key, label=None, verbs=None, value_enum=None, value_renderer=None,
                 default_active=False, default_verb=None, default_value=None,
                 encode_values=False, value_encoding='utf-8', **kwargs):
        self.key = key
        self.label = label or prettify(key)
        self.verbs = verbs or self.get_default_verbs()
        if value_renderer:
            self.set_value_renderer(value_renderer)
        elif value_enum:
            self.set_value_renderer(EnumValueRenderer(value_enum))
        else:
            self.set_value_renderer(self.value_renderer_factory)
        self.default_active = default_active
        self.default_verb = default_verb
        self.default_value = default_value

        self.encode_values = encode_values
        self.value_encoding = value_encoding

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.key))

    def get_default_verbs(self):
        """
        Returns the set of verbs which will be used by default, i.e.  unless
        overridden by constructor args etc.
        """
        verbs = getattr(self, 'default_verbs', None)
        if verbs:
            if callable(verbs):
                return verbs()
            return verbs
        return ['equal', 'not_equal', 'is_null', 'is_not_null', 'is_any']

    def set_value_renderer(self, renderer):
        """
        Set the value renderer for the filter, post-construction.
        """
        if not isinstance(renderer, FilterValueRenderer):
            renderer = renderer()
        renderer.filter = self
        self.value_renderer = renderer
        self.data_type = renderer.data_type

    def filter(self, data, verb=None, value=UNSPECIFIED):
        """
        Filter the given data set according to a verb/value pair.  If no verb
        and/or value is specified by the caller, the filter will use its own
        current verb/value by default.
        """
        verb = verb or self.verb
        value = self.get_value(value)
        filtr = getattr(self, 'filter_{0}'.format(verb), None)
        if not filtr:
            raise ValueError("Unknown filter verb: {0}".format(repr(verb)))
        return filtr(data, value)

    def get_value(self, value=UNSPECIFIED):
        return value if value is not UNSPECIFIED else self.value

    def encode_value(self, value):
        if self.encode_values and isinstance(value, six.string_types):
            return value.encode('utf-8')
        return value

    def filter_is_any(self, data, value):
        """
        Special no-op filter which does no actual filtering.  Useful in some
        cases to add an "ineffective" option to the verb list for a given grid
        filter.
        """
        return data

    def render_value(self, value=UNSPECIFIED, **kwargs):
        """
        Render the HTML needed to expose the filter's value for user input.
        """
        if value is UNSPECIFIED:
            value = self.value
        kwargs['filtr'] = self
        return self.value_renderer.render(value=value, **kwargs)


class MobileFilter(GridFilter):
    """
    Base class for mobile grid filters.
    """
    default_verbs = ['equal']

    def __init__(self, key, **kwargs):
        kwargs.setdefault('default_active', True)
        kwargs.setdefault('default_verb', 'equal')
        super(MobileFilter, self).__init__(key, **kwargs)


class AlchemyGridFilter(GridFilter):
    """
    Base class for SQLAlchemy grid filters.
    """

    def __init__(self, *args, **kwargs):
        self.column = kwargs.pop('column')
        super(AlchemyGridFilter, self).__init__(*args, **kwargs)

    def filter_equal(self, query, value):
        """
        Filter data with an equal ('=') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column == self.encode_value(value))

    def filter_not_equal(self, query, value):
        """
        Filter data with a not eqaul ('!=') query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not equal' to something else, we must also
        # include things which are nothing at all, in our result set.
        return query.filter(sa.or_(
            self.column == None,
            self.column != self.encode_value(value),
        ))

    def filter_is_null(self, query, value):
        """
        Filter data with an 'IS NULL' query.  Note that this filter does not
        use the value for anything.
        """
        return query.filter(self.column == None)

    def filter_is_not_null(self, query, value):
        """
        Filter data with an 'IS NOT NULL' query.  Note that this filter does
        not use the value for anything.
        """
        return query.filter(self.column != None)

    def filter_greater_than(self, query, value):
        """
        Filter data with a greater than ('>') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column > self.encode_value(value))

    def filter_greater_equal(self, query, value):
        """
        Filter data with a greater than or equal ('>=') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column >= self.encode_value(value))

    def filter_less_than(self, query, value):
        """
        Filter data with a less than ('<') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column < self.encode_value(value))

    def filter_less_equal(self, query, value):
        """
        Filter data with a less than or equal ('<=') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column <= self.encode_value(value))


class AlchemyStringFilter(AlchemyGridFilter):
    """
    String filter for SQLAlchemy.
    """

    def default_verbs(self):
        """
        Expose contains / does-not-contain verbs in addition to core.
        """
        return ['contains', 'does_not_contain',
                'equal', 'not_equal', 'is_null', 'is_not_null', 'is_any']

    def filter_contains(self, query, value):
        """
        Filter data with a full 'ILIKE' query.
        """
        if value is None or value == '':
            return query
        return query.filter(sa.and_(
            *[self.column.ilike(self.encode_value('%{}%'.format(v)))
              for v in value.split()]))

    def filter_does_not_contain(self, query, value):
        """
        Filter data with a full 'NOT ILIKE' query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not like' something else, we must also
        # include things which are nothing at all, in our result set.
        return query.filter(sa.or_(
            self.column == None,
            sa.and_(
                *[~self.column.ilike(self.encode_value('%{}%'.format(v)))
                  for v in value.split()]),
        ))


class AlchemyEmptyStringFilter(AlchemyStringFilter):
    """
    String filter with special logic to treat empty string values as NULL
    """

    def filter_is_null(self, query, value):
        return query.filter(
            sa.or_(
                self.column == None,
                sa.func.trim(self.column) == self.encode_value('')))

    def filter_is_not_null(self, query, value):
        return query.filter(
            sa.and_(
                self.column != None,
                sa.func.trim(self.column) != self.encode_value('')))


class AlchemyByteStringFilter(AlchemyStringFilter):
    """
    String filter for SQLAlchemy, which encodes value as bytestring before
    passing it along to the query.  Useful when querying certain databases
    (esp. via FreeTDS) which like to throw the occasional segfault...
    """
    value_encoding = 'utf-8'

    def get_value(self, value=UNSPECIFIED):
        value = super(AlchemyByteStringFilter, self).get_value(value)
        if isinstance(value, six.text_type):
            value = value.encode(self.value_encoding)
        return value

    def filter_contains(self, query, value):
        """
        Filter data with a full 'ILIKE' query.
        """
        if value is None or value == '':
            return query
        return query.filter(sa.and_(
            *[self.column.ilike(b'%{}%'.format(v)) for v in value.split()]))

    def filter_does_not_contain(self, query, value):
        """
        Filter data with a full 'NOT ILIKE' query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not like' something else, we must also
        # include things which are nothing at all, in our result set.
        return query.filter(sa.or_(
            self.column == None,
            sa.and_(
                *[~self.column.ilike(b'%{}%'.format(v)) for v in value.split()]),
        ))


class AlchemyNumericFilter(AlchemyGridFilter):
    """
    Numeric filter for SQLAlchemy.
    """
    value_renderer_factory = NumericValueRenderer

    # expose greater-than / less-than verbs in addition to core
    default_verbs = ['equal', 'not_equal', 'greater_than', 'greater_equal',
                     'less_than', 'less_equal', 'is_null', 'is_not_null', 'is_any']

    # TODO: what follows "works" in that it prevents an error...but from the
    # user's perspective it still fails silently...need to improve on front-end

    # try to detect (and ignore) common mistake where user enters UPC as search
    # term for integer field...

    def value_invalid(self, value):
        return bool(value and len(six.text_type(value)) > 8)

    def filter_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_equal(query, value)

    def filter_not_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_not_equal(query, value)

    def filter_greater_than(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_greater_than(query, value)

    def filter_greater_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_greater_equal(query, value)

    def filter_less_than(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_less_than(query, value)

    def filter_less_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_less_equal(query, value)


class AlchemyIntegerFilter(AlchemyNumericFilter):
    """
    Integer filter for SQLAlchemy.
    """

    def value_invalid(self, value):
        if value:
            if isinstance(value, int):
                return True
            if not value.isdigit():
                return True
            # TODO: this one is to avoid DataError from PG, but perhaps that
            # isn't a good enough reason to make this global logic?
            if int(value) > 2147483647:
                return True
        return False


class AlchemyBooleanFilter(AlchemyGridFilter):
    """
    Boolean filter for SQLAlchemy.
    """
    default_verbs = ['is_true', 'is_false', 'is_any']

    def filter_is_true(self, query, value):
        """
        Filter data with an "is true" query.  Note that this filter does not
        use the value for anything.
        """
        return query.filter(self.column == True)

    def filter_is_false(self, query, value):
        """
        Filter data with an "is false" query.  Note that this filter does not
        use the value for anything.
        """
        return query.filter(self.column == False)


class AlchemyNullableBooleanFilter(AlchemyBooleanFilter):
    """
    Boolean filter for SQLAlchemy which is NULL-aware.
    """
    default_verbs = ['is_true', 'is_false', 'is_null', 'is_not_null', 'is_any']


class AlchemyDateFilter(AlchemyGridFilter):
    """
    Date filter for SQLAlchemy.
    """
    value_renderer_factory = DateValueRenderer

    verb_labels = {
        'equal':                "on",
        'not_equal':            "not on",
        'greater_than':         "after",
        'greater_equal':        "on or after",
        'less_than':            "before",
        'less_equal':           "on or before",
        'is_null':              "is null",
        'is_not_null':          "is not null",
        'is_any':               "is any",
    }

    def default_verbs(self):
        """
        Expose greater-than / less-than verbs in addition to core.
        """
        return ['equal', 'not_equal', 'greater_than', 'greater_equal',
                'less_than', 'less_equal', 'is_null', 'is_not_null', 'is_any']

    def make_date(self, value):
        """
        Convert user input to a proper ``datetime.date`` object.
        """
        if value:
            try:
                dt = datetime.datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                log.warning("invalid date value: {}".format(value))
            else:
                return dt.date()


class AlchemyDateTimeFilter(AlchemyDateFilter):
    """
    SQLAlchemy filter for datetime values.
    """

    def filter_equal(self, query, value):
        """
        Find all dateimes which fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = make_utc(localtime(self.config, start))

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = make_utc(localtime(self.config, stop))

        return query.filter(self.column >= start)\
                    .filter(self.column < stop)

    def filter_not_equal(self, query, value):
        """
        Find all dateimes which do *not* fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = make_utc(localtime(self.config, start))

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = make_utc(localtime(self.config, stop))

        return query.filter(sa.or_(
            self.column < start,
            self.column <= stop))

    def filter_greater_than(self, query, value):
        """
        Find all datetimes which fall after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column >= time)

    def filter_greater_equal(self, query, value):
        """
        Find all datetimes which fall on or after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column >= time)

    def filter_less_than(self, query, value):
        """
        Find all datetimes which fall before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column < time)

    def filter_less_equal(self, query, value):
        """
        Find all datetimes which fall on or before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column < time)


class AlchemyLocalDateTimeFilter(AlchemyDateTimeFilter):
    """
    SQLAlchemy filter for *local* datetime values.  This assumes datetime
    values in the database are for local timezone, as opposed to UTC.
    """

    def filter_equal(self, query, value):
        """
        Find all dateimes which fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = localtime(self.config, start, tzinfo=False)

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = localtime(self.config, stop, tzinfo=False)

        return query.filter(self.column >= start)\
                    .filter(self.column < stop)

    def filter_not_equal(self, query, value):
        """
        Find all dateimes which do *not* fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = localtime(self.config, start, tzinfo=False)

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = localtime(self.config, stop, tzinfo=False)

        return query.filter(sa.or_(
            self.column < start,
            self.column <= stop))

    def filter_greater_than(self, query, value):
        """
        Find all datetimes which fall after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column >= time)

    def filter_greater_equal(self, query, value):
        """
        Find all datetimes which fall on or after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column >= time)

    def filter_less_than(self, query, value):
        """
        Find all datetimes which fall before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column < time)

    def filter_less_equal(self, query, value):
        """
        Find all datetimes which fall on or before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column < time)


class AlchemyGPCFilter(AlchemyGridFilter):
    """
    GPC filter for SQLAlchemy.
    """
    default_verbs = ['equal', 'not_equal']

    def filter_equal(self, query, value):
        """
        Filter data with an equal ('=') query.
        """
        if value is None or value == '':
            return query
        try:
            return query.filter(self.column.in_((
                GPC(value),
                GPC(value, calc_check_digit='upc'))))
        except ValueError:
            return query

    def filter_not_equal(self, query, value):
        """
        Filter data with a not eqaul ('!=') query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not equal' to something else, we must also
        # include things which are nothing at all, in our result set.
        try:
            return query.filter(sa.or_(
                ~self.column.in_((
                    GPC(value),
                    GPC(value, calc_check_digit='upc'))),
                self.column == None))
        except ValueError:
            return query


class AlchemyPhoneNumberFilter(AlchemyStringFilter):
    """
    Special string filter, with logic to deal with phone numbers.
    """

    def parse_value(self, value):
        newvalue = None

        # first we try to split according to typical 7- or 10-digit number
        digits = re.sub(r'\D', '', value or '')
        if len(digits) == 7:
            newvalue = "{} {}".format(digits[:3], digits[3:])
        elif len(digits) == 10:
            newvalue = "{} {} {}".format(digits[:3], digits[3:6], digits[6:])

        # if that didn't work, we can also try to split by grouped digits
        if not newvalue and value:
            parts = re.split(r'\D+', value)
            newvalue = ' '.join(parts)

        return newvalue or value

    def filter_contains(self, query, value):
        """
        Try to parse the value into "parts" of a phone number, then do a normal
        'ILIKE' query with those parts.
        """
        value = self.parse_value(value)
        return super(AlchemyPhoneNumberFilter, self).filter_contains(query, value)

    def filter_does_not_contain(self, query, value):
        """
        Try to parse the value into "parts" of a phone number, then do a normal
        'NOT ILIKE' query with those parts.
        """
        value = self.parse_value(value)
        return super(AlchemyPhoneNumberFilter, self).filter_does_not_contain(query, value)


class GridFilterSet(OrderedDict):
    """
    Collection class for :class:`GridFilter` instances.
    """

    def move_before(self, key, refkey):
        """
        Rearrange underlying key sorting, such that the given ``key`` comes
        just *before* the given ``refkey``.
        """
        # first must work out the new order for all keys
        newkeys = []
        for k in self.keys():
            if k == key:
                continue
            if k == refkey:
                newkeys.append(key)
                newkeys.append(refkey)
            else:
                newkeys.append(k)

        # then effectively replace dict contents, using new order
        items = dict(self)
        self.clear()
        for k in newkeys:
            self[k] = items[k]


class GridFiltersForm(forms.Form):
    """
    Form for grid filters.
    """

    def __init__(self, filters, **kwargs):
        self.filters = filters
        if 'schema' not in kwargs:
            schema = colander.Schema()
            for key, filtr in self.filters.items():
                node = colander.SchemaNode(colander.String(), name=key)
                schema.add(node)
            kwargs['schema'] = schema
        super(GridFiltersForm, self).__init__(**kwargs)

    def iter_filters(self):
        return self.filters.values()

    def filter_verb(self, filtr):
        """
        Render the verb selection dropdown for the given filter.
        """
        options = [tags.Option(filtr.verb_labels.get(v, "unknown verb '{}'".format(v)), v)
                   for v in filtr.verbs]
        hide_values = [v for v in filtr.valueless_verbs
                       if v in filtr.verbs]
        return tags.select('{}.verb'.format(filtr.key), filtr.verb, options, **{
            'class_': 'verb',
            'data-hide-value-for': ' '.join(hide_values)})

    def filter_value(self, filtr, **kwargs):
        """
        Render the value input element(s) for the filter.
        """
        style = 'display: none;' if filtr.verb in filtr.valueless_verbs else None
        return HTML.tag('div', class_='value', style=style,
                        c=[filtr.render_value(**kwargs)])
