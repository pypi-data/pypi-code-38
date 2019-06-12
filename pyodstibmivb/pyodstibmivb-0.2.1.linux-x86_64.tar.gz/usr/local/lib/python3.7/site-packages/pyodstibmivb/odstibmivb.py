import aiohttp
import re
import yarl


URL = "https://opendata-api.stib-mivb.be/"


def BASE_URL():
    return URL + "{}/{}"


methods = {
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

    async def do_request(self, method, id, *ids):
        """
        do the actual API request.
        ids should be a list or tuple containig 1-10 id's.
        """
        if len(ids) > 9:
            raise ValueError("only up to 10 id's are supported")

        if method not in methods:
            raise ValueError("this method does not exist")
        url = yarl.URL(
            BASE_URL().format(methods[method], "%2C".join(str(e) for e in (id, *ids))),
            encoded=True,
        )

        if self._session is None:
            async with aiohttp.ClientSession() as session:
                return await self.get_response(session, url, self.header)
        else:
            return await self.get_response(self._session, url, self.header)

    async def get_response(self, session, url, header):
        async with session.get(url, headers=header) as response:
            if response.status == 200:
                try:
                    json_data = await response.json()
                except ValueError as exception:
                    message = "Server gave incorrect data"
                    raise Exception(message) from exception

            elif response.status == 401:
                message = "401: Acces token might be incorrect or expired"
                raise HttpException(message, response.status)

            elif response.status == 403:
                message = "403: incorrect API request"
                raise HttpException(message, response.status)

            else:
                message = "Unexpected status code {}."
                raise HttpException(message, response.status)

            return json_data

    async def get_vehicle_position(self, id, *ids):
        return await self.do_request("vehicle_position", id, *ids)

    async def get_waiting_time(self, id, *ids):
        return await self.do_request("waiting_time", id, *ids)

    async def get_message_by_line(self, id, *ids):
        return await self.do_request("message_by_line", id, *ids)

    async def get_stops_by_line(self, id, *ids):
        return await self.do_request("stops_by_line", id, *ids)

    async def get_point_detail(self, id, *ids):
        return await self.do_request("point_detail", id, *ids)


class HttpException(Exception):
    def __init__(self, message, status_code):

        super().__init__(message)

        self.status_code = status_code
