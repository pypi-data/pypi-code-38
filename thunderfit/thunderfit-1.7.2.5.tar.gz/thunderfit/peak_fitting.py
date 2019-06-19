import logging

from lmfit import models
from numpy import nan

from . import utilities as utils


def get_tols(method, tol):
    """
    quick function to set the tolerances as a dictionary depending on the method being used
    :param method: str: method to use
    :param tol: tolerance as a float
    :return:
    """
    if method in ['leastsq', 'least_squares']:
        # warning: need to experiment with these/allow control maybe?
        tols = {'ftol': tol, 'xtol': tol}
    else:
        tols = {'ftol': tol}
    return tols


def prep_algo(method, tols):
    """
    depending on the algorithm either set the tolerances, give a warning or set a parameter which is depreciated to True.
    will be overhauled in future
    :param method: str: method to use
    :param tols: float tolerance
    :return:
    """
    if method == 'basinhopping' or method == 'ampgo':
        print('Warning: This is a very slow but thorough algorithm')
    if method == 'differential_evolution':
        all_bounds = True
    if method in [
        'leastsq',
        'least_squares',
        'nelder',
            'cobyla']:  # do this for all of them??
        tols = get_tols(method, tols)
    return tols


def fit_peaks(
        x_data,
        y_data,
        peak_info_dict,
        bounds,
        method='leastsq',
        tol=0.0000001):
    """
    function which does the peak fitting.
    :param x_data: np array of x data
    :param y_data: np array of y data
    :param peak_info_dict: dictionary containing information about the peaks which will be used
    :param bounds: bounds with same keys as peak_info_dict and each is a list of tuples containing lower and upper bounds
    :param method: str: minimisation method to use
    :param tol: tolerance on minimisation.
    :return: specifications dictionary for the model used, the model object iteself, the parameters of the best fitted
    values and the model_result object
    """
    impl_methods = [
        'leastsq',
        'least_squares',
        'nelder',
        'lbfgsb',
        'powell',
        'cg',
        'cobyla',
        'bfgsb',
        'differential_evolution',
        'basinhopping',
        'ampgo']
    if method not in impl_methods:
        raise ValueError(
            f"The method supplied is not supported. Available methods: {impl_methods}")
    logging.debug(f'fitting peaks:  {peak_info_dict}')

    tols = prep_algo(method, tol)  # prep for the fitting
    # build a correctly formatted dictionary for fitting
    model_specs = build_specs(peak_info_dict, bounds)
    # generate the composite model for fitting
    model, peak_params = generate_model(model_specs)

    if method in ['leastsq', 'least_squares', 'nelder', 'cobyla']:
        peaks = model.fit(
            y_data,
            peak_params,
            x=x_data,
            method=method,
            fit_kws=tols)  # fit the model to the data
        if not peaks.success:  # then raise tolerance and try again
            print(
                'peaks failed to fit, raising tolerance by one order magnitude and trying again')
            # try raising the tolerance if it fails by one order
            tols = {key: value * 10 for key, value in tols.items()}
            peaks = model.fit(
                y_data,
                peak_params,
                x=x_data,
                method=method,
                fit_kws=tols)
    else:
        peaks = model.fit(y_data, peak_params, x=x_data, method=method)

    # what are the best parameters used # shoudl create a function as an
    # abstraction barrier for this
    peak_params = peaks.best_values
    if not peaks.success:  # then didn't fit for some reason, so set everything to nan in results
        print('peaks failed to fit')
        peak_params = {key: nan for key in peak_params}

    # really should clean this up but allows flexibility for user by passing
    # the actual objects back too
    return model_specs, model, peak_params, peaks


def safe_list_get(l, idx, default):
    """fetch items safely from a list, if it isn't long enough return a default value"""
    try:
        return l[idx]
    except IndexError:
        return default

# Call this with correct arguments, should always call with all the arguments!


def build_specs(peak_info_dict: dict = {}, bounds: dict = {}):
    """
    should be depreciated in future. can get by with bypassing this, currently acts to cleanse inputs so maybe could be
    shortened/changed with that goal in mind
    :param peak_info_dict:
    :param bounds:
    :return:
    """

    """Build a specs list, which has the peak specification details for each element corresponding to a peak to fit.
    Note that each element is a dictionary containing either None, or a value for that peak i.e. the parameter guess,
    or the bounds for that value. Only some will be valid for each peak type, which will be handled elsewhere"""
    logging.debug('building specs')
    type_ = peak_info_dict.get('type', ())
    if 'SplitLorentzianModel' in type_ or 'ExponentialGaussianModel' in type_:
        raise NotImplementedError(
            "No support for this model yet: polynomialmodel, ExponentialGaussianModel and splitlorentzianmodel")
    if 'ExpressionModel' in type_:
        raise NotImplementedError("no support for expression models yet!")
    center = peak_info_dict.get('center', ())
    amplitude = peak_info_dict.get('amplitude', ())
    sigma = peak_info_dict.get('sigma', ())
    sigma_l = peak_info_dict.get('sigma_l', ())
    sigma_r = peak_info_dict.get('sigma_r', ())
    gamma = peak_info_dict.get('gamma', ())
    fraction = peak_info_dict.get('fraction', ())
    beta = peak_info_dict.get('beta', ())
    exponent = peak_info_dict.get('exponent', ())
    q = peak_info_dict.get('q', ())
    c = peak_info_dict.get('c', ())
    intercept = peak_info_dict.get('intercept', ())
    slope = peak_info_dict.get('slope', ())
    a = peak_info_dict.get('a', ())
    b = peak_info_dict.get('b', ())
    degree = peak_info_dict.get('degree', ())
    center1 = peak_info_dict.get('center1', ())
    center2 = peak_info_dict.get('center2', ())
    sigma1 = peak_info_dict.get('sigma1', ())
    sigma2 = peak_info_dict.get('sigma2', ())
    decay = peak_info_dict.get('decay', ())
    expr = peak_info_dict.get('expr', ())
    form = peak_info_dict.get('form', ())
    c0 = peak_info_dict.get('c0', ())
    c1 = peak_info_dict.get('c1', ())
    c2 = peak_info_dict.get('c2', ())
    c3 = peak_info_dict.get('c3', ())
    c4 = peak_info_dict.get('c4', ())
    c5 = peak_info_dict.get('c5', ())
    c6 = peak_info_dict.get('c6', ())
    c7 = peak_info_dict.get('c7', ())

    specs = [
        {
            'type': type_[i],
            'params': {'center': utils.safe_list_get(center, i, None),
                       'amplitude': utils.safe_list_get(amplitude, i, None),
                       'sigma': utils.safe_list_get(sigma, i, None),
                       'sigma_r': utils.safe_list_get(sigma_r, i, None),
                       'sigma_l': utils.safe_list_get(sigma_l, i, None),
                       'gamma': utils.safe_list_get(gamma, i, None),
                       'fraction': utils.safe_list_get(fraction, i, None),
                       'beta': utils.safe_list_get(beta, i, None),
                       'exponent': utils.safe_list_get(exponent, i, None),
                       'q': utils.safe_list_get(q, i, None),
                       'c': utils.safe_list_get(c, i, None),
                       'intercept': utils.safe_list_get(intercept, i, None),
                       'slope': utils.safe_list_get(slope, i, None),
                       'a': utils.safe_list_get(a, i, None),
                       'b': utils.safe_list_get(b, i, None),
                       'center1': utils.safe_list_get(center1, i, None),
                       'center2': utils.safe_list_get(center2, i, None),
                       'sigma1': utils.safe_list_get(sigma1, i, None),
                       'sigma2': utils.safe_list_get(sigma2, i, None),
                       'decay': utils.safe_list_get(decay, i, None),
                       'c0': utils.safe_list_get(c0, i, None),
                       'c1': utils.safe_list_get(c1, i, None),
                       'c2': utils.safe_list_get(c2, i, None),
                       'c3': utils.safe_list_get(c3, i, None),
                       'c4': utils.safe_list_get(c4, i, None),
                       'c5': utils.safe_list_get(c5, i, None),
                       'c6': utils.safe_list_get(c6, i, None),
                       'c7': utils.safe_list_get(c7, i, None)
                       },
            'bounds': {'center': utils.safe_list_get(bounds.get('center', []), i, (None, None)),
                       'amplitude': utils.safe_list_get(bounds.get('amplitude', []), i, (None, None)),
                       'sigma': utils.safe_list_get(bounds.get('sigma', []), i, (None, None)),
                       'sigma_r': utils.safe_list_get(bounds.get('sigma_r', []), i, (None, None)),
                       'gamma': utils.safe_list_get(bounds.get('gamma', []), i, (None, None)),
                       'fraction': utils.safe_list_get(bounds.get('fraction', []), i, (None, None)),
                       'beta': utils.safe_list_get(bounds.get('beta', []), i, (None, None)),
                       'exponent': utils.safe_list_get(bounds.get('exponent', []), i, (None, None)),
                       'q': utils.safe_list_get(bounds.get('q', []), i, (None, None)),
                       'c': utils.safe_list_get(bounds.get('c', []), i, (None, None)),
                       'intercept': utils.safe_list_get(bounds.get('intercept', []), i, (None, None)),
                       'slope': utils.safe_list_get(bounds.get('slope', []), i, (None, None)),
                       'a': utils.safe_list_get(bounds.get('a', []), i, (None, None)),
                       'b': utils.safe_list_get(bounds.get('b', []), i, (None, None)),
                       'center1': utils.safe_list_get(bounds.get('center1', []), i, (None, None)),
                       'center2': utils.safe_list_get(bounds.get('center2', []), i, (None, None)),
                       'sigma1': utils.safe_list_get(bounds.get('sigma1', []), i, (None, None)),
                       'sigma2': utils.safe_list_get(bounds.get('sigma2', []), i, (None, None)),
                       'decay': utils.safe_list_get(bounds.get('decay', []), i, (None, None)),
                       'c0': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c1': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c2': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c3': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c4': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c5': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c6': utils.safe_list_get(bounds.get('c0', []), i, (None, None)),
                       'c7': utils.safe_list_get(bounds.get('c0', []), i, (None, None))
                       },
            'expr': utils.safe_list_get(expr, i, None),
            'form': utils.safe_list_get(form, i, None),
            'degree': utils.safe_list_get(degree, i, None)
        }
        for i in range(len(type_))
    ]

    return specs


def generate_model(model_specs):
    """
    generate a composite model given information of the models to create, their guesses of params and bounds on parameters
    :param model_specs: a dictionary containing all the info on the model
    :return: a composite lmfit model
    """
    logging.debug('generating model specs')
    composite_model = None
    params = None
    for i, spec in enumerate(model_specs):
        prefix = f'm{i}__'
        if spec['type'] == 'ExpressionModel':
            expr = spec['expr']
            model = models.ExpressionModel(expr)
        elif spec['type'] in ['StepModel', 'RectangleModel']:
            form = spec['form']
            model = getattr(models, spec['type'])(prefix=prefix, form=form)
        elif spec['type'] == 'PolynomialModel':
            model = getattr(
                models,
                spec['type'])(
                prefix=prefix,
                degree=spec['degree'])
        else:
            # generate the lmfit model based on the type specified
            model = getattr(models, spec['type'])(prefix=prefix)
        # call another function to decide what to do
        model = decide_model_actions(spec, model)
        model_params = model.make_params()  # make the params object
        if params is None:  # first loop
            params = model_params
            composite_model = model
        else:  # subsequent loops
            params.update(model_params)
            composite_model = composite_model + model
    return composite_model, params


def decide_model_actions(spec, model):
    """
    either set the param hints or the bounds depending on the spec dict
    :param spec: dictionary of the params to be set on the model
    :param model: lmfit model object
    :return: the updated model object
    """
    for param_key, param_value in spec['params'].items():
        if param_value:  # then set this value
            model.set_param_hint(param_key, value=param_value)
    for bound_key, bound_value in spec['bounds'].items():
        if bound_value[0]:  # then set lower bound
            model.set_param_hint(bound_key, min=bound_value[0])
        if bound_value[1]:  # then set upper bound
            model.set_param_hint(bound_key, max=bound_value[1])
    return model
