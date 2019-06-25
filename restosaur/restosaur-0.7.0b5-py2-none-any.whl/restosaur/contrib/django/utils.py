def model_to_dict(obj, context):
    """
    Convert django model instance to dict
    """

    data = {}

    for field in obj._meta.fields:
        field_name = field.column if field.rel else field.name
        data[field.column] = getattr(obj, field_name)

    return data


def autodiscover(module_name='restapi'):
    from django.conf import settings

    try:
        from django.utils.module_loading import autodiscover_modules
    except ImportError:
        from django.utils.importlib import import_module
        from django.utils.module_loading import module_has_submodule
        autodiscover_modules = None

    if autodiscover_modules:
        autodiscover_modules(module_name)
    else:
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                import_module('%s.%s' % (app, module_name))
            except:
                if module_has_submodule(mod, module_name):
                    raise
