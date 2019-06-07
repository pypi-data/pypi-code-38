"""
Evaluation of the network reduction accuracy.
"""

import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from hynet.types_ import SolverStatus

_log = logging.getLogger(__name__)


def evaluate_reduction(opf_reference, opf_reduction, name=None):
    """
    Return an evaluation of the extent and accuracy of the reduction.

    Parameters
    ----------
    opf_reference : OPFResult
        OPF result of the scenario *before* the reduction.
    opf_reduction : OPFResult
        OPF result of the scenario *after* the reduction.
    name : object, optional
        Name of the returned series. This may be set, e.g., to the name of the
        reduction stage or characteristic parameter value.

    Returns
    -------
    evaluation : pandas.Series
        Series with information on the extent and accuracy of the reduction
        with the following entries:

        ``bus_reduction``: (``hynet_float_``)
            Ratio of the number of reduced buses w.r.t. the total number of
            buses before the reduction.
        ``branch_reduction``: (``hynet_float_``)
            Ratio of the number of reduced branches w.r.t. the total number of
            branches before the reduction.
        ``cycle_reduction``: (``hynet_float_``)
            Ratio of the number of reduced cycles w.r.t. the total number of
            cycles before the reduction.
        ``error_disp``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power dispatch error
            as defined in equation (1) in [1]_.
        ``error_disp_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power dispatch
            error.
        ``error_flow``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power branch flow
            error as defined in equation (2) in [1]_.
        ``error_flow_s``: (``hynet_float_``)
            Contribution-weighted mean relative *apparent* power branch flow
            error.

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    scenario_ref = opf_reference.scenario
    scenario_red = opf_reduction.scenario

    if opf_reference.solver_status != SolverStatus.SOLVED or \
            opf_reduction.solver_status != SolverStatus.SOLVED:
        raise ValueError("The evaluation requires successfully solved OPFs.")

    if not (opf_reference.is_physical and opf_reduction.is_physical):
        _log.warning("The evaluation is performed on a non-physical solution.")

    if not opf_reduction.injector.index.equals(opf_reference.injector.index):
        raise ValueError("The injectors of the two systems do not match.")

    if not scenario_red.branch.index.isin(scenario_ref.branch.index).all():
        raise ValueError("The branches of the reduction are not a subset "
                         "of the branches of the reference system.")

    evaluation = pd.Series()
    if name is not None:
        evaluation.name = name

    # Dispatch error
    dispatch_ref = opf_reference.injector['s']
    dispatch_red = opf_reduction.injector['s']

    dispatch_diff = dispatch_red - dispatch_ref

    evaluation.at['error_disp'] = \
        np.sum(np.abs(dispatch_diff.real)) / np.sum(np.abs(dispatch_ref.real))

    evaluation.at['error_disp_s'] = \
        dispatch_diff.abs().sum() / dispatch_ref.abs().sum()

    # Branch flow error
    idx = opf_reduction.branch.index
    flow_ref = opf_reference.branch.loc[idx, ['s_src', 's_dst']]
    flow_red = opf_reduction.branch.loc[idx, ['s_src', 's_dst']]

    flow_ref_p = np.maximum(np.abs(flow_ref['s_src'].real),
                            np.abs(flow_ref['s_dst'].real))

    flow_red_p = np.maximum(np.abs(flow_red['s_src'].real),
                            np.abs(flow_red['s_dst'].real))

    flow_ref_s = flow_ref.abs().max(axis=1)
    flow_red_s = flow_red.abs().max(axis=1)

    if flow_ref_p.size:
        evaluation.at['error_flow'] = \
            np.sum(np.abs(flow_red_p - flow_ref_p)) / np.sum(flow_ref_p)
        evaluation.at['error_flow_s'] = \
            (flow_red_s - flow_ref_s).abs().sum() / flow_ref_s.sum()
    else:
        evaluation.at['error_flow'] = np.nan
        evaluation.at['error_flow_s'] = np.nan

    # Reduction of system entities
    buses_ref = scenario_ref.num_buses
    buses_red = scenario_red.num_buses
    evaluation.at['bus_reduction'] = (buses_ref - buses_red) / buses_ref

    branches_ref = scenario_ref.num_branches
    branches_red = scenario_red.num_branches
    if branches_ref:
        evaluation.at['branch_reduction'] = \
            (branches_ref - branches_red) / branches_ref
    else:
        evaluation.at['branch_reduction'] = 0.0

    cycles_ref = scenario_ref.analyze_cycles()['num_cycles'].sum()
    cycles_red = scenario_red.analyze_cycles()['num_cycles'].sum()
    if cycles_ref:
        evaluation.at['cycle_reduction'] = \
            (cycles_ref - cycles_red) / cycles_ref
    else:
        evaluation.at['cycle_reduction'] = 0.0

    return evaluation


def show_reduction_evaluation(evaluation):
    """
    Show the evaluation of a series of reduction stages or a parameter sweep.

    Parameters
    ----------
    evaluation : pandas.DataFrame
        Data frame with information on the extent and accuracy of the
        individual reduction stages or parameters. This data frame must be
        indexed by the stage names / parameter values and comprise the
        following columns:

        ``bus_reduction``: (``hynet_float_``)
            Ratio of the number of reduced buses w.r.t. the total number of
            buses before the reduction.
        ``branch_reduction``: (``hynet_float_``)
            Ratio of the number of reduced branches w.r.t. the total number of
            branches before the reduction.
        ``cycle_reduction``: (``hynet_float_``)
            Ratio of the number of reduced cycles w.r.t. the total number of
            cycles before the reduction.
        ``error_disp``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power dispatch error
            as defined in equation (1) in [1]_.
        ``error_flow``: (``hynet_float_``)
            Contribution-weighted mean relative *active* power branch flow
            error as defined in equation (2) in [1]_.

    Returns
    -------
    fig : matplotlib.figure.Figure

    References
    ----------
    .. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
           "Feature- and Structure-Preserving Network Reduction for Large-Scale
           Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
           Italy, Jun. 2019.
    """
    if np.issubdtype(evaluation.index.dtype, np.number):
        index = evaluation.index
        labels = None
    else:
        index = 1 + np.arange(len(evaluation.index))
        labels = evaluation.index

    def set_x_labels(ax):
        ax.margins(x=0)
        if labels is None:
            return
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xticklabels(['' if not (i.is_integer() and 1 <= i <= len(labels))
                            else str(labels[int(i - 1)]) for i in ax.get_xticks()])

    fig = plt.figure(figsize=(10, 6))

    ax = fig.add_subplot(2, 1, 1)
    ax.plot(index, evaluation['bus_reduction'].values * 100,
            color='xkcd:red', marker='.', linestyle='-', linewidth=1,
            label='Buses')
    ax.plot(index, evaluation['branch_reduction'].values * 100,
            color='xkcd:sea blue', marker='.', linestyle='-', linewidth=1,
            label='Branches')
    ax.plot(index, evaluation['cycle_reduction'].values * 100,
            color='xkcd:green', marker='.', linestyle='-', linewidth=1,
            label='Cycles')
    set_x_labels(ax)
    ax.set_ylabel('Reduction in %')
    ax.legend(loc='lower right', frameon=True)

    if hasattr(evaluation, 'name'):
        ax.set_title(evaluation.name)

    ax = fig.add_subplot(2, 1, 2)
    ax.plot(index, evaluation['error_disp'].values * 100,
            color='xkcd:red', marker='.', linestyle='-', linewidth=1,
            label='Dispatch')
    ax.plot(index, evaluation['error_flow'].values * 100,
            color='xkcd:sea blue', marker='.', linestyle='-', linewidth=1,
            label='Branch flow')
    set_x_labels(ax)
    ax.set_ylabel('Error in %')
    ax.legend(loc='lower right', frameon=True)

    if evaluation.index.name:
        ax.set_xlabel(evaluation.index.name)

    fig.tight_layout()
    fig.show()
    return fig
