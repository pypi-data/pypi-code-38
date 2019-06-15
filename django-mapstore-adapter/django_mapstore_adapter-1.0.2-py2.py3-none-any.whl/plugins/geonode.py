# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from __future__ import absolute_import, unicode_literals

try:
    import json
except ImportError:
    from django.utils import simplejson as json

import logging
import traceback

from ..utils import (GoogleZoom,
                     get_wfs_endpoint,
                     get_valid_number,
                     to_json)
from ..settings import (MAP_BASELAYERS,
                        CATALOGUE_SERVICES,
                        CATALOGUE_SELECTED_SERVICE
                        )

from ..converters import BaseMapStore2ConfigConverter

from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings


logger = logging.getLogger(__name__)


class GeoNodeMapStore2ConfigConverter(BaseMapStore2ConfigConverter):

    def convert(self, viewer, request):
        """
            input: GeoNode JSON Gxp Config
            output: MapStore2 compliant str(config)
        """
        # Initialization
        viewer_obj = json.loads(viewer)

        map_id = None
        if 'id' in viewer_obj and viewer_obj['id']:
            try:
                map_id = int(viewer_obj['id'])
            except BaseException:
                pass

        data = {}
        data['version'] = 2

        # Map Definition
        try:
            # Map Definition
            ms2_map = {}
            ms2_map['projection'] = viewer_obj['map']['projection']
            ms2_map['units'] = viewer_obj['map']['units']
            ms2_map['zoom'] = viewer_obj['map']['zoom']
            ms2_map['maxExtent'] = viewer_obj['map']['maxExtent']
            ms2_map['maxResolution'] = viewer_obj['map']['maxResolution']

            # Backgrouns
            backgrounds = self.getBackgrounds(viewer, MAP_BASELAYERS)
            if backgrounds:
                ms2_map['layers'] = backgrounds
            else:
                ms2_map['layers'] = MAP_BASELAYERS + [
                    # TODO: covnert Viewer Background Layers
                    # Add here more backgrounds e.g.:
                    # {
                    # 	"type": "wms",
                    # 	"url": "https://demo.geo-solutions.it/geoserver/wms",
                    # 	"visibility": True,
                    # 	"opacity": 0.5,
                    # 	"title": "Weather data",
                    # 	"name": "nurc:Arc_Sample",
                    # 	"group": "Meteo",
                    # 	"format": "image/png",
                    # 	"bbox": {
                    # 		"bounds": {
                    # 			"minx": -25.6640625,
                    # 			"miny": 26.194876675795218,
                    # 			"maxx": 48.1640625,
                    # 			"maxy": 56.80087831233043
                    # 		},
                    # 		"crs": "EPSG:4326"
                    # 	}
                    # }, ...
                ]

            # Security Info
            info = {}
            info['canDelete'] = False
            info['canEdit'] = False
            info['description'] = viewer_obj['about']['abstract']
            info['id'] = map_id
            info['name'] = viewer_obj['about']['title']
            ms2_map['info'] = info

            # Overlays
            overlays, selected = self.get_overlays(viewer, request=request)
            if selected and 'name' in selected and selected['name'] and not map_id:
                # We are generating a Layer Details View
                center, zoom = self.get_center_and_zoom(viewer_obj['map'], selected)
                ms2_map['center'] = center
                ms2_map['zoom'] = zoom

                try:
                    # - extract from GeoNode guardian
                    from geonode.layers.views import (_resolve_layer,
                                                      _PERMISSION_MSG_MODIFY,
                                                      _PERMISSION_MSG_DELETE)
                    if _resolve_layer(request,
                                      selected['name'],
                                      'base.change_resourcebase',
                                      _PERMISSION_MSG_MODIFY):
                        info['canEdit'] = True

                    if _resolve_layer(request,
                                      selected['name'],
                                      'base.delete_resourcebase',
                                      _PERMISSION_MSG_DELETE):
                        info['canDelete'] = True
                except BaseException:
                    tb = traceback.format_exc()
                    logger.debug(tb)
            else:
                # We are getting the configuration of a Map
                # On GeoNode model the Map Center is always saved in 4326
                ms2_map['center'] = {
                    'x': get_valid_number(viewer_obj['map']['center'][0]),
                    'y': get_valid_number(viewer_obj['map']['center'][1]),
                    'crs': 'EPSG:4326'
                }

                try:
                    # - extract from GeoNode guardian
                    from geonode.maps.views import (_resolve_map,
                                                    _PERMISSION_MSG_SAVE,
                                                    _PERMISSION_MSG_DELETE)
                    if _resolve_map(request,
                                    str(map_id),
                                    'base.change_resourcebase',
                                    _PERMISSION_MSG_SAVE):
                        info['canEdit'] = True

                    if _resolve_map(request,
                                    str(map_id),
                                    'base.delete_resourcebase',
                                    _PERMISSION_MSG_DELETE):
                        info['canDelete'] = True
                except BaseException:
                    tb = traceback.format_exc()
                    logger.debug(tb)

            for overlay in overlays:
                if 'name' in overlay and overlay['name']:
                    ms2_map['layers'].append(overlay)

            data['map'] = ms2_map
        except BaseException:
            # traceback.print_exc()
            tb = traceback.format_exc()
            logger.debug(tb)

        # Default Catalogue Services Definition
        try:
            ms2_catalogue = {}
            ms2_catalogue['selectedService'] = CATALOGUE_SELECTED_SERVICE
            ms2_catalogue['services'] = CATALOGUE_SERVICES
            data['catalogServices'] = ms2_catalogue
        except BaseException:
            # traceback.print_exc()
            tb = traceback.format_exc()
            logger.debug(tb)

        # Additional Configurations
        if map_id:
            from mapstore2_adapter.api.models import MapStoreResource
            try:
                ms2_resource = MapStoreResource.objects.get(id=map_id)
                ms2_map_data = ms2_resource.data.blob
                if 'map' in ms2_map_data:
                    del ms2_map_data['map']
                data.update(ms2_map_data)
            except BaseException:
                # traceback.print_exc()
                tb = traceback.format_exc()
                logger.debug(tb)
        return json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True)

    def getBackgrounds(self, viewer, defaults):
        import copy
        backgrounds = copy.copy(defaults)
        for bg in backgrounds:
            bg['visibility'] = False
        try:
            viewer_obj = json.loads(viewer)
            layers = viewer_obj['map']['layers']
            # sources = viewer_obj['sources']
            for layer in layers:
                if 'group' in layer and layer['group'] == "background":
                    # source = sources[layer['source']]
                    def_background = [bg for bg in backgrounds if bg['name'] == layer['name']]
                    background = def_background[0] if def_background else None
                    if background:
                        background['opacity'] = layer['opacity'] if 'opacity' in layer else 1.0
                        background['visibility'] = layer['visibility'] if 'visibility' in layer else False
        except BaseException:
            backgrounds = copy.copy(defaults)
            tb = traceback.format_exc()
            logger.debug(tb)
        return backgrounds

    def get_overlays(self, viewer, request=None):
        overlays = []
        selected = None
        try:
            viewer_obj = json.loads(viewer)
            layers = viewer_obj['map']['layers']
            sources = viewer_obj['sources']

            for layer in layers:
                if 'group' not in layer or layer['group'] != "background":
                    source = sources[layer['source']]
                    overlay = {}
                    if 'url' in source:
                        overlay['type'] = "wms" if 'ptype' not in source or \
                            source['ptype'] != 'gxp_arcrestsource' else 'arcgis'
                        overlay['url'] = source['url']
                        overlay['visibility'] = layer['visibility'] if 'visibility' in layer else True
                        overlay['singleTile'] = layer['singleTile'] if 'singleTile' in layer else False
                        overlay['selected'] = layer['selected'] if 'selected' in layer else False
                        overlay['hidden'] = layer['hidden'] if 'hidden' in layer else False
                        overlay['handleClickOnLayer'] = layer['handleClickOnLayer'] if \
                            'handleClickOnLayer' in layer else False
                        overlay['wrapDateLine'] = layer['wrapDateLine'] if 'wrapDateLine' in layer else False
                        overlay['hideLoading'] = layer['hideLoading'] if 'hideLoading' in layer else False
                        overlay['useForElevation'] = layer['useForElevation'] if 'useForElevation' in layer else False
                        overlay['fixed'] = layer['fixed'] if 'fixed' in layer else False
                        overlay['opacity'] = layer['opacity'] if 'opacity' in layer else 1.0
                        overlay['title'] = layer['title'] if 'title' in layer else ''
                        overlay['name'] = layer['name'] if 'name' in layer else ''
                        overlay['group'] = layer['group'] if 'group' in layer else ''
                        overlay['format'] = layer['format'] if 'format' in layer else "image/png"
                        overlay['bbox'] = {}

                        if 'dimensions' in layer:
                            overlay['dimensions'] = layer['dimensions']

                        if 'search' in layer:
                            overlay['search'] = layer['search']

                        if 'style' in layer:
                            overlay['style'] = layer['style']

                        if 'capability' in layer:
                            capa = layer['capability']
                            if 'styles' in capa:
                                overlay['styles'] = capa['styles']
                            if 'style' in capa:
                                overlay['style'] = capa['style']
                            if 'abstract' in capa:
                                overlay['abstract'] = capa['abstract']
                            if 'attribution' in capa:
                                overlay['attribution'] = capa['attribution']
                            if 'keywords' in capa:
                                overlay['keywords'] = capa['keywords']
                            if 'dimensions' in capa and capa['dimensions']:
                                overlay['dimensions'] = self.get_layer_dimensions(dimensions=capa['dimensions'])
                            if 'llbbox' in capa:
                                overlay['llbbox'] = capa['llbbox']
                            if 'storeType' in capa and capa['storeType'] == 'dataStore':
                                overlay['search'] = {
                                    "url": get_wfs_endpoint(request),
                                    "type": "wfs"
                                }
                            if 'bbox' in capa:
                                bbox = capa['bbox']
                                if viewer_obj['map']['projection'] in bbox:
                                    proj = viewer_obj['map']['projection']
                                    bbox = capa['bbox'][proj]
                                    overlay['bbox']['bounds'] = {
                                        "minx": get_valid_number(bbox['bbox'][0]),
                                        "miny": get_valid_number(bbox['bbox'][1]),
                                        "maxx": get_valid_number(bbox['bbox'][2]),
                                        "maxy": get_valid_number(bbox['bbox'][3])
                                    }
                                    overlay['bbox']['crs'] = bbox['srs']

                        if 'bbox' in layer and not overlay['bbox']:
                            if 'bounds' in layer['bbox']:
                                overlay['bbox'] = layer['bbox']
                            else:
                                overlay['bbox']['bounds'] = {
                                    "minx": get_valid_number(layer['bbox'][0],
                                                             default=layer['bbox'][2],
                                                             complementar=True),
                                    "miny": get_valid_number(layer['bbox'][1],
                                                             default=layer['bbox'][3],
                                                             complementar=True),
                                    "maxx": get_valid_number(layer['bbox'][2],
                                                             default=layer['bbox'][0],
                                                             complementar=True),
                                    "maxy": get_valid_number(layer['bbox'][3],
                                                             default=layer['bbox'][1],
                                                             complementar=True)
                                }
                                overlay['bbox']['crs'] = layer['srs'] if 'srs' in layer else \
                                    viewer_obj['map']['projection']

                        if 'getFeatureInfo' in layer and layer['getFeatureInfo']:
                            if 'fields' in layer['getFeatureInfo'] and layer['getFeatureInfo']['fields'] and \
                                    'propertyNames' in layer['getFeatureInfo'] and \
                                    layer['getFeatureInfo']['propertyNames']:
                                fields = layer['getFeatureInfo']['fields']
                                propertyNames = layer['getFeatureInfo']['propertyNames']
                                featureInfo = {'format': 'TEMPLATE'}

                                _template = '<div>'
                                for _field in fields:
                                    _template += '<div class="row">'
                                    _template += '<div class="col-xs-4" style="font-weight: bold; word-wrap: break-word;">%s</div> \
                                        <div class="col-xs-8" style="word-wrap: break-word;">${properties.%s}</div>' % \
                                        (propertyNames[_field] if propertyNames[_field] else _field, _field)
                                    _template += '</div>'
                                _template += '</div>'

                                featureInfo['template'] = _template
                                overlay['featureInfo'] = featureInfo

                            # Push extraParams into GeoNode layerParams
                            if 'extraParams' in layer and layer['extraParams']:
                                overlay['extraParams'] = layer['extraParams']

                    # Restore the id of ms2 layer
                    if "extraParams" in layer and "msId" in layer["extraParams"]:
                        overlay["id"] = layer["extraParams"]["msId"]
                    overlays.append(overlay)
                    if not selected or ('selected' in layer and layer['selected']):
                        selected = overlay
        except BaseException:
            tb = traceback.format_exc()
            logger.debug(tb)

        return (overlays, selected)

    def get_layer_dimensions(self, dimensions):
        url = getattr(settings, "GEOSERVER_PUBLIC_LOCATION", "")
        if url.endswith('ows'):
            url = url[:-3]
        url += "gwc/service/wmts"
        dim = []
        for attr, value in dimensions.items():
            if attr == "time":
                nVal = {"name": attr, "source": {"type": "multidim-extension", "url": url}}
                dim.append(nVal)
            else:
                value["name"] = attr
                dim.append(value)
        return dim

    def get_center_and_zoom(self, view_map, overlay):
        center = {
            "x": get_valid_number(
                overlay['bbox']['bounds']['minx'] + (
                    overlay['bbox']['bounds']['maxx'] - overlay['bbox']['bounds']['minx']
                ) / 2),
            "y": get_valid_number(
                overlay['bbox']['bounds']['miny'] + (
                    overlay['bbox']['bounds']['maxy'] - overlay['bbox']['bounds']['miny']
                ) / 2),
            "crs": overlay['bbox']['crs']
        }
        zoom = view_map['zoom']
        # max_extent = view_map['maxExtent']
        # map_crs = view_map['projection']
        ov_bbox = [get_valid_number(overlay['bbox']['bounds']['minx']),
                   get_valid_number(overlay['bbox']['bounds']['miny']),
                   get_valid_number(overlay['bbox']['bounds']['maxx']),
                   get_valid_number(overlay['bbox']['bounds']['maxy']), ]
        ov_crs = overlay['bbox']['crs']
        (center_m, zoom_m) = self.project_to_mercator(ov_bbox, ov_crs, center=center)
        if center_m is not None and zoom_m is not None:
            return (center_m, zoom_m)
        else:
            return (center, zoom)

    def project_to_mercator(self, ov_bbox, ov_crs, center=None):
        try:
            srid = int(ov_crs.split(':')[1])
            srid = 3857 if srid == 900913 else srid
            poly = Polygon((
                (ov_bbox[0], ov_bbox[1]),
                (ov_bbox[0], ov_bbox[3]),
                (ov_bbox[2], ov_bbox[3]),
                (ov_bbox[2], ov_bbox[1]),
                (ov_bbox[0], ov_bbox[1])), srid=srid)
            gcoord = SpatialReference(4326)
            ycoord = SpatialReference(srid)
            trans = CoordTransform(ycoord, gcoord)
            poly.transform(trans)
            try:
                if not center:
                    center = {
                        "x": get_valid_number(poly.centroid.coords[0]),
                        "y": get_valid_number(poly.centroid.coords[1]),
                        "crs": "EPSG:3857"
                    }
                zoom = GoogleZoom().get_zoom(poly) + 1
            except BaseException:
                center = (0, 0)
                zoom = 0
                tb = traceback.format_exc()
                logger.debug(tb)
        except BaseException:
            tb = traceback.format_exc()
            logger.debug(tb)

        return (center, zoom)

    def viewer_json(self, viewer, request):
        """
            input: MapStore2 compliant str(config)
            output: GeoNode JSON Gxp Config
        """
        return to_json(viewer)
