# -*- coding: utf-8 -*-
from congo.admin.actions import make_active, make_inactive
from congo.communication import get_email_recipient_model, get_email_recipient_group_model, get_email_message_queue_model, get_email_message_model, get_sms_recipient_model, get_sms_recipient_group_model, get_sms_message_queue_model, get_sms_message_model
from congo.communication.filters import SexListFilter, VocativeListFilter
from congo.conf import settings
from congo.utils.form import add_widget_css_class
from django import shortcuts
from django.contrib import messages
from django.db.utils import IntegrityError
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.http.response import HttpResponseRedirect

modeladmin_name = settings.CONGO_ADMIN_MODEL
modeladmin = import_string(modeladmin_name)

class EmailSenderAdmin(modeladmin):
    list_display = ('name', 'email')
    fields = ('name', 'email')

class EmailRecipientGroupAdmin(modeladmin):
    list_display = ('name', 'add_date', 'change_date')
    date_hierarchy = 'add_date'
    readonly_fields = ('add_date', 'change_date')

class SMSRecipientGroupAdmin(EmailRecipientGroupAdmin):
    pass

class EmailRecipientAdmin(modeladmin):
    list_display = ('name', 'vocative', 'email', 'add_date', 'is_tester', 'is_active', 'is_confirmed')
    list_filter = (SexListFilter, VocativeListFilter, 'source', 'add_date', 'change_date', 'is_tester', 'is_active', 'is_confirmed')
    search_fields = ('name', 'email')
    date_hierarchy = 'add_date'
    fields = ('name', 'email', 'sex', 'vocative', 'source', 'add_date', 'change_date', 'is_tester', 'is_active', 'is_confirmed')
    readonly_fields = ('change_date',)
    actions = (make_active, make_inactive)
#    form = EmailRecipientForm

class SMSRecipientAdmin(modeladmin):
    list_display = ('name', 'mobile_phone', 'add_date', 'is_tester', 'is_active', 'is_confirmed')
    list_filter = ('source', 'add_date', 'change_date', 'is_tester', 'is_active', 'is_confirmed')
    search_fields = ('user__first_name', 'user__last_name', 'user__mobile_phone')
    date_hierarchy = 'add_date'
    fields = ('user', 'name', 'mobile_phone', 'source', 'add_date', 'change_date', 'is_tester', 'is_active', 'is_confirmed')
    readonly_fields = ('name', 'mobile_phone', 'change_date',)
    actions = (make_active, make_inactive)

class EmailMessageAdmin(modeladmin):
    list_display = ('sender', 'subject', 'template', 'add_date', 'is_tested')
    list_display_links = ('subject',)
    list_filter = ('sender', 'reply_to', 'template', 'add_date', 'change_date', 'is_tested')
    search_fields = ('subject', 'html_content', 'text_content')
    date_hierarchy = 'add_date'
    fields = ('sender', 'reply_to', 'subject', 'template', 'send_date', 'html_content', 'text_content', 'add_date', 'change_date', 'is_tested')
    readonly_fields = ('add_date', 'change_date', 'is_tested')
    actions = ('send_to_testers', 'add_to_queue_for_group', 'add_to_queue')

#    class Media:
#        js = (
#            '/static/tinymce/tinymce.min.js',
#            '/static/congo_admin/js/tinymce/tinymce.init.js',
#        )

    def get_urls(self):
        urls = [
            url(r'^(?P<action>(add_to_queue|add_to_queue_for_group))/$', self.action_view)
        ]
        return urls + super(EmailMessageAdmin, self).get_urls()

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EmailMessageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'text_content':
            add_widget_css_class(field, 'plain_text copy_text clear')
            field.widget.attrs['rel'] = 'id_html_content'
        return field

    # actions

    def send_to_testers(self, request, queryset):
        recipient_model = get_email_recipient_model()
        recipient_list = recipient_model.objects.filter(is_active = True, is_confirmed = True, is_tester = True)
        for message in queryset:
            subject = message.subject
            message.subject = u"[TEST] " + message.subject
            count_sent = message.send(recipient_list, user = request.user)

            if count_sent > 0:
                message.is_tested = True
                message.subject = subject
                message.save()
            messages.info(request, _(u"\"%(message)s\" wiadomości wysłano do testerów: %(x)s / %(y)s") % {'message': message, 'x': count_sent, 'y': len(recipient_list)})
    send_to_testers.short_description = _(u"Wyślij wiadomość do testerów")

    def add_to_queue_for_group(self, request, queryset):
        title = _(u"Dodaj wiadomość do kolejki dla grupy")
        action = "add_to_queue_for_group"
        group_model = get_email_recipient_group_model()
        groups = group_model.objects.all()
        object_id_set = ','.join([str(obj.id) for obj in queryset])

        extra_context = {
            "title": title,
            "action": action,
            "groups": groups,
            "object_id_set": object_id_set,
            "show_checkbox_group": True,
        }

        template = "admin/actions/%s.html" % action
        return shortcuts.render(request, template, extra_context)
    add_to_queue_for_group.short_description = _(u"Dodaj wiadomość do kolejki dla grupy")

    def add_to_queue_for_group_action(self, request):
        message_model = get_email_message_model()
        group_model = get_email_recipient_group_model()
        queue_model = get_email_message_queue_model()

        object_id_set = request.POST.get('object_id_set')
        queryset = message_model.objects.filter(id__in = object_id_set.split(','))
        group_id = request.POST.get('group_id')
        group = group_model.objects.get(id = group_id)

#        pass_site = 'pass_site' in request.POST
#        pass_subjects = 'pass_subjects' in request.POST

        for message in queryset:
            if message.is_tested:
                count_sent = 0
                kwargs = {}

#                if pass_site:
#                    kwargs['site_id'] = message.site_id
#                if pass_subjects:
#                    kwargs['subject_id_list'] = message.subject_range.all().values_list('id', flat = True)

                # @OG bulk_create
                # https://docs.djangoproject.com/en/1.8/ref/models/querysets/#django.db.models.query.QuerySet.bulk_create

                recipient_list = group.get_recipients(**kwargs)
                for recipient in recipient_list:
                    try:
                        email_queue = queue_model(recipient = recipient, message = message)
                        email_queue.save()
                        count_sent += 1
                    except IntegrityError:
                        pass
                messages.info(request, _(u"\"%(message)s\" wiadomości zostały dodane do kolejki: %(x)s / %(y)s") % {'message': message, 'x': count_sent, 'y': len(recipient_list)})
            else:
                messages.warning(request, _(u"\"%s\" wiadomość nie została dodana do kolejki, ponieważ nie jest przetestowana") % message)

    def add_to_queue(self, request, queryset):
        recipient_model = get_email_recipient_model()
        queue_model = get_email_message_queue_model()

        recipient_list = recipient_model.objects.filter(is_active = True, is_confirmed = True, is_tester = False)
        recipient_list_len = recipient_list.count()
        for message in queryset:
            if message.is_tested:
                count_queued = 0

                for recipient in recipient_list:
                    try:
                        mailing_queue = queue_model(recipient = recipient, message = message)
                        mailing_queue.save()
                        count_queued += 1
                    except IntegrityError:
                        pass

                messages.info(request, _(u"\"%(message)s\" wiadomości zostały dodane do kolejki: %(x)s / %(y)s") % {'message': message, 'x': count_queued, 'y': recipient_list_len})
            else:
                messages.warning(request, _(u"\"%s\" wiadomość nie została dodana do kolejki, ponieważ nie jest przetestowana") % message)
    add_to_queue.short_description = _(u"Dodaj wiadomość do kolejki")

class SMSMessageAdmin(modeladmin):
    list_display = ('sender', 'content_truncated', 'add_date', 'is_tested')
    list_display_links = ('content_truncated',)
    list_filter = ('sender', 'is_tested',)
    search_fields = ('content',)
    date_hierarchy = 'add_date'
    fields = ('sender', 'content', 'add_date', 'change_date', 'send_date', 'is_tested')
    readonly_fields = ('add_date', 'change_date', 'is_tested')
    actions = ('send_to_testers', 'add_to_queue_for_group', 'add_to_queue')

#    class Media:
#        js = (
#            '/static/custom_admin/js/slugify.js',
#        )

    def get_urls(self):
        urls = [
            url(r'^(?P<action>(add_to_queue_for_group))/$', self.action_view)
        ]
        return urls + super(SMSMessageAdmin, self).get_urls()

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(SMSMessageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'content':
            add_widget_css_class(field, 'sms')
        return field

    # fields

    def content_truncated(self, obj):
        return unicode(obj)
    content_truncated.admin_order_field = 'content'
    content_truncated.short_description = _(u"Treść")

    # actions

    def send_to_testers(self, request, queryset):
        recipient_model = get_sms_recipient_model()
        recipient_list = recipient_model.objects.filter(is_active = True, is_confirmed = True, is_tester = True)
        for message in queryset:
            count_sent = message.send(recipient_list, request.user)
            if count_sent > 0:
                message.is_tested = True
                message.save()
            messages.info(request, _(u"\"%(message)s\" wiadomości wysłano do testerów: %(x)s / %(y)s") % {'message': message, 'x': count_sent, 'y': len(recipient_list)})
    send_to_testers.short_description = _(u"Wyślij wiadomość do testerów")

    def add_to_queue_for_group(self, request, queryset):
        title = _(u"Dodaj wiadomość do kolejki dla grupy")
        action = "add_to_queue_for_group"
        group_model = get_sms_recipient_group_model()
        groups = group_model.objects.all()
        object_id_set = ','.join([str(obj.id) for obj in queryset])

        extra_context = {
            "title": title,
            "action": action,
            "groups": groups,
            "object_id_set": object_id_set,
        }

        template = "admin/actions/%s.html" % action
        return shortcuts.render(request, template, extra_context)
    add_to_queue_for_group.short_description = _(u"Dodaj wiadomość do kolejki dla grupy")

    def add_to_queue_for_group_action(self, request):
        message_model = get_sms_message_model()
        group_model = get_sms_recipient_group_model()
        queue_model = get_sms_message_queue_model()

        object_id_set = request.POST.get('object_id_set')
        queryset = message_model.objects.filter(id__in = object_id_set.split(','))
        group_id = request.POST.get('group_id')
        group = group_model.objects.get(id = group_id)
        recipient_list = group.get_recipients()

        for message in queryset:
            if message.is_tested:
                count_sent = 0
                for recipient in recipient_list:
                    try:
                        sms_queue = queue_model(recipient = recipient, message = message)
                        sms_queue.save()
                        count_sent += 1
                    except IntegrityError:
                        pass
                messages.info(request, _(u"\"%(message)s\" wiadomości zostały dodane do kolejki: %(x)s / %(y)s") % {'message': message, 'x': count_sent, 'y': len(recipient_list)})
            else:
                messages.warning(request, _(u"\"%s\" wiadomość nie została dodana do kolejki, ponieważ nie jest przetestowana") % message)

    def add_to_queue(self, request, queryset):
        recipient_model = get_sms_recipient_model()
        queue_model = get_sms_message_queue_model()

        recipient_list = recipient_model.objects.filter(is_active = True, is_tester = False)
        recipient_list_len = recipient_list.count()
        for message in queryset:
            if message.is_tested:
                count_queued = 0
                for recipient in recipient_list:
                    try:
                        sms_queue = queue_model(recipient = recipient, message = message)
                        sms_queue.save()
                        count_queued += 1
                    except IntegrityError:
                        pass
                messages.info(request, _(u"\"%(message)s\" wiadomości zostały dodane do kolejki: %(x)s / %(y)s") % {'message': message, 'x': count_queued, 'y': recipient_list_len})
            else:
                messages.warning(request, _(u"\"%s\" wiadomość nie została dodana do kolejki, ponieważ nie jest przetestowana") % message)
    add_to_queue.short_description = _(u"Dodaj wiadomość do kolejki")

class EmailMessageQueueAdmin(modeladmin):
    list_display = ('id', 'recipient', 'message', 'add_date', 'send_date', 'is_sent')
    list_filter = ('send_date', 'is_sent')
    search_fields = ('recipient__name', 'recipient__email', 'message__text_content')
    date_hierarchy = 'add_date'
    readonly_fields = ('add_date', 'send_date', 'is_sent')

class SMSMessageQueueAdmin(EmailMessageQueueAdmin):
    search_fields = ('recipient__name', 'recipient__mobile_phone', 'message')
