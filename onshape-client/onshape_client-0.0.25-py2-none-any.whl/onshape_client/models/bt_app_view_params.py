# coding: utf-8

"""
    Onshape REST API

    The Onshape REST API consumed by all clients.  # noqa: E501

    OpenAPI spec version: 1.97
    Contact: api-support@onshape.zendesk.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class BTAppViewParams(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'parameters': 'list[float]',
        'display_state_id': 'str',
        'transaction_id': 'str',
        'parent_change_id': 'str',
        'bom_reference_id': 'str',
        'include_hidden_instances': 'bool',
        'view_scale': 'float',
        'show_tangent_lines': 'bool',
        'compute_intersection': 'bool',
        'quality_option': 'int',
        'is_broken_out_section': 'bool',
        'is_crop_view': 'bool',
        'hidden_lines': 'str',
        'modification_id': 'str',
        'perspective': 'bool',
        'projection_angle': 'str',
        'show_threads': 'bool',
        'quality_option_type': 'str',
        'is_partial_section': 'bool',
        'broken_out_point_numbers': 'list[int]',
        'broken_out_end_conditions': 'dict(str, BTBrokenOutEndCondition)',
        'broken_out_b_boxes': 'list[float]',
        'broken_out_b_boxes_map': 'dict(str, BTBoundingBox)',
        'include_surfaces': 'bool',
        'is_surface': 'bool',
        'depth_section_end_condition': 'BTBrokenOutEndCondition',
        'model_reference_id': 'str',
        'view_matrix': 'list[float]',
        'view_direction': 'list[float]',
        'cut_point': 'list[float]',
        'offset_section_points': 'list[float]',
        'broken_out_section': 'bool',
        'crop_view': 'bool',
        'occurrence_or_part_id_to_geometry_properties': 'dict(str, dict(str, str))'
    }

    attribute_map = {
        'parameters': 'parameters',
        'display_state_id': 'displayStateId',
        'transaction_id': 'transactionId',
        'parent_change_id': 'parentChangeId',
        'bom_reference_id': 'bomReferenceId',
        'include_hidden_instances': 'includeHiddenInstances',
        'view_scale': 'viewScale',
        'show_tangent_lines': 'showTangentLines',
        'compute_intersection': 'computeIntersection',
        'quality_option': 'qualityOption',
        'is_broken_out_section': 'isBrokenOutSection',
        'is_crop_view': 'isCropView',
        'hidden_lines': 'hiddenLines',
        'modification_id': 'modificationId',
        'perspective': 'perspective',
        'projection_angle': 'projectionAngle',
        'show_threads': 'showThreads',
        'quality_option_type': 'qualityOptionType',
        'is_partial_section': 'isPartialSection',
        'broken_out_point_numbers': 'brokenOutPointNumbers',
        'broken_out_end_conditions': 'brokenOutEndConditions',
        'broken_out_b_boxes': 'brokenOutBBoxes',
        'broken_out_b_boxes_map': 'brokenOutBBoxesMap',
        'include_surfaces': 'includeSurfaces',
        'is_surface': 'isSurface',
        'depth_section_end_condition': 'depthSectionEndCondition',
        'model_reference_id': 'modelReferenceId',
        'view_matrix': 'viewMatrix',
        'view_direction': 'viewDirection',
        'cut_point': 'cutPoint',
        'offset_section_points': 'offsetSectionPoints',
        'broken_out_section': 'brokenOutSection',
        'crop_view': 'cropView',
        'occurrence_or_part_id_to_geometry_properties': 'occurrenceOrPartIdToGeometryProperties'
    }

    def __init__(self, parameters=None, display_state_id=None, transaction_id=None, parent_change_id=None, bom_reference_id=None, include_hidden_instances=None, view_scale=None, show_tangent_lines=None, compute_intersection=None, quality_option=None, is_broken_out_section=None, is_crop_view=None, hidden_lines=None, modification_id=None, perspective=None, projection_angle=None, show_threads=None, quality_option_type=None, is_partial_section=None, broken_out_point_numbers=None, broken_out_end_conditions=None, broken_out_b_boxes=None, broken_out_b_boxes_map=None, include_surfaces=None, is_surface=None, depth_section_end_condition=None, model_reference_id=None, view_matrix=None, view_direction=None, cut_point=None, offset_section_points=None, broken_out_section=None, crop_view=None, occurrence_or_part_id_to_geometry_properties=None):  # noqa: E501
        """BTAppViewParams - a model defined in OpenAPI"""  # noqa: E501

        self._parameters = None
        self._display_state_id = None
        self._transaction_id = None
        self._parent_change_id = None
        self._bom_reference_id = None
        self._include_hidden_instances = None
        self._view_scale = None
        self._show_tangent_lines = None
        self._compute_intersection = None
        self._quality_option = None
        self._is_broken_out_section = None
        self._is_crop_view = None
        self._hidden_lines = None
        self._modification_id = None
        self._perspective = None
        self._projection_angle = None
        self._show_threads = None
        self._quality_option_type = None
        self._is_partial_section = None
        self._broken_out_point_numbers = None
        self._broken_out_end_conditions = None
        self._broken_out_b_boxes = None
        self._broken_out_b_boxes_map = None
        self._include_surfaces = None
        self._is_surface = None
        self._depth_section_end_condition = None
        self._model_reference_id = None
        self._view_matrix = None
        self._view_direction = None
        self._cut_point = None
        self._offset_section_points = None
        self._broken_out_section = None
        self._crop_view = None
        self._occurrence_or_part_id_to_geometry_properties = None
        self.discriminator = None

        if parameters is not None:
            self.parameters = parameters
        if display_state_id is not None:
            self.display_state_id = display_state_id
        if transaction_id is not None:
            self.transaction_id = transaction_id
        if parent_change_id is not None:
            self.parent_change_id = parent_change_id
        if bom_reference_id is not None:
            self.bom_reference_id = bom_reference_id
        if include_hidden_instances is not None:
            self.include_hidden_instances = include_hidden_instances
        if view_scale is not None:
            self.view_scale = view_scale
        if show_tangent_lines is not None:
            self.show_tangent_lines = show_tangent_lines
        if compute_intersection is not None:
            self.compute_intersection = compute_intersection
        if quality_option is not None:
            self.quality_option = quality_option
        if is_broken_out_section is not None:
            self.is_broken_out_section = is_broken_out_section
        if is_crop_view is not None:
            self.is_crop_view = is_crop_view
        if hidden_lines is not None:
            self.hidden_lines = hidden_lines
        if modification_id is not None:
            self.modification_id = modification_id
        if perspective is not None:
            self.perspective = perspective
        if projection_angle is not None:
            self.projection_angle = projection_angle
        if show_threads is not None:
            self.show_threads = show_threads
        if quality_option_type is not None:
            self.quality_option_type = quality_option_type
        if is_partial_section is not None:
            self.is_partial_section = is_partial_section
        if broken_out_point_numbers is not None:
            self.broken_out_point_numbers = broken_out_point_numbers
        if broken_out_end_conditions is not None:
            self.broken_out_end_conditions = broken_out_end_conditions
        if broken_out_b_boxes is not None:
            self.broken_out_b_boxes = broken_out_b_boxes
        if broken_out_b_boxes_map is not None:
            self.broken_out_b_boxes_map = broken_out_b_boxes_map
        if include_surfaces is not None:
            self.include_surfaces = include_surfaces
        if is_surface is not None:
            self.is_surface = is_surface
        if depth_section_end_condition is not None:
            self.depth_section_end_condition = depth_section_end_condition
        if model_reference_id is not None:
            self.model_reference_id = model_reference_id
        if view_matrix is not None:
            self.view_matrix = view_matrix
        if view_direction is not None:
            self.view_direction = view_direction
        if cut_point is not None:
            self.cut_point = cut_point
        if offset_section_points is not None:
            self.offset_section_points = offset_section_points
        if broken_out_section is not None:
            self.broken_out_section = broken_out_section
        if crop_view is not None:
            self.crop_view = crop_view
        if occurrence_or_part_id_to_geometry_properties is not None:
            self.occurrence_or_part_id_to_geometry_properties = occurrence_or_part_id_to_geometry_properties

    @property
    def parameters(self):
        """Gets the parameters of this BTAppViewParams.  # noqa: E501


        :return: The parameters of this BTAppViewParams.  # noqa: E501
        :rtype: list[float]
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this BTAppViewParams.


        :param parameters: The parameters of this BTAppViewParams.  # noqa: E501
        :type: list[float]
        """

        self._parameters = parameters

    @property
    def display_state_id(self):
        """Gets the display_state_id of this BTAppViewParams.  # noqa: E501


        :return: The display_state_id of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._display_state_id

    @display_state_id.setter
    def display_state_id(self, display_state_id):
        """Sets the display_state_id of this BTAppViewParams.


        :param display_state_id: The display_state_id of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._display_state_id = display_state_id

    @property
    def transaction_id(self):
        """Gets the transaction_id of this BTAppViewParams.  # noqa: E501


        :return: The transaction_id of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        """Sets the transaction_id of this BTAppViewParams.


        :param transaction_id: The transaction_id of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._transaction_id = transaction_id

    @property
    def parent_change_id(self):
        """Gets the parent_change_id of this BTAppViewParams.  # noqa: E501


        :return: The parent_change_id of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._parent_change_id

    @parent_change_id.setter
    def parent_change_id(self, parent_change_id):
        """Sets the parent_change_id of this BTAppViewParams.


        :param parent_change_id: The parent_change_id of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._parent_change_id = parent_change_id

    @property
    def bom_reference_id(self):
        """Gets the bom_reference_id of this BTAppViewParams.  # noqa: E501


        :return: The bom_reference_id of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._bom_reference_id

    @bom_reference_id.setter
    def bom_reference_id(self, bom_reference_id):
        """Sets the bom_reference_id of this BTAppViewParams.


        :param bom_reference_id: The bom_reference_id of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._bom_reference_id = bom_reference_id

    @property
    def include_hidden_instances(self):
        """Gets the include_hidden_instances of this BTAppViewParams.  # noqa: E501


        :return: The include_hidden_instances of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._include_hidden_instances

    @include_hidden_instances.setter
    def include_hidden_instances(self, include_hidden_instances):
        """Sets the include_hidden_instances of this BTAppViewParams.


        :param include_hidden_instances: The include_hidden_instances of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._include_hidden_instances = include_hidden_instances

    @property
    def view_scale(self):
        """Gets the view_scale of this BTAppViewParams.  # noqa: E501


        :return: The view_scale of this BTAppViewParams.  # noqa: E501
        :rtype: float
        """
        return self._view_scale

    @view_scale.setter
    def view_scale(self, view_scale):
        """Sets the view_scale of this BTAppViewParams.


        :param view_scale: The view_scale of this BTAppViewParams.  # noqa: E501
        :type: float
        """

        self._view_scale = view_scale

    @property
    def show_tangent_lines(self):
        """Gets the show_tangent_lines of this BTAppViewParams.  # noqa: E501


        :return: The show_tangent_lines of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._show_tangent_lines

    @show_tangent_lines.setter
    def show_tangent_lines(self, show_tangent_lines):
        """Sets the show_tangent_lines of this BTAppViewParams.


        :param show_tangent_lines: The show_tangent_lines of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._show_tangent_lines = show_tangent_lines

    @property
    def compute_intersection(self):
        """Gets the compute_intersection of this BTAppViewParams.  # noqa: E501


        :return: The compute_intersection of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._compute_intersection

    @compute_intersection.setter
    def compute_intersection(self, compute_intersection):
        """Sets the compute_intersection of this BTAppViewParams.


        :param compute_intersection: The compute_intersection of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._compute_intersection = compute_intersection

    @property
    def quality_option(self):
        """Gets the quality_option of this BTAppViewParams.  # noqa: E501


        :return: The quality_option of this BTAppViewParams.  # noqa: E501
        :rtype: int
        """
        return self._quality_option

    @quality_option.setter
    def quality_option(self, quality_option):
        """Sets the quality_option of this BTAppViewParams.


        :param quality_option: The quality_option of this BTAppViewParams.  # noqa: E501
        :type: int
        """

        self._quality_option = quality_option

    @property
    def is_broken_out_section(self):
        """Gets the is_broken_out_section of this BTAppViewParams.  # noqa: E501


        :return: The is_broken_out_section of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._is_broken_out_section

    @is_broken_out_section.setter
    def is_broken_out_section(self, is_broken_out_section):
        """Sets the is_broken_out_section of this BTAppViewParams.


        :param is_broken_out_section: The is_broken_out_section of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._is_broken_out_section = is_broken_out_section

    @property
    def is_crop_view(self):
        """Gets the is_crop_view of this BTAppViewParams.  # noqa: E501


        :return: The is_crop_view of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._is_crop_view

    @is_crop_view.setter
    def is_crop_view(self, is_crop_view):
        """Sets the is_crop_view of this BTAppViewParams.


        :param is_crop_view: The is_crop_view of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._is_crop_view = is_crop_view

    @property
    def hidden_lines(self):
        """Gets the hidden_lines of this BTAppViewParams.  # noqa: E501


        :return: The hidden_lines of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._hidden_lines

    @hidden_lines.setter
    def hidden_lines(self, hidden_lines):
        """Sets the hidden_lines of this BTAppViewParams.


        :param hidden_lines: The hidden_lines of this BTAppViewParams.  # noqa: E501
        :type: str
        """
        allowed_values = ["DRAFTING", "EXCLUDED", "MARKED"]  # noqa: E501
        if hidden_lines not in allowed_values:
            raise ValueError(
                "Invalid value for `hidden_lines` ({0}), must be one of {1}"  # noqa: E501
                .format(hidden_lines, allowed_values)
            )

        self._hidden_lines = hidden_lines

    @property
    def modification_id(self):
        """Gets the modification_id of this BTAppViewParams.  # noqa: E501


        :return: The modification_id of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._modification_id

    @modification_id.setter
    def modification_id(self, modification_id):
        """Sets the modification_id of this BTAppViewParams.


        :param modification_id: The modification_id of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._modification_id = modification_id

    @property
    def perspective(self):
        """Gets the perspective of this BTAppViewParams.  # noqa: E501


        :return: The perspective of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._perspective

    @perspective.setter
    def perspective(self, perspective):
        """Sets the perspective of this BTAppViewParams.


        :param perspective: The perspective of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._perspective = perspective

    @property
    def projection_angle(self):
        """Gets the projection_angle of this BTAppViewParams.  # noqa: E501


        :return: The projection_angle of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._projection_angle

    @projection_angle.setter
    def projection_angle(self, projection_angle):
        """Sets the projection_angle of this BTAppViewParams.


        :param projection_angle: The projection_angle of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._projection_angle = projection_angle

    @property
    def show_threads(self):
        """Gets the show_threads of this BTAppViewParams.  # noqa: E501


        :return: The show_threads of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._show_threads

    @show_threads.setter
    def show_threads(self, show_threads):
        """Sets the show_threads of this BTAppViewParams.


        :param show_threads: The show_threads of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._show_threads = show_threads

    @property
    def quality_option_type(self):
        """Gets the quality_option_type of this BTAppViewParams.  # noqa: E501


        :return: The quality_option_type of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._quality_option_type

    @quality_option_type.setter
    def quality_option_type(self, quality_option_type):
        """Sets the quality_option_type of this BTAppViewParams.


        :param quality_option_type: The quality_option_type of this BTAppViewParams.  # noqa: E501
        :type: str
        """
        allowed_values = ["BEST_PERFORMANCE", "BEST_QUALITY", "BALANCED", "ADAPTIVE"]  # noqa: E501
        if quality_option_type not in allowed_values:
            raise ValueError(
                "Invalid value for `quality_option_type` ({0}), must be one of {1}"  # noqa: E501
                .format(quality_option_type, allowed_values)
            )

        self._quality_option_type = quality_option_type

    @property
    def is_partial_section(self):
        """Gets the is_partial_section of this BTAppViewParams.  # noqa: E501


        :return: The is_partial_section of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._is_partial_section

    @is_partial_section.setter
    def is_partial_section(self, is_partial_section):
        """Sets the is_partial_section of this BTAppViewParams.


        :param is_partial_section: The is_partial_section of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._is_partial_section = is_partial_section

    @property
    def broken_out_point_numbers(self):
        """Gets the broken_out_point_numbers of this BTAppViewParams.  # noqa: E501


        :return: The broken_out_point_numbers of this BTAppViewParams.  # noqa: E501
        :rtype: list[int]
        """
        return self._broken_out_point_numbers

    @broken_out_point_numbers.setter
    def broken_out_point_numbers(self, broken_out_point_numbers):
        """Sets the broken_out_point_numbers of this BTAppViewParams.


        :param broken_out_point_numbers: The broken_out_point_numbers of this BTAppViewParams.  # noqa: E501
        :type: list[int]
        """

        self._broken_out_point_numbers = broken_out_point_numbers

    @property
    def broken_out_end_conditions(self):
        """Gets the broken_out_end_conditions of this BTAppViewParams.  # noqa: E501


        :return: The broken_out_end_conditions of this BTAppViewParams.  # noqa: E501
        :rtype: dict(str, BTBrokenOutEndCondition)
        """
        return self._broken_out_end_conditions

    @broken_out_end_conditions.setter
    def broken_out_end_conditions(self, broken_out_end_conditions):
        """Sets the broken_out_end_conditions of this BTAppViewParams.


        :param broken_out_end_conditions: The broken_out_end_conditions of this BTAppViewParams.  # noqa: E501
        :type: dict(str, BTBrokenOutEndCondition)
        """

        self._broken_out_end_conditions = broken_out_end_conditions

    @property
    def broken_out_b_boxes(self):
        """Gets the broken_out_b_boxes of this BTAppViewParams.  # noqa: E501


        :return: The broken_out_b_boxes of this BTAppViewParams.  # noqa: E501
        :rtype: list[float]
        """
        return self._broken_out_b_boxes

    @broken_out_b_boxes.setter
    def broken_out_b_boxes(self, broken_out_b_boxes):
        """Sets the broken_out_b_boxes of this BTAppViewParams.


        :param broken_out_b_boxes: The broken_out_b_boxes of this BTAppViewParams.  # noqa: E501
        :type: list[float]
        """

        self._broken_out_b_boxes = broken_out_b_boxes

    @property
    def broken_out_b_boxes_map(self):
        """Gets the broken_out_b_boxes_map of this BTAppViewParams.  # noqa: E501


        :return: The broken_out_b_boxes_map of this BTAppViewParams.  # noqa: E501
        :rtype: dict(str, BTBoundingBox)
        """
        return self._broken_out_b_boxes_map

    @broken_out_b_boxes_map.setter
    def broken_out_b_boxes_map(self, broken_out_b_boxes_map):
        """Sets the broken_out_b_boxes_map of this BTAppViewParams.


        :param broken_out_b_boxes_map: The broken_out_b_boxes_map of this BTAppViewParams.  # noqa: E501
        :type: dict(str, BTBoundingBox)
        """

        self._broken_out_b_boxes_map = broken_out_b_boxes_map

    @property
    def include_surfaces(self):
        """Gets the include_surfaces of this BTAppViewParams.  # noqa: E501


        :return: The include_surfaces of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._include_surfaces

    @include_surfaces.setter
    def include_surfaces(self, include_surfaces):
        """Sets the include_surfaces of this BTAppViewParams.


        :param include_surfaces: The include_surfaces of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._include_surfaces = include_surfaces

    @property
    def is_surface(self):
        """Gets the is_surface of this BTAppViewParams.  # noqa: E501


        :return: The is_surface of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._is_surface

    @is_surface.setter
    def is_surface(self, is_surface):
        """Sets the is_surface of this BTAppViewParams.


        :param is_surface: The is_surface of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._is_surface = is_surface

    @property
    def depth_section_end_condition(self):
        """Gets the depth_section_end_condition of this BTAppViewParams.  # noqa: E501


        :return: The depth_section_end_condition of this BTAppViewParams.  # noqa: E501
        :rtype: BTBrokenOutEndCondition
        """
        return self._depth_section_end_condition

    @depth_section_end_condition.setter
    def depth_section_end_condition(self, depth_section_end_condition):
        """Sets the depth_section_end_condition of this BTAppViewParams.


        :param depth_section_end_condition: The depth_section_end_condition of this BTAppViewParams.  # noqa: E501
        :type: BTBrokenOutEndCondition
        """

        self._depth_section_end_condition = depth_section_end_condition

    @property
    def model_reference_id(self):
        """Gets the model_reference_id of this BTAppViewParams.  # noqa: E501


        :return: The model_reference_id of this BTAppViewParams.  # noqa: E501
        :rtype: str
        """
        return self._model_reference_id

    @model_reference_id.setter
    def model_reference_id(self, model_reference_id):
        """Sets the model_reference_id of this BTAppViewParams.


        :param model_reference_id: The model_reference_id of this BTAppViewParams.  # noqa: E501
        :type: str
        """

        self._model_reference_id = model_reference_id

    @property
    def view_matrix(self):
        """Gets the view_matrix of this BTAppViewParams.  # noqa: E501


        :return: The view_matrix of this BTAppViewParams.  # noqa: E501
        :rtype: list[float]
        """
        return self._view_matrix

    @view_matrix.setter
    def view_matrix(self, view_matrix):
        """Sets the view_matrix of this BTAppViewParams.


        :param view_matrix: The view_matrix of this BTAppViewParams.  # noqa: E501
        :type: list[float]
        """

        self._view_matrix = view_matrix

    @property
    def view_direction(self):
        """Gets the view_direction of this BTAppViewParams.  # noqa: E501


        :return: The view_direction of this BTAppViewParams.  # noqa: E501
        :rtype: list[float]
        """
        return self._view_direction

    @view_direction.setter
    def view_direction(self, view_direction):
        """Sets the view_direction of this BTAppViewParams.


        :param view_direction: The view_direction of this BTAppViewParams.  # noqa: E501
        :type: list[float]
        """

        self._view_direction = view_direction

    @property
    def cut_point(self):
        """Gets the cut_point of this BTAppViewParams.  # noqa: E501


        :return: The cut_point of this BTAppViewParams.  # noqa: E501
        :rtype: list[float]
        """
        return self._cut_point

    @cut_point.setter
    def cut_point(self, cut_point):
        """Sets the cut_point of this BTAppViewParams.


        :param cut_point: The cut_point of this BTAppViewParams.  # noqa: E501
        :type: list[float]
        """

        self._cut_point = cut_point

    @property
    def offset_section_points(self):
        """Gets the offset_section_points of this BTAppViewParams.  # noqa: E501


        :return: The offset_section_points of this BTAppViewParams.  # noqa: E501
        :rtype: list[float]
        """
        return self._offset_section_points

    @offset_section_points.setter
    def offset_section_points(self, offset_section_points):
        """Sets the offset_section_points of this BTAppViewParams.


        :param offset_section_points: The offset_section_points of this BTAppViewParams.  # noqa: E501
        :type: list[float]
        """

        self._offset_section_points = offset_section_points

    @property
    def broken_out_section(self):
        """Gets the broken_out_section of this BTAppViewParams.  # noqa: E501


        :return: The broken_out_section of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._broken_out_section

    @broken_out_section.setter
    def broken_out_section(self, broken_out_section):
        """Sets the broken_out_section of this BTAppViewParams.


        :param broken_out_section: The broken_out_section of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._broken_out_section = broken_out_section

    @property
    def crop_view(self):
        """Gets the crop_view of this BTAppViewParams.  # noqa: E501


        :return: The crop_view of this BTAppViewParams.  # noqa: E501
        :rtype: bool
        """
        return self._crop_view

    @crop_view.setter
    def crop_view(self, crop_view):
        """Sets the crop_view of this BTAppViewParams.


        :param crop_view: The crop_view of this BTAppViewParams.  # noqa: E501
        :type: bool
        """

        self._crop_view = crop_view

    @property
    def occurrence_or_part_id_to_geometry_properties(self):
        """Gets the occurrence_or_part_id_to_geometry_properties of this BTAppViewParams.  # noqa: E501


        :return: The occurrence_or_part_id_to_geometry_properties of this BTAppViewParams.  # noqa: E501
        :rtype: dict(str, dict(str, str))
        """
        return self._occurrence_or_part_id_to_geometry_properties

    @occurrence_or_part_id_to_geometry_properties.setter
    def occurrence_or_part_id_to_geometry_properties(self, occurrence_or_part_id_to_geometry_properties):
        """Sets the occurrence_or_part_id_to_geometry_properties of this BTAppViewParams.


        :param occurrence_or_part_id_to_geometry_properties: The occurrence_or_part_id_to_geometry_properties of this BTAppViewParams.  # noqa: E501
        :type: dict(str, dict(str, str))
        """

        self._occurrence_or_part_id_to_geometry_properties = occurrence_or_part_id_to_geometry_properties

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, BTAppViewParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
