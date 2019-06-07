"""
Import of model data into the *hynet* data format.
"""

import logging
import os.path

import numpy as np
import scipy.io
import h5py

from hynet.types_ import (hynet_float_,
                          DBInfoKey,
                          BusType,
                          BranchType,
                          InjectorType,
                          EntityType)
from hynet.data.connection import connect, DBTransaction
from hynet.data.structure import (DBInfo,
                                  DBScenario,
                                  DBBus,
                                  DBBranch,
                                  DBConverter,
                                  DBInjector,
                                  DBCapabilityRegion,
                                  DBSamplePoint,
                                  DBShunt,
                                  DBScenarioLoad,
                                  DBScenarioInjector,
                                  DBScenarioInactivity)

_log = logging.getLogger(__name__)

MAT_FILE_EXTENSION = '.mat'


class BusConstants:
    """Constants for the MATPOWER bus data, see the MATPOWER manual."""

    # Bus matrix column indices
    BUS_I = 0       # Bus number
    BUS_TYPE = 1    # Bus type
    PD = 2          # Real power demand (MW)
    QD = 3          # Reactive power demand (MVAr)
    GS = 4          # Shunt conductance as loss in MW at V = 1.0 p.u.
    BS = 5          # Shunt susceptance as injection in MVAr at V = 1.0 p.u.
    BUS_AREA = 6    # Area number
    VM = 7          # Voltage magnitude (p.u.)
    VA = 8          # Voltage angle (degrees)
    BASE_KV = 9     # Base voltage (kV)
    ZONE = 10       # (Loss) Zone
    VMAX = 11       # Maximum voltage magnitude (p.u.)
    VMIN = 12       # Minimum voltage magnitude (p.u.)

    # Bus types
    PQ = 1          # PQ-bus (fixed variables in power flow calculations)
    PV = 2          # PV-bus (fixed variables in power flow calculations)
    REF = 3         # Reference bus
    NONE = 4        # Isolated/inactive bus

    # OPF result column indices in the bus matrix
    LAM_P = 13      # Lagrange multiplier on real power balance
    LAM_Q = 14      # Lagrange multiplier on reactive power balance
    MU_VMAX = 15    # KKT multiplier on upper voltage limit
    MU_VMIN = 16    # KKT multiplier on lower voltage limit


class BranchConstants:
    """Constants for the MATPOWER branch data, see the MATPOWER manual."""

    # Branch matrix column indices
    F_BUS = 0       # "From" bus number
    T_BUS = 1       # "To" bus number
    BR_R = 2        # Series resistance (p.u.)
    BR_X = 3        # Series reactance (p.u.)
    BR_B = 4        # Total line charging susceptance (p.u.)
    RATE_A = 5      # MVA rating A (long term rating)
    RATE_B = 6      # MVA rating B (short term rating)
    RATE_C = 7      # MVA rating C (emergency rating)
    TAP = 8         # Transformer ratio
    SHIFT = 9       # Transformer phase shift (degrees)
    BR_STATUS = 10  # Status (1 - in service, 0 - out of service)
    ANGMIN = 11     # Minimum angle difference (degrees)
    ANGMAX = 12     # Maximum angle difference (degrees)

    # OPF result column indices in the branch matrix
    PF = 13         # Real power injected at "from" bus end (MW)
    QF = 14         # Reactive power injected at "from" bus end (MVAr)
    PT = 15         # Real power injected at "to" bus end (MW)
    QT = 16         # Reactive power injected at "to" bus end (MVAr)
    MU_SF = 17      # KKT multiplier on MVA limit at "from" bus
    MU_ST = 18      # KKT multiplier on MVA limit at "to" bus
    MU_ANGMIN = 19  # KKT multiplier lower angle difference limit
    MU_ANGMAX = 20  # KKT multiplier upper angle difference limit


class GeneratorConstants:
    """Constants for the MATPOWER generator data, see the MATPOWER manual."""

    # Generator matrix column indices
    GEN_BUS = 0     # Bus number
    PG = 1          # Real power output (MW)
    QG = 2          # Reactive power output (MVAr)
    QMAX = 3        # Maximum reactive power output (MVAr)
    QMIN = 4        # Minimum reactive power output (MVAr)
    VG = 5          # Voltage magnitude set point (p.u.)
    MBASE = 6       # Total MVA base of this machine
    GEN_STATUS = 7  # Status (1 - in service, 0 - out of service)
    PMAX = 8        # Maximum real power output (MW)
    PMIN = 9        # Minimum real power output (MW)
    PC1 = 10        # Lower real power output of PQ capability curve (MW)
    PC2 = 11        # Upper real power output of PQ capability curve (MW)
    QC1MIN = 12     # Minimum reactive power output at PC1 (MVAr)
    QC1MAX = 13     # Maximum reactive power output at PC1 (MVAr)
    QC2MIN = 14     # Minimum reactive power output at PC2 (MVAr)
    QC2MAX = 15     # Maximum reactive power output at PC2 (MVAr)
    RAMP_AGC = 16   # Ramp rate for load following/AGC (MW/min)
    RAMP_10 = 17    # Ramp rate for 10 minute reserves (MW)
    RAMP_30 = 18    # Ramp rate for 30 minute reserves (MW)
    RAMP_Q = 19     # Ramp rate for reactive power (2 sec timescale) (MVAr/min)
    APF = 20        # Area participation factor

    # OPF result column indices in the generator matrix
    MU_PMAX = 21    # KKT multiplier on upper active power upper limit
    MU_PMIN = 22    # KKT multiplier on lower active power upper limit
    MU_QMAX = 23    # KKT multiplier on upper reactive power upper limit
    MU_QMIN = 24    # KKT multiplier on lower reactive power upper limit

    # Generator cost matrix column indices
    MODEL = 0       # Cost model
    STARTUP = 1     # Startup cost in $
    SHUTDOWN = 2    # Shutdown cost in $
    NCOST = 3       # Number of cost coefficients (poly) or sample points (PWL)
    COST = 4        # Start column of coefficient or sample point data

    # Cost model types
    PW_LINEAR = 1   # Piecewise linear cost function
    POLYNOMIAL = 2  # Polynomial cost function


class DCLineConstants:
    """Constants for the MATPOWER DC line data, see the MATPOWER manual."""

    # DC line matrix column indices
    F_BUS = 0       # "From" bus number
    T_BUS = 1       # "To"  bus number
    BR_STATUS = 2   # Status (1 - in service, 0 - out of service)
    PMIN = 9        # Lower limit on MW flow at "from" end
    PMAX = 10       # Upper limit on MW flow at "from" end
    QMINF = 11      # Lower limit on MVAr injection at "from" bus
    QMAXF = 12      # Upper limit on MVAr injection at "from" bus
    QMINT = 13      # Lower limit on MVAr injection at "to" bus
    QMAXT = 14      # Upper limit on MVAr injection at "to" bus
    LOSS0 = 15      # Offset of linear loss function (MW)
    LOSS1 = 16      # Slope of linear loss function

    # OPF result column indices in the DC line matrix
    PF = 3          # Flow at "from" bus in MW
    PT = 4          # Flow at  "to"  bus in MW
    QF = 5          # Injection at "from" bus in MVAr
    QT = 6          # Injection at  "to"  bus in MVAr
    VF = 7          # Voltage set point at "from" bus (p.u.)
    VT = 8          # Voltage set point at "to" bus (p.u.)
    MU_PMIN = 17    # KKT multiplier on lower flow lim at "from" bus
    MU_PMAX = 18    # KKT multiplier on upper flow lim at "from" bus
    MU_QMINF = 19   # KKT multiplier on lower VAr lim at "from" bus
    MU_QMAXF = 20   # KKT multiplier on upper VAr lim at "from" bus
    MU_QMINT = 21   # KKT multiplier on lower VAr lim at "to" bus
    MU_QMAXT = 22   # KKT multiplier on upper VAr lim at "to" bus


def _load_mpc_from_mat_file(input_file):
    """
    Load the MATPOWER case struct from the MAT file.

    SciPy's MAT loading (``scipy.io.loadmat``) only supports the formats
    v4 (Level 1.0), v6, and v7 to 7.2. For later versions, ``h5py`` is
    employed. The data is preprocessed for equal structure among all versions.
    """
    mpc = {}
    try:
        mat = scipy.io.loadmat(input_file)['mpc']
        mpc['baseMVA'] = mat['baseMVA'][0][0][0][0]
        prepare_data = lambda x: x[0][0]
        prepare_dict = prepare_data
        get_keys = lambda x: x.dtype.names
    except NotImplementedError:
        mat = h5py.File(input_file, 'r')['mpc']
        mpc['baseMVA'] = mat['baseMVA'][0][0]

        def fix_empty_matrix(x):
            if x.shape == (2,):
                return np.ndarray(shape=x, dtype=hynet_float_).transpose()
            return x

        prepare_data = lambda x: fix_empty_matrix(x[()]).transpose()
        prepare_dict = lambda x: x
        get_keys = lambda x: x.keys()

    mpc['bus'] = prepare_data(mat['bus'])
    mpc['branch'] = prepare_data(mat['branch'])
    mpc['gen'] = prepare_data(mat['gen'])
    mpc['gencost'] = prepare_data(mat['gencost'])
    try:
        mpc['dcline'] = prepare_data(mat['dcline'])
    except (ValueError, KeyError):
        mpc['dcline'] = np.ndarray((0, DCLineConstants.LOSS1 + 1),
                                   dtype=hynet_float_)

    # --- CUSTOM EXTENSION: Scenario & line length information ---
    try:
        mpc['line_length'] = prepare_data(mat['line_length'])
    except (ValueError, KeyError):
        pass

    if 'line_length' in mpc:
        if mpc['line_length'].shape[0] != mpc['branch'].shape[0]:
            raise ValueError("Line length information is inconsistent.")

    try:
        scenarios = prepare_dict(mat['scenarios'])
    except (ValueError, KeyError):
        pass
    else:
        mpc['scenarios'] = {}
        for scenario in get_keys(scenarios):
            mpc['scenarios'][scenario] = {}
            scenario_data = prepare_dict(scenarios[scenario])
            for field in get_keys(scenario_data):
                mpc['scenarios'][scenario][field] = \
                    prepare_data(scenario_data[field])
    # --- CUSTOM EXTENSION: END ----------------------------------
    return mpc


def _get_gencost_sample_points(cost, p_min, p_max, num_sample_points):
    """Return the PWL function sample points for a MATPOWER ``gencost`` row."""
    cgen = GeneratorConstants
    sample_points = []
    N = int(cost[cgen.NCOST])

    if N < 1:
        return sample_points

    if cost[cgen.MODEL] == cgen.PW_LINEAR:
        for x in range(N):
            sample_points.append((cost[cgen.COST + 2*x],
                                  cost[cgen.COST + 2*x + 1]))
        return sample_points

    if cost[cgen.MODEL] == cgen.POLYNOMIAL:
        coeff = cost[cgen.COST:cgen.COST + N]

        if np.all(coeff == 0):
            return sample_points

        if N == 1:
            # Constant function
            sample_points.append((0, coeff[0]))
            sample_points.append((1, coeff[0]))
            return sample_points

        if np.all(coeff[:-2] == 0):
            # Linear function
            sample_points.append((0, coeff[-1]))
            sample_points.append((1, coeff[-1] + coeff[-2]))
            return sample_points

        # Polynomial of second or higher order
        if p_min > p_max:
            raise ValueError("The test case contains a generator with "
                             "infeasible active power limits: "
                             "PMIN = {:f} > {:f} = PMAX.".format(p_min, p_max))

        if p_min == p_max:
            constant_cost = np.polyval(coeff, p_min)
            sample_points.append((0, constant_cost))
            sample_points.append((1, constant_cost))
            _log.warning("For generators with fixed active power injection, "
                         "the conversion of polynomial cost functions is not "
                         "supported. The cost function is set to the constant "
                         "{:f} that reflects the cost at its operating point."
                         .format(constant_cost))
            return sample_points

        for x in np.linspace(p_min, p_max, num_sample_points):
            sample_points.append((x, np.polyval(coeff, x)))
        return sample_points

    raise ValueError("Invalid cost function type: {:d}".format(cost[cgen.MODEL]))


def import_matpower_test_case(input_file, output_file=None, grid_name=None,
                              description='', num_sample_points=10,
                              res_detection=False):
    """
    Import a MATPOWER test case file into *hynet*'s database format.

    This function imports a MATPOWER test case, which is stored as a MATPOWER
    test case struct ``mpc`` in a MATLAB MAT-file, to a *hynet*'s database. To
    prepare the import, start MATLAB and perform the following two steps:

    1) Load the MATPOWER test case into the variable ``mpc``::

        mpc = loadcase('your_matpower_test_case_file.m');

    2) Save the MATPOWER test case struct ``mpc`` to a MATLAB MAT file::

        save('your_matpower_test_case_file.mat', 'mpc');

    Call this function with the MAT-file as the input.

    Parameters
    ----------
    input_file : str
        MATLAB MAT-file (.mat) with the MATPOWER test case struct ``mpc``.
    output_file : str, optional
        Destination *hynet* grid database file. By default (None), the file
        name is set to the input file name with a ``.db`` extension.
    grid_name : str, optional
        Name of the grid. By default (None), the grid name is set to the input
        file name excluding the extension.
    description : str, optional
        Description of the grid model and, if applicable, copyright and
        licensing information.
    num_sample_points : int, optional
        Number of sample points that shall be used for the conversion of
        polynomial to piecewise linear cost functions (on the interval from
        minimum to maximum output). This setting is a trade-off between an
        accurate representation of the original cost function and the number
        of additional constraints in the OPF problem.
    res_detection : bool, optional
        Detection of the injector type for renewable energy sources (RES),
        which is inactive by default. This scheme is motivated by the German
        grid data, which contains PV- and wind-based injectors with zero
        marginal cost that are arranged in a specific pattern: The injectors
        that connect to the same bus are stored consecutively in the generator
        matrix. If two or more injectors connect to the same bus, then the
        *last* one is wind-based and the *second to the last* is PV-based
        generation if their marginal cost is zero. If this parameter is set to
        True, this RES detection scheme is enabled.

    Returns
    -------
    output_file : str
        Destination *hynet* grid database file name.

    Raises
    ------
    ValueError
    NotImplementedError
    """
    cbus = BusConstants
    cbra = BranchConstants
    cgen = GeneratorConstants
    cdcl = DCLineConstants

    if num_sample_points < 2:
        raise ValueError("Invalid number of sample points (use >= 2).")

    # Check file names
    if not input_file.lower().endswith(MAT_FILE_EXTENSION):
        raise ValueError("The input file is not a MATLAB MAT-file.")

    if output_file is None:
        output_file = "{:}.db".format(input_file[:-len(MAT_FILE_EXTENSION)])

    # Load MATPOWER test case data
    try:
        mpc = _load_mpc_from_mat_file(input_file)
    except Exception as exception:
        raise IOError("Failed to load the MAT file: " + str(exception))

    # Connect to the destination database
    database = connect(output_file)

    if not database.empty:
        raise ValueError("The destination database is not empty.")

    if grid_name is None:
        grid_name = os.path.basename(os.path.splitext(input_file)[0])

    scenario_id = 0             # Scenario ID for the base case
    base_case_inactivity = []   # Track base case inactivity for scenarios
    base_kv = {}                # Track bus base volt. for transformer detection
    with DBTransaction(database) as transaction:
        # General database information
        transaction.add(DBInfo(key=DBInfoKey.GRID_NAME,
                               value=grid_name))
        transaction.add(DBInfo(key=DBInfoKey.BASE_MVA,
                               value=hynet_float_(mpc['baseMVA'])))
        transaction.add(DBInfo(key=DBInfoKey.DESCRIPTION,
                               value=description))

        # Add a default scenario
        transaction.add(DBScenario(id=scenario_id,
                                   time=0.,
                                   name='Base Case',
                                   loss_price=0.,
                                   annotation=''))

        # Import bus data
        if mpc['bus'].shape[0] < 1:
            raise ValueError("The test case does not contain any buses.")

        # Use the area number as zone if there is no zone information available
        ZONE_COLUMN = cbus.ZONE
        if np.all(mpc['bus'][:, cbus.ZONE] == mpc['bus'][0, cbus.ZONE]):
            if np.any(mpc['bus'][:, cbus.BUS_AREA] != mpc['bus'][0, cbus.BUS_AREA]):
                ZONE_COLUMN = cbus.BUS_AREA

        shunt_id = 1
        for bus in mpc['bus']:
            bus_id = int(bus[cbus.BUS_I])
            transaction.add(DBBus(id=bus_id,
                                  type=BusType.AC,
                                  ref=(bus[cbus.BUS_TYPE] == cbus.REF),
                                  base_kv=bus[cbus.BASE_KV],
                                  v_min=bus[cbus.VMIN],
                                  v_max=bus[cbus.VMAX],
                                  zone=int(bus[ZONE_COLUMN]),
                                  annotation=''))
            base_kv[bus_id] = bus[cbus.BASE_KV]

            # Add shunt
            if bus[cbus.GS] != 0 or bus[cbus.BS] != 0:
                transaction.add(DBShunt(id=shunt_id,
                                        bus_id=bus_id,
                                        p=bus[cbus.GS],
                                        q=bus[cbus.BS],
                                        annotation=''))
                shunt_id += 1

            # Add load to the scenario
            if bus[cbus.PD] != 0 or bus[cbus.QD] != 0:
                transaction.add(DBScenarioLoad(scenario_id=scenario_id,
                                               bus_id=bus_id,
                                               p=bus[cbus.PD],
                                               q=bus[cbus.QD]))

            # Is this bus isolated/inactive?
            if bus[cbus.BUS_TYPE] == cbus.NONE:
                inactivity = DBScenarioInactivity(scenario_id=scenario_id,
                                                  entity_type=EntityType.BUS,
                                                  entity_id=bus_id)
                transaction.add(inactivity)
                base_case_inactivity.append(inactivity)

        # Import branch data
        for i, branch in enumerate(mpc['branch']):
            branch_id = i + 1
            src_id = int(branch[cbra.F_BUS])
            dst_id = int(branch[cbra.T_BUS])

            # TRANSFORMER DETECTION: The branch type is set to transformer if
            # the branch connects different voltage levels or if the ratio or
            # phase setting is not neutral.
            #
            # REMARK: MATPOWER includes only a phase shifting transformer at
            # the source bus, which employs a *reciprocal* tap ratio compared
            # to *hynet*.
            ratio_src = 1. if branch[cbra.TAP] == 0 else 1 / branch[cbra.TAP]
            phase_src = -branch[cbra.SHIFT]
            if base_kv[src_id] != base_kv[dst_id] or \
                    ratio_src != 1 or phase_src != 0:
                branch_type = BranchType.TRANSFORMER
            else:
                branch_type = BranchType.LINE

            rating = branch[cbra.RATE_A]
            rating = rating if rating != 0 else None

            angle_min = angle_max = 0
            if len(branch) > cbra.ANGMIN:
                angle_min = branch[cbra.ANGMIN]
            if len(branch) > cbra.ANGMAX:
                angle_max = branch[cbra.ANGMAX]
            if ((angle_min == 0 and angle_max == 0) or
                    (angle_min <= -360 and angle_max >= 360)):
                angle_min = angle_max = None

            # --- CUSTOM EXTENSION: Line length information --------------
            if 'line_length' in mpc:
                line_length = mpc['line_length'][i, 0]
            else:
                line_length = None
            # --- CUSTOM EXTENSION: END ----------------------------------

            transaction.add(DBBranch(id=branch_id,
                                     type=branch_type,
                                     src_id=src_id,
                                     dst_id=dst_id,
                                     r=branch[cbra.BR_R],
                                     x=branch[cbra.BR_X],
                                     b_src=branch[cbra.BR_B] / 2,
                                     b_dst=branch[cbra.BR_B] / 2,
                                     ratio_src=ratio_src,
                                     phase_src=phase_src,
                                     ratio_dst=1.,
                                     phase_dst=0.,
                                     length=line_length,
                                     rating=rating,
                                     angle_min=angle_min,
                                     angle_max=angle_max,
                                     drop_min=None,
                                     drop_max=None,
                                     annotation=''))

            # Is this branch inactive?
            if branch[cbra.BR_STATUS] == 0:
                inactivity = DBScenarioInactivity(scenario_id=scenario_id,
                                                  entity_type=EntityType.BRANCH,
                                                  entity_id=branch_id)
                transaction.add(inactivity)
                base_case_inactivity.append(inactivity)

        # Import DC line data
        # (REMARK: The MATPOWER DC line model is compatible with *hynet*'s
        #  converter model, i.e., DC lines are imported as AC/AC converters.)
        i = 0
        converter_id = 0
        cap_region_id = 1  # Note: This ID counter is also used for inj. cap. reg.
        while i < mpc['dcline'].shape[0]:
            converter_id += 1
            dcline = mpc['dcline'][i]
            p_min = dcline[cdcl.PMIN]
            p_max = dcline[cdcl.PMAX]
            q_min_src = dcline[cdcl.QMINF]
            q_max_src = dcline[cdcl.QMAXF]
            q_min_dst = dcline[cdcl.QMINT]
            q_max_dst = dcline[cdcl.QMAXT]
            loss_fwd = loss_bwd = dcline[cdcl.LOSS1] * 100

            # BIDIRECTIONAL LINES: The MATPOWER data format only supports
            # unidirectional lines and, as a consequence, test cases with
            # HVDC lines typically contain two entries for one line. The
            # following code combines these two entries to a bidirectional
            # HVDC line model.
            if i + 1 < len(mpc['dcline']):
                next_dcline = mpc['dcline'][i + 1]
                if (next_dcline[cdcl.F_BUS] == dcline[cdcl.T_BUS] and
                        next_dcline[cdcl.T_BUS] == dcline[cdcl.F_BUS] and
                        next_dcline[cdcl.BR_STATUS] == dcline[cdcl.BR_STATUS] and
                        next_dcline[cdcl.PMIN] == dcline[cdcl.PMIN] == 0 and
                        next_dcline[cdcl.PMAX] >= 0 and p_max >= 0):
                    p_min = -next_dcline[cdcl.PMAX]
                    q_min_src += next_dcline[cdcl.QMINT]
                    q_max_src += next_dcline[cdcl.QMAXT]
                    q_min_dst += next_dcline[cdcl.QMINF]
                    q_max_dst += next_dcline[cdcl.QMAXF]
                    loss_bwd = next_dcline[cdcl.LOSS1] * 100
                    i += 1  # Skip the second part of this bidirectional line

            # Capability region at the source and destination terminal
            cap_src_id = cap_region_id
            cap_dst_id = cap_region_id + 1
            cap_region_id += 2

            transaction.add(DBCapabilityRegion(id=cap_src_id,
                                               p_min=p_min,
                                               p_max=p_max,
                                               q_min=q_min_src,
                                               q_max=q_max_src,
                                               lt_ofs=None,
                                               lt_slp=None,
                                               rt_ofs=None,
                                               rt_slp=None,
                                               lb_ofs=None,
                                               lb_slp=None,
                                               rb_ofs=None,
                                               rb_slp=None,
                                               annotation=''))

            transaction.add(DBCapabilityRegion(id=cap_dst_id,
                                               p_min=-p_max,  # Flow *into* the
                                               p_max=-p_min,  # converter!
                                               q_min=q_min_dst,
                                               q_max=q_max_dst,
                                               lt_ofs=None,
                                               lt_slp=None,
                                               rt_ofs=None,
                                               rt_slp=None,
                                               lb_ofs=None,
                                               lb_slp=None,
                                               rb_ofs=None,
                                               rb_slp=None,
                                               annotation=''))

            # Add converter
            transaction.add(DBConverter(id=converter_id,
                                        src_id=int(dcline[cdcl.F_BUS]),
                                        dst_id=int(dcline[cdcl.T_BUS]),
                                        cap_src_id=cap_src_id,
                                        cap_dst_id=cap_dst_id,
                                        loss_fwd=loss_fwd,
                                        loss_bwd=loss_bwd,
                                        loss_fix=dcline[cdcl.LOSS0],
                                        annotation=''))

            # Is this DC line inactive?
            if dcline[cdcl.BR_STATUS] == 0:
                inactivity = DBScenarioInactivity(scenario_id=scenario_id,
                                                  entity_type=EntityType.CONVERTER,
                                                  entity_id=converter_id)
                transaction.add(inactivity)
                base_case_inactivity.append(inactivity)
            i += 1

        # Import generator data
        if mpc['gen'].shape[0] != mpc['gencost'].shape[0]:
            raise NotImplementedError("The import of reactive power cost "
                                      "functions is not supported.")

        pwl_function_id = 1
        for i, injector in enumerate(mpc['gen']):
            injector_id = i + 1
            gencost = mpc['gencost'][i]

            # Capability region at the source and destination terminal
            cap_id = cap_region_id
            cap_region_id += 1

            idx_cap_ref = [cgen.PC1, cgen.PC2, cgen.QC1MIN, cgen.QC1MAX,
                           cgen.QC2MIN, cgen.QC2MAX]
            if len(injector) > max(idx_cap_ref) and \
                    any(injector[idx_cap_ref] != 0):
                _log.warning("The import of the sloped refinements of the "
                             "generator capability are not supported. This "
                             "data is ignored, i.e., only PMIN, PMAX, QMIN, "
                             "QMAX is considered.")

            transaction.add(DBCapabilityRegion(id=cap_id,
                                               p_min=injector[cgen.PMIN],
                                               p_max=injector[cgen.PMAX],
                                               q_min=injector[cgen.QMIN],
                                               q_max=injector[cgen.QMAX],
                                               lt_ofs=None,
                                               lt_slp=None,
                                               rt_ofs=None,
                                               rt_slp=None,
                                               lb_ofs=None,
                                               lb_slp=None,
                                               rb_ofs=None,
                                               rb_slp=None,
                                               annotation=''))

            # PWL cost function for active power
            sample_points = _get_gencost_sample_points(gencost,
                                                       injector[cgen.PMIN],
                                                       injector[cgen.PMAX],
                                                       num_sample_points)
            if sample_points:
                cost_id = pwl_function_id
                pwl_function_id += 1
                for x, y in sample_points:
                    transaction.add(DBSamplePoint(id=cost_id, x=x, y=y))
            else:
                cost_id = None

            # INJECTOR TYPE: By default, it is set to conventional generation.
            # If and only if the generator offers exclusively reactive power at
            # zero cost, then it is considered as shunt compensation.
            terminal = int(injector[cgen.GEN_BUS])
            injector_type = InjectorType.CONVENTIONAL
            if cost_id is None and \
                    all(injector[[cgen.PMIN, cgen.PMAX]] == 0) and \
                    any(injector[[cgen.QMIN, cgen.QMAX]] != 0):
                injector_type = InjectorType.COMPENSATION
            # --- CUSTOM EXTENSION: RES injector type detection ----------
            if res_detection and cost_id is None:
                num_gen = mpc['gen'].shape[0]
                if i + 1 < num_gen:
                    next_terminal = int(mpc['gen'][i + 1, cgen.GEN_BUS])
                    if next_terminal == terminal:
                        if (i + 2 == num_gen or
                                int(mpc['gen'][i + 2, cgen.GEN_BUS] != terminal)):
                            next_cost = _get_gencost_sample_points(
                                mpc['gencost'][i + 1],
                                mpc['gen'][i + 1, cgen.PMIN],
                                mpc['gen'][i + 1, cgen.PMAX],
                                num_sample_points)
                            if not next_cost:
                                injector_type = InjectorType.PV
                if i >= 1:
                    prev_terminal = int(mpc['gen'][i - 1][cgen.GEN_BUS])
                    if prev_terminal == terminal:
                        if (i + 1 == num_gen or
                                int(mpc['gen'][i + 1][cgen.GEN_BUS] != terminal)):
                            prev_cost = _get_gencost_sample_points(
                                mpc['gencost'][i - 1],
                                mpc['gen'][i - 1, cgen.PMIN],
                                mpc['gen'][i - 1, cgen.PMAX],
                                num_sample_points)
                            if not prev_cost:
                                injector_type = InjectorType.WIND
            # --- CUSTOM EXTENSION: END ----------------------------------

            # Add converter
            if injector[cgen.MBASE] not in [0., mpc['baseMVA']]:
                # REMARK: The MVA base of the machine does not seem to be
                # utilized at any point in the MATPOWER code and, in the vast
                # majority of test cases, it is set to the test case MVA base.
                _log.debug("The generator MVA base does not match the MVA "
                           "base of the test case.")

            if len(injector) > cgen.RAMP_AGC:
                ramp = injector[cgen.RAMP_AGC]
                # Check if omitted and, if not, convert from MW/min to MW/h
                ramp = ramp * 60 if ramp != 0 else None
            else:
                ramp = None

            transaction.add(DBInjector(id=injector_id,
                                       type=injector_type,
                                       bus_id=terminal,
                                       cap_id=cap_id,
                                       cost_p_id=cost_id,
                                       cost_q_id=None,
                                       cost_start=gencost[cgen.STARTUP],
                                       cost_stop=gencost[cgen.SHUTDOWN],
                                       ramp_up=ramp,
                                       ramp_down=ramp,
                                       min_up=None,
                                       min_down=None,
                                       energy_min=None,
                                       energy_max=None,
                                       annotation=''))

            # Is this generator inactive?
            if injector[cgen.GEN_STATUS] <= 0:
                inactivity = DBScenarioInactivity(scenario_id=scenario_id,
                                                  entity_type=EntityType.INJECTOR,
                                                  entity_id=injector_id)
                transaction.add(inactivity)
                base_case_inactivity.append(inactivity)

        # If there is no scenario data, we're done...
        if 'scenarios' not in mpc:
            return output_file

        # --- CUSTOM EXTENSION: Scenario information -----------------
        for scenario_name in mpc['scenarios']:
            scenario_data = mpc['scenarios'][scenario_name]
            scenario_title = scenario_name.replace('_', ' ').title()

            load_p = scenario_data['load_p']
            load_q = scenario_data['load_q']
            gen_pmin = scenario_data['gen_pmin']
            gen_pmax = scenario_data['gen_pmax']
            gen_qmin = scenario_data['gen_qmin']
            gen_qmax = scenario_data['gen_qmax']

            hours = load_p.shape[1]
            if not all([x.shape[1] == hours for x in [load_p, load_q,
                                                      gen_pmin, gen_pmax,
                                                      gen_qmin, gen_qmax]]):
                raise ValueError("The scenario data is inconsistent.")

            for hour in range(hours):
                scenario_id += 1
                with DBTransaction(database) as transaction:
                    transaction.add(DBScenario(id=scenario_id,
                                               time=hour,
                                               name=scenario_title,
                                               loss_price=0.,
                                               annotation=''))

                    for i, bus_id in enumerate(mpc['bus'][:, cbus.BUS_I]):
                        if load_p[i, hour] == 0 and load_q[i, hour] == 0:
                            continue
                        transaction.add(DBScenarioLoad(scenario_id=scenario_id,
                                                       bus_id=int(bus_id),
                                                       p=load_p[i, hour],
                                                       q=load_q[i, hour]))

                    for i, injector in enumerate(mpc['gen']):
                        injector_id = i + 1
                        if (gen_pmin[i, hour] == injector[cgen.PMIN] and
                                gen_pmax[i, hour] == injector[cgen.PMAX] and
                                gen_qmin[i, hour] == injector[cgen.QMIN] and
                                gen_qmax[i, hour] == injector[cgen.QMAX]):
                            continue
                        transaction.add(DBScenarioInjector(scenario_id=scenario_id,
                                                           injector_id=injector_id,
                                                           p_min=gen_pmin[i, hour],
                                                           p_max=gen_pmax[i, hour],
                                                           q_min=gen_qmin[i, hour],
                                                           q_max=gen_qmax[i, hour],
                                                           cost_scaling=1.))

                    for inactivity in base_case_inactivity:
                        transaction.add(
                            DBScenarioInactivity(scenario_id=scenario_id,
                                                 entity_type=inactivity.entity_type,
                                                 entity_id=inactivity.entity_id))
        # --- CUSTOM EXTENSION: END ----------------------------------
    return output_file
