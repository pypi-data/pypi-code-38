from string import Formatter

import django.contrib.admin as admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape

from models import Journal, Tag, ObjectData, StringData

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.core.urlresolvers import reverse, NoReverseMatch

import actions

class ModelAdminFormatter(Formatter):
    def __init__(self, model_admin=None, filter_link=True,
            object_link=True):
        self.filter_link = filter_link
        self.object_link = object_link
        self.model_admin = model_admin
        super(ModelAdminFormatter, self).__init__()

    def build_object_link(self, value):
        content_type = ContentType.objects.get_for_model(value.__class__)
        url = u'{0}:{1}_{2}_change'.format(self.model_admin.admin_site.name,
                content_type.app_label, content_type.model)
        try:
            url = reverse(url, args=(value.pk,))
        except NoReverseMatch:
            return u''
        return u'<a href="{0}" class="external-link"></a>'.format(escape(url))

    def format_field(self, value, format_spec):
        if isinstance(value, models.Model):
            res = ''
            if self.filter_link:
                content_type = ContentType.objects.get_for_model(value.__class__)
                res = u'<a href="?objectdata__content_type={0}&objectdata__object_id={1}">{2}</a>'.format(
                            content_type.id, value.pk, escape(unicode(value)))
            else:
                res = escape(unicode(value))
            if self.object_link:
                res += self.build_object_link(value)
            return res
        return escape(super(ModelAdminFormatter, self).format_field(value, format_spec))


class ObjectDataInlineAdmin(admin.TabularInline):
    model = ObjectData
    fields = ('tag', 'content_type', 'content_object')
    readonly_fields = fields
    extra = 0
    max_num = 0

class StringDataInlineAdmin(admin.TabularInline):
    model = StringData
    fields = ('tag', 'content')
    readonly_fields = fields
    extra = 0
    max_num = 0

class JournalAdmin(admin.ModelAdmin):
    list_display = ('time', '_tag', 'user', 'ip', 'message_for_list')
    list_filter = ('tag',)
    fields = ('time', 'tag', 'user', 'ip', 'message_for_change')
    readonly_fields = fields
    inlines = (
            ObjectDataInlineAdmin, 
            StringDataInlineAdmin,
    )
    date_hierarchy = 'time'
    search_fields = ('message','tag__name','time')
    actions = [ actions.export_as_csv ]

    class Media:
        css = {
                'all': ('journal/css/journal.css',),
        }

    def queryset(self, request):
        '''Get as much data as possible using the fewest requests possible.'''
        qs = super(JournalAdmin, self).queryset(request)
        qs = qs.select_related('tag', 'template') \
               .prefetch_related('objectdata_set__content_type',
                       'stringdata_set', 'objectdata_set__tag',
                       'stringdata_set__tag', 'objectdata_set__content_object')
        return qs

    def lookup_allowed(self, key, *args, **kwargs):
        return True

    def _tag(self, entry):
        name = entry.tag.name.replace(u'-', u'\u2011')
        res = u'<a href="?tag__id__exact={0}">{1}</a>'.format(
                escape(entry.tag.id), escape(name))
        return res
    _tag.allow_tags = True
    _tag.short_description = _('tag')

    def ip(self, entry):
        '''Search and return any associated stringdata whose tag is "ip"'''
        for stringdata in entry.stringdata_set.all():
            if stringdata.tag.name == 'ip':
                return u'<a href="?stringdata__tag__id={tag_id}&' \
                       u'stringdata__content={ip}">{ip}</a>'.format(
                        tag_id=stringdata.tag.id, ip=stringdata.content)
        return _('None')
    ip.short_description = _('IP')
    ip.allow_tags = True

    def user(self, entry):
        '''Search and return any associated objectdata whose tag is "user"'''
        for objectdata in entry.objectdata_set.all():
            if objectdata.tag.name == 'user':
                return self.object_filter_link(objectdata) + \
                        self.object_link(objectdata)
        return _('None')
    user.allow_tags = True
    user.short_description = _('User')

    def object_filter_link(self, objectdata):
        if objectdata.content_object is not None:
            caption = unicode(objectdata.content_object)
        else:
            caption = _(u'<deleted {content_type} {object_id}>').format(
                    content_type=objectdata.content_type,
                    object_id=objectdata.object_id)
        return u'<a href="?objectdata__content_type={0}&objectdata__object_id={1}">{2}</a>'.format(
                    objectdata.content_type_id,
                    objectdata.object_id,
                    escape(caption))

    def object_link(self, obj_data):
        if obj_data.content_object is None:
            return u''
        url = u'{0}:{1}_{2}_change'.format(self.admin_site.name,
                obj_data.content_type.app_label,
                obj_data.content_type.model)
        try:
            url = reverse(url, args=(obj_data.object_id,))
        except NoReverseMatch:
            return ''
        return u'<a href="{0}" class="external-link"></a>'.format(url)

    def message_for_change(self, entry):
        ctx = entry.message_context()
        formatter = ModelAdminFormatter(model_admin=self, filter_link=False)
        message = formatter.format(escape(entry.template.content), **ctx)
        return u'<span>%s</span>' % message
    message_for_change.allow_tags = True
    message_for_change.short_description = _('Message')

    def message_for_list(self, entry):
        ctx = entry.message_context()
        formatter = ModelAdminFormatter(model_admin=self)
        message = formatter.format(entry.template.content, **ctx)
        return u'<span>{0}</span>'.format(message)
    message_for_list.allow_tags = True
    message_for_list.short_description = _('Message')
    message_for_list.admin_order_field = 'message'

admin.site.register(Journal, JournalAdmin)
admin.site.register(Tag)
