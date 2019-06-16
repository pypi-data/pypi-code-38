from django.contrib import messages
from django.contrib.admin.actions import delete_selected
from django.utils.translation import ugettext_lazy as _


def bulk_delete(modeladmin, request, queryset):
    """
        Bulk delete, (dropdown, in django admin list objects)
    """

    for obj in queryset.all():
        if modeladmin.has_related(obj):
            messages.error(request, _('One or more item(s) contain(s) linked model(s), could not be deleted.'))
            return

    request.POST._mutable=True
    request.POST['action'] = 'bulk_delete'
    request.POST._mutable=False

    return delete_selected(modeladmin, request, queryset)

bulk_delete.allowed_permissions = ('delete',)   
bulk_delete.short_description = _("Delete selected %(verbose_name_plural)s")
