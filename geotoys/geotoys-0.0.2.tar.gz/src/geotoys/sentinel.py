"""
This module contains a mini-wrapper for searching and downloading Sentinel data


# download single scene by known product id
>>> api.download(<product_id>)

# download all results from the search
>>> api.download_all(products)

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
>>> api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
>>> api.to_geodataframe(products)

# Get basic information about the product: its title, file size, MD5 sum, date, footprint and
# its download url
>>> api.get_product_odata(<product_id>)

# Get the product's full metadata available on the server
>>> api.get_product_odata(<product_id>, full=True)
"""
import geopandas
from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt
from shapely.geometry import Polygon

# TODO close connection
class SentinelDL(object):

    def __init__(self, user, password, platform='Sentinel-2'):
        self.api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
        self.platform = platform

    def query_bb(self, bb, ts0, ts1, ccrange=(0, 30)):
        """Search by polygon, time and cloud range

        return products
        """
        # search by polygon, time, and Hub query keywords
        if type(bb) is not tuple:
            raise TypeError("Bounding box must be a tuple of min/max values of Lon/Lat")

        footprint = geojson_to_wkt(SentinelDL.geojson_bb(*bb))

        return self.api.query(
                        footprint,
                        date = (ts0, ts1),
                        platformname = self.platform,
                        cloudcoverpercentage = ccrange
                        )

    @staticmethod
    def geojson_bb(lon0, lat0, lon1, lat1):
        """Get a bounding box area as a GeoJSON formatted dictionary
        """

        poly = Polygon([
            (lon0, lat0),
            (lon1, lat0),
            (lon1, lat1),
            (lon1, lat0),
            (lon0, lat0)
            ])

        return geopandas.GeoSeries([poly]).__geo_interface__
