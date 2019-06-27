# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from .models import Notification, NotificationForSingleUser, User, Membership, NotificationType, NotificationSystem
from .forms import NotificationForAllUserForm


# Register your models here.
class NotificationForAllUserAdmin(BaseModelAdmin):

    fields = ['title', 'description', 'type', 'products_buy_did_not', 'products_buy', 'description_for_admin', 'sent_result']
    list_display = ['title', 'description', 'type',  get_update_at, ]
    list_filter = ['type', ]
    search_fields = ['title']
    exclude = ['from_user_obj', 'model_obj', 'notification_send_type', ]
    raw_id_fields = []
    dynamic_raw_id_fields = ['products_buy_did_not', 'products_buy']
    readonly_fields = []

    actions = None
    form = NotificationForAllUserForm

    def __init__(self, *args, **kwargs):
        Klass = NotificationForAllUserAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        Notification

    def get_queryset(self, request):

        return Notification.objects.notification_type(NotificationType.ALL_USER)

    def save_model(self, request, obj, form, change):

        set_all_user = True if not obj.id else False
        obj.save()
        if set_all_user:
            queryset = User.objects.all()

            if is_app_installed('aparnik.packages.shops.orders'):

                try:
                    from aparnik.packages.shops.orders.models import Order
                    products_buy_did_not = form.cleaned_data['products_buy_did_not']
                    if products_buy_did_not.count() > 0:
                        user_products_buy_did_not = Order.objects.get_order_products(products_buy_did_not).values_list('user', flat=True)
                        queryset = queryset.exclude(pk__in=user_products_buy_did_not)
                except:
                    pass

                try:
                    products_buy = form.cleaned_data['products_buy']
                    if products_buy.count() > 0:
                        user_products_buy = Order.objects.get_order_products(products_buy).values_list('user', flat=True)
                        queryset = queryset.filter(pk__in=user_products_buy)
                except:
                    pass

                for user in queryset:
                    m1 = Membership(user=user, notification=obj)
                    m1.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(NotificationForAllUserAdmin, self).change_view(request, object_id, extra_context=extra_context)


class MembershipInline(BaseModelTabularInline):
    model = NotificationForSingleUser.users.through
    fields = ('user', 'is_read')
    readonly_fields = ('is_read', )
    raw_id_fields = ('user',)
    extra = 1
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = MembershipInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


class NotificationForSingleUserAdmin(BaseModelAdmin):

    fields = ['title', 'description', 'type', 'description_for_admin', 'sent_result']
    list_display = ['title', 'description', 'type', get_update_at,]
    list_filter = ['type', ]
    search_fields = get_user_search_fields('users') + ['title']
    exclude = ['from_user_obj', 'model_obj', 'users', 'notification_send_type', 'products_buy', 'products_buy_did_not']
    raw_id_fields = []
    dynamic_raw_id_fields = []
    readonly_fields = ()

    actions = None
    inlines = (MembershipInline,)

    def __init__(self, *args, **kwargs):
        Klass = NotificationForSingleUserAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        NotificationForSingleUser

    def get_queryset(self, request):

        return Notification.objects.notification_type(NotificationType.SINGLE_USER)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(NotificationForSingleUserAdmin, self).change_view(request, object_id, extra_context=extra_context)


class NotificationSystemAdmin(BaseModelAdmin):

    fields = ['title', 'description', 'type', 'description_for_admin', 'sent_result']
    list_display = ['title', 'description', 'type', get_update_at,]
    list_filter = ['type', ]
    search_fields = get_user_search_fields('users') + ['title']
    exclude = ['from_user_obj', 'model_obj', 'users', 'notification_send_type', 'products_buy', 'products_buy_did_not']
    raw_id_fields = []
    dynamic_raw_id_fields = []
    readonly_fields = ()

    actions = None
    inlines = (MembershipInline,)

    def __init__(self, *args, **kwargs):
        Klass = NotificationSystemAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        NotificationSystem

    def get_queryset(self, request):

        return Notification.objects.notification_type(NotificationType.SYSTEM)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(NotificationSystemAdmin, self).change_view(request, object_id, extra_context=extra_context)


admin.site.register(NotificationForSingleUser, NotificationForSingleUserAdmin)
admin.site.register(Notification, NotificationForAllUserAdmin)
admin.site.register(NotificationSystem, NotificationSystemAdmin)
