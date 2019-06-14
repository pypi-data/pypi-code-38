from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.GatewayManager import GatewayManager

ACTION_KEY_GET_GATEWAYS = "getgateways"
ACTION_KEY_ADD_EDIT_GATEWAY = "addeditgateway"
ACTION_KEY_DELETE_GATEWAY = "deletegateway"
ACTION_KEY_GET_GATEWAY_DEVICES = "getgatewaydevices"
ACTION_KEY_CONNECT_GATEWAY = "connectgateway"

class GatewayAPIModule(APIModule):
    def __init__(self):
        super(GatewayAPIModule, self).__init__()
        self.gateway_manager = GatewayManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_GATEWAYS: self.get_gateways,
            ACTION_KEY_ADD_EDIT_GATEWAY: self.add_edit_gateway,
            ACTION_KEY_DELETE_GATEWAY: self.delete_gateway,
            ACTION_KEY_GET_GATEWAY_DEVICES: self.get_gateway_devices,
            ACTION_KEY_CONNECT_GATEWAY: self.connect_gateway
        }

        return mappings

    def get_gateways(self, user, request, db):
        data = self.gateway_manager.get_gateways(user, db)
        return Status(type=STATUS_OK, data=data)

    def add_edit_gateway(self, user, request, db):
        data = self.gateway_manager.add_edit_gateway(user, request['type'], request['usr'], request['psw'],
                                                         request['changepw'],
                                                         request['ip'], request['port'], request['gateway_type'], db)
        return Status(type=STATUS_OK, data=data)

    def delete_gateway(self, user, request, db):
        data = self.gateway_manager.delete_gateway(user, request['type'], db)
        return Status(type=STATUS_OK, data=data)

    def get_gateway_devices(self, user, request, db):
        devices = self.gateway_manager.get_gateway_devices(user, request['type'], db)
        return Status(type=STATUS_OK, data={'devices': devices})

    def connect_gateway(self, user, request, db):
        data = self.gateway_manager.connect_gateway(user, request['type'], request['ip'], db)
        return Status(type=STATUS_OK, data=data)