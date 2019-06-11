#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2019 Christoph Fink, University of Helsinki
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.

""" A base class for self-aware database objects """

__all__ = [
    "Stratum"
]


import json
import requests
import shapely.geometry


from .databaseobject import (
    DatabaseObject
)
from .dictlike import (
    DictLike
)


class Stratum(DatabaseObject, DictLike):
    _ChildClass = None

    def __init__(self, url=None, data={}, *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.data = data
        self.cleanData()

    @property
    def children(self):
        return []

    def cleanData(self):
        # rename columns
        data = {}
        data["Stratum name"] = self.data.pop("Input Zone")
        data["Cause of change"] = self.data.pop("Change1")
        data["Survey type"] = self.data.pop("Type")
        data["Survey reliability"] = self.data.pop("Reliab.")
        try:
            data["Survey year"] = int(self.data.pop("Year"))
        except ValueError:
            data["Survey year"] = None
        try:
            data["Number of elephants (estimate)"] = \
                int(self.data.pop("Estimate").replace(",", ""))
        except ValueError:
            data["Number of elephants (estimate)"] = 0
        try:
            data["Number of elephants (95% C.L.)"] = \
                int(self.data.pop("95% C.L.").replace(",", ""))
        except ValueError:
            data["Number of elephants (95% C.L.)"] = 0
        data["Priority for Future Surveys"] = self.data.pop("PFS3")
        try:
            data["Area (km²)"] = int(self.data.pop("(km²)").replace(",", ""))
        except ValueError:
            data["Area (km²)"] = None

#        lon = self.data.pop("Lon.")
#        lat = self.data.pop("Lat.")
#
#        if lon[-1] == "W":
#            lon = "-" + lon[:-1]
#        else:
#            lon = lon[:-1]
#        if lat[-1] == "S":
#            lat = "-" + lat[:-1]
#        else:
#            lat = lat[:-1]
#
#        lon = float(lon)
#        lat = float(lat)
#
#        self.data["centroid"] = shapely.geometry.Point(lon, lat)

        data["url"] = self._url

        try:
            geojson = json.loads(
                requests.get(
                    self._url + "/map"
                ).text
            )

            for feature in geojson["features"]:
                properties = feature["properties"]
                if (
                    properties["aed_name"] == data["Stratum name"]
                    or properties["aed_name"] in data["Stratum name"]
                    or data["Stratum name"] in properties["aed_name"]
                ):
                    data["aed_stratum"] = properties["aed_stratum"]
                    data["geometry"] = shapely.geometry.shape({
                        "type": feature["type"],
                        "coordinates": feature["coordinates"]
                    })
                    break

        except json.decoder.JSONDecodeError:
            data["aed_stratum"] = None
            data["geometry"] = None

        self.data = data
