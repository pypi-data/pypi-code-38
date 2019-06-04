# -*- coding:utf-8 -*-
from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericForeignKey

__author__ = 'denishuang'

from django.utils.encoding import force_text
import django.db.models.fields as djfields
from django.forms.fields import TypedMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Count, Model, DateTimeField, Expression, IntegerField
import json, re
from .datautils import JSONEncoder, auto_code
from . import formutils


class TimeFieldMixin(object):
    create_time = DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = DateTimeField(u"修改时间", auto_now=True)


class CommaSeparatedIntegerField(djfields.CommaSeparatedIntegerField):
    def clean(self, value, model_instance):
        if self.choices and isinstance(value, (list, tuple)):
            for v in value:
                super(CommaSeparatedIntegerField, self).clean(v, model_instance)
            return ",".join(value)
        return super(CommaSeparatedIntegerField, self).clean(value, model_instance)

    def formfield(self, **kwargs):
        defaults = {"choices_form_class": TypedMultipleChoiceField,
                    "widget": CheckboxSelectMultiple,
                    "initial": "",
                    "empty_value": ""
                    }
        defaults.update(kwargs)
        return super(CommaSeparatedIntegerField, self).formfield(**defaults)


class MutipleGetFieldDisplayModelMixin:
    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        print value, type(value)
        if value:
            d = dict(field.flatchoices)
            return ",".join([force_text(d.get(v, v), strings_only=True) for v in value.split(",")])
        else:
            return force_text(dict(field.flatchoices).get(value, value), strings_only=True)


class CompositeChoicesField(djfields.CharField):
    def __init__(self, verbose_name=None, choice_set={}, format_str=None, **kwargs):
        self.choice_set = choice_set
        self.format_str = format_str
        super(CompositeChoicesField, self).__init__(verbose_name, **kwargs)

    def to_python(self, value):
        if not value:
            return {}
        elif isinstance(value, (str, unicode)):
            return json.loads(value)
        elif isinstance(value, (dict)):
            return value

    def get_prep_value(self, value):
        return json.dumps(value)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def formfield(self, **kwargs):
        defaults = {"form_class": formutils.CompositeChoicesField,
                    "choice_set": self.choice_set,
                    # "initial":{},
                    "format_str": self.format_str,
                    }
        defaults.update(kwargs)
        return super(CompositeChoicesField, self).formfield(**defaults)


class JSONField(djfields.Field):
    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        return json.dumps(value, indent=2, cls=JSONEncoder)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return None
        return json.loads(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': formutils.JsonField}
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)
        # return formutils.JsonField(**kwargs)

    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        return json.dumps(val, indent=2, cls=JSONEncoder)


class KeyValueJsonField(JSONField):
    def formfield(self, **kwargs):
        defaults = {'form_class': formutils.KeyValueJsonField}
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)


class WordSetField(djfields.Field):
    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        return value and "\n".join(value) or ''

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return []
        return value.split("\n")

    def formfield(self, **kwargs):
        defaults = {'form_class': formutils.WordSetField}
        defaults.update(kwargs)
        return super(WordSetField, self).formfield(**defaults)

    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        return self.get_prep_value(val)


def move_relation(src_obj, dest_obj):
    from django.db.models.deletion import get_candidate_relations_to_delete
    for related in get_candidate_relations_to_delete(src_obj._meta):
        field_name = related.field.name
        raname = related.get_accessor_name()
        if hasattr(src_obj, raname):
            related_obj = getattr(src_obj, raname)
            from django.db.models import Manager
            if isinstance(related_obj, Manager):
                related_obj.all().update(**{field_name: dest_obj})
            else:
                setattr(related_obj, field_name, dest_obj)
                related_obj.save()


def group_by(qset, group):
    return list(qset.order_by(group).values_list(group, flat=True).annotate(Count("id")))


def multi_group_by(qset, group):
    if isinstance(group, basestring):
        group = group.split(",")
    return list(qset.order_by(*group).values(*group).annotate(C=Count("id")))


def count_by(qset, group, new_group=None, count_field='id', distinct=False, sort=None):
    qset = qset.values(group).order_by(group)
    if new_group:
        from django.db.models import F
        d = {new_group: F(group)}
        qset = qset.values(**d)
    else:
        new_group = group
    dl = qset.annotate(c=Count(count_field, distinct=distinct))
    if sort is not None:
        dl = dl.order_by("%sc" % sort)
    return [(d[new_group], d["c"]) for d in dl]


def stat_by(qset, fields, group):
    r = {}
    for k, v in fields.items():
        for g, c in count_by(qset.filter(**v), group):
            r.setdefault(g, {})
            r[g][k] = c
    return r


RE_FIELD_SPLITER = re.compile(r"\.|__")


def get_related_field(obj, field_name):
    meta = obj._meta
    fs = RE_FIELD_SPLITER.split(field_name)
    for f in fs[:-1]:
        meta = meta.get_field(f).related_model._meta
    return meta.get_field(fs[-1])


def get_related_field_verbose_name(obj, field_name):
    meta = obj._meta
    fs = RE_FIELD_SPLITER.split(field_name)
    r = []
    for f in fs[:-1]:
        fd = meta.get_field(f)
        if isinstance(fd, GenericForeignKey):
            ct = obj.content_type  # 这里只做到一层，深层的暂时无法实现
            r.append(unicode(ct))
            meta = ct.model_class()._meta
        else:
            r.append(fd.verbose_name)
            meta = fd.related_model._meta
    r.append(meta.get_field(fs[-1]).verbose_name)
    return "".join(r)


def get_object_accessor_value(record, accessor):
    penultimate, remainder = accessor.penultimate(record)

    from django.db import models
    if isinstance(penultimate, models.Model):
        try:
            field = accessor.get_field(record)
            display_fn = getattr(penultimate, 'get_%s_display' % remainder, None)
            if getattr(field, 'choices', ()) and display_fn:
                return display_fn()
        except models.FieldDoesNotExist:
            pass
    from django_tables2.utils import A
    v = A(remainder).resolve(penultimate, quiet=True)
    if isinstance(v, Model):
        return unicode(v)
    elif hasattr(v, 'update_or_create'):  # a Model Manager ?
        return ";".join([unicode(o) for o in v.all()])
    return v


def object2dict4display(obj, fields):
    from django_tables2.utils import A
    return OrderedDict(
        [(f, {
            "name": f,
            "verbose_name": get_related_field_verbose_name(obj, f),
            "value": get_object_accessor_value(obj, A(f))
        }
          ) for f in fields]
    )


def get_objects_accessor_data(accessors, content_type_id, object_ids):
    from django_tables2.utils import Accessor
    from django.contrib.contenttypes.models import ContentType
    acs = [Accessor(a) for a in accessors]
    ct = ContentType.objects.get_for_id(content_type_id)
    for id in object_ids:
        obj = ct.get_object_for_this_type(id=id)
        yield [a.resolve(obj) for a in acs]

def get_model_dependants(model):
    return set([f.related_model._meta.label for f in model._meta.fields if f.many_to_one])

class QuerysetDict(object):
    def __init__(self, qset, keyFieldName, valueFieldName):
        self.qset = qset
        self.keyFieldName = keyFieldName
        self.valueFieldName = valueFieldName

    def __getitem__(self, item):
        return self.get(item)

    def get(self, item, default=None):
        obj = self.qset.filter(**{self.keyFieldName: item}).first()
        if obj:
            return getattr(obj, self.valueFieldName, default)
        return default


def translate_model_values(model, values, fields=[]):
    if not values:
        return {}
    from .datautils import choices_map_reverse
    fs = [f for f in model._meta.local_fields if f.name in fields]
    rs = {}
    for f in fs:
        v = values.get(f.verbose_name)
        if f.choices:
            m = choices_map_reverse(f.choices)
            v = m.get(v)
        if v is None and f.default != djfields.NOT_PROVIDED:
            v = f.default
        rs[f.name] = v
        # print f.verbose_name, f.choices

    return rs


class CodeMixin(object):
    def save(self, **kwargs):
        if not self.code:
            self.code = auto_code(self.name)
        return super(CodeMixin, self).save(**kwargs)


class CharCorrelation(Expression):
    def __init__(self, expressions, output_field=None):
        if not output_field:
            output_field = IntegerField()
        super(CharCorrelation, self).__init__(output_field=output_field)
        if len(expressions) != 2:
            raise ValueError('expressions must have 2 elements')
        from django.db.models import F
        fn = expressions[0]
        if not isinstance(fn, F):
            raise ValueError('expressions first element must be instance of Field (F) ')
        self.expressions = expressions

    def as_sql(self, compiler, connection):
        exp = self.expressions
        fn = exp[0].name
        a = '+'.join(['(%s like "%%%%%s%%%%")' % (fn, c) for c in set(exp[1])])
        return '(%s)' % a, []
