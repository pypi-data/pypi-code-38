from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import QtUser, GroupProperty, Orders, VipLogs, Wallet, WalletLog

admin.site.unregister(User)
admin.site.unregister(Group)


class ProfileInline(admin.StackedInline):
    model = QtUser
    max_num = 1
    fk_name = 'user'
    can_delete = False
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)


@admin.register(User)
class QtUserAdmin(UserAdmin):
    inlines = [ProfileInline, ]

    class Media:
        # js = ('/static/admin/js/fix_multi_select.js',)
        pass


class GroupInline(admin.StackedInline):
    model = GroupProperty
    max_num = 1
    can_delete = False
    inline_classes = ('grp-collapse grp-open',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupInline, ]
    list_display = ('id', 'name', 'property_price')
    list_display_links = ('id', 'name')

    def property_price(self, obj):
        return obj.groupproperty.price

    property_price.short_description = '价格'


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_sn', 'site', 'type', 'amount', 'user', 'pay_type', 'status', 'created')
    list_display_links = ('id', 'order_sn')
    list_filter = ('site',)
    search_fields = ('order_sn', 'user')


@admin.register(VipLogs)
class VipLogsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'site', 'order', 'created')
    list_filter = ('site',)
    search_fields = ('order', 'user')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'money', 'name', 'idcard', 'created')
    list_display_links = ('id', 'user')
    search_fields = ('user', 'name', 'idcard')


@admin.register(WalletLog)
class WalletLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_sn', 'user', 'change_money', 'remain', 'type', 'pay_type', 'created')
    list_display_links = ('id', 'order_sn')
    list_filter = ('user', 'pay_type')
