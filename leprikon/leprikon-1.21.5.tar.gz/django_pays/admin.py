import django
from django.contrib import admin
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .models import Gateway, Payment


class IdentifiedFieldListFilter(admin.RelatedFieldListFilter):
    def choices(self, changelist):
        yield {
            'selected': self.lookup_val_isnull is None,
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        yield {
            'selected': self.lookup_val_isnull == 'True',
            'query_string': changelist.get_query_string({self.lookup_kwarg_isnull: 'True'}),
            'display': _('Not identified'),
        }
        yield {
            'selected': self.lookup_val_isnull == 'False',
            'query_string': changelist.get_query_string({self.lookup_kwarg_isnull: 'False'}),
            'display': _('Identified'),
        }


@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'confirmation_url')

    def confirmation_url(self, obj):
        return 'https://{domain}{url}'.format(
            domain=Site.objects.get_current().domain,
            url=reverse('pays:confirm', args=(obj.slug,)),
        )
    confirmation_url.short_description = _('confirmation url')

    def get_readonly_fields(self, request, obj=None):
        # do not change secret key if not given
        if request.method == 'POST' and not request.POST.get('secret_key'):
            return ('secret_key',)
        else:
            return ()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = tuple(
        ('account_name' if f.name == 'account' else f.name) for f in Payment._meta.fields
    )[1:] + tuple(
        r.name for r in Payment._meta.related_objects
    )
    list_filter = ('gateway',) + tuple(
        (r.name, IdentifiedFieldListFilter)
        for r in Payment._meta.related_objects
    )

    def has_add_permission(self, request):
        return False

    # read only
    if django.VERSION > (2,):
        def has_change_permission(self, request, obj=None):
            return False
    else:
        def get_readonly_fields(self, request, obj=None):
            return tuple(
                f.name for f in self.model._meta.fields
                if not f.primary_key
            ) if obj else ()
