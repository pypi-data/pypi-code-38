from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.GraphDataManager import GraphDataManager

ACTION_KEY_GET_GRAPH_DATA = "getgraphdata"

class GraphDataAPIModule(APIModule):
    def __init__(self):
        super(GraphDataAPIModule, self).__init__()
        self.graph_data_manager = GraphDataManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_GRAPH_DATA: self.get_graph_data,
        }
        return mappings

    def get_graph_data(self, user, request, db) -> Status:
        graph_data = self.graph_data_manager.get_graph_data(user, request['room'], request['type'],
                                                         request['id'], request['von'], request['bis'], db)
        return Status(type=STATUS_OK, data=graph_data)