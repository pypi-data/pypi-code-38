import json

from Homevee.Helper.HomeveeCloud.CloudAPI import CloudAPI
from Homevee.Helper.HomeveeCloud.Exception import APINotAuthenticatedException, APIErrorException
from Homevee.Helper.Response import Response


class HomeveeCloudWrapper():
    def __init__(self, remote_id=None, access_token=None):
        self.cloud_api = CloudAPI(remote_id, access_token)

        self.remote_id = self.cloud_api.remote_id
        self.access_token = self.cloud_api.access_token

    def is_premium(self) -> bool:
        """
        Checks if the remote-id is premium
        :return:
        """
        response = self.cloud_api.do_get("/ispremium/"+self.remote_id, {})
        data = self.check_response(response)
        return data['is_premium']

    def send_push_notification(self, registration_ids: list, message_data: dict):
        """
        Sends a push notification to the given registration ids
        :param registration_ids: the recipients ids
        :param message_data: the data of the message
        :return:
        """
        response = self.cloud_api.do_post("/sendnotification",
                                         {'registration_ids': registration_ids,
                                          'message_data': message_data})
        data = self.check_response(response)
        return data['status']

    def set_ip(self, ip: str):
        """
        Sets the homevee-hubs local ip address
        :param ip: the ip address
        :return:
        """
        response = self.cloud_api.do_put("/setlocalip/"+self.remote_id, {'ip': ip})
        data = self.check_response(response)
        return data['status']

    def set_cert(self, cert: str):
        """
        Sets the homevee-hubs local certificates
        :param cert: the certificate
        :return:
        """
        response = self.cloud_api.do_put("/setlocalcert/"+self.remote_id, {'cert': cert})
        data = self.check_response(response)
        return data['status']

    def get_ip(self):
        """
        Get the local ip address of the hub
        :return: the ip
        """
        response = self.cloud_api.do_get("/getlocalip/"+self.remote_id, {})
        data = self.check_response(response)
        return data['local_ip']

    def get_cert(self):
        """
        Gets the local certificate of the hub
        :return: the certificate
        """
        response = self.cloud_api.do_get("/getlocalcert/"+self.remote_id, {})
        data = self.check_response(response)
        return data['local_cert']

    def check_response(self, response: Response) -> dict:
        """
        Checks the response and returns its data if valid
        :param response: the response to check
        :return: the dict with the responses data
        """
        if response is None:
            raise APIErrorException("API-Call not successful")

        if response.status_code == 401:
            raise APINotAuthenticatedException("Invalid credentials given")

        if response.status_code != 200:
            raise APIErrorException("API-Call not successful")

        return json.loads(response.response)