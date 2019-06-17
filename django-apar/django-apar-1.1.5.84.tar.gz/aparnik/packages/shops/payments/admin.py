# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields
from .models import Payment


# Register your models here.
class PaymentAdmin(BaseModelAdmin):
    list_display = ['bank_reference', 'uuid', 'user', 'method', 'status', 'order_obj', 'call_back_url', 'created_at', 'update_at']
    list_filter = ['status', 'created_at']
    search_fields = get_user_search_fields('user') + ['uuid']
    # change_list_template = 'admin/change_list_payment.html'
    raw_id_fields = ['order_obj']
    fields = []
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = PaymentAdmin
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
        Payment

    def changelist_view(self, request, extra_context=None):
        response = super(PaymentAdmin, self).changelist_view(request, extra_context=extra_context, )
        try:
            qs = response.context_data['cl'].queryset
            qs1 = Payment.objects.values('created_at', 'status')
            # qs2 = payment.objects.values('id', 'coupon__value', 'coupon__type', )

        except (AttributeError, KeyError):
            return response
        response.context_data["date_status"] = qs1

        return response

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False # this not works if has_add_permision is True
        return super(PaymentAdmin, self).change_view(request, object_id, extra_context=extra_context)


admin.site.register(Payment, PaymentAdmin)
