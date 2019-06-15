# -*- coding: utf-8 -*-

"""
onemapsg.response
~~~~~~~~~~~~~~~~~

This module contains the Response class.
"""

import polyline


class Response:

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data


class BaseResource:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k.lower()):
                setattr(self, k.lower(), v)

    def to_dict(self):
        from .utils import to_dict
        return to_dict(self)


class SearchResultItem(BaseResource):

    search_value = None
    blk_no = None
    road_name = None
    building = None
    address = None
    postal = None
    coordinates = None
    lat_long = None

    def __init__(self, **kwargs):
        if 'SEARCHVAL' in kwargs:
            self.search_value = kwargs.pop('SEARCHVAL')
        if 'X' in kwargs or 'Y' in kwargs:
            x = kwargs.pop('X')
            y = kwargs.pop('Y')
            self.coordinates = (x, y)
        if 'LATITUDE' in kwargs or 'LONGITUDE' in kwargs:
            latitude = kwargs.pop('LATITUDE')
            longitude = kwargs.pop('LONGITUDE')
            self.lat_long = (latitude, longitude)
        super().__init__(**kwargs)


class SearchResult(BaseResource):

    found = None
    total_num_pages = None
    page_num = None
    results = None

    def __init__(self, **kwargs):
        if 'results' in kwargs:
            results = kwargs.pop('results')
            self.results = [SearchResultItem(**result) for result in results]
        self.total_num_pages = kwargs.pop('totalNumPages')
        self.page_num = kwargs.pop('pageNum')
        super().__init__(**kwargs)


class GeocodeInfoItem(BaseResource):

    building_name = None
    block = None
    road = None
    postal_code = None
    coordinates = None
    lat_long = None

    def __init__(self, **kwargs):
        self.building_name = kwargs.get('BUILDINGNAME')
        self.block = kwargs.get('BLOCK')
        self.road = kwargs.get('ROAD')
        self.postal_code = kwargs.get('POSTALCODE')
        x = kwargs.get('XCOORD')
        y = kwargs.get('YCOORD')
        self.coordinates = (x, y)
        lat = kwargs.get('LATITUDE')
        long = kwargs.get('LONGITUDE')
        self.lat_long = (lat, long)
        super().__init__(**kwargs)


class GeocodeInfo(BaseResource):

    results = None

    def __init__(self, **kwargs):
        if 'GeocodeInfo' in kwargs:
            results = kwargs.pop('GeocodeInfo')
            self.results = [GeocodeInfoItem(**result) for result in results]
        super().__init__(**kwargs)


class RouteResult(BaseResource):

    # for routeType in ['walk', 'drive', 'cycle']
    status_message = None
    alternative_names = None
    route_name = None
    route_geometry = None
    route_instructions = None
    alternative_summaries = None
    via_points = None
    route_summary = None
    found_alternative = None
    status = None
    via_indices = None
    hint_data = None
    alternative_geometries = None
    alternative_instructions = None
    alternative_indices = None
    
    # for routeType='pt'
    request_parameters = None
    plan = None
    debug_output = None
    elevation_metadata = None

    def __init__(self, **kwargs):
        self.request_parameters = kwargs.get('requestParameters')
        self.debug_output = kwargs.get('debugOutput')
        self.elevation_metadata = kwargs.get('elevationMetadata')
        super().__init__(**kwargs)

    @property
    def lat_longs(self):
        """Decoded from route_geometry."""
        if self.route_geometry:
            return polyline.decode(self.route_geometry)
        return None
