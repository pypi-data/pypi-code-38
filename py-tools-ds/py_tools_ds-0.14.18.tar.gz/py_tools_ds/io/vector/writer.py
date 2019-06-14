# -*- coding: utf-8 -*-
import os

import ogr
import osr

from ...dtypes.conversion import get_dtypeStr
from ...geo.projection import EPSG2WKT


__author__ = "Daniel Scheffler"


def write_shp(path_out, shapely_geom, prj=None, attrDict=None):
    shapely_geom = [shapely_geom] if not isinstance(shapely_geom, list) else shapely_geom
    attrDict = [attrDict] if not isinstance(attrDict, list) else attrDict
    # print(len(shapely_geom))
    # print(len(attrDict))
    assert len(shapely_geom) == len(attrDict), "'shapely_geom' and 'attrDict' must have the same length."
    assert os.path.exists(os.path.dirname(path_out)), 'Directory %s does not exist.' % os.path.dirname(path_out)

    print('Writing %s ...' % path_out)
    if os.path.exists(path_out):
        os.remove(path_out)
    ds = ogr.GetDriverByName("Esri Shapefile").CreateDataSource(path_out)

    if prj is not None:
        prj = prj if not isinstance(prj, int) else EPSG2WKT(prj)
        srs = osr.SpatialReference()
        srs.ImportFromWkt(prj)
    else:
        srs = None

    geom_type = list(set([gm.type for gm in shapely_geom]))
    assert len(geom_type) == 1, 'All shapely geometries must belong to the same type. Got %s.' % geom_type

    layer = \
        ds.CreateLayer('', srs, ogr.wkbPoint) if geom_type[0] == 'Point' else\
        ds.CreateLayer('', srs, ogr.wkbLineString) if geom_type[0] == 'LineString' else \
        ds.CreateLayer('', srs, ogr.wkbPolygon) if geom_type[0] == 'Polygon' else None  # FIXME

    if isinstance(attrDict[0], dict):
        for attr in attrDict[0].keys():
            assert len(attr) <= 10, "ogr does not support fieldnames longer than 10 digits. '%s' is too long" % attr
            DTypeStr = get_dtypeStr(attrDict[0][attr])
            FieldType = \
                ogr.OFTInteger if DTypeStr.startswith('int') else \
                ogr.OFTReal if DTypeStr.startswith('float') else \
                ogr.OFTString if DTypeStr.startswith('str') else \
                ogr.OFTDateTime if DTypeStr.startswith('date') else None
            FieldDefn = ogr.FieldDefn(attr, FieldType)
            if DTypeStr.startswith('float'):
                FieldDefn.SetPrecision(6)
            layer.CreateField(FieldDefn)  # Add one attribute

    for i in range(len(shapely_geom)):
        # Create a new feature (attribute and geometry)
        feat = ogr.Feature(layer.GetLayerDefn())
        feat.SetGeometry(ogr.CreateGeometryFromWkb(shapely_geom[i].wkb))  # Make a geometry, from Shapely object

        list_attr2set = attrDict[0].keys() if isinstance(attrDict[0], dict) else []

        for attr in list_attr2set:
            val = attrDict[i][attr]
            DTypeStr = get_dtypeStr(val)
            val = int(val) if DTypeStr.startswith('int') else float(val) if DTypeStr.startswith('float') else \
                str(val) if DTypeStr.startswith('str') else val
            feat.SetField(attr, val)

        layer.CreateFeature(feat)
        feat.Destroy()

    # Save and close everything
    del ds, layer
