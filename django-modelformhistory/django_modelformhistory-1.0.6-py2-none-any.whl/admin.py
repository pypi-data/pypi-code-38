from django.contrib import admin

from .forms import HistoryModelFormMixin
from .models import Entry, ChangedData


class HistoryModelAdmin(admin.ModelAdmin):
    """
    Base class ModelAdmin to automatically store any change in history.
    Extend your ModelAdmin class to start using it :

        class FooAdmin(HistoryModelAdmin):
            pass

    """

    def get_form(self, request, obj=None, **kwargs):
        form = super(HistoryModelAdmin, self).get_form(request, obj=None, **kwargs)

        class HistoryAdminForm(HistoryModelFormMixin, form):
            class Meta(form.Meta):
                pass

            def get_history_user(self):
                return request.user

        return HistoryAdminForm


class ChangedDataInline(admin.TabularInline):
    model = ChangedData
    extra = 0


class EntryAdmin(admin.ModelAdmin):
    search_fields = ("created_by__username", "short_message")
    list_display = ("created_date", "created_by", "action_type", "short_message")
    raw_id_fields = ("created_by",)
    inlines = [ChangedDataInline]


admin.site.register(Entry, EntryAdmin)
