def checkApiParams(request_params, apiDef):

    # TODO: fazer checagem do tipo
    # TODO: verificar como lidar com o campo boolean do 'classifServerSide'

    _params = {}

    for p in apiDef:

        try:
            _params[p] = apiDef[p]['default'] if not apiDef[p]['required'] else apiDef[p]['type'](request_params[p])
        except:
            raise KeyError('Missing `{}`'.format(p))

    return _params