"""
Visualization functionality for optimal power flow results.
"""

import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from hynet.types_ import SolverType, BusType, BranchType

_log = logging.getLogger(__name__)


def _check_data_availability(result):
    """Check availability of OPF result data."""
    if result.empty:
        raise RuntimeError("The OPF result is empty.")
    if not result.is_physical:
        if result.solver.type == SolverType.QCQP:
            remark = "solver issue"
        else:
            remark = "inexact relaxation or solver issue"
        _log.warning("The OPF result does not satisfy the power "
                     "balance ({0:s}).".format(remark))


def _set_id_labels(axis, index):
    """
    Relabel the one-based linear ticks with the IDs in ``index``.
    """
    axis.set_xticklabels(
        ['' if not (i.is_integer() and 1 <= i <= len(index))
         else str(index[int(i - 1)]) for i in axis.get_xticks()])


def show_lmp_profile(result, id_label=False):
    """
    Show the LMP profile or power balance dual variables for an OPF result.

    For a consistent appearance in case of nonconsecutive or custom IDs,
    **the buses are numbered consecutively starting from 1 for the
    labeling of the x-axis**. To enforce labeling of the ticks with the
    IDs, set ``id_label=True``.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    id_label : bool, optional
        If ``True``, the linear ticks are relabeled with the bus IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    _check_data_availability(result)
    if result.num_buses < 2:
        raise RuntimeError("LMP profile visualization is only available "
                           "for two or more buses.")
    if result.solver.type == SolverType.QCQP:
        # Zero duality gap is not ensured...
        title = "KKT multipliers for {:s} power balance"
    elif not result.is_physical:
        # Relaxation is not exact...
        title = "Dual variables for {:s} power balance"
    else:
        title = "LMP profile for {:s} power"

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(2, 1, 1)
    linear_index = 1 + np.arange(result.num_buses)
    ax.plot(linear_index, result.bus['dv_bal_p'].values,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, result.bus.index)
    ax.set_title(title.format('active'))
    ax.set_ylabel('$/MWh')
    ax.set_xlabel('Bus ' + ('ID' if id_label else 'Index'))
    ax = fig.add_subplot(2, 1, 2)
    ax.plot(linear_index, result.bus['dv_bal_q'].values,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, result.bus.index)
    ax.set_title(title.format('reactive'))
    ax.set_ylabel('$/Mvarh')
    ax.set_xlabel('Bus ' + ('ID' if id_label else 'Index'))
    fig.tight_layout()
    fig.show()
    return fig


def show_voltage_profile(result, id_label=False):
    """
    Show the voltage profile for an OPF result.

    For a consistent appearance in case of nonconsecutive or custom IDs,
    **the buses are numbered consecutively starting from 1 for the
    labeling of the x-axis**. To enforce labeling of the ticks with the
    IDs, set ``id_label=True``.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    id_label : bool, optional
        If ``True``, the linear ticks are relabeled with the bus IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    _check_data_availability(result)
    if result.num_buses < 2:
        raise RuntimeError("Voltage profile visualization is only "
                           "available for two or more buses.")
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(1, 1, 1)
    linear_index = 1 + np.arange(result.num_buses)
    v_min = result.scenario.bus.loc[result.bus.index, 'v_min']
    ax.plot(linear_index, v_min.values,
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    v_max = result.scenario.bus.loc[result.bus.index, 'v_max']
    ax.plot(linear_index, v_max.values,
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, result.bus['v'].abs().values,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, result.bus.index)
    ax.set_title("Voltage profile")
    ax.set_ylabel('p.u.')
    ax.set_xlabel('Bus ' + ('ID' if id_label else 'Index'))
    fig.tight_layout()
    fig.show()
    return fig


def show_branch_flow_profile(result, id_label=False):
    """
    Show the branch flow profile for an OPF result.

    For a consistent appearance in case of nonconsecutive or custom IDs,
    **the branches are numbered consecutively starting from 1 for the
    labeling of the x-axis**. To enforce labeling of the ticks with the
    IDs, set ``id_label=True``.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    id_label : bool, optional
        If ``True``, the linear ticks are relabeled with the branch IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    _check_data_availability(result)
    if result.num_branches < 2:
        raise RuntimeError("Branch flow profile visualization is only "
                           "available for two or more branches.")
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(1, 1, 1)
    linear_index = 1 + np.arange(result.num_branches)
    ax.plot(linear_index, result.branch['effective_rating'].values,
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index,
            result.branch[['s_src', 's_dst']].abs().max(axis=1).values,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, result.branch.index)
    ax.set_title("Branch flow profile")
    ax.set_ylabel('MVA for AC / MW for DC')
    ax.set_xlabel('Branch ' + ('ID' if id_label else 'Index'))
    fig.tight_layout()
    fig.show()
    return fig


def show_ampacity_dual_profile(result, id_label=False):
    """
    Show the ampacity dual variable profile for an OPF result.

    For a consistent appearance in case of nonconsecutive or custom IDs,
    **the branches are numbered consecutively starting from 1 for the
    labeling of the x-axis**. To enforce labeling of the ticks with the
    IDs, set ``id_label=True``.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    id_label : bool, optional
        If ``True``, the linear ticks are relabeled with the branch IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    _check_data_availability(result)
    if result.num_branches < 2:
        raise RuntimeError("Ampacity dual variable profile visualization "
                           "is only available for two or more branches.")
    dv_ampacity = result.branch[['dv_i_max_src',
                                 'dv_i_max_dst']].sum(axis=1).values
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(1, 1, 1)
    linear_index = 1 + np.arange(result.num_branches)
    ax.plot(linear_index, dv_ampacity,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, result.branch.index)
    ax.set_title("Ampacity dual variable profile")
    ax.set_ylabel('Dual Variable')
    ax.set_xlabel('Branch ' + ('ID' if id_label else 'Index'))
    fig.tight_layout()
    fig.show()
    return fig


def show_converter_flow_profile(result, id_label=False):
    """
    Show the converter active power flow profile for an OPF result.

    For a consistent appearance in case of nonconsecutive or custom IDs,
    **the converters are numbered consecutively starting from 1 for the
    labeling of the x-axis**. To enforce labeling of the ticks with the
    IDs, set ``id_label=True``.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    id_label : bool, optional
        If ``True``, the linear ticks are relabeled with the converter IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    _check_data_availability(result)
    if result.num_converters < 2:
        raise RuntimeError("Converter flow profile visualization is only "
                           "available for two or more converters.")
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(2, 1, 1)
    index = result.converter.index
    linear_index = 1 + np.arange(result.num_converters)
    cap_src = result.scenario.converter.loc[index, 'cap_src']
    ax.plot(linear_index, [x.p_min for x in cap_src],
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, [x.p_max for x in cap_src],
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, result.converter['p_src'].values,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, index)
    ax.set_title("Converter flow profile at the source terminal")
    ax.set_ylabel('MW')
    ax.set_xlabel('Converter ' + ('ID' if id_label else 'Index'))
    ax = fig.add_subplot(2, 1, 2)
    cap_dst = result.scenario.converter.loc[index, 'cap_dst']
    ax.plot(linear_index, [x.p_min for x in cap_dst],
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, [x.p_max for x in cap_dst],
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, result.converter['p_dst'].values,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, index)
    ax.set_title("Converter flow profile at the destination terminal")
    ax.set_ylabel('MW')
    ax.set_xlabel('Converter ' + ('ID' if id_label else 'Index'))
    fig.tight_layout()
    fig.show()
    return fig


def show_dispatch_profile(result, id_label=False):
    """
    Show the active power injector dispatch profile for an OPF result.

    For a consistent appearance in case of nonconsecutive or custom IDs,
    **the injectors are numbered consecutively starting from 1 for the
    labeling of the x-axis**. To enforce labeling of the ticks with the
    IDs, set ``id_label=True``.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    id_label : bool, optional
        If ``True``, the linear ticks are relabeled with the injector IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    _check_data_availability(result)
    if result.num_injectors < 2:
        raise RuntimeError("Injector dispatch visualization is only "
                           "available for two or more injectors.")
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(1, 1, 1)
    linear_index = 1 + np.arange(result.num_injectors)
    cap = result.scenario.injector.loc[result.injector.index, 'cap']
    ax.plot(linear_index, [x.p_min for x in cap],
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, [x.p_max for x in cap],
            color='xkcd:light red', linestyle='--', linewidth=0.5)
    ax.plot(linear_index, result.injector['s'].values.real,
            color='xkcd:sea blue', linestyle='-', linewidth=1)
    ax.margins(x=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if id_label:
        _set_id_labels(ax, result.injector.index)
    ax.set_title("Active power injector dispatch profile")
    ax.set_ylabel('MW')
    ax.set_xlabel('Injector ' + ('ID' if id_label else 'Index'))
    fig.tight_layout()
    fig.show()
    return fig


def show_power_balance_error(result, show_duals=True, split_acdc=True,
                             id_label=False):
    """
    Show the power balance error at all AC and DC buses for an OPF result.

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    show_duals : bool, optional
        If ``True`` (default), the active and reactive power balance dual
        variables are shown as well.
    split_acdc : bool, optional
        If ``True`` (default), the results are shown separate plots for AC and
        DC buses. In this case, no x-axis labels are provided. Otherwise, all
        buses are shown in one plot and, for the x-axis labels, the buses are
        numbered consecutively starting from 1.
    id_label : bool, optional
        If ``True`` (default ``False``), the linear x-axis ticks are relabeled
        with the bus IDs.

    Returns
    -------
    fig : matplotlib.figure.Figure

    See Also
    --------
    hynet.visual.opf.show_branch_reconstruction_error
    hynet.scenario.representation.Scenario.has_hybrid_architecture
    """
    _check_data_availability(result)

    idx_ac = result.scenario.bus['type'] == BusType.AC
    idx_dc = result.scenario.bus['type'] == BusType.DC

    has_ac = idx_ac.any()
    has_dc = idx_dc.any()

    num_rows = 3 if show_duals else 1
    num_cols = [has_ac, has_dc].count(True) if split_acdc else 1

    fig = plt.figure(figsize=(10, 3*num_rows))

    def plot(row_idx, col_idx, series, ylabel, title=''):
        ax = fig.add_subplot(num_rows, num_cols, col_idx + row_idx * num_cols,
                             title=title)
        linear_index = 1 + np.arange(len(series))
        ax.plot(linear_index, series.values,
                color='xkcd:sea blue', linestyle='-', linewidth=1)
        ax.margins(x=0)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylabel(ylabel)
        if split_acdc:
            ax.tick_params(labelbottom=False)
        elif id_label:
            _set_id_labels(ax, result.bus.index)

    def plot_column(col_idx, idx_bus, col_title, unit):
        row_idx = 0
        plot(row_idx, col_idx, result.bus.loc[idx_bus, 'bal_err'].abs(),
             "Power Balance\nError in " + unit, title=col_title)
        row_idx += 1

        if not show_duals:
            return

        plot(row_idx, col_idx, result.bus.loc[idx_bus, 'dv_bal_p'],
             "Active Power Balance\nDuals in $/MWh")
        row_idx += 1

        plot(row_idx, col_idx, result.bus.loc[idx_bus, 'dv_bal_q'],
             "Reactive Power Balance\nDuals in $/Mvarh")
        row_idx += 1

    col_idx = 1
    if split_acdc:
        if has_ac:
            plot_column(col_idx, idx_ac, "AC Buses", "MVA")
            col_idx += 1

        if has_dc:
            plot_column(col_idx, idx_dc, "DC Buses", "MW")
            col_idx += 1
    else:
        plot_column(col_idx, result.bus.index, "Buses", "MVA for AC / MW for DC")
        col_idx += 1

    fig.tight_layout()
    fig.show()
    return fig


def show_branch_reconstruction_error(result,
                                     show_s_bal_err=True,
                                     show_p_bal_err=False,
                                     show_q_bal_err=False,
                                     show_p_dual=True,
                                     show_q_dual=True,
                                     show_z_bar_abs=False,
                                     show_z_bar_real=False,
                                     show_z_bar_imag=False):
    """
    Show the branch-related reconstruction error for an OPF result.

    If the SOCR of an OPF problem is solved and the graph traversal based
    rank-1 approximation is used, the branch-related "contributions" to
    the reconstruction error (and, if present, inexactness of the relaxation)
    are characterized by :math:`\kappa_k(V^\star)` defined in equation (24)
    in [1]_. Especially if the scenario features the *hybrid architecture* and
    inexactness occurred, this visualization may assist in finding the cause
    of the pathological price profile (see also [1]_, Section VII, for more
    details).

    Parameters
    ----------
    result : OPFResult
        Optimal power flow result that shall be visualized.
    show_s_bal_err : bool, optional
        If ``True`` (default), the maximum apparent power balance error
        magnitude at the adjacent buses of the branches is shown as well.
    show_p_bal_err : bool, optional
        If ``True`` (default ``False``), the maximum active power balance
        error modulus at the adjacent buses of the branches is shown as well.
    show_q_bal_err : bool, optional
        If ``True`` (default ``False``), the maximum reactive power balance
        error modulus at the adjacent buses of the branches is shown as well.
    show_p_dual : bool, optional
        If ``True`` (default), the minimum active power balance dual variable
        at the adjacent buses of the branches is shown as well.
    show_q_dual : bool, optional
        If ``True`` (default), the minimum reactive power balance dual variable
        at the adjacent buses of the branches is shown as well.
    show_z_bar_abs : bool, optional
        If ``True`` (default ``False``), the modulus of the branch series
        impedance is shown as well.
    show_z_bar_real : bool, optional
        If ``True`` (default ``False``), the modulus of the branch series
        resistance is shown as well.
    show_z_bar_imag : bool, optional
        If ``True`` (default ``False``), the modulus of the branch series
        reactance is shown as well.

    Returns
    -------
    fig : matplotlib.figure.Figure

    See Also
    --------
    hynet.visual.opf.show_power_balance_error
    hynet.scenario.representation.Scenario.has_hybrid_architecture
    hynet.qcqp.rank1approx.GraphTraversalRank1Approximator

    References
    ----------
    .. [1] M. Hotz and W. Utschick, "The Hybrid Transmission Grid Architecture:
           Benefits in Nodal Pricing," in IEEE Trans. Power Systems, vol. 33,
           no. 2, pp. 1431-1442, Mar. 2018.
    """
    scenario = result.scenario

    idx_dc = scenario.get_dc_branches()
    idx_tf = \
        scenario.branch.index[scenario.branch['type'] == BranchType.TRANSFORMER]
    idx_ac = scenario.branch.index.difference(idx_dc).difference(idx_tf)

    num_cols = [idx_tf.empty, idx_ac.empty, idx_dc.empty].count(False)
    num_rows = [show_s_bal_err, show_p_bal_err, show_q_bal_err,
                show_p_dual, show_q_dual, show_z_bar_abs, show_z_bar_real,
                show_z_bar_imag].count(True) + 1

    set_ylabel = True
    fig = plt.figure(figsize=(14, 9))

    def plot(row_idx, col_idx, values, ylabel, title=''):
        ax = fig.add_subplot(num_rows, num_cols, col_idx + row_idx * num_cols,
                             title=title)
        ax.plot(values, color='xkcd:sea blue', linestyle='-', linewidth=1)
        ax.margins(x=0)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(labelbottom=False)
        if set_ylabel:
            ax.set_ylabel(ylabel)

    def plot_column(col_idx, col_title, branch_idx):
        nonlocal set_ylabel
        row_idx = 0

        rel_err = result.branch.loc[branch_idx, 'rel_err'].values
        z_bar = scenario.branch.loc[branch_idx, 'z_bar'].values

        bus_src = scenario.branch.loc[branch_idx, 'src'].values
        bus_dst = scenario.branch.loc[branch_idx, 'dst'].values

        bal_err_src = result.bus.loc[bus_src, 'bal_err'].values
        bal_err_dst = result.bus.loc[bus_dst, 'bal_err'].values

        bal_err_max_abs = np.maximum(np.abs(bal_err_src),
                                     np.abs(bal_err_dst))
        bal_err_max_real = np.maximum(np.abs(bal_err_src.real),
                                      np.abs(bal_err_dst.real))
        bal_err_max_imag = np.maximum(np.abs(bal_err_src.imag),
                                      np.abs(bal_err_dst.imag))

        dv_bal_p_src = result.bus.loc[bus_src, 'dv_bal_p']
        dv_bal_p_dst = result.bus.loc[bus_dst, 'dv_bal_p']
        dv_bal_p_min = np.minimum(dv_bal_p_src.values, dv_bal_p_dst.values)

        dv_bal_q_src = result.bus.loc[bus_src, 'dv_bal_q']
        dv_bal_q_dst = result.bus.loc[bus_dst, 'dv_bal_q']
        dv_bal_q_min = np.minimum(dv_bal_q_src.values, dv_bal_q_dst.values)

        plot(row_idx, col_idx, rel_err,
             "Reconstruction\nError " + r"$\kappa_k(V^\star)$", title=col_title)
        row_idx += 1

        if show_s_bal_err:
            plot(row_idx, col_idx, bal_err_max_abs,
                 "Max. Adjacent\nS Bal. Error in MVA")
            row_idx += 1

        if show_p_bal_err:
            plot(row_idx, col_idx, bal_err_max_real,
                 "Max. Adjacent\nP Bal. Error in MW")
            row_idx += 1

        if show_q_bal_err:
            plot(row_idx, col_idx, bal_err_max_imag,
                 "Max. Adjacent\nQ Bal. Error in Mvar")
            row_idx += 1

        if show_p_dual:
            plot(row_idx, col_idx, dv_bal_p_min,
                 "Min. Adjacent\nP Bal. DV in $/MW")
            row_idx += 1

        if show_q_dual:
            plot(row_idx, col_idx, dv_bal_q_min,
                 "Min. Adjacent\nQ Bal. DV in $/Mvar")
            row_idx += 1

        if show_z_bar_abs:
            plot(row_idx, col_idx, np.abs(z_bar),
                 r"$|\bar{z}_k|$ in p.u.")
            row_idx += 1

        if show_z_bar_real:
            plot(row_idx, col_idx, z_bar.real,
                 r"Re$(\bar{z}_k)$ in p.u.")
            row_idx += 1

        if show_z_bar_imag:
            plot(row_idx, col_idx, z_bar.imag,
                 r"Im$(\bar{z}_k)$ in p.u.")
            row_idx += 1

        set_ylabel = False  # Only set the y-labels in the first column

    col_idx = 1
    if not idx_tf.empty:
        plot_column(col_idx, "Transformers", idx_tf)
        col_idx += 1

    if not idx_ac.empty:
        plot_column(col_idx, "AC Lines", idx_ac)
        col_idx += 1

    if not idx_dc.empty:
        plot_column(col_idx, "DC Lines", idx_dc)
        col_idx += 1

    fig.tight_layout()
    return fig
