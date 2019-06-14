import json
import traceback
from time import sleep

from iothub_client.iothub_client import IoTHubTransportProvider, IoTHubModuleClient, DeviceMethodReturnValue

from Homevee import API
from Homevee.Helper import Logger
from Homevee.Utils.Database import Database

METHOD_PROCESS_DATA = "ProcessData"

class CloudConnection():
    def __init__(self):
        self.protocol = IoTHubTransportProvider.MQTT

        self.msg_timeout = 1000
        self.timeout = 1000

        db = Database()

        cloud_host_name = "Homevee-Cloud.azure-devices.net"
        device_id = db.get_server_data("REMOTE_ID")
        shared_access_key = db.get_server_data("CLOUD_ACCESS_KEY")

        self.connection_string = "HostName="+cloud_host_name+";DeviceId="+device_id+\
                                 ";SharedAccessKey="+shared_access_key

        print("Connection String: "+self.connection_string)

        self.client = self.init_client()

        return

    # This function will be called every time a method request is received
    def method_callback(self, method_name, payload, user_context):
        retval = DeviceMethodReturnValue()
        #retval.status = 200
        #retval.response = json.dumps({"action":{"message":{"payload":"methodresponse"}}})
        #return retval

        print(method_name)

        #if True:
        #    data = json.loads(payload)
        #    response_data = API().process_data(data, Database())
        #    print(response_data)
        #    retval.status = 200
        #    retval.response = json.dumps(response_data)
        #    print("CLOUD_COMMAND => " + payload)
        #    print("RESPONSE => " + retval.response)
        #    print("##############")
        #    return retval

        if method_name == METHOD_PROCESS_DATA:
            try:
                data = json.loads(payload)

                response_data = API().process_data(data, Database())

                #print(response_data)
                #print(type(response_data))

                retval.status = 200
                retval.response = json.dumps(response_data)

                print("CLOUD_COMMAND => "+payload)
                print("RESPONSE => "+retval.response)
                print("##############")
            except:
                if Logger.IS_DEBUG:
                    traceback.print_exc()
                retval.status = 500
                retval.response = "{ \"Response\": \"Could not call method named %s\" }" % METHOD_PROCESS_DATA
        else:
            retval.status = 404
            retval.response = "{ \"Response\": \"Method %s not found\" }" % method_name

        return retval

    def init_client(self):
        print(self.connection_string)
        client = IoTHubModuleClient(self.connection_string, self.protocol)
        client.set_module_method_callback(self.method_callback, 0)
        return client

    @staticmethod
    def cloud_connection_loop():
        cloud_connection = CloudConnection()
        while(True):
            sleep(15)

if __name__ == "__main__":
    CloudConnection.cloud_connection_loop()