# -*- coding: utf-8 -*-
from django.contrib.admin.filters import ChoicesFieldListFilter, SimpleListFilter
# from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

# @OG ogarnij jak to zrobić ładnie
EMPTY_CHANGELIST_VALUE = _('(None)')

class SimpleNoneListFilter(SimpleListFilter):
    """
    Filtr zawiera dodatkową opcję "Brak" i pozwala wybrać obiekty z wartością NULL
    """

    def __init__(self, request, params, model, model_admin):
        super(SimpleNoneListFilter, self).__init__(request, params, model, model_admin)

        self.lookup_kwarg = '%s__exact' % self.parameter_name
#         self.lookup_kwarg = '%s' % self.parameter_name
        self.lookup_kwarg_isnull = '%s__isnull' % self.parameter_name

        self.lookup_val = None
        if self.lookup_kwarg in params:
            self.lookup_val = params.pop(self.lookup_kwarg)

        self.lookup_val_isnull = None
        if self.lookup_kwarg_isnull in params:
            self.lookup_val_isnull = params.pop(self.lookup_kwarg_isnull)

    def lookups(self, request, model_admin):
        """
        Must be overriden to return a list of tuples (value, verbose value)
        """
        raise NotImplementedError

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _(u'Wszystko')
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': smart_unicode(lookup) == self.lookup_val,
                'query_string': cl.get_query_string({self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]),
                'display': title,
            }
        yield {
            'selected': bool(self.lookup_val_isnull),
            'query_string': cl.get_query_string({self.lookup_kwarg_isnull: 'True'}, [self.lookup_kwarg]),
            'display': EMPTY_CHANGELIST_VALUE,
        }

class ContentTypeFilter(SimpleNoneListFilter):
    title = u"Typ zawartości"
    parameter_name = 'content_type__id'

    def lookups(self, request, model_admin):
        content_types = ContentType.objects.filter(id__in = model_admin.model.objects.all().values_list('content_type_id', flat = True).distinct())
        return [(content_type.id, unicode(content_type)) for content_type in content_types]

    def queryset(self, request, queryset):
        if self.lookup_val is not None:
            return queryset.filter(content_type__id = self.lookup_val)
        elif self.lookup_val_isnull is not None:
            return queryset.filter(content_type__id__isnull = self.lookup_val_isnull)
        else:
            return queryset

class ChoicesNoneFieldListFilter(ChoicesFieldListFilter):
    """
    Filtr zawiera dodatkową opcję "Brak" i pozwala wybrać obiekty z wartością NULL
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__exact' % field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull, None)

        super(ChoicesFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _(u'Wszystko')
        }
        for lookup, title in self.field.flatchoices:
            yield {
                'selected': smart_unicode(lookup) == self.lookup_val,
                'query_string': cl.get_query_string({self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]),
                'display': title,
            }
        yield {
            'selected': bool(self.lookup_val_isnull),
            'query_string': cl.get_query_string({self.lookup_kwarg_isnull: 'True', }, [self.lookup_kwarg]),
            'display': EMPTY_CHANGELIST_VALUE,
        }
