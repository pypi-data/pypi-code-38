from django.conf import settings as site_settings
from django.template.defaultfilters import slugify
from api.settings import URL_OVERRIDES


def get_type_name(obj):
    """
    Returns the JSON-API name for a Django model.

    :param obj: A Django model instance
    """

    from .resources import registry

    try:
        resource = registry.get(obj, 'detail')
    except KeyError:
        pass
    else:
        if hasattr(resource, 'model_name'):
            return resource.model_name

    return slugify(obj._meta.verbose_name_plural)


def get_id_field(obj):
    """
    Returns the field used to identify a Django model instance.

    :param obj: A Django model instance
    """

    m = '%s.%s' % (
        obj._meta.app_label,
        obj._meta.model_name
    )

    if m in URL_OVERRIDES:
        field, expr = URL_OVERRIDES[m]
        return field

    from .resources import registry

    try:
        resource = registry.get(obj, 'detail')
    except KeyError:
        pass
    else:
        if hasattr(resource, 'pk_field'):
            return resource.pk_field

    return 'pk'


def get_object_id(obj):
    """
    Returns the identifier for a Django model instance.

    :param obj: A Django model instance
    """

    pk_field = get_id_field(obj)
    return str(getattr(obj, pk_field))


def urlise_field_name(name):
    """
    Converts field names from the Django naming convention into the JSON-PAI
    convention.

    :param obj: The field name to convert
    :type obj: str
    """

    return name.replace('_', '-')


def unurlise_field_name(name):
    """
    Converts field names from the JSON-API naming convention into the Django
    convention.

    :param obj: The field name to convert
    :type obj: str
    """
    return name.replace('-', '_')


def get_authenticators():
    """
    Returns the default authenticator classes.
    """

    return getattr(
        site_settings,
        'API_DEFAULT_AUTHENTICATORS',
        ['api.authentication.DjangoSessionAuthenticator']
    )


def get_authorisers():
    """
    Returns the default authoriser classes.
    """

    return getattr(
        site_settings,
        'API_DEFAULT_AUTHORISERS',
        ['api.authorisation.GuestReadOnlyOrDjangoUserAuthoriser']
    )
