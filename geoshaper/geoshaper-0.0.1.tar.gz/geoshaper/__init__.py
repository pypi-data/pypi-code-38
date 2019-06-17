from json import loads
from os import remove
from shapely import geometry
from topojson import topojson
import fiona
import geopandas as gpd
import pandas as pd

DEFAULT_FORMAT = "geojson"
INPUT_FILE = "shapes"
OUTPUT_NAME = "output"

class GeoShaper:
    def __init__(self, folder_name=INPUT_FILE):
        self.gdf = self._convert(folder_name) if isinstance(folder_name, str) else folder_name


    def _isvalid(self, geom):
        try:
            geometry.shape(geom)
            return 1
        except:
            return 0


    def _maybe_cast_to_multigeometry(self, geom):
        upcast_dispatch = {
            geometry.Point: geometry.MultiPoint, 
            geometry.LineString: geometry.MultiLineString, 
            geometry.Polygon: geometry.MultiPolygon
        }
        caster = upcast_dispatch.get(type(geom), lambda x: x[0])
        return caster([geom])


    def _convert(self, folder_name):
        collection = list(fiona.open(folder_name, "r"))

        df = pd.DataFrame(collection)
        df["isvalid"] = df["geometry"].apply(lambda x: self._isvalid(x))
        df = df[df["isvalid"] == 1]

        collection = loads(df.to_json(orient="records"))
        # Converts shapes to geoDataFrame
        gdf = gpd.GeoDataFrame.from_features(collection)
        gdf.geometry = gdf.geometry.apply(self._maybe_cast_to_multigeometry)

        return gdf


    def to_geojson(self, output_name=OUTPUT_NAME):
        gdf = self.gdf
        gdf.to_file(output_name, driver="GeoJSON")


    def to_topojson(self, output_name=OUTPUT_NAME, quantization=1e6, simplify=0.0001):
        gdf = self.gdf
        gdf.to_file("_temp_geojson.json", driver="GeoJSON")
        topojson("_temp_geojson.json", output_name, quantization=quantization, simplify=simplify)
        remove("_temp_geojson.json")