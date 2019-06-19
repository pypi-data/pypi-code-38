# This file is part of Sympathy for Data.
# Copyright (c) 2014-2016 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import functools
import sys
import json
import six

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sympathy.platform.basicnode import (
    ManualContextBuilder, ConfirmChangesDialogMixin)
from sympathy.platform.exceptions import NoDataError, sywarn
from sympathy.platform import message, message_util

from sympathy.platform.os_support import raise_window, focus_widget
from sympathy.utils.prim import format_display_string

from sympathy.utils import uuid_generator
from sympathy.utils import prim

from sympathy.platform import state


# Generate unique instance to avoid situation where something
# is dragged from a completely different instance. This works fine since
# the configuration aggregation always is run in a separate process.
UNIQUE_INSTANCE = uuid_generator.generate_uuid()


# MIME-types for drag and drop.
MIME_AVAILABLE_NODE = ('application-x-sympathy-aggregation-available-node-'
                       '{}'.format(UNIQUE_INSTANCE))
MIME_SELECTED_ITEM = ('application-x-sympathy-aggregation-selected-item-'
                      '{}'.format(UNIQUE_INSTANCE))


_tab_builder = 'TabBuilder'
_wizard_builder = 'WizardBuilder'

_configure = 'configure'
_settings = 'settings'
_configure_with_wizard = 'configure_with_wizard'
_configure_with_tabbed = 'configure_with_tabbed'
_configure_modes = [True, _configure, _configure_with_wizard,
                    _configure_with_tabbed]


def clean_flow_info(flow_info_with_instances):
    """
    Return similar structure to flow_info_with_instances,
    but without the library_node_instance fields.

    Only the structure is copied, to allow for changes without
    affecting the input.
    """
    def clean_node_info(node_info):
        result = dict(node_info)
        result.pop('library_node_instance', None)
        return result

    result = dict(flow_info_with_instances)

    if 'nodes' in result:
        result['nodes'] = [clean_node_info(node_info)
                           for node_info in result['nodes']]

    if 'flows' in result:
        result['flows'] = [clean_flow_info(flow_info)
                           for flow_info in result['flows']]

    return result


class ConfigurationAggregation(object):
    """
    The configuration aggregation is supposed to be called from a separate
    worker process called aggregated_parameter_view_worker.
    """

    def __init__(self, configure, socket_bundle, flow_info_with_instances,
                 type_aliases):
        self._configure = configure
        self._type_aliases = type_aliases
        self.flow_info = flow_info_with_instances
        self._wfdthread = WaitForData(socket_bundle)

    def run(self):
        app = QtGui.QApplication.instance()
        cdm = CentralDataModel(
            self.flow_info, self._type_aliases, self._configure)
        if (self._configure in _configure_modes and
                cdm._builder == _wizard_builder):
            dialog = WizardParameterView(cdm, self._wfdthread)
        elif self._configure == _settings:
            dialog = SettingsDialog(cdm, self._wfdthread)
        else:
            dialog = TabbedParameterView(cdm, self._wfdthread)

        title = 'Parameter View' if self._configure else 'Aggregation Settings'
        dialog.setWindowTitle('{} - {}'.format(cdm.name(), title))

        # TODO(stefan): Something better here.
        dialog.resize(800, 600)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        QtCore.QTimer.singleShot(0, functools.partial(focus_widget, dialog))

        app.exec_()
        # Receive boolean in result.
        result = dialog.result() == QtGui.QDialog.Accepted
        cdm.collect_parameters(True)
        self.flow_info['json_aggregation_settings'] = json.dumps(
            cdm.to_dict())
        self.flow_info['configure'] = self._configure in _configure_modes
        return result


def info_selected_uuids(item_info_dict):
    json_aggregation_settings = item_info_dict.get(
        'json_aggregation_settings', '')
    if not json_aggregation_settings:
        return []
    aggregation_settings = json.loads(json_aggregation_settings)
    if not aggregation_settings:
        return []
    if 'uuid_selected' in aggregation_settings:
        return aggregation_settings['uuid_selected']
    elif 'selected_uuids' in aggregation_settings:
        return aggregation_settings['selected_uuids']
    return []


class WidgetManager(object):
    """Class responsible for managing widgets."""

    def __init__(self, cdm, type_aliases, lazy):
        self._type_aliases = type_aliases
        self.uuid_to_flow = {}
        self._lazy = lazy
        self._cdm = cdm
        self._uuid_to_widget = self._init_uuid_to_widget(cdm.flow_info)

    def _init_uuid_to_widget(self, info_dict, top_level=True,
                             selected_uuids_list=None):
        """
        Recursive method to walk the flow info tree
        and initialize the uuid_to_widget dictionary.

        Parameters
        ----------
        info_dict : dict
            A dictionary containing information about a flow or a node.
        top_level : bool
            True if this is the first recursiion level, False otherwise.
        selected_uuids_list : list
            List of selected uuids. If specified, this will be used instead of
            the aggregation settings in info_dict. This is useful when a legacy
            structure has been found.
        """
        result = {}
        if selected_uuids_list is None:
            selected_uuids_list = []

        def lazy_node_context(node_info_dict, node_dict):

            @prim.memoize
            def inner():
                try:
                    node_context, input_fileobjs = self._build_node_context(
                        node_info_dict, node_dict, self._type_aliases)
                except NoDataError:
                    node_context, input_fileobjs = None, None
                return node_context, input_fileobjs
            return inner

        def has_old_settings(item_info_dict):
            json_aggregation_settings = item_info_dict.get(
                'json_aggregation_settings', '')
            if not json_aggregation_settings:
                return False
            aggregation_settings = json.loads(json_aggregation_settings)
            if not aggregation_settings:
                return False
            if 'uuid_selected' in aggregation_settings:
                return True
            return False

        def item_selected(full_uuid, item_info_dict):
            uuid = uuid_generator.split_uuid(full_uuid)[1]
            return (uuid in info_selected_uuids(item_info_dict) or
                    uuid in selected_uuids_list)

        # Loop through all flows
        for flow_info_dict in info_dict['flows']:
            uuid = flow_info_dict['uuid']

            if top_level or item_selected(uuid, info_dict):
                result[uuid] = {
                    'info_dict': flow_info_dict,
                    'icon': QtGui.QIcon(),
                    'type': 'flow',
                    'requires_input_data': False,
                    'empty_parameters': False,
                    'widget': None}

                if selected_uuids_list:
                    # We are already in legacy settings, so just pass on the
                    # same list of selected uuids.
                    subresult = self._init_uuid_to_widget(
                        flow_info_dict, top_level=False,
                        selected_uuids_list=selected_uuids_list)
                elif has_old_settings(info_dict):
                    # Found legacy settings! Pass them on to the next recursion
                    # level!
                    subresult = self._init_uuid_to_widget(
                        flow_info_dict, top_level=False,
                        selected_uuids_list=info_selected_uuids(info_dict))
                else:
                    # Business as usual.
                    subresult = self._init_uuid_to_widget(
                        flow_info_dict, top_level=False)
                result.update(subresult)

                if top_level:
                    result[flow_info_dict['uuid']]['children'] = (
                        list(subresult.values()))

        # Loop through all nodes
        for node_info_dict in info_dict['nodes']:
            uuid = node_info_dict['uuid']

            if top_level or item_selected(uuid, info_dict):
                node_dict = json.loads(node_info_dict['json_node_dict'])
                node_context = lazy_node_context(node_info_dict, node_dict)

                if not self._lazy:
                    # Force evaluation of value.
                    node_context()

                widget_dict = {
                    'info_dict': node_info_dict,
                    'node_dict': json.loads(node_info_dict['json_node_dict']),
                    'icon': self._build_icon(node_info_dict.get('icon')),
                    'node_context': node_context,
                    'type': 'node',
                    'widget': None}

                widget_dict['requires_input_data'] = False
                try:
                    widget_dict['empty_parameters'] = (
                        len(node_dict['parameters']['data']) <= 1)
                except TypeError:
                    widget_dict['empty_parameters'] = True

                result[uuid] = widget_dict

        return result

    @staticmethod
    def _build_icon(svg_icon_data):
        """Build icon from SVG-data."""
        if svg_icon_data is not None:
            icon_data = QtCore.QByteArray(svg_icon_data)
            icon_data = QtCore.QByteArray.fromBase64(icon_data)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(icon_data)
            icon = QtGui.QIcon(pixmap)
            return icon
        return QtGui.QIcon()

    @staticmethod
    def _build_node_context(node_info_dict, node_dict, type_aliases):
        """Build context for node."""
        try:
            node_settings = state.node_state().attributes['node_settings']
        except KeyError:
            node_settings = {}

        state.node_state().attributes['node_settings'] = node_info_dict[
            'node_settings']

        builder = ManualContextBuilder(
            {}, {}, False, port_dummies=True, check_fns=False)

        library_node_instance = node_info_dict['library_node_instance']
        try:
            node_context = library_node_instance._build_node_context(
                node_dict, type_aliases, exclude_output=True,
                builder=builder)
            # Preventing garbage collections of the generators by returning
            # them.
            return (node_context, builder.input_fileobjs)
        except (ValueError, AttributeError):
            pass
        except:
            raise NoDataError

        state.node_state().attributes['node_settings'] = node_settings
        return (None, None)

    def icon(self, uuid):
        """Return node icon."""
        widget_dict = self._uuid_to_widget.get(uuid, None)
        if widget_dict is None:
            return QtGui.QIcon()
        return widget_dict['icon']

    def name(self, uuid):
        """Return name of node."""
        widget_dict = self._uuid_to_widget.get(uuid, None)
        if widget_dict is None:
            flow_dict = self.uuid_to_flow.get(uuid, None)
            return '<{}>'.format(flow_dict['name'])
        return widget_dict['info_dict']['name']

    def node_context(self, uuid):
        """Return context for node."""
        widget_dict = self._uuid_to_widget.get(uuid, None)
        return widget_dict['node_context']()[0]

    def widget(self, uuid):
        """
        Fetch widget with the given UUID.
        :param uuid: UUID for node.
        :return: None if invalid. Otherwise return a widget.
        """
        def widget_factory(item_dict):
            if item_dict['type'] == 'flow':
                return flow_widget(item_dict)
            elif item_dict['type'] == 'node':
                try:
                    return node_widget(item_dict)
                except Exception:
                    return None
            else:
                assert False

        def flow_widget(item_dict):
            """
            Extract widgets from selected items in the user defined
            grouping structure.
            """
            children = item_dict.get('children', [])

            def selected_order(item_dict):
                try:
                    uuid = item_dict['info_dict']['uuid']
                    res = selected_uuids.index(
                        uuid_generator.split_uuid(uuid)[1])
                except Exception:
                    res = -1
                return res

            if len(children) == 1:
                item = children[0]
                return widget_factory(item)

            group_widget = TabParameterWidget()
            selected_uuids = info_selected_uuids(item_dict['info_dict'])

            for item in sorted(item_dict.get('children', []),
                               key=selected_order):
                if item['type'] == 'flow' and item.get('children', []):
                    widget = widget_factory(item)
                    group_widget.addTab(widget, item['info_dict']['name'])
                elif item['type'] == 'node':
                    widget = widget_factory(item)
                    group_widget.addTab(widget, item['info_dict']['name'])

            return group_widget

        def node_widget(item_dict):
            """
            Extract widgets from selected items in the user defined
            grouping structure.
            """
            library_node_instance = item_dict['info_dict'][
                'library_node_instance']
            node_context = item_dict['node_context']()[0]

            # Start with trying to adjust parameters.
            try:
                library_node_instance.adjust_parameters_basic(node_context)
            except (NoDataError, AttributeError):
                item_dict['requires_input_data'] = True

            # Now try to create the widget.
            try:
                item_dict['widget'] = (
                    library_node_instance._execute_parameter_view(
                        node_context, return_widget='parameters_widget'))
            except (NoDataError, AttributeError):
                item_dict['requires_input_data'] = True

            if (uuid in self._uuid_to_widget and
                    self._uuid_to_widget[uuid]['widget'] is not None):
                return self._uuid_to_widget[uuid]['widget']

            return item_dict['widget']

        # If the widget has already been created, return it.
        if self.has_generated_widget(uuid):
            return self._uuid_to_widget[uuid]['widget']

        # otherwise, build the widget from scratch
        try:
            widget_dict = self._uuid_to_widget[uuid]
        except KeyError:
            raise KeyError("Can't find uuid {} in dict with keys {}".format(
                uuid, list(self._uuid_to_widget.keys())))
        widget_dict['widget'] = widget_factory(widget_dict)
        return widget_dict['widget']

    def widget_ok(self, uuid):
        """
        Check if widget is ok for manipulation.
        :param uuid: UUID for node.
        :return: (Ok flag, reason)
        """
        widget_dict = self._uuid_to_widget[uuid]
        reason = []
        if widget_dict['requires_input_data']:
            reason.append('Required Input Data Missing')
        if widget_dict['empty_parameters']:
            reason.append('No Parameters')
        return len(reason) == 0, '\n'.join(reason)

    def is_required_input_data_missing(self, uuid):
        widget_dict = self._uuid_to_widget[uuid]
        return widget_dict['requires_input_data']

    def has_no_parameters(self, uuid):
        widget_dict = self._uuid_to_widget[uuid]
        return widget_dict['empty_parameters']

    def has_generated_widget(self, uuid):
        try:
            return self._uuid_to_widget[uuid]['widget'] is not None
        except KeyError:
            return False


class CentralDataModel(QtCore.QObject):
    """Central storage for data within the dialog."""

    def __init__(self, flow_info_with_instances, type_aliases, configure,
                 parent=None):
        super(CentralDataModel, self).__init__(parent)

        # Properties where we store all the data:
        # flow_structure -- contains the actual structure in the flow.
        # uuid_to_item -- is a mapping between UUID to an item in the flow
        #                 structure.
        # selected_uuids -- is a list containing all the selected nodes, in the
        #                   order the user has chosen.
        self.flow_info = flow_info_with_instances
        self.flow_structure = None
        self.uuid_to_item = {}
        self.selected_uuids = []
        self.bad_settings_update = False
        self._override = True
        self._builder = _tab_builder
        self._configure = configure

        self._initialize_aggregation_settings(flow_info_with_instances)

        aggregation_settings = json.loads(
            flow_info_with_instances['json_aggregation_settings'])
        if aggregation_settings is not None:
            self._apply_aggregation_settings(aggregation_settings)
        self.check_model_integrity()

        self.widget_manager = WidgetManager(
            self, type_aliases, self.builder_lazy())

    def _shallow_uuid_to_full_uuid(self, uuid):
        """
        Return the full uuid for a shallow node/flow in the subflow given its
        partial uuid.
        Returns None if the uuid is not found.
        """
        for item in (self.flow_structure['nodes'] +
                     self.flow_structure['flows']):
            if uuid_generator.split_uuid(item['uuid'])[1] == uuid:
                return item['uuid']
        return None

    def _find_full_uuid(self, uuid, flow_structure=None):
        """
        Return a valid full uuid for a node somewhere in subflow hierarchy
        given its partial uuid.

        If several full uuids are valid for a partial uuid, which one is
        returned is implementation defined.

        Returns None if the uuid is not found.
        """
        if flow_structure is None:
            flow_structure = self.flow_structure

        for node_dict in flow_structure['nodes']:
            if uuid_generator.split_uuid(node_dict['uuid'])[1] == uuid:
                return node_dict['uuid']
        for flow_dict in flow_structure['flows']:
            full_uuid = self._find_full_uuid(uuid, flow_dict)
            if full_uuid is not None:
                return full_uuid
        return None

    def _initialize_aggregation_settings(self, flow_info_with_instances):
        """Initialize aggregation settings to default values."""
        def build_flow_structure(flow_info):
            """Build the flow structure based on the flow info dictionary."""
            self.uuid_to_item[flow_info['uuid']] = flow_info

            s = {'name': flow_info['name'],
                 'uuid': flow_info['uuid'],
                 'nodes': [{'name': x['name'],
                            'uuid': x['uuid']}
                           for x in flow_info['nodes']],
                 'flows': [build_flow_structure(x)
                           for x in flow_info['flows']]}

            for node_info in flow_info['nodes'] + flow_info['flows']:
                self.uuid_to_item[node_info['uuid']] = node_info
            return s

        self.flow_structure = build_flow_structure(flow_info_with_instances)

    def _apply_aggregation_settings(self, aggregation_settings):
        """Apply aggregation settings to the given members."""
        try:
            if 'selected_uuids' in aggregation_settings:
                # Currently used storage model.
                for uuid in aggregation_settings.get('selected_uuids', []):
                    full_uuid = self._shallow_uuid_to_full_uuid(uuid)
                    if full_uuid in self.uuid_to_item:
                        self.selected_uuids.append(full_uuid)
            elif 'group_structure' in aggregation_settings:
                # Legacy storage model. Import settings from the group
                # structure. This will get the order of the selected nodes
                # right, but some of the selected nodes will not be selected
                # after this import.
                self.selected_uuids = self._uuids_from_legacy_structure(
                    aggregation_settings['group_structure'], self._configure)

            self._override = aggregation_settings.get('override', True)
        except KeyError:
            pass

        if self._configure == _configure_with_wizard:
            self._builder = _wizard_builder
        elif self._configure == _configure_with_tabbed:
            self._builder = _tab_builder
        else:
            self._builder = aggregation_settings.get(
                'conf_view', _tab_builder)

    def _uuids_from_legacy_structure(self, group_structure, configure):
        """
        Extract selected uuids from legacy group structure.

        This has several shortcomings:
         - uuids are not full and the node could be in any subsubflow, so if
           there are several links to the same subflow it is impossible to know
           which of the nodes that should be exposed.
         - The order in the old structure was a tree, but in the new structure
           it is a list so the order can only be partially retained.

        Parameters:
        group_structure : dict
            The legacy dictionary structure.
        configure : bool
            Is the user configuring (True) or editing settings (False)? If True
            return a list of all uuids that were selected in the old structure,
            else return a list of only the shallow nodes that were selected in
            the old structure.
        """
        if configure in _configure_modes:
            selected_uuids = []
            for item in group_structure.get('children', []):
                # Add the item if it is a shallow node.
                full_uuid = self._find_full_uuid(item['uuid'])
                if item['type'] == 'node' and full_uuid in self.uuid_to_item:
                    selected_uuids.append(full_uuid)
                elif item['type'] == 'group':
                    selected_uuids.extend(
                        self._uuids_from_legacy_structure(item, configure))
            return selected_uuids
        else:
            selected_uuids = []
            for item in group_structure.get('children', []):
                # Add the item if it is a shallow node.
                full_uuid = self._shallow_uuid_to_full_uuid(item['uuid'])
                if item['type'] == 'node' and full_uuid in self.uuid_to_item:
                    selected_uuids.append(full_uuid)
                elif item['type'] == 'group':
                    selected_uuids.extend(
                        self._uuids_from_legacy_structure(item, configure))
                else:
                    # Perhaps a node has been deleted or the selection included
                    # a node within a subflow. Whatever the reason, we couldn't
                    # translate these settings perfectly. We store this
                    # information in the flag self.bad_settings_update.
                    self.bad_settings_update = True
            return selected_uuids

    def name(self):
        return format_display_string(self.flow_info.get('name', 'Flow'))

    def builder(self):
        return globals()[self._builder]

    def builder_lazy(self):
        return self.builder().lazy

    def use_wizard(self):
        if self._builder == _wizard_builder:
            return QtCore.Qt.Checked
        return QtCore.Qt.Unchecked

    def set_use_wizard(self, check):
        if check == QtCore.Qt.Checked:
            self._builder = _wizard_builder
        elif check == QtCore.Qt.Unchecked:
            self._builder = _tab_builder

    @property
    def is_linked(self):
        return self.flow_info.get('is_linked')

    @property
    def override(self):
        """
        Return the override state. True means override parameters, False means
        change the target subflow directly.
        """
        return self._override

    def set_override(self, state):
        """
        Set the override state. True means override parameters, False means
        change the target subflow directly.
        """
        self._override = bool(state)

    def available_nodes(self):
        """Return a list of all available nodes/subflows."""
        return self.flow_structure['nodes'] + self.flow_structure['flows']

    def is_selected(self, uuid):
        """Check if the given UUID is selected."""
        return uuid in self.selected_uuids

    def selected_node_uuids_recursive(self):
        """
        Return the full list of selected node UUIDs, including nodes selected
        in nested and selected flows.
        """
        def selected_in_settings(aggregation_settings):
            if 'selected_uuids' in aggregation_settings:
                return aggregation_settings['selected_uuids']
            return []

        def selected_in_flow(flow):
            json_aggregation_settings = flow.get(
                'json_aggregation_settings', None)
            if (json_aggregation_settings and
                    json_aggregation_settings != 'null'):
                aggregation_settings = json.loads(
                    json_aggregation_settings)

                selected_items = selected_in_settings(
                    aggregation_settings)

                for node in flow['nodes']:
                    uuid = node['uuid']
                    if uuid_generator.split_uuid(uuid)[1] in selected_items:
                        result.append(uuid)

                result.extend(selected_items)

                for subflow in flow['flows']:
                    uuid = subflow['uuid']
                    if uuid_generator.split_uuid(uuid)[1] in selected_items:
                        selected_in_flow(subflow)

        result = []
        selected_in_flow(self.flow_info)
        return result

    # -------------------------------------------------------------------------
    # The following are used for handling the list of selected uuids.

    def move_node_to_selected(self, uuid, row=None):
        """Move item with given UUID to the set of selected items."""
        assert not self.is_selected(uuid)
        assert self.check_model_integrity()
        self.selected_uuids.insert(row, uuid)
        assert self.check_model_integrity()

    def remove_item(self, item):
        """Remove item."""
        self.remove_uuid(item['uuid'])

    def remove_uuid(self, uuid):
        """Remove uuid."""
        assert self.check_model_integrity()
        self.selected_uuids.remove(uuid)
        assert self.check_model_integrity()

    def move_uuid(self, uuid, row=None):
        """Move item and all eventual children to a new parent."""
        assert self.check_model_integrity()
        self.remove_uuid(uuid)
        if row is None:
            self.selected_uuids.append(uuid)
        else:
            self.selected_uuids.insert(row, uuid)
        assert self.check_model_integrity()

    def remove_top_level_uuids(self, uuid_list):
        assert self.check_model_integrity()
        for uuid in uuid_list:
            self.selected_uuids.remove(uuid)
        assert self.check_model_integrity()

    def remove_items(self, item_list):
        """Remove items from selected uuids."""
        assert self.check_model_integrity()
        for item in item_list:
            self.remove_item(item)
        assert self.check_model_integrity()

    def move_uuids(self, uuid_list, row=None):
        """Move items in list."""
        assert self.check_model_integrity()
        for i, uuid in enumerate(uuid_list):
            if row is not None:
                self.move_uuid(uuid, row + i)
            else:
                self.move_uuid(uuid)
        assert self.check_model_integrity()

    def to_dict(self):
        """Serialize configuration data to dictionary."""
        selected_uuids = [uuid_generator.split_uuid(uuid)[1]
                          for uuid in self.selected_uuids]
        return {'selected_uuids': selected_uuids,
                'conf_view': self._builder,
                'override': self._override}

    def check_model_integrity(self):
        # Check that there are no duplicates in the list
        return len(set(self.selected_uuids)) == len(self.selected_uuids)

    def collect_parameters(self, done=False):
        """
        Extract configuration changes from all widgets and apply to flow_info.
        :param flow_info: Flow info dictionary.
        """
        def has_old_settings(item_info_dict):
            json_aggregation_settings = item_info_dict.get(
                'json_aggregation_settings', '')
            if not json_aggregation_settings:
                return False
            aggregation_settings = json.loads(json_aggregation_settings)
            if not aggregation_settings:
                return False
            if 'uuid_selected' in aggregation_settings:
                return True
            return False

        def uuid_selected(full_uuid, item_info_dict, selected_uuids_list):
            if selected_uuids_list is None:
                selected_uuids_list = []

            uuid = uuid_generator.split_uuid(full_uuid)[1]
            return (uuid in info_selected_uuids(item_info_dict) or
                    uuid in selected_uuids_list)

        def inner(flow_info, selected_uuids_list=None):
            for node_info in flow_info['nodes']:
                uuid = node_info['uuid']
                if (uuid_selected(uuid, flow_info, selected_uuids_list) and
                        self.widget_manager.has_generated_widget(uuid)):
                    widget = self.widget_manager.widget(uuid)
                    if widget is not None:
                        # Force widget to save parameters in node_context:
                        widget.save_parameters()

                        node_dict = json.loads(node_info['json_node_dict'])
                        node_context = self.widget_manager.node_context(uuid)
                        node_dict['parameters']['data'] = (
                            node_context.definition['parameters']['data'])
                        node_info['json_node_dict'] = json.dumps(node_dict)
            for sub_flow_info in flow_info['flows']:
                if not selected_uuids_list and has_old_settings(flow_info):
                    selected_uuids_list = info_selected_uuids(flow_info)
                inner(sub_flow_info, selected_uuids_list)

        inner(self.flow_info)


class AggregatedDialogMixin(object):
    """SuperClass for creating the Settings, Tab Parameter View or Wizard."""

    def __init__(self, central_data_model, wfdthread, *args, **kwargs):
        super(AggregatedDialogMixin, self).__init__(*args, **kwargs)

        self._central_data_model = central_data_model
        self._wfdthread = wfdthread

        self.extra_init()
        wfdthread.raise_window.connect(self.raise_window)

    def extra_init(self):
        raise NotImplementedError

    def raise_window(self):
        # if not self.isActiveWindow():
        raise_window(self)


class SettingsDialog(AggregatedDialogMixin, QtGui.QDialog):
    """Main view for the Settings and Tab Parameters views."""

    def __init__(self, central_data_model, wfdthread, parent=None):
        super(SettingsDialog, self).__init__(
            central_data_model, wfdthread, parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)

    def extra_init(self):
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)

        self._view = SettingsView(self._central_data_model)
        if self._view.layout() is not None:
            self._view.layout().setContentsMargins(0, 0, 0, 0)
        vertical_layout.addWidget(self._view)

        button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        vertical_layout.addWidget(button_box)


class TabbedParameterView(ConfirmChangesDialogMixin, AggregatedDialogMixin,
                          QtGui.QDialog):
    """Main view for the Settings and Tab Parameters views."""

    def __init__(self, central_data_model, wfdthread, parent=None):
        super(TabbedParameterView, self).__init__(
            central_data_model, wfdthread, parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)

    def extra_init(self):
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)

        self._view = ParameterView(
            self._central_data_model, self._wfdthread)
        if self._view.layout() is not None:
            self._view.layout().setContentsMargins(0, 0, 0, 0)
        vertical_layout.addWidget(self._view)

        button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        vertical_layout.addWidget(button_box)
        self._ok_button = button_box.button(QtGui.QDialogButtonBox.Ok)

        for w in self._view.widgets():
            w.valid_changed.connect(self._update_ok)
        self._update_ok()

    def cleanup(self):
        for widget in self._view.widgets():
            widget.cleanup()
            widget.valid_changed.disconnect(self._update_ok)

    def parameters_changed(self):
        widgets = self._view.widgets()
        return any(w.parameters_changed() for w in widgets)

    def _update_ok(self):
        self._ok_button.setEnabled(all(w.valid for w in self._view.widgets()))


class WizardParameterView(ConfirmChangesDialogMixin, AggregatedDialogMixin,
                          QtGui.QWizard):

    def __init__(self, central_data_model, wfdthread, parent=None):
        super(WizardParameterView, self).__init__(
            central_data_model, wfdthread, parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self._initialized_pages = []

    def page_factory(self, n, item, ntot):
        page = WizardReadyPage(n, ntot, item, self._wfdthread.request_data,
                               self._central_data_model)
        progress = WizardProgressPage(n, ntot, item,
                                      self._wfdthread.request_data)
        page.completeChanged.connect(self._update_ok)
        progress.completeChanged.connect(self._update_ok)
        self._wfdthread.data_ready.connect(progress.set_complete)
        self._wfdthread.data_blocked.connect(progress.set_blocked)
        return [progress, page]

    def extract_widgets_from_selected_items(self, item_dict, selected):
        """
        Extract widgets from selected items in the user defined
        grouping structure.
        """
        cdm = self._central_data_model

        result = []

        for item in item_dict['nodes']:
            uuid = item['uuid']

            if uuid in selected:
                if not cdm.widget_manager.has_no_parameters(uuid):
                    result.append((cdm.uuid_to_item[uuid]))

        for item in item_dict['flows']:
            result.extend(self.extract_widgets_from_selected_items(
                item, selected))

        return result

    def extra_init(self):
        # on windows the Wizard shows the WindowTitle in the wrong
        # place if we use the native style
        self.setWizardStyle(QtGui.QWizard.ClassicStyle)

        selected = self._central_data_model.selected_node_uuids_recursive()
        cdm = self._central_data_model
        items = self.extract_widgets_from_selected_items(cdm.flow_structure,
                                                         selected)
        items.sort(key=lambda x: x['level'])

        ntot = len(items)

        self.setButtonText(QtGui.QWizard.CustomButton1, 'Cancel')
        self.setButtonText(QtGui.QWizard.CustomButton2, 'OK')
        self._ok_button = self.button(QtGui.QWizard.CustomButton2)

        for n, item in enumerate(items, 1):
            for page in self.page_factory(n, item, ntot):
                self.addPage(page)

        button_layout = [QtGui.QWizard.Stretch,
                         # QtGui.QWizard.BackButton,  # not used at the moment
                         # QtGui.QWizard.NextButton,  # not used at the moment
                         QtGui.QWizard.CommitButton]

        if sys.platform == 'win32':
            button_layout += [QtGui.QWizard.CustomButton2,
                              QtGui.QWizard.CustomButton1]
        else:
            button_layout += [QtGui.QWizard.CustomButton1,
                              QtGui.QWizard.CustomButton2]

        self.setButtonLayout(button_layout)
        self.customButtonClicked[int].connect(self.custom_button_clicked)

    def cleanup(self):
        for page in self._initialized_pages:
            page.cleanup()

    def parameters_changed(self):
        if self.currentPage() is not None:
            current_widget = self.currentPage().widget()
            if current_widget is not None:
                return current_widget.parameters_changed()
        return False

    def custom_button_clicked(self, button):
        if button == 6:  # Cancel button / CustomButton1
            self.reject()
        elif button == 7:  # Ok button / CustomButton2
            self._has_quit = True
            self.accept()

    def _update_ok(self):
        self._ok_button.setEnabled(self.currentPage().isComplete())

    def initialize_page(self, page):
        self._initialized_pages.append(page)


class ParameterView(QtGui.QWidget):
    """
    View containing the aggregation.
    """
    valid_changed = QtCore.Signal()

    def __init__(self, central_data_model, wfdthread, parent=None):
        super(ParameterView, self).__init__(parent)
        self._central_data_model = central_data_model
        self._wfdthread = wfdthread
        self.current_widget = None
        self.setLayout(QtGui.QVBoxLayout())
        self._show_tab_view()

    def _show_tab_view(self):
        self.current_widget = self._central_data_model.builder().build(
            self._central_data_model, self._wfdthread)
        self.layout().addWidget(self.current_widget)

    def widgets(self):
        selected_uuids = self._central_data_model.selected_uuids

        widgets = []
        for uuid in selected_uuids:
            widget = self._central_data_model.widget_manager.widget(uuid)
            if widget is not None:
                widgets.append(widget)
        return widgets


class SettingsView(QtGui.QWidget):
    """Settings view for aggregation."""

    show_tree_view = QtCore.Signal()
    show_tab_view = QtCore.Signal()
    show_full_path_names = QtCore.Signal(bool)

    def __init__(self, central_data_model, parent=None):
        super(SettingsView, self).__init__(parent)

        if central_data_model.bad_settings_update:
            QtGui.QMessageBox.warning(
                self, "Imperfect settings update",
                "The aggregation settings for this subflow are stored in an "
                "old format. Unfortunately, Sympathy for Data was unable to "
                "completely update the settings to the newest format. This "
                "can result in nodes being deselected.")

        use_wizard = QtGui.QCheckBox('Configure using wizard')
        use_wizard.setCheckState(central_data_model.use_wizard())
        use_wizard.setToolTip(
            "<p>When checked, configuration will be done in a wizard showing "
            "the configuration dialogs for the selected nodes, one at a "
            "time. The nodes will be shown in dependency order and the "
            "wizard makes sure that every preceding node is executed"
            "before each selected node dialog. This can be useful since"
            "some nodes use the input data to improve the configuration"
            "GUI. See subflow documentation for details and examples.</p>")

        override_checkbox = QtGui.QCheckBox('Override parameters')
        override_checkbox.setChecked(central_data_model.override)
        override_checkbox.setToolTip(
            "<p>If checked, any changes to parameters done via a link to this "
            "subflow will be stored as overrides in the flow containing the "
            "link without modifying this subflow. If unchecked, any "
            "parameter changes will be stored in this subflow. See subflow "
            "documentation for details and examples.</p>")

        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                                 QtGui.QSizePolicy.Expanding))

        self.available_tree = AvailableTreeView(self)
        self.selected_tree = SelectedTreeView(self)

        available_container = QtGui.QWidget()
        available_layout = QtGui.QVBoxLayout()
        available_container.setLayout(available_layout)
        available_layout.addWidget(QtGui.QLabel('Available Nodes'))
        available_layout.addWidget(self.available_tree)

        selected_container = QtGui.QWidget()
        selected_layout = QtGui.QVBoxLayout()
        selected_layout.addWidget(QtGui.QLabel('Selected Nodes'))
        selected_container.setLayout(selected_layout)
        selected_layout.addWidget(self.selected_tree)

        splitter.addWidget(available_container)
        splitter.addWidget(selected_container)

        vertical_layout = QtGui.QVBoxLayout()

        self.setLayout(vertical_layout)
        vertical_layout.addWidget(splitter)
        vertical_layout.addWidget(use_wizard)
        if central_data_model.is_linked:
            vertical_layout.addWidget(override_checkbox)

        self.available_model = AvailableModel(central_data_model)
        self.available_tree.setModel(self.available_model)

        self.selected_model = SelectedModel(central_data_model)
        self.selected_tree.setModel(self.selected_model)

        self.selected_model.rowsInserted[QtCore.QModelIndex, int, int].connect(
            self.available_tree.clearSelection)
        self.selected_model.rowsInserted[QtCore.QModelIndex, int, int].connect(
            self.available_tree.update)
        self.selected_model.layoutChanged.connect(self.available_tree.update)

        self.selected_tree.highlight.connect(
            self.available_tree.set_highlight)

        use_wizard.stateChanged.connect(central_data_model.set_use_wizard)
        override_checkbox.stateChanged.connect(central_data_model.set_override)


class AvailableTreeView(QtGui.QTreeView):
    """View for available nodes."""

    def __init__(self, parent=None):
        super(AvailableTreeView, self).__init__(parent)
        self.setHeaderHidden(True)
        # self.available_tree.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(True)
        self.setUpdatesEnabled(True)

    @QtCore.Slot(list)
    def set_highlight(self, uuid):
        """Set list of UUID:s to be highlighted."""
        self.model().highlighted = uuid
        # HACK(stefan): Force update on Windows platforms. update() does not
        #               seem to do anything on Windows.
        # (Magnus):     Linux behaves the same way.
        if sys.platform == 'win32' or sys.platform.startswith('linux'):
            self.setAlternatingRowColors(True)
            self.setAlternatingRowColors(False)
        self.update()


class AvailableModel(QtCore.QAbstractListModel):
    """
    Data model for source node list view.
    """

    def __init__(self, central_data_model, parent=None):
        super(AvailableModel, self).__init__(parent)
        self._central_data_model = central_data_model
        self.highlighted = []
        palette = QtGui.QPalette()
        self.highlight_brush = palette.midlight()

    def mimeData(self, index_list):
        data = QtCore.QMimeData()
        uuid_list = [
            {'uuid': self.data(index, QtCore.Qt.UserRole),
             'instance': UNIQUE_INSTANCE}
            for index in index_list if index.isValid()]
        byte_array = QtCore.QByteArray(json.dumps(uuid_list))
        data.setData(MIME_AVAILABLE_NODE, byte_array)
        return data

    def mimeTypes(self):
        return [MIME_AVAILABLE_NODE]

    def supportedDragActions(self):
        return QtCore.Qt.CopyAction

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        item = self._central_data_model.available_nodes()[row]
        item_uuid = item['uuid']
        if role == QtCore.Qt.DisplayRole:
            return item['name']
        elif role == QtCore.Qt.DecorationRole:
            icon = self._central_data_model.widget_manager.icon(item_uuid)
            return icon
        elif role == QtCore.Qt.BackgroundRole:
            if item['uuid'] in self.highlighted:
                return self.highlight_brush
        elif role == QtCore.Qt.UserRole:
            return item_uuid
        return None

    def flags(self, index):
        if not index.isValid():
            return 0
        item_uuid = self.data(index, QtCore.Qt.UserRole)

        if self._central_data_model.is_selected(item_uuid):
            return QtCore.Qt.NoItemFlags
        else:
            return (QtCore.Qt.ItemIsSelectable |
                    QtCore.Qt.ItemIsDragEnabled |
                    QtCore.Qt.ItemIsEnabled)

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            return 'header'

    def rowCount(self, parent_index):
        if parent_index.isValid():
            return 0
        else:
            return len(self._central_data_model.available_nodes())


class SelectedTreeView(QtGui.QTreeView):
    """View for selected nodes in a group view."""

    highlight = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(SelectedTreeView, self).__init__(parent)

        self._remove_action = QtGui.QAction('Remove items', self)
        self._remove_action.setShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Delete))
        self._remove_action.setShortcutContext(
            QtCore.Qt.WidgetWithChildrenShortcut)
        self.addAction(self._remove_action)
        self._remove_action.triggered.connect(self._handle_remove_items)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.setMouseTracking(True)
        self.setHeaderHidden(True)
        # self.selected_tree.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def mouseMoveEvent(self, event):
        def get_all_children(item_):
            items_ = list()
            items_.append(item_['uuid'])
            try:
                for child in item_['children']:
                    items_.extend(get_all_children(child))
            except KeyError:
                pass
            return items_

        super(SelectedTreeView, self).mouseMoveEvent(event)
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.highlight.emit([])
        item = self.model().data(index, QtCore.Qt.UserRole)
        if item is not None:
            items = get_all_children(item)
            self.highlight.emit(items)
        else:
            self.highlight.emit([])

    def leaveEvent(self, event):
        super(SelectedTreeView, self).leaveEvent(event)
        self.highlight.emit([])

    def setModel(self, model):
        if self.model() is not None:
            self.model().layoutChanged.disconnect(self.clearSelection)
        super(SelectedTreeView, self).setModel(model)
        model.layoutChanged.connect(self.clearSelection)

    def _handle_remove_items(self):
        index_list = self.selectedIndexes()
        self.model().remove_items(index_list)


class SelectedModel(QtCore.QAbstractListModel):
    """Data model for selected node tree view."""

    def __init__(self, central_data_model, parent=None):
        super(SelectedModel, self).__init__(parent)
        self._central_data_model = central_data_model
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def mimeData(self, index_list):
        data = QtCore.QMimeData()
        uuid_list = [
            {'uuid': self.data(index, QtCore.Qt.UserRole)['uuid'],
             'instance': UNIQUE_INSTANCE}
            for index in index_list if index.isValid()]
        byte_array = QtCore.QByteArray(json.dumps(uuid_list))
        data.setData(MIME_SELECTED_ITEM, byte_array)
        return data

    def mimeTypes(self):
        return [MIME_AVAILABLE_NODE, MIME_SELECTED_ITEM]

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def dropMimeData(self, mime_data, drop_action, row, column, parent_index):
        if drop_action == QtCore.Qt.IgnoreAction:
            return True

        if column > 0:
            return False

        if row != -1:
            begin_row = row
        elif parent_index.isValid():
            begin_row = parent_index.row()
        else:
            begin_row = self.rowCount(QtCore.QModelIndex())

        if mime_data.hasFormat(MIME_AVAILABLE_NODE):
            # Dropping something from the set of available nodes.
            package_list = json.loads(
                mime_data.data(MIME_AVAILABLE_NODE).data().decode('ascii'))
            uuid_list = [x['uuid'] for x in package_list
                         if x['instance'] == UNIQUE_INSTANCE]
            if len(uuid_list) == 0:
                return False
            end_row = begin_row + len(uuid_list)
            self.beginInsertRows(parent_index, begin_row, end_row - 1)
            for row_index, node_uuid in zip(range(begin_row, end_row),
                                            uuid_list):
                self._central_data_model.move_node_to_selected(
                    node_uuid, row_index)
            self.endInsertRows()

        if mime_data.hasFormat(MIME_SELECTED_ITEM):
            # Moving node among the set of selected nodes.
            package_list = json.loads(
                mime_data.data(MIME_SELECTED_ITEM).data())
            uuid_list = [x['uuid'] for x in package_list
                         if x['instance'] == UNIQUE_INSTANCE]
            if len(uuid_list) == 0:
                return False
            self.layoutAboutToBeChanged.emit()
            self._central_data_model.move_uuids(uuid_list, begin_row)
            self.layoutChanged.emit()

        return True

    def insertRow(self, row, parent_index):
        return True

    def insertRows(self, row, count, parent_index):
        return True

    def removeRow(self, row, parent_index):
        return True

    def removeRows(self, row, count, parent_index):
        return True

    def data(self, index, role):
        if not index.isValid():
            return None

        uuid = self._central_data_model.selected_uuids[index.row()]
        item = self._central_data_model.uuid_to_item[uuid]
        if role == QtCore.Qt.DisplayRole:
            return item['name']
        elif role == QtCore.Qt.DecorationRole:
            return self._central_data_model.widget_manager.icon(uuid)
        elif role == QtCore.Qt.UserRole:
            return item
        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        uuid = self._central_data_model.selected_uuids[index.row()]
        item = self._central_data_model.uuid_to_item[uuid]
        if item is None:
            return QtCore.Qt.NoItemFlags
        return (QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsDragEnabled |
                QtCore.Qt.ItemIsEnabled)

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            return 'header'

    def rowCount(self, index):
        return len(self._central_data_model.selected_uuids)

    def remove_items(self, index_list):
        uuid_list = [self._central_data_model.selected_uuids[index.row()]
                     for index in index_list if index.isValid()]
        self.layoutAboutToBeChanged.emit()
        self._central_data_model.remove_top_level_uuids(uuid_list)
        self.layoutChanged.emit()


class WaitForData(QtCore.QObject):

    data_ready = QtCore.Signal(six.text_type)
    data_blocked = QtCore.Signal(six.text_type)
    raise_window = QtCore.Signal()

    def __init__(self, socket_bundle, parent=None):
        super(WaitForData, self).__init__(parent)
        self._socket_bundle = socket_bundle
        self._comm = message_util.QtMessageReader(
            socket_bundle.socket, parent=self)
        self._comm.received.connect(self.handle_input)
        self._uuids_done = set()
        self._uuids_requested = set()

    def put_request(self, msg):
        self._reqs.put(msg)

    def handle_input(self, msgs):
        for msg in msgs:
            if msg.type == message.DataReadyMessage:
                self._uuids_done.add(msg.data)
                self.data_ready.emit(msg.data)
            elif msg.type == message.DataBlockedMessage:
                self.data_blocked.emit(msg.data)
            elif msg.type == message.RaiseWindowMessage:
                self.raise_window.emit()

    def request_data(self, msg):
        if msg.type in (message.DataRequestMessage,
                        message.StatusDataRequestMessage):
            uuid = msg.data
            self._uuids_requested.add(uuid)
            self._socket_bundle.socket.write(
                self._socket_bundle.output_func(msg))
        else:
            self._socket_bundle.socket.write(
                self._socket_bundle.output_func(msg))


class WizardReadyPage(QtGui.QWizardPage):
    def __init__(self, n, ntot, item, reqs, cdm, parent=None):
        super(WizardReadyPage, self).__init__(parent)
        self._item = item
        self._cdm = cdm
        self._reqs = reqs
        self._layout = QtGui.QVBoxLayout()
        self.setTitle('{} ({}/{})'.format(item['name'], n, ntot))
        self.setLayout(self._layout)
        self.setCommitPage(True)
        self._dirty = False

    def initializePage(self):
        self._widget = self._cdm.widget_manager.widget(self._item['uuid'])
        if self._widget is None:
            self._widget = LabelParameterWidget(
                'Configuration could not be shown. '
                'This can prevent further configuration.')
        else:
            self._dirty = True
            self._widget.valid_changed.connect(self.completeChanged)
            self.completeChanged.emit()
        self._layout.addWidget(self._widget)
        self.wizard().initialize_page(self)

    def validatePage(self):
        is_complete = self.isComplete()
        if is_complete:
            self._cdm.collect_parameters()
            self._reqs(message.AggConfigUpdateMessage(
                clean_flow_info(self._cdm.flow_info)))
        return is_complete

    def isComplete(self):
        if self._dirty:
            return self._widget.valid or False
        return True

    def widget(self):
        return self._widget

    def cleanup(self):
        if self._dirty:
            self._widget.valid_changed.disconnect(self.completeChanged)
            self._widget.cleanup()
            self._dirty = False


class NullSignal(object):
    def connect(self, *args, **kwargs):
        pass

    def disconnect(self, *args, **kwargs):
        pass


class NullParameterMixin(object):
    valid_changed = NullSignal()

    def parameters_changed(self):
        return False

    def cleanup(self):
        pass

    @property
    def valid(self):
        return True


class LabelParameterWidget(NullParameterMixin, QtGui.QLabel):
    pass


class TabParameterWidget(NullParameterMixin, QtGui.QTabWidget):
    valid_changed = QtCore.Signal()

    def __init__(self):
        super(TabParameterWidget, self).__init__()

    def parameters_changed(self):
        return any(w.parameters_changed() for w in self.widgets())

    def addTab(self, widget, *args):
        res = super(TabParameterWidget, self).addTab(widget, *args)
        widget.valid_changed.connect(self.valid_changed)
        return res

    @property
    def valid(self):
        return all(widget.valid for widget in self.widgets())

    def widgets(self):
        return (self.widget(i) for i in range(self.count()))

    def cleanup(self):
        for widget in self.widgets():
            widget.cleanup()
            widget.valid_changed.disconnect(self.valid_changed)


class FailedParameterWidget(NullParameterMixin, QtGui.QWidget):
    def __init__(self, parent=None):
        super(FailedParameterWidget, self).__init__(parent)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtGui.QLabel('Invalid'))
        layout.setAlignment(QtCore.Qt.AlignCenter)


class WizardProgressPage(QtGui.QWizardPage):
    def __init__(self, n, ntot, item, reqs, parent=None):
        super(WizardProgressPage, self).__init__(parent)
        self._reqs = reqs
        self._uuid = item['uuid']
        self._item = item
        layout = QtGui.QVBoxLayout()
        self._label = QtGui.QLabel('Executing previous nodes...')
        layout.addWidget(self._label)
        self._progressbar = QtGui.QProgressBar()
        # Only indicate that we are busy, no specific progress:
        self._progressbar.setRange(0, 0)
        layout.addWidget(self._progressbar)
        self.setLayout(layout)
        self.setTitle('{} ({}/{})'.format(item['name'], n, ntot))
        self._is_complete = False
        self.setCommitPage(True)
        self._timer = QtCore.QTimer(parent=self)
        self._timer.setInterval(500)
        self._dirty = False

    def initializePage(self):
        self.completeChanged.connect(self.commit_page)
        self._reqs(message.DataRequestMessage(self._uuid))
        self._timer.timeout.connect(self._ask_for_data)
        self._timer.start()
        self._dirty = True
        self.wizard().initialize_page(self)

    def isComplete(self):
        return self._is_complete

    def set_complete(self, uuid):
        if uuid == self._uuid:
            if not self._is_complete:
                self._is_complete = True
            self.completeChanged.emit()

    def set_blocked(self, uuid):
        self.cleanup()
        self._label.setText(
            'WARNING: Execution is blocked and cannot proceed!\n\n'
            'Close this configuration and fix the cause of any previous '
            'node execution errors or invalid configurations\n'
            'before attempting to re-configure.\n')

    def commit_page(self):
        if self is self.wizard().currentPage() and self.isComplete():
            self.cleanup()
            # QtGui.QWizard.next(), not an iterator.
            self.wizard().next()

    def widget(self):
        return None

    def cleanup(self):
        if self._dirty:
            self.completeChanged.disconnect(self.commit_page)
            self._timer.timeout.disconnect(self._ask_for_data)
            self._timer.stop()
            self._dirty = False

    def _ask_for_data(self):
        self._reqs(message.StatusDataRequestMessage(self._uuid))


class WizardBuilder(object):
    """Wizard view style view for aggregated nodes."""

    lazy = True

    @staticmethod
    def build(cdm, wfdthread):
        selected = cdm.selected_node_uuids_recursive()

        def page_factory(n, item):
            page = WizardReadyPage(n, ntot, item, wfdthread.request_data, cdm)
            progress = WizardProgressPage(
                n, ntot, item, wfdthread.request_data)
            wfdthread.data_ready.connect(progress.set_complete)
            return [progress, page]

        def extract_widgets_from_selected_items(item_dict):
            """
            Extract widgets from selected items in the user defined
            grouping structure.
            """
            result = []

            for item in item_dict['nodes']:
                uuid = item['uuid']

                if uuid in selected:
                    if not cdm.widget_manager.has_no_parameters(uuid):
                        result.append((cdm.uuid_to_item[uuid]))

            for item in item_dict['flows']:
                result.extend(extract_widgets_from_selected_items(item))

            return result

        items = extract_widgets_from_selected_items(cdm.flow_structure)
        items.sort(key=lambda x: x['level'])

        wfdthread.start()
        wizard = QtGui.QWizard()
        ntot = len(items)

        for n, item in enumerate(items, 1):
            for page in page_factory(n, item):
                wizard.addPage(page)

        return wizard

    @staticmethod
    def disassemble(widget):
        # Removes all widgets, but does not delete them.
        # widget.clear()
        pass


class TabBuilder(object):
    """Tab view style view for aggregated nodes."""

    lazy = False

    @staticmethod
    def build(central_data_model, wfdthread):

        def extract_widgets_from_selected_items(selected_uuids):
            """
            Extract widgets from selected items in the user defined
            grouping structure.
            """
            wm = central_data_model.widget_manager

            # Don't use a TabWidget if there is only one child widget.
            if len(selected_uuids) == 1:
                return wm.widget(selected_uuids[0])

            group_tab_widget = TabParameterWidget()
            for i, uuid in enumerate(selected_uuids):
                failed = False
                widget = wm.widget(uuid)
                if (wm.is_required_input_data_missing(uuid) or
                        wm.has_no_parameters(uuid)):
                    failed = True
                    widget = None
                if widget is None:
                    widget = FailedParameterWidget()
                    failed = True
                index = group_tab_widget.addTab(
                    widget, wm.icon(uuid),
                    format_display_string(wm.name(uuid)))
                group_tab_widget.setTabToolTip(
                    index, format_display_string(wm.name(uuid)))

                # Disable tabs which are not valid.
                ok, reason = wm.widget_ok(uuid)
                group_tab_widget.setTabEnabled(index, ok and not failed)
                if not ok:
                    group_tab_widget.setTabToolTip(index, reason)
                    # Also print a warning.
                    sywarn("{}: {}".format(wm.name(uuid), reason))

                # Try to select a valid default tab.
                if ok and not failed:
                    current_index = group_tab_widget.currentIndex()
                    if not group_tab_widget.isTabEnabled(current_index):
                        group_tab_widget.setCurrentIndex(i)

            return group_tab_widget

        widget_ = extract_widgets_from_selected_items(
            central_data_model.selected_uuids)
        return widget_

    @staticmethod
    def disassemble(widget):
        # Removes all widgets, but does not delete them.
        widget.clear()
