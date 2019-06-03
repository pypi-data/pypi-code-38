import re
import requests


BASE_URL = 'https://opendata-api.stib-mivb.be/{}/{}'

methods = {
        'vehicle_position': 'OperationMonitoring/4.0/VehiclePositionByLine',
        'waiting_time': 'OperationMonitoring/4.0/PassingTimeByPoint',
        'message_by_line': 'OperationMonitoring/4.0/MessageByLine',
        'stops_by_line': 'NetworkDescription/1.0/PointByLine',
        'point_detail': 'NetworkDescription/1.0/PointDetail'
        }


class ODStibMivb:
    """Interface with Stib-Mivb Open Data API"""

    def __init__(self, access_token):
        self.__session = requests.Session()
        self.access_token = access_token
        self.__header = {'Authorization': 'Bearer '+self.access_token}

    @property
    def session(self):
        return self.__session

    @property
    def access_token(self):
        """The access code to acces the api"""
        return self.__access_token

    @access_token.setter
    def access_token(self, value):
        if re.fullmatch('[a-zA-Z0-9]{32}', value):
            # pylint: disable=W0201
            self.__access_token = value
        else:
            raise ValueError('invalid format for access token')

    @property
    def header(self):
        """http header in which te access code will be set"""
        return self.__header

    def do_request(self, method, ids):
        """
        do the actual API request.
        ids should be a list or tuple containig 1-10 id's.
        """
        if len(ids) > 10:
            raise ValueError("only up to 10 id's are supported")
        if method not in methods:
            raise ValueError('this method does not exist')
        url = BASE_URL.format(methods[method], '%2C'.join(str(e) for e in ids))
        try:
            with requests.get(url, headers=self.header) as response:
                #import pdb; pdb.set_trace()
                #response = self.session.get(url, headers=self.header)
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                    except ValueError as e:
                        m = 'looks like something is wrong on the server side.'
                        raise ValueError(m) from e
                else:
                    m = 'Unexpected status code {}. Are you sure the id is correct?'
                    raise RuntimeError(m.format(response.status_code))

        except requests.exceptions.RequestException as e:
            try:
                self.session.get('https://1.1.1.1/', timeout=1)
            except requests.exceptions.ConnectionError:
                m = "Your internet connection doesn't seem to be working."
                raise requests.exceptions.ConnectionError(m) from e
            else:
                m = "The Stib-Mivb API doesn't seem to be working."
                raise requests.exceptions.RequestException(m) from e

        return json_data

    def get_vehicle_position(self, ids):
        return self.do_request('vehicle_position', ids)

    def get_waiting_time(self, ids):
        return self.do_request('waiting_time', ids)

    def get_message_by_line(self, ids):
        return self.do_request('message_by_line', ids)

    def get_stops_by_line(self, ids):
        return self.do_request('stops_by_line', ids)

    def get_point_detail(self, ids):
        return self.do_request('point_detail', ids)
