try:
    import geopandas
    import pandas
    import shapely
except ImportError:
    print("GeoPandas is not found. Please install GeoPandas first.")

import sys
from .libgeoda import GeoDa, GeoDaTable
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def print_crs(gdf_crs):
    prj_str = ''
    for k, v in gdf_crs.items():
        param = '+' + k + '=' + v + ' '
        prj_str += param
    return prj_str

def geopandas_to_geoda(gdf):
    print("geopandas_to_geoda")

    geoms = gdf.geometry
    n_rows = len(gdf)
    n_cols = gdf.columns.size
    col_nms = gdf.columns

    # Table
    gda_tbl = GeoDaTable()

    for i in range(n_cols):
        col_nm = str(col_nms[i])
        if col_nm == 'geometry':
            continue
        col_type = gdf[col_nm].dtype
        vals = gdf[col_nm].to_list()
        if col_type == 'float64' or col_type == 'float':
            gda_tbl.AddRealColumn(col_nm, vals)
        elif col_type == 'int64' or col_type == 'int':
            gda_tbl.AddIntColumn(col_nm, vals)
        else:
            gda_tbl.AddStringColumn(col_nm, vals)

    # Geoms
    wkb_bytes = bytes()
    if sys.version_info[0] < 3: wkb_bytes = bytearray()
    wkb_size = []
    for i in range(n_rows):
        wkb = geoms[i].to_wkb()
        wkb_bytes += wkb
        wkb_size.append(len(wkb))

    # map type
    gdf.geom_type
    map_type = "map_polygons"

    # random file name
    layer_name = id_generator()

    # projection
    prj = str(print_crs(gdf.crs))

    gda = GeoDa(gda_tbl, layer_name, map_type,  wkb_bytes, tuple(wkb_size), prj)

    return gda

def geoda_to_geopandas(gda):
    print("geoda_to_geopandas")

    n_cols = gda.GetNumCols()
    col_nms = gda.GetFieldNames()
    col_tps = gda.GetFieldTypes()

    # pandas DF
    data = {}
    for i in range(n_cols):
        c_nm = col_nms[i]
        c_tp = col_tps[i]
        if c_tp == "integer":
            data[c_nm] = gda.GetIntegerCol(c_nm)
        elif c_tp == "numeric":
            data[c_nm] = gda.GetNumericCol(c_nm)
        else:
            if sys.version_info[0] < 3: 
                vals = gda.GetStringCol(c_nm)
                vals = [str(i) for i in vals]
                data[c_nm] = vals
            else:
                data[c_nm] = gda.GetStringCol(c_nm)
    df = pandas.DataFrame(data)

    # geometries
    geoms = []
    wkb_array = gda.GetGeometryWKB()
    for wkb in wkb_array:
        if sys.version_info[0] < 3: wkb = bytearray(wkb)
        shapely_obj = shapely.wkb.loads(bytes(wkb))
        geoms.append(shapely_obj)

    gdf = geopandas.GeoDataFrame(df, geometry=geoms)

    # projection
    return gdf