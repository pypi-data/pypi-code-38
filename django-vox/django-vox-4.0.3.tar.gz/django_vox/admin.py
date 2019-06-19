import django.contrib.messages
import django.forms.utils
import django.http
from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.helpers import Fieldset, ACTION_CHECKBOX_NAME
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from . import models, registry


class SelectWithSubjectData(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_subjects = {}
        self.use_attachments = {}
        self.use_from_address = {}

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        option_attrs = {"data-editor": self.editor_types.get(value)}
        data_use_fields = {
            "data-subject": self.use_subjects,
            "data-from_address": self.use_from_address,
            "data-attachment": self.use_attachments,
        }
        for key, item in data_use_fields.items():
            option_attrs[key] = "true" if item.get(value) else "false"
        if selected:
            option_attrs.update(self.checked_attribute)
        return {
            "name": name,
            "value": value,
            "label": label,
            "selected": selected,
            "index": index,
            "attrs": option_attrs,
            "type": self.input_type,
            "template_name": self.option_template_name,
        }


class BackendChoiceField(forms.ChoiceField):
    widget = SelectWithSubjectData

    def __init__(self, choices=(), *args, **kwargs):
        backs = list(choices)
        choice_pairs = [(back.ID, back.VERBOSE_NAME) for back in backs]
        use_subjects = dict([(back.ID, back.USE_SUBJECT) for back in backs])
        use_from_address = dict([(back.ID, back.USE_FROM_ADDRESS) for back in backs])
        use_attachments = dict([(back.ID, back.USE_ATTACHMENTS) for back in backs])
        editor_types = dict([(back.ID, back.EDITOR_TYPE) for back in backs])
        super().__init__(choices=choice_pairs, *args, **kwargs)
        self.widget.use_subjects = use_subjects
        self.widget.use_attachments = use_attachments
        self.widget.use_from_address = use_from_address
        self.widget.editor_types = editor_types

    def set_backend_choices(self, backends):
        choice_pairs = [(back.ID, back.VERBOSE_NAME) for back in backends]
        use_subjects = dict([(back.ID, back.USE_SUBJECT) for back in backends])
        use_from_address = dict([(back.ID, back.USE_FROM_ADDRESS) for back in backends])
        use_attachments = dict([(back.ID, back.USE_ATTACHMENTS) for back in backends])
        editor_types = dict([(back.ID, back.EDITOR_TYPE) for back in backends])
        self.choices = choice_pairs
        self.widget.use_subjects = use_subjects
        self.widget.use_attachments = use_attachments
        self.widget.use_from_address = use_from_address
        self.widget.editor_types = editor_types


class TemplateInlineFormSet(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["notification"] = self.instance
        return kwargs


class TemplateForm(forms.ModelForm):
    backend = BackendChoiceField(choices=registry.backends.all())
    recipients = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False
    )
    attachments = forms.MultipleChoiceField(
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_("Attachments"), is_stacked=False),
    )

    class Meta:
        model = models.Template
        fields = [
            "notification",
            "backend",
            "recipients",
            "subject",
            "content",
            "attachments",
            "from_address",
            "bulk",
            "enabled",
        ]

    def __init__(self, notification=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if notification is not None:
            self.fields["recipients"].choices = notification.get_recipient_choices()
            self.fields["attachments"].choices = self.get_attachment_choices(
                notification
            )
        self.initial["attachments"] = [a.key for a in self.instance.attachments.all()]
        self.initial["recipients"] = self.instance.recipients.split(",")

    def save(self, commit=True):
        # data will be a set of the added items
        self.instance.recipients = ",".join(set(self.cleaned_data["recipients"]))
        instance = super().save(commit=commit)
        if commit:
            attach_data = set(self.cleaned_data["attachments"])
            # we need to sync it with the saved items
            query = ~Q(key__in=attach_data) & Q(template=instance)
            models.TemplateAttachment.objects.filter(query).delete()
            added_attachments = []
            for attachment in instance.attachments.all():
                if attachment.key in attach_data:
                    attach_data.remove(attachment.key)
            for key in attach_data:
                added_attachments.append(
                    models.TemplateAttachment(template=instance, key=key)
                )
            if added_attachments:
                models.TemplateAttachment.objects.bulk_create(added_attachments)
        return instance

    def clean(self):
        data = self.cleaned_data
        notification = data["notification"]
        try:
            notification.preview(data["backend"], data["content"])
        except Exception as exc:
            raise ValidationError(str(exc))

    @staticmethod
    def get_attachment_choices(notification):
        param_models = notification.get_parameter_models()
        for model_key, model in param_models.items():
            label = "" if model_key == "object" else model_key.title()
            yield from models.get_model_attachment_choices(label, model_key, model)


class SiteContactForm(forms.ModelForm):
    protocol = forms.ChoiceField(choices=registry.get_protocol_choices())

    class Meta:
        model = models.SiteContact
        fields = ["name", "protocol", "address", "enable_filter"]


class NotificationForm(forms.ModelForm):
    class Meta:
        model = models.Notification
        fields = ["codename", "object_type", "description", "target_type"]


class NotificationIssueForm(forms.Form):

    objects = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Objects"),
        widget=FilteredSelectMultiple(verbose_name=_("Objects"), is_stacked=False),
        help_text=_("A separate notification will be issued for each object."),
    )

    def __init__(self, notification, *args, **kwargs):
        self.notification = notification
        model_cls = notification.object_type.model_class()
        self.declared_fields["objects"].queryset = model_cls.objects
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if commit:
            objects = self.cleaned_data["objects"]
            for obj in objects:
                self.notification.issue(obj)


class TemplateInline(admin.StackedInline):
    model = models.Template
    form = TemplateForm
    formset = TemplateInlineFormSet
    min_num = 0
    extra = 0


class NotificationAdmin(admin.ModelAdmin):
    change_form_template = "django_vox/change_form.html"
    list_display = (
        "__str__",
        "description",
        "required",
        "template_count",
        "last_updated",
    )
    list_filter = ("object_type",)
    inlines = [TemplateInline]
    form = NotificationForm
    issue_form = NotificationIssueForm
    issue_template = "django_vox/issue.html"

    fields = ["codename", "object_type", "description"]

    class Media:
        css = {
            "all": ("django_vox/markitup/images.css", "django_vox/markitup/style.css")
        }
        js = (
            "admin/js/jquery.init.js",
            "django_vox/markitup/jquery.markitup.js",
            "django_vox/notification_fields.js",
        )

    # only show inlines on change forms
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []

    def get_urls(self):
        return [
            url(
                r"^preview/(?P<backend_id>.+)/$",
                self.admin_site.admin_view(self.preview),
                name="django_vox_preview",
            ),
            url(
                r"^(?P<notification_id>\w+)/preview/(?P<backend_id>.+)/$",
                self.admin_site.admin_view(self.notification_preview),
                name="django_vox_notification_preview",
            ),
            url(
                r"^(?P<notification_id>\w+)/variables/$",
                self.admin_site.admin_view(self.variables),
                name="django_vox_variables",
            ),
            url(
                r"^(?P<notification_id>\w+)/issue/$",
                self.admin_site.admin_view(self.issue),
                name="django_vox_issue",
            ),
        ] + super().get_urls()

    def preview(self, request, backend_id):
        if not request.user.is_staff:
            raise PermissionDenied
        if request.method != "POST":
            return django.http.HttpResponseNotAllowed(("POST",))

        try:
            backend = registry.backends.by_id(backend_id)
            message = request.POST["body"]
            params = {}
            result = backend.preview_message("", message, params)
        except Exception as exc:
            result = "Unable to make preview: {}".format(str(exc))
        return django.http.HttpResponse(result)

    def notification_preview(self, request, notification_id, backend_id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        notification = self.get_object(request, unquote(notification_id))
        if notification is None:
            raise django.http.Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": force_text(self.model._meta.verbose_name),
                    "key": escape(notification_id),
                }
            )
        if request.method != "POST":
            return django.http.HttpResponseNotAllowed(("POST",))
        try:
            result = notification.preview(backend_id, request.POST["body"])
        except Exception as exc:
            result = "Unable to make preview: {}".format(str(exc))
        return django.http.HttpResponse(result)

    def variables(self, request, notification_id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        notification = self.get_object(request, unquote(notification_id))
        if notification is None:
            raise django.http.Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": force_text(self.model._meta.verbose_name),
                    "key": escape(notification_id),
                }
            )
        if request.method != "POST":
            return django.http.HttpResponseNotAllowed(("POST",))
        result = notification.get_recipient_variables()
        return django.http.JsonResponse(result, safe=False)

    def issue(self, request, notification_id, form_url=""):
        if not self.has_change_permission(request):
            raise PermissionDenied
        notification = self.get_object(request, unquote(notification_id))
        if notification is None:
            raise django.http.Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": force_text(self.model._meta.verbose_name),
                    "key": escape(notification_id),
                }
            )
        if request.method == "POST":
            form = self.issue_form(notification, request.POST)
            if form.is_valid():
                form.save()
                msg = gettext("Notification sent successfully.")
                django.contrib.messages.success(request, msg, fail_silently=True)
                return django.http.HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            notification._meta.app_label,
                            notification._meta.model_name,
                        ),
                        args=(notification.pk,),
                    )
                )
        elif request.method == "GET":
            form = self.issue_form(notification)
        else:
            return django.http.HttpResponseNotAllowed(("POST",))

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Send notification: %s") % escape(str(notification)),
            "media": self.media + admin_form.media,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.model._meta,
            "original": notification,
            "save_as": False,
            "show_save": True,
        }
        context.update(self.admin_site.each_context(request))
        request.current_app = self.admin_site.name

        status = 200 if form.is_valid() else 400
        return TemplateResponse(request, self.issue_template, context, status=status)

    def get_readonly_fields(self, request, obj=None):
        if self.has_delete_permission(request, obj):
            return ["object_type"] if obj else []
        return [
            "codename",
            "object_type",
            "description",
            "required",
            "actor_type",
            "target_type",
        ]

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return super().has_delete_permission(request)
        return super().has_delete_permission(request) and not obj.from_code

    def save_form(self, request, form, change):
        result = super().save_form(request, form, change)
        if not change:
            result.from_code = False
        return result

    @staticmethod
    def template_count(obj):
        return obj.template_set.count()


class NotifyForm(forms.Form):

    backend = BackendChoiceField(label=_("Backend"))
    from_address = forms.CharField(label=_("From Address"), required=False)
    subject = forms.CharField(label=_("Subject"), required=False)
    content = forms.CharField(label=_("Content"), required=True, widget=forms.Textarea)

    def __init__(self, backends, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["data-preview-url"] = reverse(
            "admin:django_vox_preview", args=("__backend__",)
        )
        self.fields["backend"].set_backend_choices(backends)


def notify(modeladmin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied

    notification = models.OneTimeNotification
    model = queryset.model
    protocols = set()
    opts = modeladmin.model._meta

    if model in registry.objects:
        registration = registry.objects[model].registration
        # we don't want to have to evaluate this too many times
        query_list = list(queryset)

        if isinstance(registration, registry._ModelRegistration):
            for obj in query_list:
                for contact in obj.get_contacts_for_notification(notification):
                    protocols.add(contact.protocol)
        else:
            protocols = set(registration.get_supported_protocols())

        # now filter protocols to make sure there's an appropriate backend
        all_backends = tuple(
            b for p in protocols for b in registry.backends.by_protocol(p)
        )
        backends = tuple(b for b in all_backends if b.ALLOW_MANUAL_SENDING)
    else:
        all_backends = ()
        backends = ()
        protocols = ()
        query_list = []

    if not backends:
        form = NotifyForm(backends, {})
        if all_backends:
            error = "The {} model has contacts, but they don’t support manual sending."
        elif protocols:
            error = "The {} model has contacts, but they don’t have enabled backends."
        else:
            error = "The {} model is not registered or missing contact methods."
        form.full_clean()
        form.add_error("backend", error.format(model._meta.verbose_name))
    elif request.POST.get("post"):
        form = NotifyForm(backends, request.POST)
    else:
        form = NotifyForm(backends)
    context = {
        "title": _("Notify"),
        "opts": opts,
        "form": form,
        "action_checkbox_name": ACTION_CHECKBOX_NAME,
        "queryset": query_list,
        "fieldset": Fieldset(
            form, fields=("backend", "from_address", "subject", "content")
        ),
    }

    if request.POST.get("post") == "yes":
        if form.is_valid():
            # okay, now we issue the notification
            backend = registry.backends.by_id(form.cleaned_data["backend"])
            contacts = [
                c
                for cs in (
                    registration.get_contacts(obj, backend.PROTOCOL, notification)
                    for obj in query_list
                )
                for c in cs
            ]
            result = notification.send(
                backend.ID,
                contacts,
                form.cleaned_data["from_address"],
                form.cleaned_data["subject"],
                form.cleaned_data["content"],
            )
            if result is None:
                msg = gettext("Notification sent successfully.")
                django.contrib.messages.success(request, msg, fail_silently=True)
            else:
                msg = gettext("Error sending notification (%s).") % result
                django.contrib.messages.error(request, msg, fail_silently=True)
            return django.http.HttpResponseRedirect(
                reverse(
                    "%s:%s_%s_changelist"
                    % (modeladmin.admin_site.name, opts.app_label, opts.model_name)
                )
            )

    return TemplateResponse(request, "django_vox/notify.html", context)


class SiteContactSettingInline(admin.TabularInline):
    model = models.SiteContactSetting


class SiteContactAdmin(admin.ModelAdmin):
    form = SiteContactForm
    inlines = [SiteContactSettingInline]
    list_display = ("name", "address", "protocol")


def resend(_admin, _request, queryset):
    for failed in queryset.all():
        failed.resend()


class FailedMessageAdmin(admin.ModelAdmin):
    list_display = ("backend", "from_address", "to_addresses", "created_at")
    list_filter = ("backend", "from_address", "to_addresses")
    actions = (resend,)

    # there's no real point in an add button here
    def has_add_permission(self, request):
        return False


admin.site.register(models.SiteContact, SiteContactAdmin)
admin.site.register(models.FailedMessage, FailedMessageAdmin)
admin.site.register(models.Notification, NotificationAdmin)
