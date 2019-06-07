import json
import threading
from contextlib import contextmanager
from typing import Iterator, Tuple

import numpy as np
import pandas as pd
from google.protobuf.json_format import MessageToJson

from treelab.event_handling.event_handler import *
from treelab.event_handling.listenable import *
import time
from treelab.consts import UpdateAction, DatePattern, DateFormatter, FieldTypeMap
from treelab.helper import generate_id
from functools import wraps
from treelab.utils.misc_utils import get_event_identifier
from treelab.utils.decorator_utils import wait_for_first_event
from datetime import datetime, timedelta
import re
from treelab.utils.sleep_cycle_utils import cycle, dormancy
from treelab.config import create_sleep_time


class Treelab:
    @staticmethod
    def add_workspace(workspace_name: str):
        return Workspace(name=workspace_name)

    @staticmethod
    def workspace(workspace_id: str):
        return Workspace(workspace_id=workspace_id)

    @staticmethod
    def get_workspace(workspace_id: str, workspace_name: str = ''):
        return Workspace(workspace_id=workspace_id, name=workspace_name)

    @staticmethod
    def get_all_workspaces():
        return [Treelab.get_workspace(res.id, res.name) for res in TreeLabClient.get_all_workspaces().result]


class _TreelabObject(BasicListenable):
    def __init__(self):
        super().__init__(None)
        self._id = "default_id"
        self._name = "default_name"

    @property
    def id(self):
        return self._id

    @property
    def workspace(self):
        return self._workspace

    @property
    def name(self):
        return self._name

    @property
    @abstractmethod
    def data(self):
        raise NotImplementedError('Data not implemented in '.format(self.__class__))

    @property
    def __repr_fields__(self):
        raise NotImplementedError

    @abstractmethod
    def _get_event_id(self, event: EventPayload):
        return event.workspaceId

    def should_be_listened(self, event: EventPayload, listener: Listener):
        if self.id == self._get_event_id(event):
            return True
        return False

    def __repr__(self):
        items = {k: self.__dict__[k] for k in self.__repr_fields__}
        items = dict([('object_type', self.__class__.__name__)] + list(items.items()))
        return str(items)


class Workspace(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'topic'}

    def __init__(self, workspace_id=None, name="", topic="#"):
        super().__init__()
        self.topic = topic
        self._name = name
        self._id = self._create_workspace(workspace_id=workspace_id)
        self._setup_init_subscription()
        self._workspace = self

    @cycle(event_name='workspace')
    def _create_workspace(self, workspace_id: str) -> str:
        if not workspace_id:
            workspace_id = TreeLabClient.create_workspace(CreateWorkspaceInput(name=self.name)).id
            time.sleep(create_sleep_time)
            return workspace_id
        else:
            if not self.name:
                workspace_projection = TreeLabClient.get_workspace(GetWorkspaceInput(id=workspace_id))
                self._name = workspace_projection.name
            return workspace_id

    def _setup_init_subscription(self):
        subscription_input = WorkspaceSubscriptionInput(workspaceId=self.id, topic=self.topic)
        self._event_handler = EventHandler(subscription_input)

    @property
    def event_handler(self) -> EventHandler:
        return self._event_handler

    def register(self, listener: Union[Listener, Callable[[EventPayload], Any]], thread_num: int = 0):
        """
        Register a listener to event handler, the listener are in type of either function that takes an EventPayload
        as parameter, or a Listener, you can specify whether to run this task on a new thread by the parameter
        on_new_thread
        :param listener:
        :param thread_num:
        :return:
        """
        listener = self._get_real_listener(listener)
        listener._thread_num = thread_num
        self.event_handler.register(listener=listener)

    def register_list(self, listeners: List[Union[Listener, Callable[[EventPayload], Any]]]):
        """
        Register a list of listeners to event handler
        :param listeners:
        :return:
        """
        for listener in listeners:
            self.register(listener)

    def _get_real_listener(self, listener: Union[Listener, Callable[[EventPayload], Any]]) -> Listener:
        if isinstance(listener, Callable):
            listener = FunctionListener(listener, self.event_handler.get_new_listener_name())

        return listener

    def get_core(self, core_id: str):
        """
        Get a core based on core_id
        :param core_id:
        :return:
        """
        return Core(workspace=self, core_id=core_id, name='')

    def get_cores_by_name(self, core_name: str) -> list:
        """
        get cores by core_name
        :param core_name:
        :return:
        """
        cores = [core for core in self.get_all_cores() if core.name == core_name]
        return cores

    @cycle('get_all_cores')
    def get_all_cores(self):
        cores = TreeLabClient.get_all_cores(GetCoresInput(workspaceId=self.id))
        return [self.get_core(core.id) for core in cores.result]

    def core(self, core_id: str):
        """
        Get a core based on core_id, equivalent to get_core
        :param core_id:
        :return:
        """
        return self.get_core(core_id)

    def add_core(self, core_name: str, color: CoreColor = CoreColor.lightRed, icon: Icon = Icon.briefcase):
        """
        Add a core with core_name, and color and icon as option
        :param core_name:
        :param color:
        :param icon:
        :return:
        """
        return Core(workspace=self, name=core_name, color=color, icon=icon)

    def dispose(self):
        """
        Closing the subscription streams created by grpc
        :return:
        """
        self.event_handler.dispose()

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        if event.eventName.split('.')[-1] == 'CellCreated':
            return event.coreCreatedDto.workspaceId
        else:
            return event.workspaceId


class Core(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'icon', 'color'}

    def __init__(self, name: str, core_id: str = None, workspace: Workspace = None,
                 color: CoreColor = CoreColor.lightBlack, icon: Icon = Icon.book):
        super().__init__()
        self._name = name
        self.color = color
        self.icon = icon
        self.tables = {}
        self._id = self._add_core(core_id, workspace)

    @cycle('core')
    def _add_core(self, core_id: str, workspace: Workspace):
        if workspace:
            self._workspace = workspace
            if core_id:
                core_projection = TreeLabClient.get_core(
                    GetCoreInput(workspaceId=self.workspace.id, coreId=core_id))
                self._name = core_projection.name
                self.color = CoreColor(core_projection.color)
                self.icon = Icon(core_projection.icon)
                return core_id
            else:
                add_core_input = AddCoreInput(workspaceId=self.workspace.id, coreName=self.name,
                                              color=self.color.value, icon=self.icon.value)
                core_id = TreeLabClient.add_core(add_core_input, workspace_id=self.workspace.id,
                                                 wait_till_complete=True).id
                time.sleep(create_sleep_time)
            return core_id
        else:
            raise ValueError("You need to get/create the core from the workspace!")

    def remove_core(self):
        remove_core_input = RemoveCoreInput(workspaceId=self.workspace.id, coreId=self.id)
        core_id = TreeLabClient.remove_core(remove_core_input)
        return core_id

    def update_core(self, core_name: str, color: CoreColor = CoreColor.lightBlack, icon: Icon = Icon.book):
        update_core_input = UpdateCoreInput(workspaceId=self.workspace.id, coreName=core_name, color=color.value,
                                            icon=icon.value)
        core_id = TreeLabClient.update_core(update_core_input)
        return core_id

    def add_table_with_content(self, table_name: str, view_name: str, view_type: ViewType,
                               column_config_inputs: List[ColumnConfigInput],
                               data_matrix: Union[List[List], np.array, pd.DataFrame]):

        """
        Add a table with content in type of TableContent
        :param table_name:
        :param view_name:
        :param view_type:
        :param column_config_inputs:
        :param data_matrix:
        :return:
        """
        table = self.add_table(table_name=table_name, default_view=False, default_column_row=False)
        view_id = table.add_view(view_name=view_name, view_type=view_type).id

        if isinstance(data_matrix, List):
            if len(data_matrix) == 0:
                raise ValueError('The size of the data matrix must not be zero')
            data_matrix = np.array(data_matrix)

        n_rows, n_cols = data_matrix.shape
        rows = table.add_rows(n_rows=n_rows)

        columns = table.add_columns(column_configs=column_config_inputs)
        cells = table.get_cells(rows, columns, mode='intersection') \
            .reshape(data_matrix.shape)
        cells.update(data_matrix)

        return table, view_id

    def get_table(self, table_id: str):
        """
        Get table from table_id
        :param table_id:
        :return:
        """
        table = Table(table_id=table_id, core=self)

        return table

    def table(self, table_id: str):
        """
        Get table from table_id, equivalent to get_table
        :param table_id:
        :return:
        """
        return self.get_table(table_id)

    def get_tables_by_name(self, table_name: str):
        tables = [table for table in self.get_all_tables() if table.name == table_name]
        return tables

    @cycle('get_all_tables')
    def get_all_tables(self):
        get_tables_input = GetTablesInput(workspaceId=self.workspace.id, coreId=self.id)
        tables = TreeLabClient.get_all_tables(get_tables_input)
        all_tables = [self.get_table(table.id) for table in tables.result]
        return all_tables

    def add_table(self, table_name: str, default_view: bool = True, default_column_row: bool = False):

        """
        Create a table based on table_name
        not specified
        :param table_name:
        :param default_view:bool
                    if true,add view,else not add view
        :return:
        """
        table = Table(name=table_name, core=self)
        if default_view:
            table.add_view(view_name='Default View')
            if default_column_row:
                table.add_column_text(field_name="Default Column 1")
                table.add_column_text(field_name="Default Column 2")
                table.add_row()
        return table

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        return event.coreId

    def snapshots(self):
        """
        add core snapshots method
        :return:
        """

        tables = self.get_all_tables()
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        core = self.workspace.add_core(core_name='-'.join([self.name, local_time]), color=self.color,
                                       icon=self.icon)
        # Get the sequential index of table_id and table in the original core, such as
        # {'tblb580a4b6688459f2': 0, 'tblb580a4b70d8cf590': 1}
        # table_id_dict = {table.id: i for i, table in enumerate(tables)}
        all_dict = {}
        remove_duplicate_reference = {}
        for i, table in enumerate(tables):
            if not table.data.views:
                continue
            # Get the column index and table_id of each RECORD_REFERENCE,such as
            # {0: 'tblb580a4b70d8cf590', 6: 'tblb580a4b70d8cf590'}
            column_configs = list(table.data.columns.values())
            column_index = {index: column_config.foreign_table_id for index, column_config in enumerate(column_configs)
                            if
                            FieldType(column_config.field_type) is FieldType.RECORD_REFERENCE}
            remove_duplicate_reference.update(
                {table.id: column_index})
            # Dataframe for each table
            df = table.data_frame()
            array = df.copy()
            for col_index, table_id in column_index.items():
                # Gets the index of the row of the current table，such as
                # {'rowb580a4b7870d4775': 0, 'rowb580a4b7c58ea840': 1}
                row_id_dict = {row_id: i for i, row_id in enumerate(self.get_table(table_id).data_frame().index.values)}
                data = array.iloc[:, col_index].map(
                    lambda x: {table_id: [row_id_dict[y['id']] for y in x] if x else ''})
                # (i,col_index) Represents the index number of the current table and the index with external keys,
                # such as (0,0), data.values means Data for each row，such as [{4: [0, 1]} {4: ''}] ,4 is The index
                # number of the associated table，[0,1] means The line number of this outer key table，Each dictionary
                # represents a line
                all_dict.update({(table.id, col_index): data.values})
        new_table_dict = {}
        for i, table in enumerate(tables):
            if not table.data.views:
                continue
            # Build table, build view, build row, dataframe is the dataframe of the original table
            table_name = table.name
            table_snapshots = core.add_table(table_name, default_view=False, default_column_row=False)
            view_ids = [table_snapshots.add_view(view_name=view.name, view_type=ViewType(view.view_type)).id for view in
                        list(table.data.views.values())]
            column_configs = list(table.data.columns.values())
            # columns = table_snapshots.add_columns(view_id=view_ids[0], column_configs=column_configs)
            rows = table_snapshots.add_rows(n_rows=len(table.data.rows.values()))
            df = table.data_frame()

            new_table_dict.update({table.id: (df, view_ids, column_configs, rows, table_snapshots)})
        for k, v in all_dict.items():
            # Replace the corresponding index in the new core according to the related tableid and rowid index in
            # the original core
            df, view_ids, column_configs, rows, table_snapshots = new_table_dict[k[0]]
            for i, refer in enumerate(v):
                for key, row_indexs in refer.items():
                    refer_rows = ','.join([new_table_dict[key][3][index].id for index in row_indexs]) if isinstance(
                        row_indexs, list) else ''
                    column_configs[k[1]].foreign_table_id = new_table_dict[key][4].id
                    df.iloc[i, k[1]] = refer_rows
            new_table_dict[k[0]] = (df, view_ids, column_configs, rows, table_snapshots)
        for k, v in new_table_dict.items():
            #  and finally add column and update cell
            df, view_ids, column_configs, rows, table_snapshots = v
            for key, value in remove_duplicate_reference[k].items():
                # df_, view_ids_, column_configs_, rows_, table_snapshots = v
                if value in remove_duplicate_reference:
                    indexs = []
                    for m, n in remove_duplicate_reference[value].items():
                        if n != '':
                            indexs.append(m)
                    if len(indexs) > 0:
                        new_table_dict[value][0].drop(new_table_dict[value][0].columns[indexs], axis=1, inplace=True)
                        indexs.reverse()
                        for i in indexs:
                            new_table_dict[value][2].pop(i)
                            remove_duplicate_reference[value][i] = ''
            if not column_configs:
                continue
            columns = table_snapshots.add_columns(column_configs=column_configs)
            cells = table_snapshots.get_cells(rows, columns, mode='intersection') \
                .reshape(df.shape)
            cells.update(df.values)
        return core


class Table(_TreelabObject):
    __repr_fields__ = {'_id'}

    def __init__(self, name: str = None, table_id: str = None, core: Core = None, online_update: bool = True):
        super().__init__()
        self._name = name
        self._id = self._add_table(table_id, core)
        self.online_update = online_update
        if self.online_update:
            self._register_online_listener()

    @staticmethod
    @cycle('update_data')
    def _update_data(table):
        get_table_input = GetTableInput(workspaceId=table.workspace.id,
                                        coreId=table.core.id, tableId=table.id)
        table_projection = TreeLabClient.get_table(get_table_input)
        table_dict = json.loads(MessageToJson(table_projection))
        table._data = _TableData(table=table, table_dict=table_dict)

    def _register_online_listener(self):
        class _TableListener(Listener[Table]):
            def run(self, event: EventPayload):
                # TODO
                # waiting for the update from treelab-api, the data through `GetTable` is not immediately available
                # though the event is already received, adding a sleep right now
                wait_for_first_event(event.workspaceId, event_name=get_event_identifier(event))
                for table in self.listenable_list:
                    Table._update_data(table)

        self._update_data(table=self)
        self.listen_to(_TableListener('table_listener_{}'.format(self.id)))

    @cycle('table')
    def _add_table(self, table_id: str, core: Core):
        if core:
            self.core = core
            self._workspace = self.core.workspace
            if table_id:
                table_projection = TreeLabClient.get_table(
                    GetTableInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=table_id))
                self._name = table_projection.name
                return table_id
            else:
                add_table_input = AddTableInput(workspaceId=self.workspace.id, coreId=self.core.id, tableName=self.name)
                table_id = TreeLabClient.add_table(add_table_input, workspace_id=self.workspace.id).id
                time.sleep(create_sleep_time)
                return table_id
        else:
            raise ValueError("You need to get/create the table from the core!")

    def data_frame(self, view_id: str = ''):
        """
        Initialize table data to form a DataFrame format and column name mapping
        :param view_id: If empty, the default is the data of the first view
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            view = self.get_views()[0]
        return view.data_frame

    def data_frames(self, view_ids: List[str] = None):
        """
        Convert the original view's data to a data_frame format，
        the index of the data_frame is the row id, and the column is the column id
        :param view_ids:
        :return: pandas.data_frame
        """
        data_frames = []
        if view_ids:
            data_frames = [self.data.view_datas.get(view_id).df for view_id in view_ids if
                           view_id in list(self.data.view_datas.keys())]
        else:
            view_datas = list(self.data.view_datas.values())
            if len(view_datas) > 0:
                data_frames = [view.df for view in view_datas]
        return data_frames

    def get_row(self, row_id: str, view_id: str = ''):
        """
        Get row by row_id
        :param row_id:
        :param view_id:
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        row = view.get_row(row_id)
        return row

    def row(self, row_id: str, view_id: str = ''):
        """
        Get row by row_id, equivalent to get_row
        :param row_id:
        :param view_id:
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        return view.get_row(row_id=row_id)

    def add_row(self):
        """
        Add a single row to the table
        :return:
        """
        row = Row(table=self)
        return row

    def add_rows(self, n_rows: int):
        """
        Add rows with number
        :param n_rows:
        :return:
        """
        if n_rows <= 0:
            raise ValueError('n_rows has to be a number larger than 0')
        rows = RowArray(parent_object=self, objects=[self.add_row() for _ in range(n_rows)],
                        workspace=self.workspace)

        return rows

    def get_rows(self, row_ids: List[str] = None, view_id: str = ''):
        """
        Get rows by row_ids, if row_ids are not specified, get all rows from the table,
        :param row_ids:
        :param view_id
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        row_array = view.get_rows(row_ids)
        return row_array

    def get_cell(self, row, column, view_id: str = ''):
        """
        Get a single cell from known row and column
        :param row:
        :param column:
        :param view_id:
        :param
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        cell = view.get_cell(row, column)
        return cell

    def get_cells(self, rows: List = None, columns: List = None, mode: str = 'all', view_id: str = ''):
        """
        Get cells from rows and columns
        :param rows:
        :param columns:
        :param mode:
            if mode == intersection:
                returns the cells on the intersection of all rows and columns
            if mode == pair:
                returns the cells based on row/column pairs, in this case, the size
                of rows has to be equal to the size of column
            if mode == all:
                return all cells under this table, rows and columns will be ignored in this case
        :param view_id:
        :return: cells: CellCollection
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        cell_array = view.get_cells(rows, columns, mode)
        return cell_array

    def add_column(self, field_type: FieldType = None, field_name: str = None, order: int = 1,
                   foreign_table_id: str = None,
                   column_config_input: ColumnConfigInput = None, default_number: float = 0.0,
                   precision: int = 1, choices: List[List[Union[Choice, Any]]] = [], date_format: DateFormat = None,
                   include_time: bool = True,
                   time_format: TimeFormat = None, use_gmt: bool = True):
        """
        Add a single column or column_config_input as as parameter which includes the four mentioned above
        :param field_type:
        :param field_name:
        :param order:
        :param foreign_table_id:
        :param column_config_input:
        :param default_number:
                    FieldType is NUMBER
        :param precision:
                    FieldType is NUMBER
        :param choices:
                    List contains two parameters, name and color. Name is of type STR and color is of type color
                    FieldType is MULTI_SELECT or SELECT
                    example:
                        [['a',Color.lightRed],
                        ['b',Color.pink]]
        :param date_format:
                    FieldType is DATETIME
        :param include_time:
                    FieldType is DATETIME
        :param time_format:
                    FieldType is DATETIME
        :param use_gmt:
                    FieldType is DATETIME
        :return:
        """
        if column_config_input:
            column = Column(table=self, field_type=FieldType(column_config_input.type),
                            field_name=column_config_input.name,
                            order=column_config_input.order,
                            foreign_table_id=column_config_input.foreignTableId,
                            default_number=column_config_input.defaultNumber,
                            precision=column_config_input.precision, choices=column_config_input.choices,
                            date_format=DateFormat(
                                column_config_input.dateFormat) if column_config_input.dateFormat else '',
                            include_time=column_config_input.includeTime,
                            time_format=TimeFormat(
                                column_config_input.timeFormat) if column_config_input.timeFormat else '',
                            use_gmt=column_config_input.useGMT)
            self._update_data(self)
            return column
        else:
            if field_type is None or field_name is None:
                raise ValueError('Field type, field name and order cannot be None')
            column = Column(table=self, field_type=field_type, field_name=field_name, order=order,
                            foreign_table_id=foreign_table_id, default_number=default_number,
                            precision=precision, choices=choices, date_format=date_format,
                            include_time=include_time,
                            time_format=time_format, use_gmt=use_gmt)
            self._update_data(self)
            return column

    def add_column_text(self, field_name: str, order: int = 1):
        return self.add_column(field_type=FieldType.TEXT, field_name=field_name,
                               order=order)

    def add_column_datetime(self, field_name: str, order: int = 1, include_time: bool = True,
                            use_gmt: bool = True, date_format: DateFormat = DateFormat.FRIENDLY,
                            time_format: TimeFormat = TimeFormat.TWELVE_HOUR):
        return self.add_column(field_type=FieldType.DATETIME,
                               field_name=field_name,
                               order=order,
                               date_format=date_format,
                               include_time=include_time, time_format=time_format,
                               use_gmt=use_gmt)

    def add_column_recode_reference(self, field_name: str, foreign_table_id: str, order: int = 1):
        return self.add_column(field_type=FieldType.RECORD_REFERENCE,
                               field_name=field_name, order=order,
                               foreign_table_id=foreign_table_id)

    def add_column_number(self, field_name: str, order: int = 1, default_number: int = 12,
                          precision: int = 1):
        return self.add_column(field_type=FieldType.NUMBER, field_name=field_name,
                               order=order,
                               default_number=default_number, precision=precision)

    def add_column_multi_select(self, field_name: str, choices: List[List[Union[Choice, Any]]],
                                order: int = 1):
        return self.add_column(field_type=FieldType.MULTI_SELECT,
                               field_name=field_name,
                               order=order,
                               choices=choices)

    def add_column_select(self, field_name: str, choices: List[List[Union[Choice, Any]]],
                          order: int = 1):
        return self.add_column(field_type=FieldType.SELECT,
                               field_name=field_name,
                               order=order,
                               choices=choices)

    @staticmethod
    def column_config_input_for_record_reference(column_name: str, foreign_table_id: str,
                                                 order: int = 1) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_record_reference
        :param column_name:
        :param foreign_table_id:
        :param order:
        :return:
        """
        return ColumnConfigInput(type=FieldType.RECORD_REFERENCE.value, name=column_name, order=order,
                                 foreignTableId=foreign_table_id)

    @staticmethod
    def column_config_input_for_text(column_name: str, order: int = 1) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_text
        :param column_name:
        :param order:
        :return:
        """
        return ColumnConfigInput(type=FieldType.TEXT.value, name=column_name, order=order)

    @staticmethod
    def column_config_input_for_datetime(column_name: str, order: int = 1,
                                         date_format: DateFormat = DateFormat.FRIENDLY,
                                         include_time: bool = True,
                                         time_format: TimeFormat = TimeFormat.TWELVE_HOUR,
                                         use_gmt: bool = True) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_datetime
        :param column_name:
        :param order:
        :param date_format:
        :param include_time:
        :param time_format:
        :param use_gmt:
        :return:
        """
        return ColumnConfigInput(type=FieldType.DATETIME.value, name=column_name, order=order,
                                 dateFormat=date_format.value,
                                 includeTime=include_time, timeFormat=time_format.value,
                                 useGMT=use_gmt)

    @staticmethod
    def column_config_input_for_number(column_name: str, order: int = 1, default_number: int = 12,
                                       precision: int = 1) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_number
        :param column_name:
        :param order:
        :param default_number:
        :param precision:
        :return:
        """
        return ColumnConfigInput(type=FieldType.NUMBER.value, name=column_name, order=order,
                                 defaultNumber=default_number, precision=precision)

    @staticmethod
    def column_config_input_for_multi_select(column_name: str, choices: List[List[Union[Choice, Any]]],
                                             order: int = 1) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_multi_select
        :param column_name:
        :param choices:
        :param order:
        :return:
        """
        return ColumnConfigInput(type=FieldType.MULTI_SELECT.value, name=column_name, order=order,
                                 choices=choices)

    @staticmethod
    def column_config_input_for_select(column_name: str, choices: List[List[Union[Choice, Any]]],
                                       order: int = 1) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_select
        :param column_name:
        :param choices:
        :param order:
        :return:
        """
        return ColumnConfigInput(type=FieldType.SELECT.value, name=column_name, order=order,
                                 choices=choices)

    def add_columns(self, column_configs: List[Union[ColumnConfigInput, Any]]):
        """
        Add columns with List of column configs
        :param column_configs:
        :return:
        """
        if isinstance(column_configs[0], Column):
            columns = ColumnArray(self,
                                  [self.add_column(field_type=column_config.field_type,
                                                   field_name=column_config.name, order=column_config.order,
                                                   foreign_table_id=column_config.foreign_table_id,
                                                   default_number=column_config.default_number,
                                                   precision=column_config.precision,
                                                   choices=column_config.choices,
                                                   date_format=DateFormat(
                                                       column_config.date_format) if column_config.date_format else '',
                                                   include_time=column_config.include_time,
                                                   time_format=TimeFormat(
                                                       column_config.time_format) if column_config.time_format else '',
                                                   use_gmt=column_config.use_gmt)
                                   for column_config in
                                   column_configs], self.workspace)
        elif isinstance(column_configs[0], ColumnConfigInput):
            columns = ColumnArray(self,
                                  [self.add_column(column_config_input=column_config) for column_config
                                   in
                                   column_configs],
                                  self.workspace)
        else:
            columns = None
        return columns

    def get_column_by_id(self, col_id: str, view_id: str = ''):
        """
        Get a single column by column id from the table

        :param col_id:
        :param view_id:To distinguish different views under the table
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        column = view.get_column_by_id(col_id)
        return column

    def get_columns_by_name(self, field_name: str, view_id: str = ''):
        """
        Get a single column by field name from the table

        :param field_name:
        :param view_id:To distinguish different views under the table
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            # view = list(self.data.views.values())[0]
            view = self.get_views()[0]
        columns = view.get_columns_by_name(field_name)
        return columns

    def column(self, col_id: str, view_id: str = ''):
        """
        Get a single column by column id from the table, equivalent to get_column_by_id
        :param col_id:
        :param view_id:To distinguish different views under the table
        :return:
        """
        return self.get_column_by_id(col_id=col_id, view_id=view_id)

    def get_columns(self, col_ids: List[str] = None, mode: str = 'all', view_id: str = ''):
        """
        Get either columns by either column ids or all columns under the table
        :param col_ids:
        :param mode:
            if mode == 'id':
                return columns by col_ids
            if mode == 'all':
                return all columns under this table, col_ids, if passed, will be ignored in this case
        :param view_id:To distinguish different views under the table
        :return:
        """
        if view_id:
            view = self.get_view(view_id)
        else:
            view = self.get_views()[0]
            # view = list(self.data.views.values())[0]
        col_array = view.get_columns(col_ids, mode)
        return col_array

    def get_view(self, view_id: str):
        """
        Get a view from view_id
        :param view_id:
        :return:
        """
        view = self.data.views.get(view_id)
        return view

    def get_views(self, view_ids: List[str] = None, mode: str = 'all'):
        """
        Get views by a list of view_ids
        :param view_ids:
        :param mode:
        :return:
        """
        if mode == 'all':
            views = list(self.data.views.values())
        elif mode == 'id':
            if view_ids is None:
                raise ValueError('view_ids should not be None when mode equals id')
            views = [self.get_view(view_id=view_id) for view_id in view_ids]
        else:
            raise ValueError('{} mode is not supported, please select mode between id and all'.format(mode))

        return ViewArray(parent_object=self, objects=views, workspace=self.workspace)

    def get_views_by_name(self, name: str):
        views = self.get_views().select_by_name(name)
        return views

    def add_view(self, view_name, view_type: ViewType = ViewType.GRID):
        """
        Add a view to the table
        :param view_name:
        :param view_type:
        :return:
        """
        view = View(table=self, name=view_name, view_type=view_type)
        self._update_data(self)

        return view

    def update(self, data_matrix: Union[List[List], np.array, pd.DataFrame]):
        """
        Update table content with data_matrix
        The shape of cell_type_matrix and data_matrix must be consistent and used to verify the cell field type
        :param data_matrix:
        :return:
        """
        self.get_cells().update(data_matrix)

    @property
    def data(self):
        """
        Get the table data in _TableData
        :return:
        """

        if not self.online_update or not hasattr(self, '_data'):
            self._update_data(self)
        return self._data

    def _get_event_id(self, event: EventPayload):
        return event.tableId


class View(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'view_type'}

    def __init__(self, name: str, view_type: ViewType = ViewType.GRID, view_id: str = None,
                 table: Table = None):
        super().__init__()
        self._name = name
        self.view_type = view_type
        self._id = self._add_view(view_id=view_id, table=table)
        self.table = table

    def data(self):
        view = self.table.data.view_datas.get(self.id)
        return view

    @property
    def columns(self):
        return self.data().columns

    @property
    def rows(self):
        return self.data().rows

    @property
    def cells(self):
        return self.data().cells

    @property
    def data_frame(self):
        """
        Initialize table data to form a DataFrame format and column name mapping
        :return:
        """
        df = self.data().df
        return df

    def _add_view(self, view_id: str, table: Table):
        if table:
            self.table = table
            self.core = self.table.core
            self._workspace = self.core.workspace
            if view_id:
                return view_id
            else:
                add_view_input = AddViewInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.table.id,
                                              view=ViewDefinitionInput(name=self.name, type=self.view_type.value))
                view_id = TreeLabClient.add_view(add_view_input, workspace_id=self.workspace.id,
                                                 wait_till_complete=True).id
                time.sleep(create_sleep_time)
                return view_id
        else:
            raise ValueError("You need to get/create the view from the table!")

    def _get_event_id(self, event: EventPayload):
        return event.viewId

    def get_columns(self, col_ids: List[str] = None, mode: str = 'all'):
        """
        Get either columns by either column ids or all columns under the table
        :param col_ids:
        :param mode:
            if mode == 'id':
                return columns by col_ids
            if mode == 'all':
                return all columns under this table, col_ids, if passed, will be ignored in this case
        :return:
        """
        if mode == 'all':
            columns = list(self.columns.values())
        elif mode == 'id':
            if col_ids is None:
                raise ValueError('col_ids should not be None when mode equals id')
            columns = [self.column(col_id=col_id) for col_id in col_ids]
        else:
            raise ValueError('{} mode is not supported, please select mode between id and all'.format(mode))

        col_array = ColumnArray(self, columns, self.workspace)

        return col_array

    def get_column_by_id(self, col_id: str):

        column = self.columns.get(col_id)

        return column

    def get_columns_by_name(self, field_name: str):
        """
        Get a single column by field name from the table

        :param field_name:
        :return:
        """
        columns = self.get_columns(mode='all').select_by_name(field_name)
        return columns

    def column(self, col_id: str):
        """
        Get a single column by column id from the table, equivalent to get_column_by_id
        :param col_id:
        :return:
        """
        return self.get_column_by_id(col_id=col_id)

    def get_row(self, row_id: str):
        """
        Get row by row_id
        :param row_id:
        :return:
        """
        row = self.rows.get(row_id)
        return row

    def row(self, row_id: str):
        return self.get_row(row_id=row_id)

    def get_rows(self, row_ids: List[str] = None):
        """
        Get rows by row_ids, if row_ids are not specified, get all rows from the table,
        :param row_ids:
        :return:
        """
        if row_ids:
            rows = [self.get_row(row_id=row_id) for row_id in row_ids]
        else:
            rows = list(self.rows.values())
        row_array = RowArray(parent_object=self, objects=rows, workspace=self.workspace)
        return row_array

    def get_cell(self, row, column):
        """
        Get a single cell from known row and column
        :param row:
        :param column:
        :param
        :return:
        """
        return Cell(self.table, self, row, column)

    def get_cells(self, rows: List = None, columns: List = None, mode: str = 'all'):
        """
        Get cells from rows and columns
        :param rows:
        :param columns:
        :param mode:
                    if mode == intersection:
                        returns the cells on the intersection of all rows and columns
                    if mode == pair:
                        returns the cells based on row/column pairs, in this case, the size
                        of rows has to be equal to the size of column
                    if mode == all:
                        return all cells under this table, rows and columns will be ignored in this case
        :return: cells: CellCollection
        """
        if (rows is None or columns is None) and mode != 'all':
            raise ValueError('rows and columns cannot be None for mode != all')

        if mode == 'intersection':
            cells = [Cell(self.table, self, row, column) for row in rows for column in columns]
        elif mode == 'pair':
            if len(rows) != len(columns):
                raise ValueError("The size of rows has to equal to the size of columns when all_cells are set as False")
            cells = [Cell(self.table, self, row, column) for row, column in zip(rows, columns)]
        elif mode == 'all':
            cells = list(self.data().cells.values())
        else:
            raise ValueError('{} mode is not supported, please select mode between intersection, pair and all'
                             .format(mode))

        return CellArray(self, cells, self.workspace)


class Row(_TreelabObject):
    __repr_fields__ = {'_id'}

    def __init__(self, row_id: str = None, table: Table = None, order: int = 1, view: View = None):
        super().__init__()
        self.order = order
        self._id = self._add_row(row_id, table)
        self.view = view

    def _add_row(self, row_id: str, table: Table):
        if table:
            self.table = table
            self.core = self.table.core
            self._workspace = self.core.workspace
            if row_id:
                return row_id
            else:
                add_row_input = AddRowInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.table.id)
                row_id = TreeLabClient.add_row(add_row_input, workspace_id=self.workspace.id,
                                               wait_till_complete=True).id
                time.sleep(create_sleep_time)
                return row_id
        else:
            raise ValueError("You need to get/create the row from the table!")

    def update(self, vector: Union[List, pd.Series], columns: List = None):
        if not columns:
            columns = list(self.table.data.columns.values())

        if len(columns) != len(vector):
            raise ValueError("The size of column_ids must equals to the size of row!")

        self.table.get_cells([self], columns, mode='intersection').update([vector])
        self.table._update_data(self.table)

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        return event.rowId


class Column(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'order', 'foreign_table_id', 'field_type'}

    def __init__(self, col_id: str = None, field_name: str = '', order: int = 0,
                 foreign_table_id: str = '',
                 table: Table = None, field_type: FieldType = FieldType.TEXT, default_number: float = 0.0,
                 precision: int = 1, choices: List[List[Union[Choice, Any]]] = [], date_format: DateFormat = None,
                 include_time: bool = True,
                 time_format: TimeFormat = None, use_gmt: bool = True, view: View = None):
        """
        :param col_id:
        :param field_name:
        :param order:
        :param foreign_table_id:
        :param table:
        :param field_type:
        :param default_number:
                    FieldType is NUMBER
        :param precision:
                    FieldType is NUMBER
        :param choices:
                    List contains two parameters, name and color. Name is of type STR and color is of type color
                    FieldType is MULTI_SELECT or SELECT
                    example:
                        [['a',Color.lightRed],
                        ['b',Color.pink]]
        :param date_format:
                    FieldType is DATETIME
        :param include_time:
                    FieldType is DATETIME
        :param time_format:
                    FieldType is DATETIME
        :param use_gmt:
        """
        super().__init__()
        self.field_type = field_type
        self.order = order
        self.foreign_table_id = foreign_table_id
        self.default_number = default_number
        self.precision = precision
        self.choices = self._get_choices(choices)
        self.date_format = date_format
        self.include_time = include_time
        self.time_format = time_format
        self.use_gmt = use_gmt
        self._name = field_name
        self._id = self._add_column(col_id, table)
        self.view = view

    @staticmethod
    def _get_choices(choices):
        if choices and isinstance(choices[0], Choice):
            return choices
        elif choices and isinstance(choices[0], dict):
            return [Choice(id=choice['id'], name=choice['name'], color=choice['color']) for choice in choices]
        return [Choice(id=generate_id(), name=choice[0], color=choice[1].value) for choice in choices]

    def _add_column(self, col_id: str, table: Table):
        if table:
            self.table = table
            self.core = self.table.core
            self._workspace = self.core.workspace
            if col_id:
                return col_id
            else:
                if self.field_type is FieldType.TEXT:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order)
                elif self.field_type is FieldType.DATETIME:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order,
                                                      dateFormat=self.date_format.value,
                                                      includeTime=self.include_time, timeFormat=self.time_format.value,
                                                      useGMT=self.use_gmt)
                elif self.field_type is FieldType.MULTI_SELECT or self.field_type is FieldType.SELECT:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order,
                                                      choices=self.choices)
                elif self.field_type is FieldType.NUMBER:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order,
                                                      defaultNumber=self.default_number, precision=self.precision)
                elif self.field_type is FieldType.RECORD_REFERENCE:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order,
                                                      foreignTableId=self.foreign_table_id)
                # elif self.field_type is FieldType.FORMULA:
                #     column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order,
                #                                       foreignTableId=self.foreign_table_id)
                # elif self.field_type is FieldType.LOOKUP:
                #     column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order,
                #                                       foreignTableId=self.foreign_table_id)
                # elif self.field_type is FieldType.MULTI_ATTACHMENT:
                #     column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, order=self.order)
                else:
                    raise ValueError('Not FieldType')

                add_col_input = AddColumnInput(workspaceId=self.workspace.id, coreId=self.core.id,
                                               tableId=self.table.id,
                                               columnConfig=column_config)
                col_id = TreeLabClient.add_column(add_col_input, workspace_id=self.workspace.id,
                                                  wait_till_complete=True).id
                time.sleep(create_sleep_time)
                return col_id
        else:
            raise ValueError("You need to get/create the column from the table!")

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        return event.columnId


class Cell(_TreelabObject):
    __repr_fields__ = {'_id'}

    def __init__(self, table: Table, view: View, row: Row, column: Column, value=None):
        """

        :param table:
        :param row:
        :param column:
        :param value:


        """
        super().__init__()
        self.table = table
        self.view = view
        self.core = self.table.core
        self._workspace = self.core.workspace
        self.row = row
        self.column = column
        self._value = value
        self._id = '{}:{}'.format(column.id, row.id)

    def get_value(self):
        if self._value:
            return self._value
        else:
            if self.view.cells:
                data = self.view.cells.get((self.row.id, self.column.id))
                return data.value if data else None

    @dormancy('cell_update')
    def update(self, value):
        """
        Update the value of the cell, the field_type can be inferred from self.row.field_type
        :param value:
                    column_type is FieldType.TEXT
        :return:
        """
        if self.column.field_type is FieldType.RECORD_REFERENCE:
            value = value.split(',')
            if isinstance(value, list):
                for row_id in value:
                    cell_value_input = CellValueInput(type=self.column.field_type.value, foreignRowId=row_id)
                    self._update_cell(UpdateAction.ADD_VALUE, cell_value_input)
        else:
            if self.column.field_type is FieldType.MULTI_SELECT:

                cell_value_input = CellValueInput(type=self.column.field_type.value, selectedItems=value)

            elif self.column.field_type is FieldType.SELECT:
                cell_value_input = CellValueInput(type=self.column.field_type.value, selectedItem=value)

            elif self.column.field_type is FieldType.TEXT:
                cell_value_input = CellValueInput(type=self.column.field_type.value, text=value)

            elif self.column.field_type is FieldType.NUMBER:
                cell_value_input = CellValueInput(type=self.column.field_type.value, number=float(value))

            elif self.column.field_type is FieldType.DATETIME:
                cell_value_input = CellValueInput(type=self.column.field_type.value, dateTime=_datetime_to_utc(value))
            else:
                raise ValueError('Not Cell_Type')
            self._update_cell(UpdateAction.SET_VALUE, cell_value_input)
            time.sleep(create_sleep_time)

    def _update_cell(self, action: UpdateAction, update_cell_input: UpdateCellInput):
        update_cell_input = UpdateCellInput(workspaceId=self.workspace.id, coreId=self.core.id,
                                            tableId=self.table.id, columnId=self.column.id,
                                            rowId=self.row.id,
                                            action=UpdateCellActionInput(type=action.value,
                                                                         value=update_cell_input))
        _ = TreeLabClient.update_cell(update_cell_input, workspace_id=self.workspace.id,
                                      wait_till_complete=True).id

    @property
    def data(self):
        return self.view.cells.get((self.row.id, self.column.id))

    @property
    def value(self):
        """
        Get the last updated value dict if there is any, this is not guaranteed to be the most updated value,
        for most updated data, using cell.data
        :return:
        """
        return self._value

    # @property
    # def text(self):
    #     """
    #     Get the last updated value dict if there is any, this is not guaranteed to be the most updated value,
    #     for most updated data, using cell.data
    #     :return:
    #     """
    #     return self.value['text']

    def _get_event_id(self, event: EventPayload):
        return '{}:{}'.format(event.columnId, event.rowId)


class _ViewDF:
    def __init__(self, rows=None, columns=None, cells=None, df=None):
        self.rows = rows
        self.columns = columns
        self.cells = cells
        self.df = df


class _TableData:
    def __init__(self, table: Table, table_dict: Dict):
        self.table = table
        self.table_dict = table_dict
        self._parse_dict(table_dict)
        self._parse_views()

    def _parse_views(self):
        """
        Initialize table data to form a DataFrame format and column name mapping
        :return:
        """
        self._view_datas = {}
        for view_id, data in self._views_dict.items():
            if 'rows' in data and 'columns' in data:
                row_ids = data.get('rows').keys()
                column_ids = data.get('columns').keys()
                content = []
                # if not row_ids or not column_ids:
                #     self._view_datas[view_id] = _ViewDF(df=pd.DataFrame())
                #     continue
                for row_id in row_ids:
                    cells = data.get('cells')
                    row_data = [
                        cells.get((row_id, column_id)).value if cells.get(
                            (row_id, column_id)) is not None else ''
                        for column_id in column_ids]
                    content.append(row_data)
                df_data = pd.DataFrame(data=content, index=row_ids, columns=column_ids)
                view_df = _ViewDF(columns=data.get('columns'), rows=data.get('rows'), cells=data.get('cells'),
                                  df=df_data)
                self._view_datas[view_id] = view_df

    def _parse_dict(self, table_dict: Dict):
        self._views_dict, self._views = {}, {}
        views = table_dict.get('views')
        if not views:
            return
        for view_dict in views:
            self._rows, self._columns, self._cells = {}, {}, {}
            view_id = view_dict['id']
            view_type = view_dict['type']
            view_name = view_dict['name']
            view = View(name=view_name, view_type=view_type, view_id=view_id, table=self.table)
            self.views[view_id] = view
            self._views_dict[view_id] = {}
            if 'columns' in view_dict:
                for column_dict in view_dict['columns']:
                    column_id = column_dict['id']
                    column_type = FieldType(column_dict['type'])
                    column_name = column_dict['name']
                    foreign_table_id, default_number, precision, choices, date_format, include_time, time_format, \
                    use_gmt = self._set_default_value()
                    if column_type in [FieldType.TEXT, FieldType.MULTI_ATTACHMENT]:
                        pass
                    elif column_type is FieldType.RECORD_REFERENCE:
                        foreign_table_id = column_dict['foreignTableId']
                    elif column_type is FieldType.NUMBER:
                        default_number = column_dict.get('defaultNumber')
                        precision = column_dict['precision']
                    elif column_type in [FieldType.SELECT, FieldType.MULTI_SELECT]:
                        choices = json.loads(column_dict['choices'])
                    elif column_type is FieldType.DATETIME:
                        date_format = column_dict['dateFormat']
                        include_time = column_dict.get('includeTime')
                        time_format = column_dict['timeFormat']
                        use_gmt = column_dict.get('useGMT')
                    else:
                        raise ValueError('Not FieldType')
                    column = Column(col_id=column_id, field_name=column_name,
                                    foreign_table_id=foreign_table_id,
                                    table=self.table, field_type=column_type, default_number=default_number,
                                    precision=precision, choices=choices, date_format=date_format,
                                    include_time=include_time,
                                    time_format=time_format, use_gmt=use_gmt, view=view)
                    self._columns[column_id] = column
            self._views_dict[view_id].update({'columns': self._columns})
            if 'rows' in view_dict:
                for row_dict in view_dict['rows']:
                    row_id = row_dict['id']
                    row = Row(row_id=row_id, table=self.table, view=view)
                    self._rows[row_id] = row
                    if 'cells' in row_dict:
                        for cell_dict in row_dict['cells']:
                            column_id = cell_dict['columnId']
                            column_type = FieldType(cell_dict.get('type'))
                            if column_type in [FieldType.SELECT, FieldType.MULTI_SELECT]:
                                value = json.loads(
                                    cell_dict.get(FieldTypeMap[column_type.value].value)) if cell_dict.get(
                                    FieldTypeMap[column_type.value].value) else []
                            elif column_type is FieldType.NUMBER:
                                value = cell_dict.get(FieldTypeMap[column_type.value].value, 0.0)
                            else:
                                value = cell_dict.get(FieldTypeMap[column_type.value].value)
                            cell = Cell(table=self.table, view=view, row=row, column=self._columns[column_id],
                                        value=value)
                            self._cells[row_id, column_id] = cell
            self._views_dict[view_id].update({'rows': self._rows, 'cells': self._cells})
        first_view_id = list(self._views.keys())
        if len(first_view_id) > 0:
            first_view = self._views_dict.get(first_view_id[0])
            self._rows = first_view.get('rows') if 'rows' in first_view else {}
            self._columns = first_view.get('columns') if 'columns' in first_view else {}
            self._cells = first_view.get('cells') if 'cells' in first_view else {}
        else:
            self._rows = {}
            self._columns = {}
            self._cells = {}

    @staticmethod
    def _set_default_value():
        foreign_table_id = ''
        default_number = 0.0
        precision = 1
        choices = []
        date_format = None
        include_time = True
        time_format = None
        use_gmt = True
        return foreign_table_id, default_number, precision, choices, date_format, include_time, time_format, use_gmt

    @property
    def cells(self) -> Dict:
        return self._cells

    @property
    def rows(self) -> Dict:
        return self._rows

    @property
    def views(self) -> Dict:
        return self._views

    @property
    def columns(self) -> Dict:
        return self._columns

    @property
    def view_datas(self) -> Dict:
        return self._view_datas

    @property
    def views_dict(self) -> Dict:
        return self._views_dict


class _TreelabObjectArray(Listenable, Generic[GenericType.PT, GenericType.T]):
    def __init__(self, parent_object: GenericType.PT, objects: List[GenericType.T], workspace):
        super().__init__(workspace)
        self._objects = objects
        self.parent_object = parent_object
        self._size = len(objects)

    def __iter__(self) -> Iterator[GenericType.T]:
        return self._objects.__iter__()

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self.parent_object, self._objects[item], self.workspace)
        else:
            if self.size == 0:
                raise ValueError('Cannot indexing an empty _TreelabObjectArray')
            return self._objects[item]

    def __contains__(self, obj: GenericType.T) -> bool:
        return obj in self._objects

    def __len__(self) -> int:
        return len(self._objects)

    @property
    def size(self):
        return self._size

    def select(self, filter_func: Callable[[GenericType.T], bool], max_size: int = None):
        """
        Select the objects that meet conditions specified by filter_func
        :param filter_func:
        :param max_size:
        :return:
        """
        selected_objs: List[GenericType.T] = list(filter(filter_func, self._objects))
        if max_size:
            selected_objs = selected_objs[:max_size]

        return _TreelabObjectArray(self.parent_object, selected_objs, self.workspace)

    def select_by_name(self, name):
        return self.select(filter_func=lambda obj: obj.name == name)

    def sort(self, sort_function: Callable[[GenericType.T], bool], max_size: int = None):
        """
        Sort the objects by sort_function
        :param sort_function:
        :param max_size:
        :return:
        """
        sorted_objs: List[GenericType.T] = sorted(self._objects, key=sort_function)[:max_size]
        if max_size:
            sorted_objs = sorted_objs[:max_size]

        return _TreelabObjectArray(self.parent_object, sorted_objs, self.workspace)

    def listen_to(self, listener: Union[Callable[[EventPayload], Any], Listener], name: str = None,
                  thread_num: int = 0, user_only: bool = True):
        """
        Register the listener to every single object in the collection
        :param listener:
        :param name:
        :param thread_num:
        :param user_only:
        :return:
        """
        for i, obj in enumerate(self._objects):
            obj.listen_to(listener, '{}_{}'.format(name, i), thread_num, user_only)

    def __repr__(self):
        return self._objects.__repr__()


class CellArray(_TreelabObjectArray[Table, Cell]):
    def __init__(self, parent_object: GenericType.PT, objects: List[GenericType.T], workspace: Workspace):
        super().__init__(parent_object, objects, workspace)
        self._shape = (self.size, 1)

    @property
    def shape(self):
        return self._shape

    @property
    def matrix(self) -> np.array:
        """
        Get the text matrix representation of the cells
        :return:
        """
        # return self.parent_object.data.cells
        return self._objects
        # matrix = np.array([[self.objects[i * self.shape[1] + j].data.text for j in range(self.shape[1])]
        #                    for i in range(self.shape[0])])
        #
        # return matrix

    def update_all(self, value: str):
        """
        Update all the cells with the same value
        :param value:
        :return:
        """
        for obj in self._objects:
            obj.update(value=value)

    def reshape(self, shape: Tuple[int, int]):
        """
        Reshaping cells to certain shape as long as the size matches the product of width and length of the shape
        :param shape:
        :return:
        """
        m, n = shape
        if m * n != self.size:
            raise ValueError('The product of width and length of the shape must equals to the size of cells')
        self._shape = shape

        return self

    def flatten(self):
        """
        Flattening the cells into vector
        :return:
        """
        self._shape = (self.size, 1)

        return self

    def update(self, data_matrix: Union[List[List], np.array, pd.DataFrame],
               reshape: bool = True):
        """
        Update the cells with data_matrix, use reshape when you want to fit the matrix into the cells
        The shape of cell_type_matrix and data_matrix must be consistent and used to verify the cell field type
        :param data_matrix:
        :param reshape:
        :return:
        """
        data_matrix = self._convert_to_matrix(data_matrix)
        n_rows, n_cols = data_matrix.shape

        if reshape:
            self.reshape(data_matrix.shape)
        for i in range(n_rows):
            for j in range(n_cols):
                if data_matrix[i, j] != '':
                    self._objects[i * n_cols + j].update(value=data_matrix[i, j])

    @staticmethod
    def _convert_to_matrix(data):
        if isinstance(data, List):
            if len(data) == 0:
                raise ValueError('The size of the data matrix must not be zero')
            data = np.array(data)

        return data

    def values_dict(self) -> Dict:
        return {obj.id: obj.value for obj in self._objects}

    def __repr__(self):
        return self.matrix.__repr__()


class CoreArray(_TreelabObjectArray[Workspace, Core]):
    pass


class TableArray(_TreelabObjectArray[Core, Table]):
    pass


class RowArray(_TreelabObjectArray[Table, Row]):
    pass


class ColumnArray(_TreelabObjectArray[Table, Column]):
    pass


class ViewArray(_TreelabObjectArray[Table, View]):
    pass


@contextmanager
def subscribe_under(workspace: Workspace, wait_time: int = 0):
    try:
        yield
    finally:
        workspace.event_handler._subscribe_all()
        print('All listeners subscribed')
        threading.Event().wait(wait_time)
        workspace.dispose()


def subscribe(workspaces: List[Workspace], wait_time: int = 0):
    """
    Wrapper for subscribing multiple workspaces
    """

    def decorator(subscription_func):
        @wraps(subscription_func)
        def wrapper():
            for workspace in workspaces:
                subscription_func(workspace)
                workspace.event_handler._subscribe_all()

            threading.Event().wait(wait_time)
            # Disposing all workspaces
            for workspace in workspaces:
                workspace.dispose()

        return wrapper

    return decorator


def get_choice(choices: List[List]):
    """
    Set the choice for column
    :param choices:
                for example :
                get_choice([['a', SelectColor.blue], ['b', SelectColor.green], ['c', SelectColor.pink]])
    :return:
    """
    return [Choice(id=generate_id(), name=choice[0], color=choice[1].value) for choice in choices]


def _datetime_to_utc(date: str):
    """
    convert time to utc
    :param date :
                for example :
                    yyyy-mm-dd = '%Y-%m-%d' 2019-12-25
                    yyyy-mm-dd hh-mm-ss = '%Y-%m-%d %H:%M:%S' 2019-06-05 10:19:02
                    dd-mm-yyyy = '%d-%m-%Y' 25-12-2019
                    dd-mm-yyyy hh-mm-ss = '%d-%m-%Y %H:%M:%S' 25-12-2019 10:19:02
                    mm-dd-yyyy = '%m-%d-%Y' 12-25-2019
                    mm-dd-yyyy hh-mm-ss = '%m-%d-%Y %H:%M:%S' 12-25-2019 10:19:02
    :return:
    """
    if date.find('T') > -1:
        return date

    new_date = date.replace('_', '-').replace('.', '-').replace('/', '-')
    result = _utc(new_date)
    if result:
        return result
    else:
        raise ValueError('Unsupported date format', date)


def _utc(new_date):
    for date_pattern in DatePattern:
        flag = re.match(date_pattern.value, new_date)
        if flag:
            new_date = datetime.strptime(new_date, DateFormatter[date_pattern.name].value)
            utc_time = new_date - timedelta(hours=8)
            utc_time = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            return utc_time
    return None
