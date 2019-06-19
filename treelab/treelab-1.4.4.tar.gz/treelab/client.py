import treelab.grpc_treelab.messages.service_pb2_grpc as treelab_service
from treelab.consts import GRPCConfig
from treelab.grpc_treelab.messages.service_pb2 import *
from treelab.utils.decorator_utils import *

"""
Interfacing Treelab gRPC APIs
"""


class TreeLabClient:
    def __init__(self, token: str):
        self.metadata = [('access_token', token)]
        self.channel = grpc.insecure_channel(GRPCConfig.ip)
        self.client = treelab_service.TreeLabApiServiceStub(self.channel)

    @wait("WorkspaceCreated")
    def create_workspace(self, create_workspace_input: CreateWorkspaceInput):
        return self.client.CreateWorkspace, create_workspace_input, self.metadata

    @wait("WorkspaceUpdated")
    def update_workspace(self, update_workspace_input: UpdateWorkspaceInput):
        return self.client.UpdateWorkspace, update_workspace_input, self.metadata

    @wait("CoreCreated")
    def add_core(self, add_core_input):
        return self.client.AddCore, add_core_input, self.metadata

    @wait("CoreRemoved")
    def remove_core(self, remove_core_input: RemoveCoreInput):
        return self.client.RemoveCore, remove_core_input, self.metadata

    @wait("CoreUpdated")
    def update_core(self, update_core_input: UpdateCoreInput):
        return self.client.UpdateCore, update_core_input, self.metadata

    @wait("TableCreated")
    def add_table(self, add_table_input: AddTableInput):
        return self.client.AddTable, add_table_input, self.metadata

    @wait("TableNameUpdated")
    def update_table_name(self, update_table_name_input: UpdateTableNameInput):
        return self.client.UpdateTableName, update_table_name_input, self.metadata

    @wait("TableRemoved")
    def remove_table(self, remove_table_input: RemoveTableInput):
        return self.client.RemoveTable, remove_table_input, self.metadata

    @wait("ViewAdded")
    def add_view(self, add_view_input: AddViewInput):
        return self.client.AddView, add_view_input, self.metadata

    @wait("ViewUpdated")
    def update_view(self, update_view_input: UpdateViewInput):
        return self.client.UpdateView, update_view_input, self.metadata

    @wait("ViewRemoved")
    def remove_view(self, remove_view_input: RemoveViewInput):
        return self.client.RemoveView, remove_view_input, self.metadata

    @wait("ColumnAddedToView")
    def add_column(self, add_column_input: AddColumnInput):
        return self.client.AddColumn, add_column_input, self.metadata

    @wait("ColumnConfigUpdated")
    def update_column(self, update_column_input: UpdateColumnInput):
        return self.client.UpdateColumn, update_column_input, self.metadata

    @wait("ColumnWidthUpdated")
    def update_column_width(self, update_column_width_input: UpdateColumnWidthInput):
        return self.client.UpdateColumnWidth, update_column_width_input, self.metadata

    @wait("ColumnOrderUpdated")
    def update_column_order(self, reorder_column_input: ReorderColumnInput):
        return self.client.ReorderColumn, reorder_column_input, self.metadata

    @wait("ColumnRemoved")
    def remove_column(self, remove_column_input: RemoveColumnInput):
        return self.client.RemoveColumn, remove_column_input, self.metadata

    @wait("RowAddedToView")
    def add_row(self, add_row_input: AddRowInput):
        return self.client.AddRow, add_row_input, self.metadata

    @wait("RowOrderUpdated")
    def update_row_order(self, reorder_row_input: ReorderRowInput):
        return self.client.ReorderRow, reorder_row_input, self.metadata

    @wait("RowRemoved")
    def remove_row(self, remove_row_input: RemoveRowInput):
        return self.client.RemoveRow, remove_row_input, self.metadata

    @wait("CellUpdated")
    def update_cell(self, update_cell_input: UpdateCellInput):
        return self.client.UpdateCell, update_cell_input, self.metadata

    def get_all_workspaces(self):
        return self.client.GetAllWorkspaces(EmptyInput(), metadata=self.metadata)

    def subscribe_to_workspace(self, subscription_input: WorkspaceSubscriptionInput):
        return self.client.SubscribeToWorkspace(subscription_input, metadata=self.metadata)

    def get_workspace(self, get_workspace_input: GetWorkspaceInput):
        return self.client.GetWorkspace(get_workspace_input, metadata=self.metadata)

    def get_table(self, get_table_input: GetTableInput):
        return self.client.GetTable(get_table_input, metadata=self.metadata)

    def get_all_tables(self, get_tables_input: GetTablesInput):
        return self.client.GetAllTables(get_tables_input, metadata=self.metadata)

    def get_core(self, get_core_input: GetCoreInput):
        return self.client.GetCore(get_core_input, metadata=self.metadata)

    def get_all_cores(self, get_cores_input: GetCoresInput):
        return self.client.GetAllCores(get_cores_input, metadata=self.metadata)

    def get_cell_by_column_and_row_id(self, get_cell_by_column_and_row_id_input: GetCellByColumnAndRowIdInput):
        return self.client.GetCellByColumnAndRowId(get_cell_by_column_and_row_id_input, metadata=self.metadata)

    def get_lookup_cell(self, get_lookup_cell_by_column_and_row_id_input:
    GetLookupCellByColumnAndRowIdInput):
        return self.client.GetLookupCellByColumnAndRowId(get_lookup_cell_by_column_and_row_id_input,
                                                         metadata=self.metadata)
