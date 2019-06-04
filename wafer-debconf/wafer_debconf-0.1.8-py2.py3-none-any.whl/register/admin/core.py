from django.contrib import admin
from django.db.models import Q


class NotNullFilter(admin.SimpleListFilter):
    title = 'Filter title not set'

    parameter_name = 'parameter name not set'

    def lookups(self, request, model_admin):

        return (
            ('not_null', 'Not empty only'),
            ('null', 'Empty only'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'not_null':
            is_null_false = {
                self.parameter_name + "__isnull": False
            }
            exclude = {
                self.parameter_name: ""
            }
            return queryset.filter(**is_null_false).exclude(**exclude)

        if self.value() == 'null':
            is_null_true = {
                self.parameter_name + "__isnull": True
            }
            param_exact = {
                self.parameter_name + "__exact": ""
            }
            return queryset.filter(Q(**is_null_true) | Q(**param_exact))
