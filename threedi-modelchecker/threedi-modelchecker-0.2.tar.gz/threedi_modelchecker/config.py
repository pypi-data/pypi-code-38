from sqlalchemy import Integer
from sqlalchemy import and_
from sqlalchemy import cast
from sqlalchemy import or_

from .checks.base import ConditionalCheck
from .checks.base import GeneralCheck
from .checks.base import NotNullCheck
from .checks.factories import generate_enum_checks
from .checks.factories import generate_foreign_key_checks
from .checks.factories import generate_geometry_checks
from .checks.factories import generate_geometry_type_checks
from .checks.factories import generate_type_checks
from .checks.factories import generate_unique_checks
from .checks.other import BankLevelCheck, CrossSectionShapeCheck
from .checks.other import TimeseriesCheck
from .checks.other import Use0DFlowCheck
from .threedi_model import models
from .threedi_model.models import constants

FOREIGN_KEY_CHECKS = []
UNIQUE_CHECKS = []
INVALID_TYPE_CHECKS = []
INVALID_GEOMETRY_CHECKS = []
INVALID_GEOMETRY_TYPE_CHECKS = []
INVALID_ENUM_CHECKS = []

TIMESERIES_CHECKS = [
    TimeseriesCheck(models.BoundaryCondition1D.timeseries),
    TimeseriesCheck(models.BoundaryConditions2D.timeseries),
    TimeseriesCheck(models.Lateral1d.timeseries),
    TimeseriesCheck(models.Lateral2D.timeseries),
]

RANGE_CHECKS = [
    GeneralCheck(
        column=models.CrossSectionLocation.friction_value,
        criterion_valid=models.CrossSectionLocation.friction_value > 0,
    ),
    GeneralCheck(
        column=models.Culvert.friction_value,
        criterion_valid=models.Culvert.friction_value >= 0,
    ),
    GeneralCheck(
        column=models.GroundWater.phreatic_storage_capacity,
        criterion_valid=and_(
            models.GroundWater.phreatic_storage_capacity >= 0,
            models.GroundWater.phreatic_storage_capacity <= 1
        ),
    ),
    GeneralCheck(
        column=models.ImperviousSurface.area,
        criterion_valid=models.ImperviousSurface.area >= 0,
    ),
    GeneralCheck(
        column=models.ImperviousSurface.dry_weather_flow,
        criterion_valid=models.ImperviousSurface.dry_weather_flow >= 0,
    ),
    GeneralCheck(
        column=models.ImperviousSurfaceMap.percentage,
        criterion_valid=models.ImperviousSurfaceMap.percentage >= 0,
    ),
    GeneralCheck(
        column=models.Interflow.porosity,
        criterion_valid=and_(
            models.Interflow.porosity >= 0,
            models.Interflow.porosity <= 1,
        ),
    ),
    GeneralCheck(
        column=models.Interflow.impervious_layer_elevation,
        criterion_valid=models.Interflow.impervious_layer_elevation >= 0,
    ),
    GeneralCheck(
        column=models.Orifice.discharge_coefficient_negative,
        criterion_valid=models.Orifice.discharge_coefficient_negative >= 0,
    ),
    GeneralCheck(
        column=models.Orifice.discharge_coefficient_positive,
        criterion_valid=models.Orifice.discharge_coefficient_positive >= 0,
    ),
    GeneralCheck(
        column=models.Orifice.friction_value,
        criterion_valid=models.Orifice.friction_value >= 0,
    ),
    GeneralCheck(
        column=models.Pipe.dist_calc_points,
        criterion_valid=models.Pipe.dist_calc_points > 0,
    ),
    GeneralCheck(
        column=models.Pipe.friction_value,
        criterion_valid=models.Pipe.friction_value >= 0,
    ),
    GeneralCheck(
        column=models.Pumpstation.upper_stop_level,
        criterion_valid=and_(
            models.Pumpstation.upper_stop_level > models.Pumpstation.lower_stop_level,
            models.Pumpstation.upper_stop_level > models.Pumpstation.start_level,
        )
    ),
    GeneralCheck(
        column=models.Pumpstation.lower_stop_level,
        criterion_valid=and_(
            models.Pumpstation.lower_stop_level < models.Pumpstation.start_level,
            models.Pumpstation.lower_stop_level < models.Pumpstation.upper_stop_level,
        )
    ),
    GeneralCheck(
        column=models.Pumpstation.start_level,
        criterion_valid=and_(
            models.Pumpstation.start_level > models.Pumpstation.lower_stop_level,
            models.Pumpstation.start_level < models.Pumpstation.upper_stop_level,
        )
    ),
    GeneralCheck(
        column=models.Pumpstation.capacity,
        criterion_valid=models.Pumpstation.capacity >= 0,
    ),
    GeneralCheck(
        column=models.SimpleInfiltration.infiltration_rate,
        criterion_valid=models.SimpleInfiltration.infiltration_rate >= 0,
    ),
    GeneralCheck(
        column=models.Surface.nr_of_inhabitants,
        criterion_valid=models.Surface.nr_of_inhabitants >= 0,
    ),
    GeneralCheck(
        column=models.Surface.dry_weather_flow,
        criterion_valid=models.Surface.dry_weather_flow >= 0,
    ),
    GeneralCheck(
        column=models.Surface.area,
        criterion_valid=models.Surface.area >= 0,
    ),
    GeneralCheck(
        column=models.SurfaceMap.percentage,
        criterion_valid=and_(
            models.SurfaceMap.percentage >= 0,
            models.SurfaceMap.percentage <= 100,
        ),
    ),
    GeneralCheck(
        column=models.SurfaceParameter.outflow_delay,
        criterion_valid=models.SurfaceParameter.outflow_delay >= 0,
    ),
    GeneralCheck(
        column=models.SurfaceParameter.max_infiltration_capacity,
        criterion_valid=models.SurfaceParameter.max_infiltration_capacity >= 0,
    ),
    GeneralCheck(
        column=models.SurfaceParameter.min_infiltration_capacity,
        criterion_valid=models.SurfaceParameter.min_infiltration_capacity >= 0,
    ),
    GeneralCheck(
        column=models.SurfaceParameter.infiltration_decay_constant,
        criterion_valid=models.SurfaceParameter.infiltration_decay_constant >= 0,
    ),
    GeneralCheck(
        column=models.SurfaceParameter.infiltration_recovery_constant,
        criterion_valid=models.SurfaceParameter.infiltration_recovery_constant >= 0,
    ),
    GeneralCheck(
        column=models.Weir.discharge_coefficient_negative,
        criterion_valid=models.Weir.discharge_coefficient_negative >= 0,
    ),
    GeneralCheck(
        column=models.Weir.discharge_coefficient_positive,
        criterion_valid=models.Weir.discharge_coefficient_positive >= 0,
    ),
    GeneralCheck(
        column=models.Weir.friction_value,
        criterion_valid=models.Weir.friction_value >= 0,
    ),
]

OTHER_CHECKS = [
    BankLevelCheck(),
    CrossSectionShapeCheck(),
    # 1d boundary conditions cannot be connected to a pumpstation
    GeneralCheck(
        column=models.BoundaryCondition1D.connection_node_id,
        criterion_invalid=or_(
            models.BoundaryCondition1D.connection_node_id == models.Pumpstation.connection_node_start_id,  # noqa: E501
            models.BoundaryCondition1D.connection_node_id == models.Pumpstation.connection_node_end_id,  # noqa: E501
        )
    ),
    GeneralCheck(
        column=models.GlobalSetting.nr_timesteps,
        criterion_valid=cast(models.GlobalSetting.output_time_step, Integer)
        % cast(models.GlobalSetting.sim_time_step, Integer) == 0
    ),
    Use0DFlowCheck()
]

CONDITIONAL_CHECKS = [
    ConditionalCheck(
        criterion=(models.ConnectionNode.id == models.Manhole.connection_node_id),
        check=GeneralCheck(
            column=models.ConnectionNode.storage_area,
            criterion_valid=models.ConnectionNode.storage_area > 0
        )
    ),
    ConditionalCheck(
        criterion=(models.CrossSectionLocation.bank_level != None),
        check=GeneralCheck(
            column=models.CrossSectionLocation.reference_level,
            criterion_valid=(models.CrossSectionLocation.reference_level
                             < models.CrossSectionLocation.bank_level)
        )
    ),
    ConditionalCheck(
        criterion=(models.GlobalSetting.timestep_plus == True),
        check=NotNullCheck(
            column=models.GlobalSetting.maximum_sim_time_step,
        )
    ),
    ConditionalCheck(
        criterion=or_(
            models.GlobalSetting.initial_groundwater_level_file != None,
            models.GlobalSetting.initial_groundwater_level != None
        ),
        check=NotNullCheck(
            column=models.GlobalSetting.initial_groundwater_level_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GlobalSetting.initial_waterlevel_file != None,
        check=NotNullCheck(
            column=models.GlobalSetting.water_level_ini_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GlobalSetting.initial_waterlevel_file != None,
        check=NotNullCheck(
            column=models.GlobalSetting.water_level_ini_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GlobalSetting.dem_obstacle_detection == True,
        check=GeneralCheck(
            column=models.GlobalSetting.dem_obstacle_height,
            criterion_valid=models.GlobalSetting.dem_obstacle_height > 0
        )
    ),
    ConditionalCheck(
        criterion=models.GroundWater.equilibrium_infiltration_rate_file != None,
        check=NotNullCheck(
            column=models.GroundWater.equilibrium_infiltration_rate_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GroundWater.infiltration_decay_period_file != None,
        check=NotNullCheck(
            column=models.GroundWater.infiltration_decay_period_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GroundWater.groundwater_hydro_connectivity_file != None,
        check=NotNullCheck(
            column=models.GroundWater.groundwater_hydro_connectivity_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GroundWater.groundwater_impervious_layer_level_file != None,
        check=NotNullCheck(
            column=models.GroundWater.groundwater_impervious_layer_level_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GroundWater.initial_infiltration_rate_file != None,
        check=NotNullCheck(
            column=models.GroundWater.initial_infiltration_rate_type,
        )
    ),
    ConditionalCheck(
        criterion=models.GroundWater.phreatic_storage_capacity_file != None,
        check=NotNullCheck(
            column=models.GroundWater.phreatic_storage_capacity_type,
        )
    ),
    ConditionalCheck(
        criterion=models.Interflow.interflow_type != constants.InterflowType.NO_INTERLFOW,  # noqa: E501
        check=NotNullCheck(
            column=models.Interflow.porosity,
        )
    ),
    ConditionalCheck(
        criterion=models.Interflow.interflow_type in [
            constants.InterflowType.LOCAL_DEEPEST_POINT_SCALED_POROSITY,
            constants.InterflowType.GLOBAL_DEEPEST_POINT_SCALED_POROSITY,
        ],
        check=NotNullCheck(
            column=models.Interflow.porosity_layer_thickness,
        )
    ),
    ConditionalCheck(
        criterion=models.Interflow.interflow_type != constants.InterflowType.NO_INTERLFOW,  # noqa: E501
        check=NotNullCheck(
            column=models.Interflow.impervious_layer_elevation,
        )
    ),
    ConditionalCheck(
        criterion=models.Interflow.interflow_type != constants.InterflowType.NO_INTERLFOW,  # noqa: E501
        check=GeneralCheck(
            column=models.Interflow.hydraulic_conductivity,
            criterion_valid=or_(
                models.Interflow.hydraulic_conductivity != None,
                models.Interflow.hydraulic_conductivity_file != None,
            )
        )
    ),
    ConditionalCheck(
        criterion=models.GlobalSetting.dem_file == None,
        check=GeneralCheck(
            column=models.Channel.calculation_type,
            criterion_valid=models.Channel.calculation_type.notin_([
                constants.CalculationType.EMBEDDED,
                constants.CalculationType.CONNECTED,
                constants.CalculationType.DOUBLE_CONNECTED
            ])
        )
    ),
]


ALL_CHECKS = []


class Config:
    """Collection of checks

    Some checks are generated by a factory. These are usually very generic
    checks which apply to many columns, such as foreign keys."""

    def __init__(self, models):
        self.models = models
        self.checks = []
        self.generate_checks()

    def generate_checks(self):
        FOREIGN_KEY_CHECKS = []
        UNIQUE_CHECKS = []
        INVALID_TYPE_CHECKS = []
        INVALID_GEOMETRY_CHECKS = []
        INVALID_GEOMETRY_TYPE_CHECKS = []
        INVALID_ENUM_CHECKS = []
        # Call the check factories:
        for model in self.models:
            FOREIGN_KEY_CHECKS += generate_foreign_key_checks(model.__table__)
            UNIQUE_CHECKS += generate_unique_checks(model.__table__)
            INVALID_TYPE_CHECKS += generate_type_checks(model.__table__)
            INVALID_GEOMETRY_CHECKS += generate_geometry_checks(model.__table__)
            INVALID_GEOMETRY_TYPE_CHECKS += generate_geometry_type_checks(model.__table__)  # noqa: E501
            INVALID_ENUM_CHECKS += generate_enum_checks(model.__table__)

        self.checks += FOREIGN_KEY_CHECKS
        self.checks += UNIQUE_CHECKS
        self.checks += INVALID_TYPE_CHECKS
        self.checks += INVALID_GEOMETRY_CHECKS
        self.checks += INVALID_GEOMETRY_TYPE_CHECKS
        self.checks += INVALID_ENUM_CHECKS
        self.checks += OTHER_CHECKS
        self.checks += TIMESERIES_CHECKS
        self.checks += RANGE_CHECKS
        self.checks += CONDITIONAL_CHECKS
        return None
