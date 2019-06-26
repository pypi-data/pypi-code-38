from unittest import mock

import django.http
from django.contrib.admin import AdminSite
from django.contrib.auth import models as auth_models
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.test import TestCase

import django_vox.admin
import django_vox.models
import django_vox.registry
import django_vox.backends.activity

from . import models


class MockAnonUser:

    is_active = False
    is_staff = False
    is_authenticated = False

    @staticmethod
    def has_perm(_perm):
        return False


class MockSuperUser:

    is_active = True
    is_staff = True
    is_authenticated = True

    @staticmethod
    def has_perm(_perm):
        return True


class MockRequest:
    def __init__(self, method, parameters=None):
        self.method = method
        self.user = MockSuperUser()
        self.GET = {}
        self.POST = {}
        if parameters is not None:
            if method == "POST":
                self.POST = parameters
            else:
                self.GET = parameters
        self.META = {"SCRIPT_NAME": ""}


class MockAnonRequest(MockRequest):
    def __init__(self, method, parameters=None):
        super().__init__(method, parameters)
        self.user = MockAnonUser()


class VariableTests(TestCase):
    """Test the variables that are used in admin"""

    fixtures = ["test"]

    @staticmethod
    def test_variables():
        notification = models.ArticleRegistration.created.get_notification(
            models.Article
        )
        variables = notification.get_recipient_variables()
        assert {
            "si",
            "se",
            "c:sub",
            "c:author",
            "_static",
            "re:sub",
            "re:author",
        } == variables.keys()
        # check recipient variables first:
        for key in ("si", "se", "c:sub", "c:author"):
            assert variables[key]["value"] == "recipient"
        static = variables["_static"]
        assert len(static) == 3
        assert static[0]["label"] == "Article"
        assert static[0]["value"] == "object"
        assert static[1]["label"] == "Actor"
        assert static[1]["value"] == "actor"
        assert static[2]["label"] == "Target"
        assert static[2]["value"] == "target"


class TemplateFormTests(TestCase):
    """
    Test template specific forms
    """

    fixtures = ["test"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = django_vox.models.Template
        self.form_class = django_vox.admin.TemplateForm

    def test_template_form(self):
        template = self.model_class.objects.get(pk=1)
        notification = template.notification
        blank_form = self.form_class()
        add_form = self.form_class(notification=notification)
        change_form = self.form_class(notification=notification, instance=template)

        add_initial = {"attachments": [], "recipients": ["re"]}
        change_initial = {
            "notification": 7,
            "backend": "email-html",
            "subject": "Subscriber email",
            "content": ...,
            "recipients": ["c:sub"],
            "from_address": "",
            "enabled": True,
            "bulk": False,
            "attachments": ["object.author.vcard"],
        }

        assert add_initial == add_form.initial
        for key, value in change_initial.items():
            if value is not ...:
                assert value == change_form.initial.get(key)

        assert [] == blank_form.fields["recipients"].choices
        assert [] == blank_form.fields["attachments"].choices
        re_choices = [
            ("si", "Site Contacts"),
            ("re:sub", "Target's Subscribers"),
            ("re:author", "Target's Author"),
            ("se", "Actor"),
            ("c:sub", "Subscribers"),
            ("c:author", "Author"),
        ]
        assert re_choices == add_form.fields["recipients"].choices
        at_choices = [
            ("target.author.vcard", "Target/Author/Contact Info"),
            ("actor.vcard", "Actor/Contact Info"),
            ("object.author.vcard", "Author/Contact Info"),
        ]
        assert at_choices == add_form.fields["attachments"].choices

        backend_opts = add_form.fields["backend"].widget.optgroups(
            "backend", "email-html"
        )
        opt = next(x[0] for _, x, _idx in backend_opts if x[0]["value"] == "email-html")

        opt_attrs = {
            "data-editor": "html",
            "data-subject": "true",
            "data-from_address": "true",
            "data-attachment": "true",
            "selected": True,
        }
        assert "Email (HTML)" == opt["label"]
        assert opt["selected"]
        assert opt_attrs == opt["attrs"]

    def test_template_form_save(self):
        template = self.model_class.objects.get(pk=1)
        data = {
            "attachments": ["actor.vcard", "object.author.vcard"],
            "notification": 1,
            "backend": "email-html",
            "content": "bad content {% if %}",
        }
        change_form = self.form_class(
            data=data, notification=template.notification, instance=template
        )
        change_form.full_clean()
        assert not change_form.is_valid()
        data["content"] = "okay content"
        change_form.full_clean()
        assert change_form.is_valid()
        change_form.save()

        new_attachments = self.model_class.objects.get(pk=1).attachments.all()
        new_attachment_keys = {"actor.vcard", "object.author.vcard"}
        assert new_attachment_keys == set((a.key for a in new_attachments))


class NotificationAdminTests(TestCase):
    """Test NotificationAdmin"""

    fixtures = ["test"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = django_vox.models.Notification
        self.admin = django_vox.admin.NotificationAdmin(self.model_class, AdminSite())

    def test_template_count(self):
        model_obj = self.model_class.objects.get_by_natural_key(
            "tests", "article", "created"
        )
        assert 2 == self.admin.template_count(model_obj)

    def test_get_urls(self):
        names = (u.name for u in self.admin.get_urls() if u.name is not None)
        name_set = set(
            (un for un in names if not un.startswith("django_vox_notification"))
        )
        assert 3 == len(name_set)
        expected = {"django_vox_issue", "django_vox_preview", "django_vox_variables"}
        assert expected == name_set

    def test_fields(self):
        base_fields = ["codename", "object_type", "description"]
        from_code_ro = [
            "codename",
            "object_type",
            "description",
            "required",
            "actor_type",
            "target_type",
        ]
        new_obj = self.model_class()
        model_obj = self.model_class.objects.get_by_natural_key(
            "tests", "article", "created"
        )
        request = MockRequest("GET")
        assert base_fields == self.admin.get_fields(request)
        assert [] == self.admin.get_readonly_fields(request)
        assert ["object_type"] == self.admin.get_readonly_fields(request, new_obj)
        assert from_code_ro == self.admin.get_readonly_fields(request, model_obj)

    def test_issue(self):
        notification = self.model_class.objects.get_by_natural_key(
            "tests", "article", "created"
        )
        obj = models.Article.objects.first()
        with mock.patch("django_vox.models.Notification.issue"):
            # no POST parameters, so won't be valid
            request = MockRequest("POST", {})
            response = self.admin.issue(request, str(notification.id))
            assert response.status_code == 400
            assert "This field is required" in response.rendered_content
            # this should 404
            with self.assertRaises(django.http.Http404):
                self.admin.issue(request, "9000")
            # this POST should work
            # we have to perform some malarky because of an isinstance
            # check in django 1.10
            request = MockRequest("POST", {"objects": (obj.pk,)})
            mock_request = mock.Mock(spec=django.http.HttpRequest)
            for attr in request.__dir__():
                if not attr.startswith("_"):
                    setattr(mock_request, attr, getattr(request, attr))
            response = self.admin.issue(mock_request, str(notification.id))
            assert response.status_code == 302

    def test_get_inline_instances(self):
        request = MockRequest("GET", {})
        obj = self.model_class.objects.get_by_natural_key("tests", "article", "created")
        assert [] == self.admin.get_inline_instances(request)
        inline = self.admin.get_inline_instances(request, obj=obj)[0]
        formset = inline.get_formset(request, obj=obj)(instance=obj)
        assert obj == formset.get_form_kwargs(0)["notification"]

    def test_preview(self):
        anon_request = MockAnonRequest("POST", {"body": "Hello World"})
        get_request = MockRequest("GET", {"body": "Hello World"})
        post_request = MockRequest("POST", {"body": "Hello World"})

        with self.assertRaises(PermissionDenied):
            self.admin.preview(anon_request, "email-html")

        response = self.admin.preview(get_request, "email-html")
        assert response.status_code == 405

        response = self.admin.preview(post_request, "email-html9000")
        assert response.status_code == 200
        assert b"Unable to make preview: 'email-html9000'" == response.content

        response = self.admin.preview(post_request, "email-html")
        assert response.status_code == 200
        assert b"Hello World" == response.content

    def test_notification_preview(self):
        anon_request = MockAnonRequest("POST", {"body": "Hello World"})
        get_request = MockRequest("GET", {"body": "Hello World"})
        syntax_request = MockRequest("POST", {"body": "{% if %}"})
        good_request = MockRequest("POST", {"body": "Hello {{content}}"})
        backend = "email-html"
        bad_backend = "email-html9000"
        notification = "7"  # article created notification id
        bad_notification = "9000"

        with self.assertRaises(PermissionDenied):
            self.admin.notification_preview(anon_request, notification, backend)

        with self.assertRaises(django.http.Http404):
            self.admin.notification_preview(good_request, bad_notification, backend)

        response = self.admin.notification_preview(
            good_request, notification, bad_backend
        )
        assert 200 == response.status_code
        assert b"Unable to make preview: 'email-html9000'" == response.content

        response = self.admin.notification_preview(get_request, notification, backend)
        assert response.status_code == 405

        response = self.admin.notification_preview(
            syntax_request, notification, backend
        )
        assert response.status_code == 200
        assert response.content.startswith(b"Unable to make preview:")

        response = self.admin.notification_preview(good_request, notification, backend)
        assert response.status_code == 200
        assert b"Hello Why are there so many blog demos" == response.content


class NotifyAdminTests(TestCase):
    """Test notify actoin"""

    fixtures = ["test"]

    def test_subscribers(self):
        model_admin = django_vox.admin.NotificationAdmin(models.Subscriber, AdminSite())
        queryset = models.Subscriber.objects.all()
        get_anon_request = MockAnonRequest("GET")
        get_request = MockRequest("GET")
        bad_post_request = MockRequest("POST", {"post": "yes", "action": "notify"})
        post_data = {
            "post": "yes",
            "action": "notify",
            "backend": "email-html",
            "_selected_action": 1,
            "subject": "foo",
            "content": "bar",
        }
        post_request = MockRequest("POST", post_data)

        with self.assertRaises(PermissionDenied):
            django_vox.admin.notify(model_admin, get_anon_request, queryset)

        result = django_vox.admin.notify(model_admin, get_request, queryset)
        assert 200 == result.status_code

        # This shouldn't actually send, because it's missing required data
        assert 0 == len(mail.outbox)
        django_vox.admin.notify(model_admin, bad_post_request, queryset)
        assert 0 == len(mail.outbox)
        # now let's actually try to send this thing
        django_vox.admin.notify(model_admin, post_request, queryset)
        assert 1 == len(mail.outbox)
        assert "bar" == mail.outbox[0].body
        # test message sending failure
        with self.settings(EMAIL_BACKEND="Can't import this!"):
            django_vox.admin.notify(model_admin, post_request, queryset)
        failed_message = django_vox.models.FailedMessage.objects.all()
        assert len(failed_message) == 1
        assert (
            "Can't import this! doesn't look like a module path"
            == failed_message[0].error
        )

    def test_unregistered(self):
        # this model's not registered
        model_admin = django_vox.admin.NotificationAdmin(auth_models.Group, AdminSite())
        queryset = auth_models.Group.objects.all()
        get_request = MockRequest("GET")
        result = django_vox.admin.notify(model_admin, get_request, queryset)
        assert 200 == result.status_code
        assert (
            "The group model is not registered or missing contact methods."
            in result.rendered_content
        )

    def test_no_enabled_backends(self):
        model_admin = django_vox.admin.NotificationAdmin(models.Subscriber, AdminSite())
        queryset = models.Subscriber.objects.all()
        get_request = MockRequest("GET")
        # now we'll disable all the backends
        backends = django_vox.registry.BackendManager([])
        with mock.patch("django_vox.registry.backends", new=backends):
            result = django_vox.admin.notify(model_admin, get_request, queryset)
            assert 200 == result.status_code
            assert (
                "The subscriber model has contacts, "
                "but they don’t have enabled backends." in result.rendered_content
            )

    def test_no_sendabled_backends(self):
        model_admin = django_vox.admin.NotificationAdmin(models.Subscriber, AdminSite())
        queryset = models.Subscriber.objects.all()
        get_request = MockRequest("GET")
        # now we'll disable all the backends
        backends = django_vox.registry.BackendManager(
            [django_vox.backends.activity.Backend]
        )
        with mock.patch("django_vox.registry.backends", new=backends):
            result = django_vox.admin.notify(model_admin, get_request, queryset)
            assert 200 == result.status_code
            assert (
                "The subscriber model has contacts, "
                "but they don’t support manual sending." in result.rendered_content
            )


def test_notify_form():
    form = django_vox.admin.NotifyForm(
        django_vox.registry.backends.by_protocol("email")
    )
    backend_ids = {"email-md", "email-html", "postmark-template", "email"}
    preview_url = "/admin/django_vox/notification/preview/__backend__/"
    assert preview_url == form.fields["content"].widget.attrs["data-preview-url"]
    assert backend_ids == set((key for key, _ in form.fields["backend"].choices))
