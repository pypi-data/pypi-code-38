
class ReadOnlyAdminPreMixin(object):
    """
    Mixin for :class:`django.contrib.admin.options.ModelAdmin`
    that makes the model admin read only.

    Examples:

        Typical usage::

            from ievv_opensource.ievv_djangoadmin import ievv_djangoadmin_mixins

            @admin.register(MyModel)
            class MyModelAdmin(ievv_djangoadmin_mixins.ReadOnlyAdminPreMixin,
                               admin.ModelAdmin):
                list_display = [
                    # ...
                ]
                search_fields = [
                    # ...
                ]
                # ...

    """
    #: Overridden change form template that removes
    #: the save buttons.
    change_form_template = 'ievv_djangoadmin/ievv_djangoadmin_mixins/' \
                           'read_only_change_form.django.html'

    #: Set to ``None`` - no actions by default.
    actions = None

    def get_readonly_fields(self, request, obj=None):
        """
        Returns all the fields on the model,
        so all fields are read only.
        """
        return [f.name for f in self.model._meta.get_fields() if f.concrete]

    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj=obj)

    def has_add_permission(self, request):
        """
        Returns ``False`` - so no add permission.
        """
        return False

    def has_delete_permission(self, request, id=None):
        """
        Returns ``False`` - so no delete permission.
        """
        return False
