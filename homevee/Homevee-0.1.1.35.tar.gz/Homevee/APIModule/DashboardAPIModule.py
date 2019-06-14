from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.DashboardManager import DashboardManager

ACTION_KEY_GET_USER_DASHBOARD_ITEMS = "getuserdashboarditems"
ACTION_KEY_GET_USER_FAVOURITE_DEVICES = "getuserfavouritedevices"
ACTION_KEY_SET_EDIT_USER_DASHBOARD = "edituserdashboard"
ACTION_KEY_SET_GET_USER_DASHBOARD = "getuserdashboard"

class DashboardAPIModule(APIModule):
    def __init__(self):
        super(DashboardAPIModule, self).__init__()
        self.dashboard_manager = DashboardManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_USER_DASHBOARD_ITEMS: self.get_user_dashboard_items,
            ACTION_KEY_GET_USER_FAVOURITE_DEVICES: self.get_user_favourite_devices,
            ACTION_KEY_SET_EDIT_USER_DASHBOARD: self.edit_user_dashboard,
            ACTION_KEY_SET_GET_USER_DASHBOARD: self.get_user_dashboard
        }

        return mappings

    def get_user_dashboard_items(self, user, request, db):
        try:
            data = self.dashboard_manager.get_user_dashboard_items(user, db)
            if data is not None:
                return Status(type=STATUS_OK, data={'dashboard':data})
            else:
                return Status(type=STATUS_ERROR)
        except:
            return Status(type=STATUS_ERROR)

    def get_user_favourite_devices(self, user, request, db):
        try:
            data = self.dashboard_manager.get_user_favourite_devices(user, db)
            if data is not None:
                return Status(type=STATUS_OK, data={'dashboard':data})
            else:
                return Status(type=STATUS_ERROR)
        except:
            return Status(type=STATUS_ERROR)

    def edit_user_dashboard(self, user, request, db):
        try:
            success = self.dashboard_manager.edit_user_dashboard(user, request['dashboarddata'], db)
            if success:
                return Status(type=STATUS_OK)
            else:
                return Status(type=STATUS_ERROR)
        except:
            return Status(type=STATUS_ERROR)

    def get_user_dashboard(self, user, request, db):
        try:
            data = self.dashboard_manager.get_user_dashboard(user, db)
            if data is not None:
                return Status(type=STATUS_OK, data=data)
            else:
                return Status(type=STATUS_ERROR)
        except:
            return Status(type=STATUS_ERROR)