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


import geopandas
import os.path
import sys

from .lib import (
    DatabaseRoot
)


def main():
    try:
        outputFilename = sys.argv[1]
        if outputFilename in ["--help", "-h"]:
            print(
                (
                    "Usage: \n" +
                    "    {script:s} [outputFilename=output.gpkg]"
                ).format(script=os.path.basename(sys.argv[0])),
                file=sys.stderr
            )
            return -1

    except IndexError:
        outputFilename = "africanelephantdatabase.gpkg"

    for year in DatabaseRoot():
        try:
            del df  # noqa: F821
        except UnboundLocalError:
            pass
        for continent in year:
            for region in continent:
                for country in region:
                    # print(country.name)
                    for inputSystem in country:
                        # print("    " + inputSystem.name)
                        data = {
                            "Continent": continent.name,
                            "Region": region.name,
                            "Country": country.name,
                            "inputSystem": inputSystem.name
                        }
                        for stratum in inputSystem:
                            data.update(stratum.data)
                            try:
                                df.loc[len(df)] = data  # noqa: F821
                            except UnboundLocalError:
                                df = geopandas.GeoDataFrame(data)  # noqa: F821

        df = df.drop_duplicates(list(df.columns)[:-1])

        df["geometry"].crs = {'init': 'epsg:4326'}
        df.to_file(
            outputFilename,
            layer=year.name,
            driver="GPKG"
        )


if __name__ == "__main__":
    main()
