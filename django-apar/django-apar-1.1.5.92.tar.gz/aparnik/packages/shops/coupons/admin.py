# -*- coding: utf-8 -*-


from django.contrib import admin
from django.utils.timezone import now
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from .models import CouponForAllUser, CouponForCoustomUser, CouponForLimitedUser


class CouponListFilter(SimpleListFilter):
    title = _('Expire Coupon')
    parameter_name = 'expire_at'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All Coupon')),
            (None, _('Available')),
            ('expire', _('Expire Coupons')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset.all()
        elif self.value() == None:
            return queryset.filter(expire_at__date__gte=now())
        elif self.value() == 'expire':
            return queryset.filter(expire_at__date__lt=now())

    def choices(self, cl):
        yield {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('Available'),  # Changed All to Hide archived.
        }
        for lookup, title in self.lookup_choices:
            # TODO delete the default one !
            if str(lookup) == 'None':
                continue
            yield {
                'selected': self.value() == str(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


# Register your models here.
class CouponAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display = (
        'id', 'code', 'value', 'type', 'max_price_order', 'min_price_order', get_update_at, 'expire_at',
    )
    list_filter = [CouponListFilter, 'type']
    search_fields = ['code', 'type', 'value']
    actions = None

     # permission

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(CouponAdmin, self).change_view(request, object_id, extra_context=extra_context)


class CouponForAllUserAdmin(CouponAdmin):

    exclude = ('for_users', 'for_limited_users_value')


class MembershipInline(admin.TabularInline):
    model = CouponForCoustomUser.users.through
    fields = ('user', 'is_redeem')
    readonly_fields = ('is_redeem', )
    raw_id_fields = ('user',)
    extra = 1


class CouponForLimitedUserAdmin(CouponAdmin):
    search_fields = CouponAdmin.search_fields + get_user_search_fields('users')
    exclude = ('for_users', )
    inlines = (MembershipInline,)


class CouponForCoustomUserAdmin(CouponAdmin):
    search_fields = CouponAdmin.search_fields + get_user_search_fields('users')
    exclude = ('for_users', 'for_limited_users_value')
    inlines = (MembershipInline,)


admin.site.register(CouponForAllUser, CouponForAllUserAdmin)
admin.site.register(CouponForCoustomUser, CouponForCoustomUserAdmin)
admin.site.register(CouponForLimitedUser, CouponForLimitedUserAdmin)