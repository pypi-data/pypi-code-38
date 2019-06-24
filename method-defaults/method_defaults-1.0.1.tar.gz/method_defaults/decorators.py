from functools import wraps
import inspect

from configobj import ConfigObj

from .config_manager import Config


def defaults(source, sections=False, force=False):
    """
    Apply parameter values from configuration file

    @param source:  Configuration input.
    @type  source:  Either a filepath, a file-like object or a Config object.

    @param sections:  Limits the scope from where the parameters are taken.
    @type  sections:  str, [str].
                      Each str is a hierarchy of sections in dot notation.
                      Example: ['section1.nested_section', 'section2']
    @def   sections:  By default only the general key-value pairs are the scope

    @param force:  Whether to override kwargs values or not.
    @type  force:  bool

    @return:  Decorated function partially applied with paramters from conf.
    @rtype :  func

    @raise e:  Description
    """
    config = Config(source)
    scope = config._get_sections(sections)

    def inside_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_params = inspect.signature(func).parameters
            for name, param in func_params.items():
                if not force and name in kwargs:
                    continue
                if name in scope:
                    try:
                        val = getattr(
                            ConfigObj(scope),
                            "as_%s" % param.annotation.__name__)(name)
                    except Exception:
                        val = scope.get(name)
                    kwargs[name] = val

            res = func(*args, **kwargs)
            return res
        return wrapper
    return inside_decorator
