# -*- coding: utf8 -*-
from functools import partial

import pyproj
from geoalchemy2 import WKTElement
import json
import geojson
import re
from shapely import geometry
import requests
import os
from operator import attrgetter

from shapely.ops import transform, unary_union
from geoalchemy2 import shape

from oe_geoutils.data.models import LocatieElement


def process_location_elements(crab_gateway, admin_grenzen_client, contour, municipalities_niscodes=None):
    """

    :param crab_gateway: gateway for accessing crab data
    :param admin_grenzen_client: client for accessing administrative borders
    :param contour: contour
    :param municipalities_niscodes: list of municipality niscodes not be considered
    :return: list of location elements
    """
    municipalities_niscodes = municipalities_niscodes if municipalities_niscodes else []
    admin_municipalities = admin_grenzen_client.get_admin_objecten(contour, 'gemeente')
    admin_municipalities_niscodes = set([int(admin_municipality['id']) for admin_municipality in admin_municipalities])

    location_elementens = []
    for municipality_niscode in admin_municipalities_niscodes.difference(municipalities_niscodes):
        crab_client = crab_gateway()
        crab_gem = crab_client.get_gemeente_by_niscode(municipality_niscode)
        gemeente_naam = crab_gem.naam
        gemeente_crab_id = crab_gem.id
        provincie_niscode = crab_gem.provincie.niscode
        provincie_naam = crab_gem.provincie.naam
        location_element = LocatieElement(
            type='https://id.erfgoed.net/vocab/ontology#LocatieElement',
            gemeente_niscode=municipality_niscode,
            gemeente_naam=gemeente_naam,
            gemeente_crab_id=gemeente_crab_id,
            provincie_niscode=provincie_niscode,
            provincie_naam=provincie_naam)
        location_elementens.append(location_element)

    return location_elementens


def convert_wktelement_to_geojson(wktelement):
    """
    This function converts a wktelement (from GeoAlchemy) to a geojson
    :param wktelement: WKTElement
    :return: geojson
    """
    if wktelement is None:
        return None
    try:
        geom = shape.to_shape(wktelement)
        srid = wktelement.srid
        json_element = json.dumps(geometry.mapping(geom))
        geojson_element = geojson.loads(json_element)
        geojson_element['crs'] = {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::{0}".format(srid)
            }
        }

        return geojson_element

    except (AssertionError, AttributeError):
        raise AssertionError("WKTelement is niet geldig: %s" % wktelement)


def convert_geojson_to_wktelement(value):
    """
    This function converts a geojson to a wktelement that can be used by GeoAlchemy.
    :param value: geojson
    :return: WKTElement
    """
    if value is None or not value:
        return None
    try:
        s = json.dumps(value)
        g1 = geojson.loads(s)
        g2 = geometry.shape(g1)
        srid = get_srid_from_geojson(g1)

        return WKTElement(data=g2.wkt, srid=srid)

    except ValueError:
        raise ValueError("GeoJson is niet geldig: %s" % value)


def get_srid_from_geojson(value):
    """
    This function returns the srid of a geojson
    :param value: geojson
    :return: spatial reference identifier (srid)
    """
    if value is None or not value:
        return None

    try:
        if 'crs' not in value:
            return 4326
        srid = _find_srid(value['crs']['properties']['name'])
        return srid
    except Exception as e:  # pragma NO COVER
        raise ValueError("Geen geldige srid gevonden in GeoJson: %s" % value, e)


def find_srid(text):
    li = [int(x) for x in re.findall(r'\d+', text) if len(x) in [4, 5]]
    return max(li) if len(li) > 0 else None


def remove_dupl_values(list_coord):
    dupl_coord_indexes = [i for i in range(0, len(list_coord)) if i != 0 and
                          list_coord[i] == list_coord[i - 1]]
    [list_coord.pop(i) for i in sorted(dupl_coord_indexes, reverse=True)]


def remove_dupl_coords(coords, tree_types=(list, tuple)):
    """
    This function will remove duplicate consecutive coordinates
    :param coords: input coordinates
    """
    for o in coords:
        if isinstance(o[0][0], tree_types):
            remove_dupl_coords(o, tree_types)
        else:
            remove_dupl_values(o)


def check_within_flanders(geojson_input, tolerance=10):
    """
    :param geojson_input: geojson geometrie
    :param tolerance: buffer tolerance distance of Flanders
    :return: True if the input geojson is within the Flanders region, otherwise False
    """
    if geometry.shape(geojson_input).within(get_flanders_geometry().buffer(tolerance)):
        return True
    return False


def check_in_flanders(geojson_input, check_getijdezone=0):
    """
    :param geojson_input: geojson geometrie
    :param check_getijdezone: bool, check in tidal zone is necessary
    :return: True if the input geojson intersects with Flanders region, otherwise False
    """
    in_flanders = False
    geojson_input_shape = geometry.shape(geojson_input)
    if geojson_input_shape.intersects(get_flanders_geometry()):
        in_flanders = True
    if not in_flanders and check_getijdezone:
        if geojson_input_shape.intersects(get_flanders_tidal_zone_geometry()):
            in_flanders = True
    return in_flanders


def _get_geometry(file_path):
    with open(file_path) as geof:
        features = json.load(geof)
    output_geojson = features['features'][0]['geometry']
    return geometry.shape(output_geojson)


def get_flanders_geometry():
    here = os.path.abspath(os.path.dirname(__file__))
    return _get_geometry(here + '/fixtures/vlaams_gewest.geojson')


def get_flanders_tidal_zone_geometry():
    here = os.path.abspath(os.path.dirname(__file__))
    return _get_geometry(here + '/fixtures/vlaams_gewest_getijdenzone.geojson')


def provincie_niscode(gemeente_niscode):
    """
    geef de niscode van de provincie op basis van de niscode van de gemeente

    :param gemeente_niscode: niscode van de gemeente
    :return: niscode van de provincie
    """
    pcode = str(gemeente_niscode)[0]
    if pcode == '2':
        return int('20001')
    else:
        return int('{0}0000'.format(pcode))


def get_centroid_xy(value):
    """
    Returns the centroid x,y of a geojson polygon.
    If the geojson is a multipolygon. It return the centroid of the biggest polygon
    :param value: geojson
    :return: x,y
    """
    geometry_element = convert_geojson_to_geometry(value)
    if geometry_element.type == 'MultiPolygon':
        geometry_element_polygons = list(geometry_element.geoms)
        largest_polygon = max(geometry_element_polygons, key=attrgetter('area'))
        centroid = largest_polygon.centroid.wkt
    else:
        centroid = geometry_element.centroid.wkt
    return ','.join([x for x in re.findall(r'\d+.\d+', centroid)])


def add_crab_ids(crabpy_gateway, address):
    gemeente = address.get("gemeente")
    if gemeente:
        gewest_ids = [2, 1, 3]
        gemeente_val = None
        for gewest_id in gewest_ids:
            gemeenten = crabpy_gateway.list_gemeenten(gewest_id)
            gemeente_val = next((g for g in gemeenten if g.naam.lower() == gemeente.lower()), None)
            if gemeente_val:
                address['gemeente'] = "" + gemeente_val.naam
                address['gemeente_id'] = gemeente_val.id
                break
        straat_naam = address.get("straat")
        if gemeente_val and straat_naam:
            straat_val = next((s for s in gemeente_val.straten if s.label.lower() == straat_naam.lower()), None)
            if straat_val:
                address["straat"] = "" + straat_val.label
                address["straat_id"] = straat_val.id
                huisnummer_naam = address.get("huisnummer")
                if huisnummer_naam:
                    huisnummer_val = next((n for n in straat_val.huisnummers
                                           if n.huisnummer.lower() == huisnummer_naam.lower()), None)
                    if huisnummer_val:
                        address["huisnummer"] = "" + huisnummer_val.huisnummer
                        address["huisnummer_id"] = huisnummer_val.id
        return address


def epsg(value, use_epsg_prefix):
    """
    Deze functie geeft de epsg-code uit de waarde terug. Wanneer use_epsg_prefix "True" dan de srid teruggegeven met prefix EPSG:
    :param value: string/int waarde met epsg-code
    :param use_epsg_prefix: boolean wanneer true dan epsg-prefix toevoegen
    :return: string/int epsg-code
    """
    if not value:
        raise ValueError(
            "De opgegeven srid is leeg en kan niet worden omgezet naar een epsg-code")
    srid = _find_srid(str(value))
    if srid is None:
        raise ValueError(
            "Deze opgegeven srid kan niet worden omgezet naar een epsg-code: %s" % value)

    if use_epsg_prefix:
        return 'EPSG:' + str(srid)
    else:
        return srid


def _find_srid(text):
    """
    Deze functie geeft de srid terug uit een string
    :param text: string
    :return: spatial reference identifier (srid)
    """
    li = [int(x) for x in re.findall(r'\d+', str(text)) if len(x) in [4, 5]]
    if len(li) > 0:
        return max(li)
    else:
        raise ValueError("Geen geldige input voor srid")


def transform_projection(shape, old_srid, new_srid):
    """
    Deze functie projecteert een shapely geometrie van huidige srid naar nieuwe srid
    :param shape: shapely geometrie
    :param old_srid: huidige srid
    :param new_srid: nieuwe srid
    :return: shapely geometrie geprojecteerd naar nieuwe srid
    """
    try:
        if old_srid == new_srid:
            return shape

        project = partial(
            pyproj.transform,
            pyproj.Proj(init=old_srid),
            pyproj.Proj(init=new_srid)
        )

        return transform(project, shape)
    except Exception as e:
        raise ValueError(
            "Transformatie van projectiesysteem kan niet worden uitgevoerd tussen %s en %s" % (
                old_srid, new_srid), e)


def convert_geojson_to_geometry(value):
    """
    Deze functie converteert geojson naar een geometry(shapely)
    :param value: geojson
    :return: geometry (shapely)
    """
    if value is None:
        return None
    try:
        return unary_union(geometry.shape(value))
    except Exception as e:
        raise ValueError("GeoJson is niet geldig: %s" % value, e)


def convert_geometry_to_geojson(value, srid):
    """
    Deze functie converteert geometry(shapely) naar een geojson
    :param vaulue: geometry (shapely)
    :param srid: srid (example: 31370)
    :return: geojson
    """
    if value is None:
        return None

    try:
        json_value = json.dumps(geometry.mapping(value))
        if srid is None or not value:
            return geojson.loads(json_value)
        else:
            return geojson.loads(json_value.rsplit('}', 1)[0] +
                                 ', "crs": {"type": "name", "properties": {"name": "' + epsg(
                srid, True) + '" }}}')
    except Exception as e:
        raise ValueError("Geometry is niet geldig: %s" % value, e)


def nearest_location(geojson_element, crabpy_gateway=None):
    """
    Returns the nearest location. If a crabpy_gateway is given, the crab id's will be added to the address.
    Uses the agiv service https://loc.geopunt.be/geolocation/Location?xy=<x,y>
    where <x,y> are the coordinates of the centroid of the geometry (polygon).
    The agiv service returns crab, urbis en poi location types only in Flanders and Brussels.
    :param value: geojson
    :return: - crab address
             - None if the nearest address is nog crab type
    """
    xy = get_centroid_xy(geojson_element)

    r = requests.get('https://loc.geopunt.be/geolocation/Location?xy={0}'.format(xy))
    result = r.json()
    if 'LocationResult' not in result \
            or len(result['LocationResult']) == 0 \
            or 'crab' not in result['LocationResult'][0]['LocationType']:
        return None
    locres = result['LocationResult'][0]['FormattedAddress']
    straat_huisnummer, postcode_gemeente = locres.rsplit(', ', 1)
    straat, huisnummer = straat_huisnummer.rsplit(' ', 1)
    postcode, gemeente = postcode_gemeente.split(' ', 1)
    gemeente = gemeente.replace(' ({})'.format(postcode), '')
    address = {
        'straat': straat,
        'huisnummer': huisnummer,
        'omschrijving_straat': straat + ', ' + huisnummer,
        'postcode': postcode,
        'gemeente': gemeente,
        'land': 'BE'
    }
    if crabpy_gateway:
        return add_crab_ids(crabpy_gateway, address)
    else:
        return address


class AdminGrenzenClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_admin_objecten(self, geojson_input, admin_grens_type, return_geometry=0):
        """
        This function returns the administrative areas objects which intersects with the input geojson
        :param geojson_input: geojson
        :param admin_grens_type: type of returned administrative objects
        :param return_geometry: boolean indicating whether the geometry of the returned objects should also be included
        :
        :return: list of administrative areas objects
        """
        if check_in_flanders(geojson_input):
            data = {
                'geef_geometrie': return_geometry,
                'type': admin_grens_type,
                'geometrie': geojson_input
            }
            res = requests.post(
                url=self.base_url,
                json=data,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
            res.raise_for_status()
            return json.loads(res.text)
        else:
            return []

    def get_gemeenten(self, geojson_input):
        """
        This function returns the names of the municipalities which intersects with the input geojson
        :param geojson_input: geojson
        :return: list of municipalities
        """
        results = self.get_admin_objecten(geojson_input, 'gemeente')
        return [gemeente['naam'] for gemeente in results]

    def get_provincies(self, geojson_input):
        """
        This function returns the names of the provinces which intersects with the input geojson
        :param geojson_input: geojson
        :return: list of municipalities
        """
        results = self.get_admin_objecten(geojson_input, 'provincie')
        return [provincie['naam'] for provincie in results]

    @staticmethod
    def _get_lagest_admin_obj(results, geojson_input):
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return {'niscode': results[0]['id'], 'naam': results[0]['naam']}
        else:
            input_polygon = convert_geojson_to_geometry(geojson_input)
            for result in results:
                admin_geom = convert_geojson_to_geometry(result['geometrie'])
                result['intersection_area'] = admin_geom.intersection(input_polygon).area
            largest_m = max(results, key=lambda x: x['intersection_area'])
            return {'niscode': largest_m['id'], 'naam': largest_m['naam']}

    def get_gemeente(self, geojson_input):
        """
        This function returns the name of the municipality which intersects with the input geojson.
        If more municipalities intersect. The municipality is returned with the largest intersection
        :param value: administratievegrenzen_url
        :param value: geojson
        :return: municipality
        """
        results = self.get_admin_objecten(geojson_input, 'gemeente', 1)
        return self._get_lagest_admin_obj(results, geojson_input)

    def get_provincie(self, geojson_input):
        """
        This function returns the name of the province which intersects with the input geojson.
        If more provinces intersect. The province is returned with the largest intersection.
        :param value: administratievegrenzen_url
        :param value: geojson
        :return: province
        """
        results = self.get_admin_objecten(geojson_input, 'provincie', 1)
        return self._get_lagest_admin_obj(results, geojson_input)

    def check_erfgoedgemeenten(self, geojson_input, erfgoedgemeenten_list):
        """
        :param geojson_input: geojson geometry
        :param erfgoedgemeenten_list: list of niscodes of municipalities
        :return: dict including key status and optional key message
                 status "ok" when the geojson does not intersect with one of given municipalities
                 status "warn" when the geojson intersects partially with one of given municipalities
                 status "error" when the geojson is within one of given municipalities
        """
        gemeenten = self.get_admin_objecten(geojson_input, 'gemeente')
        erfgoedgemeenten = [gemeente for gemeente in gemeenten if
                            int(gemeente['id']) in json.loads(erfgoedgemeenten_list)]
        if len(erfgoedgemeenten) > 0:
            if len(gemeenten) == len(erfgoedgemeenten):
                return {
                    "status": "error",
                    "message": "Let op, de zone van deze melding is gelegen in een onroerenderfgoedgemeente en "
                               "kan niet bewaard worden. Gelieve de melding in te dienen bij deze gemeente."}
            else:
                return {
                    "status": "warn",
                    "message": "Let op, deze melding ligt deels in een onroerenderfgoedgemeente . "
                               "Gelieve de melding vooronderzoek eveneens in te dienen bij deze gemeente."}
        return {"status": "ok"}
