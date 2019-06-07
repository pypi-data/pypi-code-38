"""
Feature- and structure-preserving network reduction for large-scale grids.

This subpackage of *hynet* implements the reduction strategy for large-scale
grid models as introduced in [1]_, which aims at reducing model complexity
while preserving relevant features and the relation to the structure of the
original model. Please refer to [1]_ for more details.

References
----------
.. [1] J. Sistermanns, M. Hotz, D. Hewes, R. Witzmann, and W. Utschick,
       "Feature- and Structure-Preserving Network Reduction for Large-Scale
       Transmission Grids," 13th IEEE PES PowerTech Conference, Milano,
       Italy, Jun. 2019.
"""

from hynet.reduction.large_scale.features import (add_feature_columns,
                                                  add_bus_features,
                                                  add_converter_features,
                                                  add_branch_features,
                                                  add_congestion_features,
                                                  add_standard_features)

from hynet.reduction.large_scale.combination import reduce_system

from hynet.reduction.large_scale.topology import reduce_by_topology
from hynet.reduction.large_scale.coupling import (reduce_by_coupling,
                                                  get_critical_injector_features)
from hynet.reduction.large_scale.market import reduce_by_market

from hynet.reduction.large_scale.subgrid import (reduce_subgrid,
                                                 create_bus_id_map,
                                                 preserve_aggregation_info,
                                                 restore_aggregation_info)

from hynet.reduction.large_scale.evaluation import (evaluate_reduction,
                                                    show_reduction_evaluation)

from hynet.reduction.large_scale.sweep import (sweep_rel_impedance_thres,
                                               sweep_feature_depth,
                                               sweep_max_price_diff)
