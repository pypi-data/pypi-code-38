"""
Module for optimizing with the shgo optimizer in ESPEI

"""

import logging, time, sys

import sympy
import numpy as np
from numpy.linalg import LinAlgError
from scipy.optimize import shgo, dual_annealing

from pycalphad import Model
from pycalphad.codegen.callables import build_callables

from espei.core_utils import get_prop_data
from espei.utils import database_symbols_to_fit, optimal_parameters
from espei.error_functions import calculate_activity_error, calculate_thermochemical_error, calculate_zpf_error


TRACE = 15  # TRACE logging level


def lnlikelihood(params, comps=None, dbf=None, phases=None, datasets=None,
           symbols_to_fit=None, phase_models=None, weight_dict=None,
           callables=None, thermochemical_callables=None,
           ):
    """Calculate the likelihood, $$ \ln p(\theta|y) $$ """
    starttime = time.time()
    weight_dict = weight_dict if weight_dict is not None else {}
    parameters = {param_name: param for param_name, param in zip(symbols_to_fit, params)}
    try:
        multi_phase_error = calculate_zpf_error(dbf, comps, phases, datasets, phase_models,
                                                parameters=parameters, callables=callables,
                                                data_weight=weight_dict.get('ZPF', 1.0),
                                                )
    except (ValueError, LinAlgError) as e:
        multi_phase_error = -np.inf
    actvity_error = calculate_activity_error(dbf, comps, phases, datasets, parameters=parameters, phase_models=phase_models, callables=callables, data_weight=weight_dict.get('ACR', 1.0))
    single_phase_error = calculate_thermochemical_error(dbf, comps, phases, datasets, parameters, phase_models=phase_models, callables=thermochemical_callables, weight_dict=weight_dict)
    total_error = multi_phase_error + single_phase_error + actvity_error
    logging.log(TRACE, 'Likelihood - {:0.2f}s - Thermochemical: {:0.3f}. ZPF: {:0.3f}. Activity: {:0.3f}. Total: {:0.3f}.'.format(time.time() - starttime, single_phase_error, multi_phase_error, actvity_error, total_error))
    return np.array(total_error, dtype=np.float64)



def lnprob(params, dbf=None, comps=None, phases=None, datasets=None,
           symbols_to_fit=None, phase_models=None, scheduler=None, weight_dict=None,
           callables=None, thermochemical_callables=None
           ):
    """
    Returns the log probability of a set of parameters

    $$ \ln p(y|\theta) \propto \ln p(\theta) + \ln p(\theta|y) $$

    Parameters
    ----------
    params : array_like
        Array of parameters to fit.
    dbf : pycalphad.Database
        Database to consider
    comps : list
        List of active component names
    phases : list
        List of phases to consider
    datasets : espei.utils.PickleableTinyDB
        Datasets that contain single phase data
    phase_models : dict
        Phase models to pass to pycalphad calculations
    callables : dict
        Callables to pass to pycalphad
    symbols_to_fit : list
        List of names of parameter symbols to replace. Must correspond (same
        shape and order) to ``params``.
    phase_models : dict
        Dictionary of {phase name: Model instance}
    scheduler : None
        Deprecated.
    callables : dict
        Dictionary of {phase name: {phase callables dict}}
    thermochemical_callables :
        Dictionary of {output property: {phase name: {phase callables dict}}}.
        These callables must have ideal mixing portions removed.
    weight_dict : dict
        Dictionary of weights for each data type, e.g. {'ZPF': 20, 'HM': 2}

    Returns
    -------
    float

    """
    logging.debug('Parameters - {}'.format(params))
    loglike = lnlikelihood(params, comps=comps, dbf=dbf, phases=phases, datasets=datasets,
           symbols_to_fit=symbols_to_fit, phase_models=phase_models,
           callables=callables, thermochemical_callables=thermochemical_callables,
                           weight_dict=weight_dict,
                           )

    logprob = loglike
    logging.log(TRACE, 'Proposal - lnlike: {:0.4f}, lnprob: {:0.4f}'.format(loglike, logprob))
    return -logprob

def lnprob_ctx(x, ctx):
    """Call lnprob by passing the context as kwargs"""
    return lnprob(x, **ctx)


def espei_opt(dbf, datasets, scheduler=None, n=10, bound_factor=0.5, iters=1):
    """
    Run Markov Chain Monte Carlo on the Database given datasets

    Parameters
    ----------
    dbf : Database
        A pycalphad Database to fit with symbols to fit prefixed with `VV`
        followed by a number, e.g. `VV0001`
    datasets : PickleableTinyDB
        A database of single- and multi-phase to fit
    mcmc_data_weights : dict
        Dictionary of weights for each data type, e.g. {'ZPF': 20, 'HM': 2}

    Returns
    -------
    dbf : Database
        Resulting pycalphad database of optimized parameters
    """
    comps = sorted([sp for sp in dbf.elements])
    symbols_to_fit = database_symbols_to_fit(dbf)

    if len(symbols_to_fit) == 0:
        raise ValueError('No degrees of freedom. Database must contain symbols starting with \'V\' or \'VV\', followed by a number.')
    else:
        logging.info('Fitting {} degrees of freedom.'.format(len(symbols_to_fit)))

    for x in symbols_to_fit:
        if isinstance(dbf.symbols[x], sympy.Piecewise):
            logging.debug('Replacing {} in database'.format(x))
            dbf.symbols[x] = dbf.symbols[x].args[0].expr

    # get initial parameters and remove these from the database
    # we'll replace them with SymPy symbols initialized to 0 in the phase models
    initial_parameters = np.array([np.array(float(dbf.symbols[x])) for x in symbols_to_fit])


    # construct the models for each phase, substituting in the SymPy symbol to fit.
    logging.log(TRACE, 'Building phase models (this may take some time)')
    logging.debug('Building GM callables.')
    # 0 is placeholder value
    phases = sorted(dbf.phases.keys())
    sympy_symbols_to_fit = [sympy.Symbol(sym) for sym in symbols_to_fit]
    orig_parameters = {sym: p for sym, p in zip(symbols_to_fit, initial_parameters)}
    eq_callables = build_callables(dbf, comps, phases, model=Model, parameter_symbols=orig_parameters)
    # because error_context expencts 'phase_models' key, change it
    eq_callables['phase_models'] = eq_callables.pop('model')
    eq_callables.pop('phase_records')
    # we also need to build models that have no ideal mixing for thermochemical error and to build them for each property we might calculate
    # TODO: potential optimization to only calculate for phase/property combos that we have in the datasets
    # first construct dict of models without ideal mixing
    mods_no_idmix = {}
    for phase_name in phases:
        # we have to pass the list of Symbol objects to fit so they are popped from the database and can properly be replaced.
        mods_no_idmix[phase_name] = Model(dbf, comps, phase_name, parameters=sympy_symbols_to_fit)
        mods_no_idmix[phase_name].models['idmix'] = 0
    # now construct callables for each possible property that can be calculated
    thermochemical_callables = {}  # will be dict of {output_property: eq_callables_dict}
    whitelist_properties = ['HM', 'SM', 'CPM']
    whitelist_properties = whitelist_properties + [prop+'_MIX' for prop in whitelist_properties]
    for prop in whitelist_properties:
        # try to find them in datasets, skipping the build if they aren't there
        search_prop = prop + '_FORM' if '_' not in prop else prop
        total_props = 0
        for phase_name in phases:
            total_props += len(get_prop_data(comps, phase_name, search_prop, datasets))
        if total_props == 0:
            logging.debug('Skipping build of {} callables because no {} datasets were found.'.format(prop, search_prop))
            continue
        else:
            logging.debug('Building {} callables.'.format(prop))
        thermochemical_callables[prop] = build_callables(dbf, comps, phases, model=mods_no_idmix, output=prop, parameter_symbols=orig_parameters, build_gradients=False)
        # pop off the callables not used in properties because we don't want them around (they should be None, anyways)
        thermochemical_callables[prop].pop('phase_records')
        thermochemical_callables[prop].pop('model')
    logging.log(TRACE, 'Finished building phase models')

    # context for the log probability function
    error_context = {'comps': comps, 'dbf': dbf,
                     'phases': phases, 'phase_models': eq_callables['phase_models'],
                     'datasets': datasets, 'symbols_to_fit': symbols_to_fit,
                     'thermochemical_callables': thermochemical_callables,
                     'callables': eq_callables,
                     }

    # bounds: -0.5, 0.5 of the parameter value
    bounds = []
    for p in initial_parameters:
        minmax = (-bound_factor*p+p, bound_factor*1.2*p+p)  # slightly assymetric bounds prevent from starting at the correct solution
        bounds.append((np.min(minmax), np.max(minmax)))

    print(initial_parameters)
    print(bounds)

    optim_res = shgo(lnprob_ctx, bounds, args=(error_context,), callback=print, n=n, iters=iters)
    # logging.log(TRACE, 'Intial parameters: {}'.format(initial_parameters))
    # logging.log(TRACE, 'Optimal parameters: {}'.format(optimal_params))
    # logging.log(TRACE, 'Change in parameters: {}'.format(np.abs(initial_parameters - optimal_params) / initial_parameters))
    # for param_name, value in zip(symbols_to_fit, optimal_params):
    #     dbf.symbols[param_name] = value
    # logging.info('MCMC complete.')
    return dbf, optim_res
