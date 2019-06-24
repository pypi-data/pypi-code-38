"""
Meteocat API python module
"""

from datetime import datetime
from datetime import timedelta               
from time import time
from math import radians, cos, sin, asin, sqrt
import pytz

import requests

from meteocat_api.exceptions import APIException
from meteocat_api.Site import Site
from meteocat_api.Observation import Observation
from meteocat_api.Timestep import Timestep

BASE_URL = "https://api.meteo.cat/xema/v1"
SITES_URL = "estacions/metadades?estat=ope&data="
OBSERVATION_URL = "variables/mesurades/32/ultimes?codiEstacio="
CATALOG_URL = "variables/mesurades/metadades"

DATE_FORMAT = "%Y-%m-%dZ"
OBSERVATION_DATE_FORMAT = "%Y-%m-%dT%H:%MZ"

# See:
# https://apidocs.meteocat.gencat.cat/section/referencia-tecnica/operacions/


class Manager(object):
    """
    Meteocat API Manager object
    """

    def __init__(self, api_key=""):
        self.api_key = api_key
        self.call_response = None

        # The list of sites changes infrequently so limit to requesting it
        # every hour.
        self.sites_last_update = 0
        self.sites_last_request = None
        self.sites_update_time = 1800

    def __call_api(self, path, api_url=BASE_URL):
        """
        Call the meteocat_api api using the requests module

        """

        url = "%s/%s" % (api_url, path)
        payload = {'x-api-key': self.api_key}
        
        req = requests.get(url, headers = payload, verify = False)

        try:
            data = req.json()
        except ValueError:
            raise APIException("meteocat_api has not returned any data, this could be due to an incorrect API key")
        self.call_response = data
        if req.status_code != 200:
            msg = [data[m] for m in ("message", "error_message", "status") \
                      if m in data][0]
            raise Exception(msg)        
        return data

    def _distance_between_coords(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        Haversine formula states that:

        d = 2 * r * arcsin(sqrt(sin^2((lat1 - lat2) / 2 +
        cos(lat1)cos(lat2)sin^2((lon1 - lon2) / 2))))

        where r is the radius of the sphere. This assumes the earth is spherical.
        """

        # Convert the coordinates of the points to radians.
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        r = 6371

        d_hav = 2 * r * asin(sqrt((sin((lat1 - lat2) / 2))**2 + \
                                  cos(lat1) * cos(lat2) * (sin((lon1 - lon2) / 2)**2 )))

        return d_hav

    def get_sites(self):
        """
        This function returns a list of Site object.
        """

        time_now = time()
        if (time_now - self.sites_last_update) > self.sites_update_time or self.sites_last_request is None:

            date = datetime.now().strftime(DATE_FORMAT)

            data = self.__call_api(SITES_URL + date)
            sites = list()            
            for jsoned in data:
                site = Site()
                site.name = jsoned['nom']
                site.id = jsoned['codi']
                site.latitude = jsoned['coordenades']['latitud']
                site.longitude = jsoned['coordenades']['longitud']

                site.region = jsoned['municipi']['nom']

                site.elevation = jsoned['altitud']

                site.api_key = self.api_key

                sites.append(site)
            self.sites_last_request = sites
            # Only set self.sites_last_update once self.sites_last_request has
            # been set
            self.sites_last_update = time_now
        else:
            sites = self.sites_last_request

        return sites

    def get_nearest_site(self, latitude=None,  longitude=None):

        """
        This function returns the nearest Site object to the specified
        coordinates.
        """
        if longitude is None:
            print('ERROR: No latitude given.')
            return False

        if latitude is None:
            print('ERROR: No latitude given.')
            return False

        nearest = False
        distance = None
        sites = self.get_sites()
        # Sometimes there is a TypeError exception here: sites is None
        # So, sometimes self.get_all_sites() has returned None.
        for site in sites:
            new_distance = \
                self._distance_between_coords(
                    float(site.longitude),
                    float(site.latitude),
                    float(longitude),
                    float(latitude))

            if ((distance == None) or (new_distance < distance)):
                distance = new_distance
                nearest = site

        # If the nearest site is more than 30km away, raise an error
        if distance > 30:
            raise APIException("There is no site within 30km.")

        return nearest

    def get_observation_for_site(self, site_id):
        """
        Get observations for the provided site

        Returns last temperature observation
        """        

        observation = Observation()
        observation.id = site_id
        observation.date = datetime.now()
        
        data = self.__call_api(OBSERVATION_URL + site_id)

        for record in data['lectures']:
            new_timestep = Timestep()
            new_timestep.date = datetime.strptime(record['data'], OBSERVATION_DATE_FORMAT).replace(tzinfo=pytz.UTC) + timedelta(minutes=30)
            new_timestep.temperature = record['valor']
            	
            observation.timesteps.append(new_timestep)            	            

        return observation
