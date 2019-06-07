import requests
import json


class HostIP:

    def __init__(self):
        self.requestsSession = requests.session()

    def get_ip_info(self, ip=''):
        ip_json = self.requestsSession.get(
            'http://api.hostip.info/get_json.php',
            params={
                'ip': ip,
                'position': 'true'
            }
        ).content.decode()
        ip_json = json.loads(ip_json)
        return IP(
            ip=ip_json['ip'],
            country_name=ip_json['country_name'],
            country_code=ip_json['country_code'],
            city_and_state=ip_json['city'],
            lat=ip_json['lat'],
            lng=ip_json['lng']
        )


class IP:

    def __init__(self, ip, country_name, country_code, city_and_state, lat, lng):
        self.ip = ip
        # make the country name in lowercase, and make it's first letter uppercase
        country_name = country_name.lower()
        country_name = list(country_name)
        country_name[0] = country_name[0].upper()
        country_name = ''.join(country_name)
        self.country_name = country_name
        self.country_code = country_code
        city_and_state = city_and_state
        self.city = city
        self.state = state
        self.lat = lat
        self.lng = lng
        self.coordinates = lat + ',' + lng

