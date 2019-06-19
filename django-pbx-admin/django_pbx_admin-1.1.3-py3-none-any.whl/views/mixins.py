import urllib

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy


class PermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("pbx_admin:login")

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class FooterMixin:
    """Changes success_url to object's edit url if
    there is _continue in post request.
    Otherwise redirects to attribute default_success_url
    Also adds cancel_url.
    """

    success_url = None
    cancel_url = None
    no_cancel = False
    admin = None

    def get_success_url(self):
        if self.request.POST.get("_continue"):
            kwargs = self.kwargs.copy()
            if self.admin.url_kwarg not in kwargs:
                obj = self.object or self.get_object()
                if self.admin.pk_url_kwarg is not None:
                    kwargs[self.admin.url_kwarg] = obj.pk
                if self.admin.slug_field is not None:
                    kwargs[self.admin.url_kwarg] = getattr(obj, self.admin.slug_field)
            return self.admin.edit_url(**kwargs)
        admin_url = self.admin.get_success_url(self)
        if admin_url:
            return admin_url
        if self.success_url:
            return self.success_url
        return self.get_default_url()

    def get_cancel_url(self):
        admin_url = self.admin.get_cancel_url(self)
        if admin_url:
            return admin_url
        if self.cancel_url:
            return self.cancel_url
        return self.get_default_url()

    def get_default_url(self):
        kwargs = self.kwargs.copy()
        kwargs.pop(self.admin.pk_url_kwarg, "")
        kwargs.pop(self.admin.slug_url_kwarg, "")
        return self.admin.list_url(**kwargs)


class MessagesMixin:
    """
    Handle messages from django messages framework. Divide messages into
    two groups: to be display as bar or as modal.
    """

    def _update_messages(self, context):
        messages_storage = messages.get_messages(self.request)
        context["bar_messages"] = []
        context["modal_messages"] = []
        for msg in messages_storage:
            msg.tags_set = set(msg.tags.split())
            if {"bar", "success"} & msg.tags_set:
                context["bar_messages"].append(msg)
            else:
                context["modal_messages"].append(msg)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self._update_messages(context)


class AdminViewMixin(PermissionMixin, MessagesMixin):
    admin = None

    success_message_template = "%s"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["admin"] = self.admin
        context["model"] = self.admin.model
        context["opts"] = self.admin.opts

        perms = self.admin.get_model_perms(self.request)
        context["model_perms"] = perms
        context["can_add"] = perms["add"] and bool(self.admin.add_view_class)
        context["can_change"] = perms["change"] and bool(self.admin.edit_view_class)
        context["can_delete"] = perms["delete"] and bool(self.admin.delete_view_class)
        context["can_duplicate"] = perms["duplicate"] and bool(self.admin.duplicate_view_class)

        context.update(self.admin.get_context_data(self.request, **self.kwargs))

        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            self.admin.dispatch(self)
        except PermissionDenied:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        obj_name = self.admin.opts.verbose_name.capitalize()
        if "name" in cleaned_data:
            obj_name += ' "{}" '.format(cleaned_data["name"])
        return self.success_message_template % obj_name


class FormsetsMixin:
    def get_formset_kwargs(self):
        kwargs = {}
        if hasattr(self, "object"):
            kwargs["instance"] = self.object
        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})
        return kwargs

    def get_formsets(self):
        formsets = self.admin.get_formsets(getattr(self, "object", None))
        return [
            formset(prefix=prefix, **self.get_formset_kwargs())
            for prefix, formset in formsets.items()
        ]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except AttributeError:
            pass

        form = self.get_form()
        formsets = self.get_formsets()

        if form.is_valid() and all(formset.is_valid() for formset in formsets):
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets=None):
        handler = super().form_valid(form)

        if formsets:
            for formset in formsets:
                if hasattr(self, "object"):
                    formset.instance = self.object
                formset.save()

        return handler

    def form_invalid(self, form, formsets=None):
        context = self.get_context_data(form=form, formsets=formsets)
        return self.render_to_response(context)


class ListSelectionMixin:
    def get_filtered_queryset(self, request):
        ids = request.POST.get("ids", "")
        queryset = self.admin.get_queryset(self.request, **self.kwargs)

        if ids == "all":
            params = request.POST.get("search_params", "")
            form_class = self.admin.search_form_class
            form = form_class(
                data={k: v[0] for k, v in urllib.parse.parse_qs(params[1:]).items()}
            )
            if form.is_valid():
                return queryset.filter(**form.get_filters())
        elif ids:
            return queryset.filter(pk__in=ids.split(","))

        return queryset.none()
