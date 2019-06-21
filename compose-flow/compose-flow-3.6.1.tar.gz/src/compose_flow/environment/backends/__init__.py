import importlib


def get_backend(name: str, *args, **kwargs) -> object:
    """
    Returns the requested backend object
    """
    module_path = f'compose_flow.environment.backends.{name}_backend'

    module = importlib.import_module(module_path)
    backend_cls = getattr(module, f'{name.capitalize()}Backend')

    return backend_cls(*args, **kwargs)
