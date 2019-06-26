from django.contrib import admin
from ievv_opensource.ievv_tagframework.models import Tag, TaggedObject


class TagAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'taglabel', 'tagtype'
    ]
    list_filter = [
        'tagtype'
    ]
    fields = [
        'taglabel',
        'tagtype',
    ]

admin.site.register(Tag, TagAdmin)


class TaggedObjectAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tag', 'content_object'
    ]
    list_filter = [
        'tag__tagtype'
    ]
    fields = [
        'tag',
    ]

admin.site.register(TaggedObject, TaggedObjectAdmin)
