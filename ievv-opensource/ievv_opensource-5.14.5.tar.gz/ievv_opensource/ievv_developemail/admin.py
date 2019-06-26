from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from ievv_opensource.ievv_developemail.models import DevelopEmail


@admin.register(DevelopEmail)
class DevelopEmailAdmin(admin.ModelAdmin):
    list_display_links = ['get_edit']
    list_display = [
        'get_subject',
        'created_datetime',
        'from_email',
        'to_emails',
        'id',
        'get_edit',
    ]

    search_fields = [
        'id',
        'from_email',
        'to_emails',
        'raw_message',
    ]

    list_filter = [
        'created_datetime',
        'from_email',
    ]

    def get_edit(self, obj):
        return 'Edit'
    get_edit.short_description = 'Edit'

    def get_subject(self, developemail):
        view_url = reverse('admin:developemail_as_html', args=(developemail.id,))
        return format_html(
            '<a href="{url}">{label}</a>',
            url=view_url,
            label=developemail.subject_with_fallback)
    get_subject.short_description = 'Subject'
    get_subject.admin_order_field = 'subject'

    def get_urls(self):
        urls = super(DevelopEmailAdmin, self).get_urls()
        my_urls = [
            url(r'^(\d+)/as_html/$',
                self.admin_site.admin_view(self.as_html_view),
                name='developemail_as_html'),
            url(r'^(\d+)/as_plain/$',
                self.admin_site.admin_view(self.as_plain_view),
                name='developemail_as_plain'),
            url(r'^(\d+)/as_raw/$',
                self.admin_site.admin_view(self.as_raw_view),
                name='developemail_as_raw'),
        ]
        return my_urls + urls

    def _as_mail_preview_view(self, request, developemail_id, mode):
        context = {
            'developemail': get_object_or_404(DevelopEmail, id=developemail_id),
            'mode': mode,
            'developemail_count': DevelopEmail.objects.count()
        }
        return TemplateResponse(request, 'ievv_developemail/admin/as-{}.django.html'.format(mode), context)

    def as_plain_view(self, request, developemail_id):
        return self._as_mail_preview_view(request=request, developemail_id=developemail_id,
                                          mode='plain')

    def as_html_view(self, request, developemail_id):
        return self._as_mail_preview_view(request=request, developemail_id=developemail_id,
                                          mode='html')

    def as_raw_view(self, request, developemail_id):
        return self._as_mail_preview_view(request=request, developemail_id=developemail_id,
                                          mode='raw')
