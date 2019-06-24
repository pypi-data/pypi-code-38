#pylint: disable=C0330,bad-whitespace
"""
Artificial system for OPF regression tests.

This testing data is embedded as code to obtain simple and robust access to it.
"""

import numpy as np

from hynet.types_ import (hynet_id_,
                          hynet_float_,
                          hynet_complex_,
                          BusType,
                          BranchType,
                          InjectorType)
from hynet.scenario.representation import Scenario
from hynet.scenario.capability import HalfSpace, CapRegion, ConverterCapRegion
from hynet.scenario.cost import PWLFunction
from hynet.test.regression import OPFVerificationData


# =============================================================================
# ============================= TEST SYSTEM SETUP =============================
# =============================================================================

TEST_SYSTEM = Scenario()
TEST_SYSTEM.id = 0
TEST_SYSTEM.name = 'default'
TEST_SYSTEM.time = 25.26  # 1d 01:15:36
TEST_SYSTEM.database_uri = 'test_system.db'
TEST_SYSTEM.grid_name = 'Artificial System for Testing Purposes'
TEST_SYSTEM.base_mva = 100
TEST_SYSTEM.loss_price = 0.25
TEST_SYSTEM.description = ("Manually synthesized system with several special "
                           "cases for testing purposes.")
TEST_SYSTEM.annotation = ''


# === BUS DATA ===

TEST_SYSTEM.bus['id'] = np.arange(1, 12, dtype=hynet_id_)
TEST_SYSTEM.bus['type'] = np.array([BusType.AC] * 5 +
                                   [BusType.DC] * 3 +
                                   [BusType.AC] * 2 +
                                   [BusType.DC], dtype=BusType)
TEST_SYSTEM.bus['ref'] = np.array([False] * 2 +
                                  [True] +
                                  [False] * 2 +
                                  [True] +
                                  [False] * 2 +
                                  [True] +
                                  [False] * 2, dtype=bool)
TEST_SYSTEM.bus['base_kv'] = np.array([380] * 5 +
                                      [585] * 3 +
                                      [220] * 2 +
                                      [10], dtype=hynet_float_)
TEST_SYSTEM.bus['y_tld'] = np.array([0.05j] +
                                    [0.03+0.05j] +
                                    [0j] * 9, dtype=hynet_complex_)
TEST_SYSTEM.bus['load'] = np.array([0j,
                                    300 + 100j,
                                    300 + 100j,
                                    400 + 129j,
                                    0j,
                                    0j,
                                    0j,
                                    0j,
                                    38 + 13j,
                                    0j,
                                    3.3], dtype=hynet_complex_)
TEST_SYSTEM.bus['v_min'] = np.array([0.9] * 9 +
                                    [1.025] +
                                    [0.9], dtype=hynet_float_)
TEST_SYSTEM.bus['v_max'] = np.array([1.1] * 10 +
                                    [1.2], dtype=hynet_float_)
TEST_SYSTEM.bus['zone'] = np.array([None] * 11, dtype=object)
TEST_SYSTEM.bus['annotation'] = np.array([''] * 11, dtype=str)
TEST_SYSTEM.bus.set_index('id', inplace=True)


# === BRANCH DATA ===

TEST_SYSTEM.branch['id'] = np.array([1, 2, 3, 4, 7, 6, 5, -1, -2, -3],
                                    dtype=hynet_id_)
TEST_SYSTEM.branch['type'] = np.array([BranchType.LINE] +
                                      [BranchType.TRANSFORMER] * 2 +
                                      [BranchType.LINE] * 7, dtype=BranchType)
TEST_SYSTEM.branch['src'] = np.array([1, 1, 5, 2, 6, 8, 10, 9, 1, 6],
                                     dtype=hynet_id_)
TEST_SYSTEM.branch['dst'] = np.array([2, 4, 1, 3, 7, 7, 9, 10, 4, 7],
                                     dtype=hynet_id_)
TEST_SYSTEM.branch['z_bar'] = np.array([0.00281 + 0.02810j,
                                        0.00304 + 0.03040j,
                                        0.00064 + 0.00640j,
                                        0.00108 + 0.01080j,
                                        0.00297 + 0.00000j,
                                        0.00297 + 0.00000j,
                                        0.00281 + 0.02810j,
                                        0.00281 + 0.02810j,
                                        0.00304 + 0.03040j,
                                        0.00297 + 0.00000j],
                                       dtype=hynet_complex_)
TEST_SYSTEM.branch['y_src'] = np.array([0.00356j,
                                        0.00329j,
                                        0.01563j,
                                        0.00926j,
                                        0.00000j,
                                        0.00000j,
                                        0.00000j,
                                        0.00000j,
                                        0.00329j,
                                        0.00000j], dtype=hynet_complex_)
TEST_SYSTEM.branch['y_dst'] = TEST_SYSTEM.branch['y_src'].copy()
TEST_SYSTEM.branch['rho_src'] = np.array([1 + 0j] +
                                         [0.95 + 0.01j] +
                                         [1 + 0j] * 4 +
                                         [1.05 + 0.02j] +
                                         [1 + 0j] +
                                         [0.95 + 0.01j] +
                                         [1 + 0j], dtype=hynet_complex_)
TEST_SYSTEM.branch['rho_dst'] = np.array([1 + 0j] * 7 +
                                         [1.05+0.02j] +
                                         [1 + 0j] * 2, dtype=hynet_complex_)
TEST_SYSTEM.branch['length'] = np.array([np.nan] * 10, dtype=hynet_float_)
TEST_SYSTEM.branch['rating'] = np.array([400,
                                         250,
                                         500,
                                         None,
                                         250,
                                         125,
                                         50,
                                         50,
                                         250,
                                         250], dtype=hynet_float_)
TEST_SYSTEM.branch['angle_min'] = np.array([-4,
                                            -50,
                                            None,
                                            -50] +
                                           [np.nan] * 6, dtype=hynet_float_)
TEST_SYSTEM.branch['angle_max'] = np.array([None,
                                            -0.82,
                                            5,
                                            50,
                                            None,
                                            None,
                                            1] +
                                           [np.nan] * 3, dtype=hynet_float_)
TEST_SYSTEM.branch['drop_min'] = np.array([-10,
                                           -7,
                                           None,
                                           -10,
                                           None,
                                           -0.4] +
                                          [np.nan] * 4, dtype=hynet_float_)
TEST_SYSTEM.branch['drop_max'] = np.array([10,
                                           None,
                                           10,
                                           10,
                                           0,
                                           None,
                                           4.815] +
                                          [np.nan] * 3, dtype=hynet_float_)
TEST_SYSTEM.branch['annotation'] = np.array([''] * 10, dtype=str)
TEST_SYSTEM.branch.set_index('id', inplace=True)


# === CONVERTER DATA ===

TEST_SYSTEM.converter['id'] = np.arange(1, 6, dtype=hynet_id_)
TEST_SYSTEM.converter['src'] = np.array([3, 7, 5, 1, 8], dtype=hynet_id_)
TEST_SYSTEM.converter['dst'] = np.array([6, 4, 8, 2, 7], dtype=hynet_id_)
TEST_SYSTEM.converter['cap_src'] = \
    np.array([ConverterCapRegion([-50, 50], [-30, 30],
                                 rt=HalfSpace(0.1, -0.05)),
              ConverterCapRegion([-500, 500]),
              ConverterCapRegion([-240, 240], [-3, 1]),
              ConverterCapRegion([-10, 10]),
              ConverterCapRegion([-5, 5])], dtype=ConverterCapRegion)
TEST_SYSTEM.converter['cap_dst'] = \
    np.array([ConverterCapRegion([-500, 500]),
              ConverterCapRegion([-500, 500], [-2, 2]),
              ConverterCapRegion([-139, 240]),
              ConverterCapRegion([-10, 10]),
              ConverterCapRegion([-5, 5])], dtype=ConverterCapRegion)
TEST_SYSTEM.converter['loss_fwd'] = np.array([1.0] * 5, dtype=hynet_float_)
TEST_SYSTEM.converter['loss_bwd'] = np.array([2.0] * 5, dtype=hynet_float_)
TEST_SYSTEM.converter['loss_fix'] = np.array([0.75] +
                                             [0.0] * 4, dtype=hynet_float_)
TEST_SYSTEM.converter['annotation'] = np.array([''] * 5, dtype=str)
TEST_SYSTEM.converter.set_index('id', inplace=True)


# === INJECTOR DATA ===

TEST_SYSTEM.injector['id'] = np.arange(1, 7, dtype=hynet_id_)
TEST_SYSTEM.injector['bus'] = np.array([1, 3, 5, 7, 10, 11], dtype=hynet_id_)
TEST_SYSTEM.injector['type'] = np.array([InjectorType.CONVENTIONAL,
                                         InjectorType.RENEWABLE,
                                         InjectorType.PROSUMER,
                                         InjectorType.LOAD,
                                         InjectorType.WIND,
                                         InjectorType.PV], dtype=InjectorType)
TEST_SYSTEM.injector['cap'] = \
    np.array([CapRegion([0, 210], [-155, 155],
                        lt=HalfSpace(0.5, 0.3)),
              CapRegion([0, 520], [-390, 390]),
              CapRegion([0, 600], [-450, 450],
                        rt=HalfSpace(0.5, -1),
                        rb=HalfSpace(0.5, 1)),
              CapRegion([0, 50]),
              CapRegion([0, 100], [-25, 25]),
              CapRegion([0, 10])], dtype=CapRegion)
TEST_SYSTEM.injector['cost_p'] = \
    np.array([PWLFunction(((0, 1), (0, 14))),
              PWLFunction(((0, 1), (0, 30))),
              PWLFunction(((0, 1), (0, 10))),
              PWLFunction(((0, 1), (0, 15))),
              PWLFunction(((0, 1), (0, 58))),
              None], dtype=PWLFunction)
TEST_SYSTEM.injector['cost_q'] = \
    np.array([PWLFunction(((-1, 0, 1), (1, 0, 1))),
              PWLFunction(((-1, 0, 1), (1, 0, 1))),
              PWLFunction(((-1, 0, 1), (1, 0, 1))),
              None,
              PWLFunction(((-1, 0, 1), (1, 0, 1))),
              None], dtype=PWLFunction)
TEST_SYSTEM.injector['cost_start'] = np.array([0.0] * 6, dtype=hynet_float_)
TEST_SYSTEM.injector['cost_stop'] = np.array([0.0] * 6, dtype=hynet_float_)
TEST_SYSTEM.injector['annotation'] = np.array([''] * 6, dtype=str)
TEST_SYSTEM.injector.set_index('id', inplace=True)


# =============================================================================
# ============================ REFERENCE SOLUTION =============================
# =============================================================================

# The reference solution below was created using the IPOPT solver with
# tol=1e-7 using the following procedure:
#
# >>> import hynet as ht
# >>> from hynet.test.system import TEST_SYSTEM
# >>> from hynet.test.regression import OPFVerificationData
# >>> result = ht.calc_opf(TEST_SYSTEM, solver=ht.solver.ipopt.QCQPSolver())
# >>> print(OPFVerificationData.create(result))

REFERENCE_SOLUTION = OPFVerificationData(
    OPTIMAL_VALUE=19655.22273549465,
    VOLTAGES=\
        np.array([1.0919586 +0.07750003j,
                  1.08905516+0.00113417j,
                  1.1       +0.j        ,
                  1.01644898+0.0575343j ,
                  1.09504455+0.10429503j,
                  1.09666635+0.j        ,
                  1.09628691+0.j        ,
                  1.0999994 +0.j        ,
                  1.09998981+0.j        ,
                  1.04935731-0.01552334j,
                  1.02769582+0.j        ]),
    BRANCH_FLOW_SRC=\
        np.array([296.22710879  +2.29512619j,
                   93.18572865 +66.49986007j,
                  458.49715249 +48.72515685j,
                    0.51120455-111.50356669j,
                   14.01099107  +0.j        ,
                  137.4995977   +0.j        ,
                   19.0093649   +6.59364905j,
                  -19.          -6.5j       ,
                   93.18572865 +66.49986007j,
                   14.01099107  +0.j        ]),
    CONVERTER_FLOW_SRC=\
        np.array([ 28.30503321-4.0847257j ,
                  216.53322113+0.j        ,
                  140.40404289-0.99997736j,
                    9.99999974+0.j        ,
                    1.50040251+0.j        ]),
    DISPATCH=\
        np.array([ 35.22687002 +88.06805944j,
                  328.65482601+206.3100792j ,
                  598.90119538 +47.72517948j,
                   49.99999946  +0.j        ,
                   38.01872981 +13.1872981j ,
                    3.3         +0.j        ]),
    DV_BALANCE_P=\
        np.array([ 1.12417151e+01,
                   3.02360457e+01,
                   3.00000001e+01,
                   3.06866128e+01,
                   1.00000217e+01,
                   3.03560606e+01,
                   3.03772467e+01,
                   3.00709779e+01,
                   5.80602080e+01,
                   5.79999998e+01,
                  -3.63471732e-06]),
    DV_CAP_P_MAX=\
        np.array([1.35240259e-07,
                  1.23527354e-07,
                  2.15108598e-05,
                  1.53772471e+01,
                  3.81346868e-07,
                  3.52781494e-06]),
    DV_V_MAX=\
        np.array([2.03408114e-03,
                  9.86592092e-04,
                  1.09514608e+04,
                  1.36215692e-04,
                  7.16133310e+04,
                  3.22771939e-03,
                  2.89837525e-03,
                  1.76416102e+01,
                  1.05373417e+00,
                  2.17661720e-04,
                  6.15778506e-05])
)
