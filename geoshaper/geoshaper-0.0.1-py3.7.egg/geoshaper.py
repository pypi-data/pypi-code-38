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

    def convert(self, folder_name=INPUT_FILE, output_format=DEFAULT_FORMAT, output_name=OUTPUT_NAME):
        if output_format not in ["geojson", "topojson"]:
            raise "output_format only accepts geojson/topojson"

        collection = list(fiona.open(folder_name, "r"))

        df = pd.DataFrame(collection)
        df["isvalid"] = df["geometry"].apply(lambda x: self._isvalid(x))
        df = df[df["isvalid"] == 1]

        collection = loads(df.to_json(orient="records"))
        # Converts shapes to geoDataFrame
        gdf = gpd.GeoDataFrame.from_features(collection)
        gdf.geometry = gdf.geometry.apply(self._maybe_cast_to_multigeometry)

        output = "{}.json".format(OUTPUT_NAME)

        if output_format == "geojson":
            gdf.to_file(output, driver="GeoJSON")
        else:
            gdf.to_file("temp_geojson.json", driver="GeoJSON")
            topojson("temp_geojson.json", output, quantization=1e6, simplify=0.0001)
            remove("temp_geojson.json")
        
        print("{} has been saved successfully!".format(output))