from api.exceptions import UnprocessableEntityError
from api.utils import get_id_field, unurlise_field_name
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models import FieldDoesNotExist


def qs_name_to_kwarg(name, context):
    """
    A helper function that converts JSON-API filter expressions into Django
    filter keyword arguments.

    :param name: The field name, as given by the JSON-API client.
    :type name: str
    :param context: The root model meta object, as found in `<Model>._meta`.
    """

    parts = unurlise_field_name(name).split('.')
    found_parts = []

    while True:
        part = parts.pop(0)

        try:
            field = context.get_field(part)
        except FieldDoesNotExist:
            raise UnprocessableEntityError(
                'Invalid filter field',
                {
                    'field': name
                }
            )

        if isinstance(field, (ForeignKey, ManyToManyField)):
            if not any(parts):
                found_parts.append(part)
                found_parts.append(
                    get_id_field(
                        field.related_model
                    )
                )
            else:
                context = field.related_model._meta
                found_parts.append(part)
        elif any(parts):
            raise UnprocessableEntityError(
                'Invalid filter field',
                {
                    'field': name
                }
            )
        else:
            found_parts.append(part)

        if not any(parts):
            break

    return '__'.join(found_parts)
