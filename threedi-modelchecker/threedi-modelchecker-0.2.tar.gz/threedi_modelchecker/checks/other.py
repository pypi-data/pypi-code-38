from sqlalchemy import func

from threedi_modelchecker.checks import patterns
from .base import BaseCheck
from ..threedi_model import constants
from ..threedi_model import models


class BankLevelCheck(BaseCheck):
    """Check 'CrossSectionLocation.bank_level' is not null if
    calculation_type is CONNECTED or DOUBLE_CONNECTED.
    """

    def __init__(self):
        super().__init__(column=models.CrossSectionLocation.bank_level)

    def get_invalid(self, session):
        q = session.query(self.table).filter(
            models.CrossSectionLocation.bank_level == None,
            models.CrossSectionLocation.channel.has(
                models.Channel.calculation_type.in_(
                    [
                        constants.CalculationType.CONNECTED,
                        constants.CalculationType.DOUBLE_CONNECTED,
                    ]
                )
            ),
        )
        return q.all()

    def description(self):
        return "CrossSectionLoaction.Banklevel cannot be null when calculation_type " \
               "is CONNECTED or DOUBLE_CONNECTED"


class CrossSectionShapeCheck(BaseCheck):
    """Check if all CrossSectionDefinition.shape are valid"""

    def __init__(self):
        super().__init__(column=models.CrossSectionDefinition.shape)

    def get_invalid(self, session):
        cross_section_definitions = session.query(self.table)
        invalid_cross_section_shapes = []

        for cross_section_definition in cross_section_definitions.all():
            shape = cross_section_definition.shape
            width = cross_section_definition.width
            height = cross_section_definition.height
            if shape == constants.CrossSectionShape.RECTANGLE:
                if not valid_rectangle(width, height):
                    invalid_cross_section_shapes.append(cross_section_definition)
            elif shape == constants.CrossSectionShape.CIRCLE:
                if not valid_circle(width):
                    invalid_cross_section_shapes.append(cross_section_definition)
            elif shape == constants.CrossSectionShape.EGG:
                if not valid_egg(width, height):
                    invalid_cross_section_shapes.append(cross_section_definition)
            if shape == constants.CrossSectionShape.TABULATED_RECTANGLE:
                if not valid_tabulated_shape(width, height):
                    invalid_cross_section_shapes.append(cross_section_definition)
            elif shape == constants.CrossSectionShape.TABULATED_TRAPEZIUM:
                if not valid_tabulated_shape(width, height):
                    invalid_cross_section_shapes.append(cross_section_definition)
        return invalid_cross_section_shapes

    def description(self):
        return "Invalid CrossSectionShape"


def valid_rectangle(width, height):
    width_match = patterns.POSITIVE_FLOAT_REGEX.fullmatch(width)
    if height:  # height is not required
        height_match = patterns.POSITIVE_FLOAT_REGEX.fullmatch(height)
    else:
        height_match = True
    return width_match and height_match


def valid_circle(width):
    return patterns.POSITIVE_FLOAT_REGEX.fullmatch(width)


def valid_egg(width, height):
    width_match = patterns.POSITIVE_FLOAT_LIST_REGEX.fullmatch(width)
    height_match = patterns.POSITIVE_FLOAT_LIST_REGEX.fullmatch(height)
    if not width_match or not height_match:
        return False
    return len(width.split(" ")) == len(height.split(" "))


def valid_tabulated_shape(width, height):
    """Return if the tabulated shape is valid.

    Validating that the strings `width` and `height` contain positive floats
    was previously done using a regex. However, experiments showed that
    trying to split the string and reading in the floats is much faster.

    :param width: string of widths
    :param height: string of heights
    :return: True if the shape if valid
    """
    height_string_list = height.split(" ")
    width_string_list = width.split(" ")
    if len(height_string_list) != len(width_string_list):
        return False
    try:
        first_height = float(height_string_list[0])
        if first_height != 0:
            return False
    except ValueError:
        return False
    for h_string, w_string in zip(height_string_list, width_string_list):
        try:
            h = float(h_string)
            w = float(w_string)
            if h < 0:
                return False
            if w < 0:
                return False
        except ValueError:
            return False
    return True


class TimeseriesCheck(BaseCheck):
    """Check that `column` has the time series pattern: digit,float\n

    The first digit is the timestep in minutes, the float is a value depending
    on the type of timeseries.

    Example of a timeserie: 0,-0.5\n59,-0.5\n60,-0.5\n61,-0.5\n9999,-0.5

    All timeseries in the table should contain the same timesteps.
    """

    def get_invalid(self, session):
        invalid_timeseries = []
        required_timesteps = {}
        rows = session.query(self.table).all()

        for row in rows:
            timeserie = row.timeseries
            if not patterns.TIMESERIES_REGEX.fullmatch(timeserie):
                invalid_timeseries.append(row)
                continue

            timesteps = {
                time for time, *_ in patterns.TIMESERIE_ENTRY_REGEX.findall(timeserie)
            }
            if not required_timesteps:
                # Assume the first timeserie defines the required timesteps.
                # All others should have the same timesteps.
                required_timesteps = timesteps
                continue
            if timesteps != required_timesteps:
                invalid_timeseries.append(row)

        return invalid_timeseries

    def description(self):
        return "Invalid timeseries"


class Use0DFlowCheck(BaseCheck):
    """Check that when use_0d_flow in global settings is configured to 1 or to
    2, there is at least one impervious surface or surfaces respectively.
    """

    def __init__(self):
        super().__init__(column=models.GlobalSetting.use_0d_inflow)

    def to_check(self, session):
        """Return a Query object on which this check is applied"""
        return session.query(models.GlobalSetting).filter(
            models.GlobalSetting.use_0d_inflow != 0
        )

    def get_invalid(self, session):
        surface_count = session.query(func.count(models.Surface.id)).scalar()
        impervious_surface_count = session.query(
            func.count(models.ImperviousSurface.id)
        ).scalar()

        invalid_rows = []
        for row in self.to_check(session):
            if row.use_0d_inflow == 1 and impervious_surface_count == 0:
                invalid_rows.append(row)
            elif row.use_0d_inflow == 2 and surface_count == 0:
                invalid_rows.append(row)
            else:
                continue
        return invalid_rows

    def description(self):
        return (
            "When %s is used, there should exists at least one "
            "(impervious) surface." % self.column
        )


class ConnectionNodes(BaseCheck):
    """Check that all connection nodes are connected to at least one of the
    following objects:
    - Culvert
    - Channel
    - Pipe
    - Orifice
    - Pumpstation
    - Weir
    """

    def __init__(self):
        super().__init__(column=models.ConnectionNode.id)

    def get_invalid(self, session):
        raise NotImplementedError
