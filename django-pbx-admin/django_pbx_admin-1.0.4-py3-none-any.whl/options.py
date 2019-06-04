import itertools

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import get_permission_codename
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import ForeignKey
from django.forms import (
    ModelForm,
    HiddenInput,
    modelform_factory,
    inlineformset_factory,
)
from django.http import Http404
from django.urls import reverse, include
from django.utils.translation import ugettext_lazy as _

from pbx_admin.forms import SearchForm
from pbx_admin.views import (
    AdminListView,
    AdminCreateView,
    AdminUpdateView,
    AdminShowView,
    AdminDeleteView,
    AdminDeleteMultipleView,
    CSVExportView,
)


class ModelAdmin:
    model = None
    queryset = None

    # parent-children relation
    parent = None
    parent_field = None
    is_inner = False

    # url pattern
    namespace = None
    pk_url_kwarg = None
    slug_url_kwarg = None
    slug_url_pattern = None
    slug_field = None

    # add/edit view
    form_class = ModelForm
    fields = ()
    fieldsets = ()

    # add/edit view actions
    success_url = None
    cancel_url = None
    no_cancel = False

    # list view
    search_form_class = None
    list_display = ("id",)
    list_ordering = None
    export_fields = None  # fields for csv export

    # add & duplicate modals
    add_modal_fields = ()
    add_modal_form_attrs = {}
    duplicate_modal_fields = ()
    duplicate_async = False

    # templates
    list_template_name = "pbx_admin/list.html"
    add_template_name = None
    edit_template_name = "pbx_admin/edit.html"

    # view classes
    list_view_class = AdminListView
    add_view_class = AdminCreateView
    edit_view_class = AdminUpdateView
    show_view_class = AdminShowView
    delete_view_class = AdminDeleteView
    delete_multiple_view_class = AdminDeleteMultipleView
    # Duplicate View Class have to implemented separately
    duplicate_view_class = None
    csv_export_view_class = CSVExportView

    # other
    only_menu_actions = False

    def __init__(self, model, admin_site, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = model
        if self.queryset is None:
            self.queryset = self.model.objects.all()
        self.opts = self.model._meta
        self.admin_site = admin_site
        self.children = []

        if self.namespace is None:
            self.namespace = self.opts.model_name

        if parent:
            self.parent = parent
            self.parent.children.append(self)
            parent_model = self.parent.model._meta.concrete_model
            parent_fields = [
                field
                for field in self.model._meta.fields
                if isinstance(field, ForeignKey) and field.related_model == parent_model
            ]
            if parent_fields:
                self.parent_field = parent_fields[0]

        if self.add_template_name is None:
            self.add_template_name = self.edit_template_name

        self._init_url_kwarg()
        self._init_fields()
        self._init_forms()
        self._init_formsets()

    def __str__(self):
        return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)

    def _init_url_kwarg(self):
        # urls init
        if not self.pk_url_kwarg and not self.slug_url_kwarg:
            self.pk_url_kwarg = "pk"
            parent = self.parent
            while parent:
                self.pk_url_kwarg = "sub_" + self.pk_url_kwarg
                parent = parent.parent

        if self.slug_url_kwarg is not None and self.slug_field is None:
            self.slug_field = self.slug_url_kwarg

        self.url_kwarg = self.pk_url_kwarg or self.slug_url_kwarg

    def _init_fields(self):
        if self.fields and self.fieldsets:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'fieldsets' is not permitted."
            )
        elif self.fieldsets:
            self.fields = self._get_fields_from_fieldsets(self.fieldsets)
        elif self.fields:
            self.fieldsets = ((None, {"fields": self.fields}),)
        elif hasattr(self.form_class, "Meta") and hasattr(
            self.form_class.Meta, "fields"
        ):
            # if fields and fieldsets are not defined,
            # use all form fields by defining __all__
            # this allows to include also dynamically generated forms
            # e.g. for EditorStep & EditorComponent
            self.fields = self.form_class.Meta.fields
            self.fieldsets = ((None, {"fields": "__all__"}),)

    def _init_forms(self):
        if self.form_class is None:
            self.form_class = ModelForm

        try:
            fields = self.form_class.Meta.fields
        except AttributeError:
            fields = self.fields

        p_field = self.parent_field
        if p_field and p_field.name not in fields:
            try:
                widgets = self.form_class.Meta.widgets.copy()
            except AttributeError:
                widgets = {}
            widgets[p_field.name] = HiddenInput
            fields = (p_field.name,) + tuple(fields)
            self.form_class = modelform_factory(
                self.model,
                form=self.form_class,
                fields=(p_field.name,) + tuple(fields),
                widgets=widgets,
            )
        else:
            self.form_class = modelform_factory(
                self.model, form=self.form_class, fields=fields
            )

        if not self.search_form_class:
            model_fields = {f.name for f in self.model._meta.fields}
            self.search_form_class = modelform_factory(
                self.model,
                form=SearchForm,
                fields=[f for f in self.list_display if f in model_fields],
            )

        if not self.export_fields:
            self.export_fields = (
                self.form_class.Meta.fields if self.form_class else self.fields
            )
            if not any(field in self.export_fields for field in ("id", "pk")):
                self.export_fields = ("id",) + tuple(self.export_fields)

    def _init_formsets(self):
        self.formsets = {}
        formset_id = 0
        for title, fieldset in self.fieldsets:
            if "formset" in fieldset:
                formset = fieldset["formset"]
                fieldset.setdefault("prefix", f"formset-{formset_id}")

                fieldsets = fieldset.get("fieldsets")
                if fieldsets:
                    fields = self._get_fields_from_fieldsets(fieldsets)
                    form = modelform_factory(
                        formset.model, form=formset.form, fields=fields
                    )
                    formset = inlineformset_factory(
                        self.model, formset.model, form=form, formset=formset
                    )

                self.formsets[fieldset["prefix"]] = formset
                formset_id += 1

    def _get_fields_from_fieldsets(self, fieldsets):
        return tuple(
            itertools.chain(
                *(fieldset.get("fields", ()) for title, fieldset in fieldsets)
            )
        )

    def get_object_url_pattern(self):
        if self.pk_url_kwarg is not None:
            return rf"(?P<{self.pk_url_kwarg}>\d+)"
        if self.slug_url_kwarg is not None:
            return rf"(?P<{self.slug_url_kwarg}>{self.slug_url_pattern})"

    def build_url(self, name, **kwargs):
        namespace_list = [self.namespace]
        parent = self.parent
        while parent:
            namespace_list = [parent.namespace] + namespace_list
            parent = parent.parent
        namespace = ":".join([self.admin_site.name] + namespace_list)
        return reverse(f"{namespace}:{name}", kwargs=kwargs)

    def list_url(self, **kwargs):
        return self.build_url("list", **kwargs)

    def add_url(self, **kwargs):
        return self.build_url("add", **kwargs)

    def edit_url(self, **kwargs):
        return self.build_url("edit", **kwargs)

    def delete_url(self, **kwargs):
        return self.build_url("delete", **kwargs)

    def show_url(self, **kwargs):
        return self.build_url("show", **kwargs)

    @property
    def can_duplicate(self):
        return self.duplicate_view_class and hasattr(self.model, "duplicate")

    @property
    def hide_from_index(self):
        return self.parent or self.is_inner

    def get_urlpatterns(self):
        urlpatterns = []

        if self.list_view_class:
            urlpatterns.append(url(r"^$", self.list_view, name="list"))

        obj_pattern = self.get_object_url_pattern()

        if self.add_view_class:
            urlpatterns.append(url(r"^add/$", self.add_view, name="add"))
        if self.edit_view_class:
            urlpatterns.append(
                url(
                    rf"^{obj_pattern}/$" if obj_pattern else "",
                    self.edit_view,
                    name="edit",
                )
            )

        if self.delete_view_class:
            urlpatterns.append(
                url(rf"^{obj_pattern}/delete/$", self.delete_view, name="delete")
            )
        if self.delete_multiple_view_class:
            urlpatterns.append(
                url(r"^delete/$", self.delete_multiple_view, name="delete-multiple")
            )

        if self.show_view_class:
            urlpatterns.append(
                url(
                    rf"^{obj_pattern}/show/$" if obj_pattern else "",
                    self.show_view,
                    name="show",
                )
            )

        if self.can_duplicate:
            urlpatterns.append(
                url(
                    rf"^{obj_pattern}/duplicate/$",
                    self.duplicate_view,
                    name="duplicate",
                )
            )

        if self.csv_export_view_class:
            urlpatterns.append(
                url(r"^export-to-csv", self.csv_export_view, name="csv-export")
            )

        for admin in self.children:
            urlpatterns += admin.get_urls()

        return urlpatterns

    def get_urls(self):
        urlpatterns = (self.get_urlpatterns(), "pbx_admin")

        if self.parent:
            prefix = r"{}/{}/".format(
                self.parent.get_object_url_pattern(), self.namespace
            )
        else:
            prefix = r"^{}/".format(self.namespace)

        return [url(prefix, include(urlpatterns, namespace=self.namespace))]

    def _get_default_view_kwargs(self):
        return {"admin": self, "model": self.model}

    def _get_single_object_view_kwargs(self):
        kwargs = self._get_default_view_kwargs()
        kwargs.update(
            {
                "pk_url_kwarg": self.pk_url_kwarg,
                "slug_url_kwarg": self.slug_url_kwarg,
                "slug_field": self.slug_field,
                "success_url": self.success_url,
                "cancel_url": self.cancel_url,
            }
        )
        return kwargs

    def list_view(self, request, *args, **kwargs):
        view_kwargs = self._get_default_view_kwargs()
        return self.list_view_class.as_view(
            form_class=self.search_form_class,
            list_display=self.list_display,
            ordering=self.list_ordering or self.list_display,
            template_name=self.list_template_name,
            **view_kwargs,
        )(request, *args, **kwargs)

    def add_view(self, request, *args, **kwargs):
        view_kwargs = self._get_single_object_view_kwargs()
        return self.add_view_class.as_view(
            form_class=self.form_class,
            template_name=self.add_template_name,
            no_cancel=self.no_cancel,
            **view_kwargs,
        )(request, *args, **kwargs)

    def edit_view(self, request, *args, **kwargs):
        view_kwargs = self._get_single_object_view_kwargs()
        return self.edit_view_class.as_view(
            form_class=self.form_class,
            template_name=self.edit_template_name,
            no_cancel=self.no_cancel,
            **view_kwargs,
        )(request, *args, **kwargs)

    def delete_view(self, request, *args, **kwargs):
        view_kwargs = self._get_single_object_view_kwargs()
        return self.delete_view_class.as_view(**view_kwargs)(request, *args, **kwargs)

    def delete_multiple_view(self, request, *args, **kwargs):
        view_kwargs = self._get_default_view_kwargs()
        return self.delete_multiple_view_class.as_view(**view_kwargs)(
            request, *args, **kwargs
        )

    def duplicate_view(self, request, *args, **kwargs):
        return self.duplicate_view_class.as_view(
            admin=self,
            model=self.model,
            pk_url_kwarg=self.pk_url_kwarg,
            slug_url_kwarg=self.slug_url_kwarg,
            slug_field=self.slug_field,
            async_=self.duplicate_async,
        )(request, *args, **kwargs)

    def show_view(self, request, *args, **kwargs):
        view_kwargs = self._get_single_object_view_kwargs()
        return self.show_view_class.as_view(
            form_class=self.form_class,
            template_name=self.edit_template_name,
            no_cancel=self.no_cancel,
            **view_kwargs,
        )(request, *args, **kwargs)

    def csv_export_view(self, request, *args, **kwargs):
        view_kwargs = self._get_default_view_kwargs()
        return self.csv_export_view_class.as_view(
            export_fields=self.export_fields, **view_kwargs
        )(request, *args, **kwargs)

    def get_queryset(self, request, **kwargs):
        if self.parent_field:
            parent_obj = self.parent.get_object(request, **kwargs)
            return self.queryset.filter(**{self.parent_field.name: parent_obj})
        return self.queryset

    def get_object(self, request, **kwargs):
        if self.url_kwarg not in kwargs:
            return None

        queryset = self.get_queryset(request, **kwargs)

        # Next, try looking up by primary key.
        pk = kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        slug = kwargs.get(self.slug_url_kwarg)
        if slug is not None and pk is None:
            queryset = queryset.filter(**{self.slug_field: slug})

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": self.opts.verbose_name}
            )
        return obj

    def get_initial(self, request, **kwargs):
        if self.parent_field:
            parent_obj = self.parent.get_object(request, **kwargs)
            return {self.parent_field.name: parent_obj}
        return {}

    def get_initial_object(self, request, **kwargs):
        """
        Return initial object passed to the form in add view.
        Django initializes this as Model() if instance is None,
        we're changing this behavior to assign parent object to instance.
        This way, we don't have to override Form.save() to assign it
        nor define extra form input for it.
        """
        instance = self.model()
        if self.parent_field:
            p_obj = self.parent.get_object(request, **kwargs)
            setattr(instance, self.parent_field.name, p_obj)
        return instance

    def delete(self, obj):
        obj.delete()

    def dispatch(self, view):
        if True not in self.get_model_perms(view.request).values():
            raise PermissionDenied()

    def get_breadcrumbs(self, request, obj=None, **kwargs):
        # filter out only parents pk_url_kwargs from kwargs
        list_kwargs = {}
        p = self.parent
        while p:
            list_kwargs[p.pk_url_kwarg] = kwargs.get(p.pk_url_kwarg)
            p = p.parent

        qs = self.model.objects.all()

        if self.parent_field:
            p_obj = self.parent.get_object(request, **list_kwargs)
            qs = qs.filter(**self.parent_field.get_forward_related_filter(p_obj))
            breadcrumbs = self.parent.get_breadcrumbs(request, p_obj, **list_kwargs)
        else:
            breadcrumbs = []

        breadcrumbs += [
            (
                f"{self.model._meta.verbose_name_plural} ({qs.count()})",
                self.list_url(**list_kwargs),
            )
        ]

        if obj and obj.pk:
            breadcrumb_url = (
                self.edit_url
                if self.has_change_permission(request, obj=obj)
                else self.show_url
            )
            breadcrumbs += [(getattr(obj, "name", str(obj)), breadcrumb_url(**kwargs))]
        elif obj:
            breadcrumbs += [
                (_("New %s") % self.opts.verbose_name, self.add_url(**kwargs))
            ]

        return breadcrumbs

    def get_cancel_url(self, view):
        pass

    def get_success_url(self, view):
        pass

    def get_context_data(self, request, **kwargs):
        return {"page_title": self.get_page_title(request, **kwargs)}

    def get_form_class(self, view):
        return self.form_class

    def get_form_kwargs(self, view):
        return {}

    def get_formset_kwargs(self, view):
        return {}

    def get_search_form(self, view, form):
        return form

    def get_add_modal_form(self, view, **form_kwargs):
        if self.add_modal_fields:
            return modelform_factory(
                self.model, form=ModelForm, fields=self.add_modal_fields
            )(**form_kwargs)

    def get_duplicate_modal_form(self, view, **form_kwargs):
        if self.duplicate_modal_fields:
            return modelform_factory(
                self.model, form=ModelForm, fields=self.duplicate_modal_fields
            )(**form_kwargs)

    def get_fieldsets(self, form=None):
        return self.fieldsets

    def get_formsets(self, obj=None):
        return self.formsets

    def get_menu_items(self, request, **kwargs):
        menu_items = []
        for admin in self.children:
            if admin.has_show_permission(request):
                list_url = ""
                if self.url_kwarg in kwargs:
                    list_url = admin.list_url(**kwargs)
                menu_items.append(((list_url, admin.opts.verbose_name_plural)))

        if menu_items:
            if self.url_kwarg in kwargs:
                main_url = (
                    self.edit_url(**kwargs)
                    if self.has_change_permission(request)
                    else self.show_url(**kwargs)
                )
            else:
                main_url = self.add_url(**kwargs)
            menu_items = [(main_url, _("Main"))] + menu_items

        return menu_items

    def get_list_actions(self, request, obj):
        obj_id = getattr(obj, self.slug_field or "id")
        actions = []
        if self.has_change_permission(request, obj):
            actions.append({"icon": "pencil", "label": _("Edit"), "url": f"{obj_id}/"})
        if self.has_show_permission(request, obj):
            actions.append({"icon": "eye", "label": _("Show"), "url": f"{obj_id}/show"})
        if self.can_duplicate and self.has_duplicate_permission(request, obj):
            action = {"icon": "copy", "label": _("Duplicate")}
            if self.duplicate_modal_fields:
                action["url"] = "#"
                action["attrs"] = {
                    "data-toggle": "modal",
                    "data-target": "#duplicate-modal",
                    "data-id": obj_id,
                }
            else:
                action["url"] = f"{obj_id}/duplicate/"
            actions.append(action)
        if self.has_delete_permission(request, obj):
            actions.append(
                {
                    "icon": "trash",
                    "label": _("Delete"),
                    "url": f"{obj_id}/delete/",
                    "attrs": {
                        "class": " modal-confirm-click",
                        "data-modal-type": "confirm-deletion",
                        "data-modal-number": "1",
                        "data-modal-title-1": _("Confirm deletion"),
                        "data-modal-body-1": _('Delete %s "%s"?')
                        % (self.opts.verbose_name, obj),
                    },
                }
            )
        return actions

    def get_model_perms(self, request):
        return {
            "add": self.has_add_permission(request),
            "change": self.has_change_permission(request),
            "delete": self.has_delete_permission(request),
            "duplicate": self.has_duplicate_permission(request),
            "show": self.has_show_permission(request),
        }

    def has_add_permission(self, request):
        opts = self.opts
        codename = get_permission_codename("add", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("change", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_show_permission(self, request, obj=None):
        if self.has_change_permission(request, obj):
            return True
        opts = self.opts
        codename = get_permission_codename("show", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_module_permission(self, request):
        return request.user.has_module_perms(self.opts.app_label)

    def has_duplicate_permission(self, request, obj=None):
        return self.has_change_permission(request, obj=obj)

    def get_page_title(self, request, **kwargs):
        title = ""
        if self.model:
            model_title = self.model._meta.verbose_name.title()
            if self.url_kwarg in kwargs:
                obj = self.get_object(request, **kwargs)
                title = "{} - {} | ".format(getattr(obj, "name", str(obj)), model_title)
            else:
                title = "{} list | ".format(model_title)

        return _("{}Printbox Dashboard {}".format(title, settings.PRINTBOX_SITE_NAME))
