"""Concurrent read-process-write example"""

import concurrent.futures
from itertools import islice
from time import sleep

import rasterio


CHUNK = 100


def chunkify(iterable, chunk=CHUNK):
    it = iter(iterable)
    while True:
        piece = list(islice(it, chunk))
        if piece:
            yield piece
        else:
            return


def compute(path, window):
    """Simulates an expensive computation

    Gets source data for a window, sleeps, reverses bands.

    Note: Numpy ufuncs release GIL and are parallelizable.
    """
    with rasterio.open(path) as src:
        data = src.read(window=window)
    sleep(0.1)
    return data[::-1]


def main(infile, outfile, max_workers=1):

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

        with rasterio.open(infile) as src:

            with rasterio.open(outfile, "w", **src.profile) as dst:

                windows = [window for ij, window in dst.block_windows()]

                for chunk in [windows]:  # chunkify(windows):

                    future_to_window = dict()

                    for window in chunk:
                        future = executor.submit(compute, infile, window)
                        future_to_window[future] = window

                    for future in concurrent.futures.as_completed(future_to_window):
                        window = future_to_window[future]
                        result = future.result()
                        dst.write(result, window=window)


if __name__ == "__main__":
    import sys

    infile, outfile, num = sys.argv[1:4]
    main(infile, outfile, max_workers=int(num))
