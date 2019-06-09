from . import visitor
import functools
import loady
import traceback

OBJECT = '_object'
CLASS = '_class'
ERROR = '_error'
TYPENAME = '_'
NOTHING = object()
ATTRIBUTES = 'TIMEDATA_ATTRIBUTES'
RAISE = True


def fill(project):
    visitor.visit(project, _fill_class)
    visitor.visit(project, _construct)
    visitor.visit(project, _set_attributes)


def _errors(fn):
    """
    A decorator that wraps a function and catches exceptions, storing their
    value with an entry in the parent dictionary called `'_error'`
    """

    @functools.wraps(fn)
    def wrapper(parent, key, node):
        try:
            fn(parent, key, node)
        except Exception:
            if RAISE:
                raise

            error = fn.__name__, parent, key, node, traceback.format_exc()
            parent.setdefault(ERROR, []).append(error)

    return wrapper


@_errors
def _fill_class(parent, key, node):
    if key == TYPENAME:
        parent[CLASS] = loady.code.load_code(node)


@_errors
def _construct(parent, key, node):
    if key == CLASS:
        parent[OBJECT] = node()


@_errors
def _set_attributes(parent, key, node):
    if not parent or OBJECT not in parent or key.startswith('_'):
        return

    cls = parent[CLASS]

    attributes = getattr(cls, ATTRIBUTES, None)
    if not (attributes is None or key in attributes):
        raise ValueError('Unknown attribute ' + key)

    if isinstance(attributes, dict):
        attr = attributes[key]
        if callable(attr):
            node = attr(node)

    setattr(parent[OBJECT], key, node)
