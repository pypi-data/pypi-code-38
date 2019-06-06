"""Read-process-write"""

import concurrent.futures
from itertools import islice
from time import sleep

import rasterio


CHUNK = 100

infile = '/home/sean/satellite/nearmap/sf2423.tif'
outfile = '/tmp/concurred.tif'


def chunkify(iterable, chunk=CHUNK):
    it = iter(iterable)
    while True:
        piece = list(islice(it, chunk))
        if piece:
            yield piece
        else:
            return


#def compute(window, data):
#    sleep(0.1)
#    return (window, data)


def compute(path, window):
    with rasterio.open(path) as src:
        data = src.read(window=window)
    sleep(0.01)
    return data[::-1]


def run(max_workers=1):

    with rasterio.open(infile) as src:

        with rasterio.open(outfile, "w", **src.profile) as dst:

            windows = [window for ij, window in dst.block_windows()]

            for window in windows:

                result = compute(infile, window)
                #result = src.read(window=window)
                #sleep(0.01)
                dst.write(result, window=window)


if __name__ == "__main__":
    import sys
    max_workers = int(sys.argv[1])
    run(max_workers)
