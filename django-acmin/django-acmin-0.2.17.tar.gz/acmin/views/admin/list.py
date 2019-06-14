from collections import OrderedDict

from django.db.models import Q
from django.forms import ChoiceField, forms
from django.views import generic
from django.views.generic.list import BaseListView

from acmin.models import Permission, PermissionItem, Filter, Field
from acmin.utils import param, json_response
from .mixins import ContextMixin, AccessMixin


class SearchMixin(BaseListView):
    def get_toolbar_search_params(self):
        fields = [field.attribute for field in Field.get_fields(self.request.user, self.model)]
        return {k: v for k, v in self.request.GET.items() if k in fields and v}

    def get_request_model_filters(self):
        fields = [field.attribute for field in Field.get_fields(self.request.user, self.model)]
        return {k: v for k, v in self.request.GET.items() if k in fields and v}


class FuzzySearchMixin(BaseListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get("___fuzzy_search_key__")
        if keyword and len(keyword) > 0:
            search_attributes = Field.get_search_attributes(self.request.user, self.model)
            if search_attributes:
                q = Q()
                for attribute in search_attributes:
                    q = q | Q(**{f'{attribute.replace(".", "__")}__icontains': keyword})
                queryset = queryset.filter(q)

        return queryset


class FilterForm(forms.Form):
    pass


class ToolbarSearchFormMixin(SearchMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["toolbar_search_form"] = self.get_toolbar_search_form()
        return context

    def get_toolbar_search_form(self):
        choices = self.get_toolbar_search_fields() + self.get_toolbar_extra_search_choices()
        if choices:
            fields = OrderedDict(choices)
            form = FilterForm()
            form.fields = fields
            return form

    def get_toolbar_extra_search_choices(self):
        return []

    def get_toolbar_search_fields(self):
        user = self.request.user
        choices = []
        group_fields = Field.get_group_fields(user, self.model, has_contenttype=True)
        params = self.get_toolbar_search_params()
        for fields in group_fields:
            fields = [field for field in  fields  if field.filterable]
            last_options = None
            last_default_value = None
            for index in range(len(fields)):
                field = fields[index]
                attribute = field.attribute
                cls = field.model
                queryset = None
                if index == 0:
                    queryset = cls.objects
                else:
                    last_attribute = fields[index - 1].attribute
                    last_value = params.get(last_attribute) or last_default_value
                    if last_value and last_options:
                        filters = {last_attribute[len(attribute) + 1:] + "_id": int(last_value)}
                        queryset = cls.objects.filter(**filters)

                queryset = Filter.filter(queryset, self.request, cls)
                options = [(e.id, str(e)) for e in queryset.all()] if queryset else []
                label = field.verbose_name
                if len(options) > 1:
                    options = [('', '选择%s' % label)] + options
                if options:
                    choices.append(
                        (attribute, ChoiceField(initial=params.get(attribute, ""), label=label, choices=options, )))

                last_default_value = options[0][0] if options else None
                last_options = options

        return choices


class OrderMixin(BaseListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get("sort")
        if sort:
            queryset = queryset.order_by(sort.replace('.', '__'))

        return queryset


class ToolbarSearchMixin(SearchMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.get_toolbar_search_params()
        fields_group = Field.get_group_fields(self.request.user, self.model, has_contenttype=True)
        for fields in fields_group:
            for field in fields:
                value = params.get(field.attribute, None)
                if value:
                    queryset = queryset.filter(**{field.attribute.replace(".", "__") + "_id": value})
                    break

        sort = self.request.GET.get("sort")
        if sort:
            queryset = queryset.order_by(sort.replace('.', '__'))

        return queryset


class ChoiceResponseMixin(BaseListView):
    def get(self, request, *args, **kwargs):
        choices, attribute, value = param(request, ["choices", "attribute", "value"])
        from acmin.models import Field
        field = Field.get_field(self.request.user, self.model, attribute)
        if choices and attribute and (value or field.nullable):
            queryset = self.model.objects
            if value:
                queryset = queryset.filter(**{attribute.replace(".", "__") + "_id": int(value)})
            queryset = Filter.filter(queryset, self.request, self.model)
            return json_response([{"id": obj.id, "title": str(obj)} for obj in queryset.all()], safe=False)
        return super().get(request, args, kwargs)


class AdminListView(
    ChoiceResponseMixin,
    FuzzySearchMixin,
    ToolbarSearchFormMixin,
    ToolbarSearchMixin,
    OrderMixin,
    ContextMixin,
    AccessMixin,
    generic.ListView
):
    context_object_name = 'list'
    paginate_by = 30
    form_class = None

    def get_model_list_fields(self):
        return [field for field in Field.get_fields(self.request.user, self.model, has_contenttype=False) if
                field.listable]

    def get_relation_fields(self):
        user = self.request.user
        fields = [field for field in Field.get_fields(user, self.model, has_contenttype=True) if
                  field.listable and Permission.has_permission(user, field.model, PermissionItem.listable)]
        return fields

    def get_list_fields(self):
        return self.get_relation_fields() + self.get_model_list_fields()

    def get_template_names(self):
        return [f'admin/{self.model.__name__}/list.html', 'acmin/admin/base/list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"list_fields": self.get_list_fields()})
        context["view_type"] = 'list'
        for obj in context.get("list"):
            setattr(obj, "_request", self.request)

        return context

    def get_queryset(self):
        return Filter.filter(super().get_queryset(), self.request, self.model)

    def has_permission(self):
        item = PermissionItem.selectable if param(self.request, "choices") else PermissionItem.listable
        return Permission.has_permission(self.request.user, self.model, item)
