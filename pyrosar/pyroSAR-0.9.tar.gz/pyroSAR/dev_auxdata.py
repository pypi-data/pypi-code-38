import os
from pyroSAR import identify
from pyroSAR.auxdata import DEMHandler
from spatialist import bbox

with bbox({'xmin': 11.5, 'xmax': 11.9, 'ymin': 51, 'ymax': 51.5}, crs=4326) as box:
    with DEMHandler([box]) as handler:
        for demType in ['AW3D30', 'SRTM 1Sec HGT', 'SRTM 3Sec', 'TDX90m']:
            print(handler.coord_ids(box.extent, demType))
