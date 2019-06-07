from api.resources import registry
from api.utils import get_id_field
from django.forms import (
    DateField, DateTimeField,
    ModelChoiceField, ModelMultipleChoiceField,
    ValidationError
)

from django.utils.dateparse import parse_datetime
from .packing import PackingMixin
from .resources import ResourceMixin


class ModelMixin(ResourceMixin, PackingMixin):
    """
    View mixin for packing and unpacking Django model instances.
    """

    def get_resource(self):
        """
        Helper method to return the resource for this view. Requires the
        setting of a `resource_class` property.
        """

        if not hasattr(self, '_resource_cache'):
            if hasattr(self, 'resource_class'):
                self._resource_cache = self.resource_class(
                    **self.get_resource_kwargs()
                )
            else:
                self._resource_cache = registry.get(
                    self.model, 'detail'
                )(
                    **self.get_resource_kwargs()
                )

        return self._resource_cache

    def patch_form_fields(self, form):
        """
        Overrides model-choice form fields so that resources that don't use a
        standard primary key can allow related forms to specify the object
        with the non-standard key.
        """

        for name, field in form.fields.items():
            if isinstance(field, (ModelChoiceField, ModelMultipleChoiceField)):
                field.to_field_name = get_id_field(field.queryset.model)

            if isinstance(field, DateField):
                field.input_formats = ['%Y-%m-%d']

            if isinstance(field, DateTimeField):
                def mp_datetimefield_to_python(value):
                    if value is None:
                        return

                    value = value.strip()

                    try:
                        return parse_datetime(value)
                    except (ValueError, TypeError):
                        raise ValidationError(
                            field.error_messages['invalid'],
                            code='invalid'
                        )

                field.input_formats = ['%Y-%m-%dT%H:%M:%S%z']
                field.to_python = mp_datetimefield_to_python
