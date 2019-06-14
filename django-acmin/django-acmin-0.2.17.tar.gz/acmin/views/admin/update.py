from django.urls import reverse
from django.views.generic.edit import UpdateView

from acmin.models import Permission, PermissionItem, Field
from acmin.utils import param, json_response, attr
from .form import AdminFormView


class AdminUpdateView(AdminFormView, UpdateView):
    success_message = "更新成功!"

    def get(self, request, *args, **kwargs):
        partial, attribute, value = param(request, ["partial", "attribute", "value"])
        pk = kwargs.get("pk")
        if partial and attribute and value and pk:
            instance = self.model.objects.filter(pk=pk).first()
            python_type = attr(Field.get_field(self.request.user, self.model, attribute), "python_type")
            if "django.db.models.fields.BooleanField" == python_type:
                value = True if value == "true" else False

            setattr(instance, attribute, value)
            instance.save()
            return json_response({"success": True})

        return super().get(request, args, kwargs)

    def is_clone(self):
        return self.request.GET.get("clone") is not None

    def get_template_names(self):
        name = "create.html" if self.is_clone() else "update.html"
        return [f"admin/{self.model.__name__}/{name}", f'acmin/admin/base/{name}']

    def has_permission(self):
        return Permission.has_permission(self.request.user, self.model, PermissionItem.viewable)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = self.get_object().get_absolute_url()
        context["view_type"] = 'update'
        if self.is_clone():
            obj = context["object"]
            obj.id = ""
            context["form_action"] = reverse(f'{self.model.__name__}-create')
            context["is_clone"] = True

        setattr(context.get('object'), "_request", self.request)
        return context
