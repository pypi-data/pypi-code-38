
def make_gauss_or_lor(model, spec, all_bounds):
    w_min = spec['bounds']['sigma'][0]
    w_max = spec['bounds']['sigma'][1]
    x_min = spec['bounds']['center'][0]
    x_max = spec['bounds']['center'][1]

    model.set_param_hint('sigma', value=spec['params']['sigma'], min=w_min, max=w_max)
    model.set_param_hint('center', value=spec['params']['center'], min=x_min, max=x_max)
    if all_bounds:  # for differential_evolution algorithm this is needed
        y_min = spec['bounds']['amplitude'][0]
        y_max = spec['bounds']['amplitude'][1]
        model.set_param_hint('amplitude', value=spec['params']['amplitude'], min=y_min, max=y_max)
    else:  # otherwise we don't put any bounds on
        model.set_param_hint('amplitude', value=spec['params']['amplitude'])
    return model

def make_split_lor(model, spec, all_bounds):
    w_min = spec['bounds']['sigma'][0]
    w_max = spec['bounds']['sigma'][1]
    w_r_min = spec['bounds']['sigma_r'][0]
    w_r_max = spec['bounds']['sigma_r'][1]
    x_min = spec['bounds']['center'][0]
    x_max = spec['bounds']['center'][1]

    model.set_param_hint('sigma', value=spec['params']['sigma'], min=w_min, max=w_max)
    model.set_param_hint('sigma_r', value=spec['params']['sigma_r'], min=w_r_min, max=w_r_max)
    model.set_param_hint('center', value=spec['params']['center'], min=x_min, max=x_max)
    if all_bounds:  # for differential_evolution algorithm this is needed
        y_min = spec['bounds']['amplitude'][0]
        y_max = spec['bounds']['amplitude'][1]
        model.set_param_hint('amplitude', value=spec['params']['amplitude'], min=y_min, max=y_max)
    else:  # otherwise we don't put any bounds on
        model.set_param_hint('amplitude', value=spec['params']['amplitude'])
    return model

