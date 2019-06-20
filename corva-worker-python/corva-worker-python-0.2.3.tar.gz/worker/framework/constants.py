parameters = {
    "global": {
        "app-name": "my-app",
        "app-key": "my-app-key",
        "event-type": "scheduler",
        "query-limit": 1000,
    },
}


def get(key, default=None):
    if not key:
        if default:
            return default

        raise KeyError("No key provided")

    path = key.split(".")
    value = parameters

    while path:
        current_key = path.pop(0)

        if current_key not in value:
            if default:
                return default

            raise KeyError("{0} not found in path".format(current_key))

        value = value.get(current_key)

    return value


def update(additional_parameters):
    """
    The purpose of this method is to update the existing parameters data
    with the provided additional parameters. Note that the globals will
    be replaced if the additional parameters contains global node.
    :param additional_parameters:
    :return:
    """
    globals = parameters.pop('global')
    additional_globals = additional_parameters.pop('global', {})
    globals.update(additional_globals)
    parameters.update(additional_parameters)
    if globals:
        parameters['global'] = globals
