from django.contrib import admin
from .models import Menu, Province, City, Area, SmsCode, Links, SiteProperty, Site, BaiduPushLog, VisitLogs

# 先移除系统的站点菜单
admin.site.unregister(Site)


# 类型InlineModelAdmin：表示在模型的编辑页面嵌入关联模型的编辑
# 子类TabularInline：以表格的形式嵌入
# 子类StackedInline：以块的形式嵌入
# 设置站点属性与站点在同一管理面板
class SitePropertyInline(admin.StackedInline):
    model = SiteProperty
    max_num = 1
    can_delete = False
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)


@admin.register(Site)
class SitePropertyAdmin(admin.ModelAdmin):
    inlines = (SitePropertyInline,)
    list_display = ('id', 'domain', 'name', 'property_slug')
    list_display_links = ('id', 'domain', 'name')

    def property_slug(self, obj):
        return obj.siteproperty.slug

    property_slug.short_description = '站点标签'


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'parent']
    list_display_links = ['id', 'title']


@admin.register(SmsCode)
class SmsAdmin(admin.ModelAdmin):
    list_display = ['id', 'mobile', 'code', 'ip', 'user_agent', 'created']
    list_display_links = ['id', 'mobile']


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    hidden_menu = True

    def get_model_perms(self, request):
        return {}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    hidden_menu = True

    def get_model_perms(self, request):
        return {}


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']


@admin.register(Links)
class SitePropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'domain', 'desc', 'created')
    list_display_links = ('id', 'title')

    def save_model(self, request, obj, form, change):
        if not obj.domain.startswith('http'):
            obj.domain = 'http://%s' % obj.domain
        return super().save_model(request, obj, form, change)


@admin.register(BaiduPushLog)
class BaiduPushLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'url', 'site', 'status', 'created')
    list_display_links = ('id', 'title')
    list_filter = ('site', 'status', 'url')


@admin.register(VisitLogs)
class VisitLogsAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'passport', 'ip', 'referrer', 'user_agent', 'created')
    list_display_links = ('id', 'url')
