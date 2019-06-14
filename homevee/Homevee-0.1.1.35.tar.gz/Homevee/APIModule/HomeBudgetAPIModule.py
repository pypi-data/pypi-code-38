'''
        elif action == "gethomebudgetdata":
            response = HomeBudgetManager().get_home_budget_data(user, request['startdate'], db)
        elif action == "gethomebudgetdatadayitems":
            response = HomeBudgetManager().get_home_budget_data_day_items(user, request['date'], db)
        elif action == "gethomebudgetdatagraph":
            response = HomeBudgetManager().get_home_budget_data_graph(user, request['startdate'], request['enddate'],
                                                                      db)
        elif action == "addedithomebudgetdata":
            response = HomeBudgetManager().add_edit_home_budget_data(user, request['id'], request['date'],
                                                                     request['info'], request['amount'], db)
        elif action == "deletehomebudgetdata":
            response = HomeBudgetManager().delete_home_budget_data(user, request['id'], db)
'''

from Homevee.APIModule import APIModule
from Homevee.Exception import NoPermissionException
from Homevee.Item.Status import *
from Homevee.Manager.HomeBudgetManager import HomeBudgetManager

ACTION_KEY_GET_HOME_BUDGET_DATA = "gethomebudgetdata"
ACTION_KEY_GET_HOME_BUDGET_DATA_DAY_ITEMS = "gethomebudgetdatadayitems"
ACTION_KEY_GET_HOME_BUDGET_DATA_GRAPH = "gethomebudgetdatagraph"
ACTION_KEY_ADD_EDIT_HOME_BUDGET_DATA = "addedithomebudgetdata"
ACTION_KEY_DELETE_HOME_BUDGET_DATA = "deletehomebudgetdata"

class HomeBudgetAPIModule(APIModule):
    def __init__(self):
        super(HomeBudgetAPIModule, self).__init__()
        self.home_budget_manager = HomeBudgetManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_HOME_BUDGET_DATA: self.get_home_budget_data,
            ACTION_KEY_GET_HOME_BUDGET_DATA_DAY_ITEMS: self.get_home_budget_data_items,
            ACTION_KEY_GET_HOME_BUDGET_DATA_GRAPH: self.get_home_budget_data_graph,
            ACTION_KEY_ADD_EDIT_HOME_BUDGET_DATA: self.add_edit_home_budget_data,
            ACTION_KEY_DELETE_HOME_BUDGET_DATA: self.delete_home_budget_data
        }

        return mappings

    def get_home_budget_data(self, user, request, db):
        data = self.home_budget_manager.get_home_budget_data(user, request['startdate'], db)
        return Status(type=STATUS_OK, data=data)

    def get_home_budget_data_items(self, user, request, db):
        data = self.home_budget_manager.get_home_budget_data_day_items(user, request['date'], db)
        return Status(type=STATUS_OK, data={'items':data})

    def get_home_budget_data_graph(self, user, request, db):
        data = self.home_budget_manager.get_home_budget_data_graph(user, request['startdate'], request['enddate'], db)
        return Status(type=STATUS_OK, data=data)

    def add_edit_home_budget_data(self, user, request, db):
        try:
            self.home_budget_manager.add_edit_home_budget_data(user, request['id'],
                            request['date'], request['info'], request['amount'], db)
            return Status(type=STATUS_OK)
        except(NoPermissionException):
            return Status(type=STATUS_NO_PERMISSION)
        except:
            return Status(type=STATUS_ERROR)

    def delete_home_budget_data(self, user, request, db):
        try:
            self.home_budget_manager.delete_home_budget_data(user, request['id'], db)
            return Status(type=STATUS_OK)
        except(NoPermissionException):
            return Status(type=STATUS_NO_PERMISSION)
        except:
            return Status(type=STATUS_ERROR)