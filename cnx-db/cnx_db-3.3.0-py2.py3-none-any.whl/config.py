import os

__all__ = ('discover_settings')


def discover_settings(settings=None):
    """Discover settings from environment variables

    ``DB_URL`` is required, while ``DB_READONLY_URL`` and ``DB_SUPER_URL``
    are not required and while default to ``DB_URL``. However, be aware
    that some parts of the application may not function correctly
    without these optional values set.

    :param dict settings: An existing settings value
    :return: dictionary of settings
    :rtype: dict

    .. seealso::

       See also :ref:`configuration_chapter` for environment variables,
       defaults and required settings.

    """
    if settings is None:
        settings = {}

    # Retrieve the required url setting first, so that it can later be used
    # as the default for the optional urls.
    common_url = os.environ.get('DB_URL', None)
    if common_url is None:
        if settings.get('db.common.url') is None:
            raise RuntimeError("'DB_URL' environment variable "
                               "OR the 'db.common.url' setting MUST "
                               "be defined")
        else:
            common_url = settings['db.common.url']

    # Set remaining urls, defaulting to the common url when not present.
    readonly_url = os.environ.get('DB_READONLY_URL', common_url)
    super_url = os.environ.get('DB_SUPER_URL', common_url)

    new_settings = {
        'db.common.url': common_url,
        'db.readonly.url': readonly_url,
        'db.super.url': super_url,
    }

    # Only amend the existing settings by setting the default.
    for k, v in new_settings.items():
        settings.setdefault(k, v)
    return settings
