from ..models import AeInitial


class NonAeInitialModelAdminMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ae_initial":
            if request.GET.get("ae_initial"):
                kwargs["queryset"] = AeInitial.objects.filter(
                    id__exact=request.GET.get("ae_initial", 0)
                )
            else:
                kwargs["queryset"] = AeInitial.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if obj:
            fields = fields + ("ae_initial",)
        return list(fields)
