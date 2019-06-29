def checkApiParams(request_params, apiDef):

    _params = {}

    for p in apiDef:

        if p not in request_params and apiDef[p]['required']:
            raise KeyError('Missing `{}`'.format(p))

        elif p not in request_params:
            _params[p] = apiDef[p]['type'](apiDef[p]['default'])

        else:
            _params[p] = apiDef[p]['type'](request_params[p])

    return _params