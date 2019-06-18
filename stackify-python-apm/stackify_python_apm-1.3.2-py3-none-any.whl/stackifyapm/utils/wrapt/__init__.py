__version_info__ = ('1', '10', '11')
__version__ = '.'.join(__version_info__)

from .wrappers import (  # noqa E401
    ObjectProxy,
    CallableObjectProxy,
    FunctionWrapper,
    BoundFunctionWrapper,
    WeakFunctionProxy,
    resolve_path,
    apply_patch,
    wrap_object,
    wrap_object_attribute,
    function_wrapper,
    wrap_function_wrapper,
    patch_function_wrapper,
    transient_function_wrapper,
)

from .decorators import (  # noqa E401
    adapter_factory,
    AdapterFactory,
    decorator,
    synchronized,
)

from .importer import (  # noqa E401
    register_post_import_hook,
    when_imported,
    notify_module_loaded,
    discover_post_import_hooks,
)

try:
    from inspect import getcallargs
except ImportError:
    from .arguments import getcallargs  # noqa E401
