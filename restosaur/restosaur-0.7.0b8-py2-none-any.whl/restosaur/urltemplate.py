import re

RE_PARAMS = re.compile('(/:([a-zA-Z_]+))')


def to_url(urltemplate, params, strict=False):
    uri = urltemplate
    params_to_replace = RE_PARAMS.findall(urltemplate)

    if params_to_replace:
        for needle, key in params_to_replace:
            try:
                uri = uri.replace(needle, '/%s' % params[key])
            except KeyError:
                if strict:
                    raise
    return uri


def get_parameters(urltemplate):
    params = RE_PARAMS.findall(urltemplate)
    return list(map(lambda x: x[1], params))


def remove_parameters(urltemplate):
    uri = urltemplate

    params_to_replace = RE_PARAMS.findall(urltemplate)
    for needle, key in params_to_replace:
        uri = uri.replace(needle, '')
    return uri
