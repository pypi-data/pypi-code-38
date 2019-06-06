"""
Methods for generating datasets in various formats from GeoTIFF files
"""
import concurrent.futures
import rasterio
import numpy
import pandas

from tfol.utils import make_nparray, utc_timestamp

def as_xarray(catalog):
    """
    Create an xarray dataset from a collection of GeoTiff files
    """
    raise NotImplementedError()


def as_zarr(catalog):
    """
    Create a zarr dataset from a collection of GeoTiff files

    Zarr datasets are optimal Dask analysis.
    """
    raise NotImplementedError()


def _sample(fp, x, y, bands):
    """
    Produce data frame with row of band values for each point

    Parameters
    ----------
    fp: str
        Path to GeoTIFF file to be sampled
    xy: list of tuple
        x, y coordinate pairs
    bands: list of str
        Names corresponding to each band of data in the GeoTIFFs

    Returns
    -------
    df: pandas.DataFrame
        Dataframe containing data sampled from GeoTIFF. Each row corresponds to sample
        from each location sampled.
    """
    from tfol.utils import timestamp_from_filename

    try:
        # Cast to iterable if single coordinate and merge to list of points
        xy = numpy.vstack([make_nparray(x), make_nparray(y)]).T

        # Open GeoTiff, sample all bands for given locations
        src = rasterio.open(fp)
        result = src.sample(xy)

        # Generate band names if not provided
        if not bands:
            # Labels from GeoTIFF descriptions
            if any(src.descriptions):
                bands = src.descriptions
            # Generic enumerated labels
            else:
                bands = [f"band_{i}" for i in range(len(src.descriptions))]

        # Create dataframe from rasterio sample generator, and timestamps and locations
        df = pandas.DataFrame(result, columns=bands)
        df["timestamp"] = [timestamp_from_filename(fp)]*len(df)
        df["x"] = x
        df["y"] = y

    except Exception as e:
        raise e

    return df

def as_dataframe(files, x, y, bands=None, n_cpu=3):
    """
    Create a dataframe from GeoTIFFs for given time(-range) and position(s)

    Parameters
    ----------
    files: list of str
        List of GeoTIFF file paths to sample for points and compile to a DataFrame
    x: list of floats
        X coordinate positions corresponding to coordinate system in GeoTIFFs
    y: list of floats
        Y coordinate positions corresponding to coordinate system in GeoTIFFs
    bands: list of str
        Names corresponding to each band of data in the GeoTIFFs
    n_cpu: int
        Number of CPUs to use for running the GeoTIFF sampling

    Returns
    -------
    df: pandas.DataFrame
        Dataframe containing data sampled from all provided GeoTIFFs
    """

    # Sample all points for each file concurrently
    dataframes = list()
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_cpu) as executor:
        futures = [executor.submit(_sample, fp, x, y, bands) for fp in files]
        for future in concurrent.futures.as_completed(futures):
            # Append resulting dataframe file file to list of those to be merged
            try:
                dataframes.append(future.result())
            except Exception as e:
                raise e
            else:
                continue

    # Concatenate dataframes, sort and index by time and positions
    index_cols = ["timestamp", "x", "y"]
    df = pandas.concat(dataframes).sort_values(index_cols).set_index(index_cols)

    return df
