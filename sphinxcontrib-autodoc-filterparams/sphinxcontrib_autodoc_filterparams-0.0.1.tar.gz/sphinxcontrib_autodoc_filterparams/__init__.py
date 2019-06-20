import inspect
import re

from sphinx.util import logging
from sphinx.util.inspect import Signature

__version__ = '0.0.1'

_ext = 'sphinxcontrib_autodoc_filterparams'
_log = logging.getLogger(__name__)
_rex = re.compile(':(?:param|type)\\s+((?:\\\\\\*){0,2})([^:]+):')


def process_docstring(app, what, name, obj, options, lines):
    filter_params = getattr(app.config, _ext, None)
    stars = bool(getattr(app.config, _ext + '_stars', True))

    if filter_params is None or not callable(obj) or not lines:
        return
    if not callable(filter_params):
        _log.error(_ext + ' is not callable')
        return

    for i in range(len(lines) - 1, -1, -1):
        match = _rex.match(lines[i])
        if match is None:
            continue
        name = match.group(2)
        if stars:
            name = match.group(1).replace('\\', '') + name
        if not filter_params(obj, name):
            lines.pop(i)


def process_signature(app, what, name, obj, options,
                      signature, return_annotation):
    filter_params = getattr(app.config, _ext, None)
    stars = bool(getattr(app.config, _ext + '_stars', True))

    if filter_params is None or not callable(obj) or signature is None:
        return signature
    if not callable(filter_params):
        _log.error(_ext + ' is not callable')
        return signature

    signature = Signature(obj)

    def _filter(param):
        param_name = param.name
        var_pos = param.kind is inspect.Parameter.VAR_POSITIONAL
        var_kw = param.kind is inspect.Parameter.VAR_KEYWORD
        if stars:
            if var_pos:
                param_name = '*' + param_name
            elif var_kw:
                param_name = '**' + param_name
        keep = filter_params(obj, param_name)
        if not keep and not var_pos and not var_kw \
                and param.default is inspect.Parameter.empty:
            _log.warning(_ext + ': Param ' + param_name + ' has no default!')
        return keep

    signature.signature = signature.signature.replace(
        parameters=filter(_filter, signature.signature.parameters.values()),
        return_annotation=inspect.Signature.empty
    )

    return signature.format_args().replace('\\', '\\\\'), None


def setup(app):
    app.add_config_value(_ext, None, 'env')
    app.add_config_value(_ext + '_stars', True, 'env')
    app.connect('autodoc-process-signature', process_signature)
    app.connect('autodoc-process-docstring', process_docstring)
    return {
        'version': '0.0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }

