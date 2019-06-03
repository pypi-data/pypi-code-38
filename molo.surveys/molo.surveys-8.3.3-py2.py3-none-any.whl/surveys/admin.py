from wagtail.contrib.modeladmin.options import ModelAdmin

from .models import SegmentUserGroup


class SegmentUserGroupAdmin(ModelAdmin):
    model = SegmentUserGroup
    menu_label = 'User groups for segments'
    menu_icon = 'group'
    menu_order = 1
    add_to_settings_menu = True
    list_display = ('name',)
    search_fields = ('name',)
