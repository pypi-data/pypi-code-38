from rest_framework.relations import PKOnlyObject
from collections import OrderedDict
from rest_framework import serializers
from rest_framework.fields import SkipField

from aparnik.settings import aparnik_settings


class ModelSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        """Object instance -> Dict of primitive datatypes."""
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                value = None
            else:
                value = field.to_representation(attribute)

            if aparnik_settings.API_PRODUCT_MODE:
                ret[field.field_name] = {
                    'value': value,
                    # You can find more field attributes here
                    # https://github.com/encode/django-rest-framework/blob/master/rest_framework/fields.py#L324
                    'verbose_name': field.label,
                    'read_only': field.read_only,
                    'placeholder': field.label,
                    'type': type(value).__name__,
                    # 'write_only': field.write_only,
                    'help_text': field.help_text,
                }
            else:
                ret[field.field_name] = value

        return ret
