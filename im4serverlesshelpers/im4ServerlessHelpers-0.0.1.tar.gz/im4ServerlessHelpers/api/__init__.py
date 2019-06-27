def checkApiParams(request_params, apiDef):

    # TODO: fazer checagem do tipo
    # TODO: verificar como lidar com o campo boolean do 'classifServerSide'

    _params = {}

    for p in apiDef:

        try:
            _params[p] = request_params[p]
        except:
            if not apiDef[p]['required']:
                _params[p] = apiDef[p]['default']
            else:
                raise KeyError('Missing `{}`'.format(p))

    return _params