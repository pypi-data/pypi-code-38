"""
interact async with the opendata api of the Belgian STIB MIVB public transport company
"""

import re

import aiohttp
import yarl

URL = "https://opendata-api.stib-mivb.be/"


def base_url():
    """ return the base url for the api """
    return URL + "{}/{}"


METHODS = {
    "vehicle_position": "OperationMonitoring/4.0/VehiclePositionByLine",
    "waiting_time": "OperationMonitoring/4.0/PassingTimeByPoint",
    "message_by_line": "OperationMonitoring/4.0/MessageByLine",
    "stops_by_line": "NetworkDescription/1.0/PointByLine",
    "point_detail": "NetworkDescription/1.0/PointDetail",
}


class ODStibMivb:
    """Interface with Stib-Mivb Open Data API"""

    def __init__(self, access_token, session=None):
        self.access_token = access_token
        self._session = session

    @property
    def access_token(self):
        """The access code to acces the api"""
        return self.__access_token

    @access_token.setter
    def access_token(self, value):
        value = value.lower()
        if re.fullmatch("[a-z0-9]{32}", value):
            # pylint: disable=W0201
            self.__access_token = value
            self.__header = {"Authorization": "Bearer " + self.access_token}
        else:
            raise ValueError("invalid format for access token")

    @property
    def header(self):
        """http header in which te access code will be set"""
        return self.__header

    async def do_request(self, method, id_, *ids):
        """
        Create a session if needed and do the API request
        """
        if method not in METHODS:
            raise ValueError("this method does not exist")

        if self._session is None:
            async with aiohttp.ClientSession() as session:
                return await self.get_response_unlimited(session, method, id_, *ids)
        else:
            return await self.get_response_unlimited(self._session, method, id_, *ids)

    async def get_response_unlimited(self, session, method, *ids):
        """
        if needed split up the api request in multiple 10 argument requests
        """
        response_unlimited = {}
        i = 0
        while i < len(ids):
            url = yarl.URL(
                base_url().format(
                    METHODS[method], "%2C".join(str(e) for e in ids[i : i + 10])
                ),
                encoded=True,
            )
            response = await self.get_response(session, url)
            assert len(response.keys()) == 1
            for key in response.keys():
                if key in response_unlimited.keys():
                    response_unlimited[key].extend(response[key])
                else:
                    response_unlimited[key] = response[key]
            i = i + 10
        return response_unlimited

    async def get_response(self, session, url):
        """
        Do the actual api request
        """
        async with session.get(url, headers=self.header) as response:
            if response.status == 200:
                try:
                    json_data = await response.json()
                except ValueError as exception:
                    message = "Server gave incorrect data"
                    raise Exception(message) from exception

            elif response.status == 401:
                message = "401: Acces token might be incorrect or expired"
                raise HttpException(message, await response.text(), response.status)

            elif response.status == 403:
                message = "403: incorrect API request"
                raise HttpException(message, await response.text(), response.status)

            else:
                message = "Unexpected status code {}."
                raise HttpException(message, await response.text(), response.status)

            return json_data

    async def get_vehicle_position(self, id_, *ids):
        """do the vehicle position api request"""
        return await self.do_request("vehicle_position", id_, *ids)

    async def get_waiting_time(self, id_, *ids):
        """do the waiting time api request"""
        return await self.do_request("waiting_time", id_, *ids)

    async def get_message_by_line(self, id_, *ids):
        """do the message by line api request"""
        return await self.do_request("message_by_line", id_, *ids)

    async def get_message_by_line_with_point_detail(self, id_, *ids):
        """
        do the message by line api request,
        and get the point id of the mentioned stops in the response
        """
        response = await self.do_request("message_by_line", id_, *ids)
        for line in response["messages"]:
            point_ids = [id_["id"] for id_ in line["points"]]
            point_details = await self.get_point_detail(*point_ids)
            line["points"] = point_details["points"]
        return response

    async def get_stops_by_line(self, id_, *ids):
        """do the stops by line api request"""
        return await self.do_request("stops_by_line", id_, *ids)

    async def get_point_detail(self, id_, *ids):
        """do the point detail api request"""
        return await self.do_request("point_detail", id_, *ids)


class HttpException(Exception):
    """ HTTP exception class with message text, and status code"""

    def __init__(self, message, text, status_code):

        super().__init__(message)

        self.status_code = status_code
        self.text = text
