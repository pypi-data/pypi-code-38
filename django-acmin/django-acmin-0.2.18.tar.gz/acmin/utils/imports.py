import pkgutil


def import_class(name):
    import importlib
    module_name, class_name = name.rsplit(".", 1)
    module = importlib.import_module('.', module_name)
    return getattr(module, class_name)


def import_model(app_name, name):
    from django.apps import apps as django_apps
    if isinstance(name, str):
        result = None
        if "." in name:  # "hotel.Channel"
            result = django_apps.get_model(name)
        if not result:
            try:
                result = django_apps.get_model(app_name, name.lower())
            except Exception:
                pass
        if not result:
            try:
                result = import_class("%s.models.%s" % (app_name, name.capitalize()))
            except Exception:
                pass

        if result:
            return result
        raise Exception(f"Cannot import model by {app_name} {name}")


class ModuleProxyCache(dict):
    def __missing__(self, key):
        if '.' not in key:
            return __import__(key)

        module_name, class_name = key.rsplit('.', 1)

        module = __import__(module_name, {}, {}, [class_name])
        handler = getattr(module, class_name)

        # We cache a NoneType for missing imports to avoid repeated lookups
        self[key] = handler

        return handler


_cache = ModuleProxyCache()


def import_string(path):
    """
    Path must be module.path.ClassName

    >>> cls = import_string('sentry.models.Group')
    """
    result = _cache[path]
    return result


def import_submodules(context, root_module, path):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_submodules(locals(), __name__, __path__)
    """
    for loader, module_name, is_pkg in pkgutil.walk_packages(path, root_module + '.'):
        # this causes a Runtime error with model conflicts
        # module = loader.find_module(module_name).load_module(module_name)
        module = __import__(module_name, globals(), locals(), ['__name__'])
        for k, v in vars(module).items():
            if not k.startswith('_'):
                context[k] = v
        context[module_name] = module


def import_sub_classes(context, root_module, path):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_sub_classes(locals(), __name__, __path__)
    """
    for loader, module_name, is_pkg in pkgutil.walk_packages(path, root_module + '.'):
        module = __import__(module_name, globals(), locals(), ['__name__'])
        for k, v in vars(module).items():
            is_class = hasattr(v, '__name__')
            has_module = hasattr(v, "__module__")
            if not k.startswith('_') and is_class and has_module:
                name = v.__name__
                if name[0:1].isupper() and v.__module__.startswith(root_module):
                    context[k] = v
        context[module_name] = module
