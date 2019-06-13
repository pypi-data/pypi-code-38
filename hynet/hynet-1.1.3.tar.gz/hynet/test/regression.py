"""
Support for OPF regression tests.
"""

import logging
from collections import namedtuple

import numpy as np

_log = logging.getLogger(__name__)


class OPFVerificationData(namedtuple('OPFVerificationData',
                                     ['OPTIMAL_VALUE',
                                      'VOLTAGES',
                                      'BRANCH_FLOW_SRC',
                                      'CONVERTER_FLOW_SRC',
                                      'DISPATCH',
                                      'DV_BALANCE_P',
                                      'DV_CAP_P_MAX',
                                      'DV_V_MAX'])):
    """
    OPF solution verification data for regression tests.

    This class contains the minimum amount of reference data to properly verify
    the outcome of an OPF calculation. It was introduced to compactly embed the
    reference solution for installation testing in *hynet*'s code - it's not
    too pleasing, but simple and robust ;)
    """
    @staticmethod
    def create(result):
        """
        Return a OPF verification data object for the given OPF result.

        Parameters
        ----------
        result : hynet.opf.result.OPFResult
            OPF result for which the OPF verification data shall be created.

        Returns
        -------
        reference : OPFVerificationData
            OPF verification data.
        """
        return OPFVerificationData(
            OPTIMAL_VALUE=result.optimal_value,
            VOLTAGES=result.bus['v'].values,
            BRANCH_FLOW_SRC=result.branch['s_src'].values,
            CONVERTER_FLOW_SRC=(result.converter['p_src']
                                - 1j * result.converter['q_src']).values,
            DISPATCH=result.injector['s'].values,
            DV_BALANCE_P=result.bus['dv_bal_p'].values,
            DV_CAP_P_MAX=result.injector['dv_cap_p_max'].values,
            DV_V_MAX=result.bus['dv_v_max'].values
        )


def _rel_mae(value, reference):
    """Return the relative mean absolute error."""
    return np.sum(np.abs(value - reference)) / np.sum(np.abs(reference))


def verify_opf_result(result, reference, tolerance):
    """
    Verify an OPF result versus a reference solution.

    The OPF result is verified by comparing the OPF verification data to a
    reference solution by calculating the respective relative mean absolute
    errors and checking them against a tolerance threshold. As the bus voltage
    magnitudes are less rigid (in particular w.r.t. relaxations), the error
    threshold is relaxed for those comparisons.

    Parameters
    ----------
    result : OPFVerificationData
        OPF solution that shall be verified.
    reference : OPFVerificationData
        Reference OPF solution.
    tolerance : .hynet_float_
        Tolerance on the relative mean absolute error of the individual result
        vectors.

    Raises
    ------
    ValueError
        In case any mismatch beyond the tolerance is detected.
    """
    MESSAGE_END = " not match the expected result."

    # REMARK: The checks are formulated in a negated form to detect NaNs as well.
    _log.debug("Relative mean absolute errors to reference OPF solution:")

    rel_err = _rel_mae(result.OPTIMAL_VALUE, reference.OPTIMAL_VALUE)
    _log.debug(" - Optimal objective value: {:.6e}".format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The optimal objective does" + MESSAGE_END)

    rel_err = _rel_mae(np.abs(result.VOLTAGES), np.abs(reference.VOLTAGES))
    _log.debug(" - Bus voltage magnitudes: {:.6e}".format(rel_err))
    if not rel_err <= 10 * tolerance:  # Be tolerant for the relaxations... :)
        raise ValueError("The optimal bus voltage magnitudes do" + MESSAGE_END)

    rel_err = _rel_mae(np.angle(result.VOLTAGES), np.angle(reference.VOLTAGES))
    _log.debug(" - Bus voltage angles: {:.6e}".format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The optimal bus voltage angles do" + MESSAGE_END)

    rel_err = _rel_mae(result.BRANCH_FLOW_SRC, reference.BRANCH_FLOW_SRC)
    _log.debug(" - Branch flows (at source bus): {:.6e}".format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The branch flows do" + MESSAGE_END)

    rel_err = _rel_mae(result.CONVERTER_FLOW_SRC, reference.CONVERTER_FLOW_SRC)
    _log.debug(" - Converter flows (at source bus): {:.6e}".format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The converter flows do" + MESSAGE_END)

    rel_err = _rel_mae(result.DISPATCH, reference.DISPATCH)
    _log.debug(" - Injector dispatch: {:.6e}".format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The injector dispatch does" + MESSAGE_END)

    rel_err = _rel_mae(result.DV_BALANCE_P, reference.DV_BALANCE_P)
    _log.debug(" - Active power balance dual variables: {:.6e}".format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The active power balance dual variables do" +
                         MESSAGE_END)

    rel_err = _rel_mae(result.DV_CAP_P_MAX, reference.DV_CAP_P_MAX)
    _log.debug(" - Injector active power UB dual variables: {:.6e}"
               .format(rel_err))
    if not rel_err <= tolerance:
        raise ValueError("The injector active power UB dual variables do" +
                         MESSAGE_END)

    rel_err = _rel_mae(result.DV_V_MAX, reference.DV_V_MAX)
    _log.debug(" - Voltage UB dual variables: {:.6e}".format(rel_err))
    if not rel_err <= 10 * tolerance:
        raise ValueError("The voltage UB dual variables do" + MESSAGE_END)
