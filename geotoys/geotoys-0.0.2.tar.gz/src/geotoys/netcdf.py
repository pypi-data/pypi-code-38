"""
Methods for perfoming common tasks with NetCDF files
"""

def find_dim(nc, name):
    KEY_NAMES = {
        'time': ['time', 'Time'],
        'lon': ['lon', 'longitude'],
        'lat': ['lat', 'latitude']
        }

    var = None
    for k in KEY_NAMES[name]:
        if k in nc.variables:
            var = k
            break

    if not var:
        raise ValueError(
            f'Variable {name} not found in netCDF. '
            f'Available variables: {nc.variables.keys}'
            )

    return k


def get_lons_lats(nc):
    """
    Read longitude and latitude values from NetCDF
    """
    lons = nc.variables[find_dim(nc, 'lon')][:]
    lats = nc.variables[find_dim(nc, 'lat')][:]

    return lons, lats


def get_timestamps(nc):
    """
    Read timestamps from netCDF time variable
    """
    import netCDF4
    import numpy
    import pandas

    # Find time variable
    time_key = find_dim(nc, 'time')

    # Get timestamps from netCDF time variable
    timestamps = None
    if time_key:
        try:
            times = nc.variables[time_key]
            timestamps = netCDF4.num2date(times[:], times.units)
            timestamps = numpy.array([pandas.Timestamp(ts) for ts in timestamps])
        except Exception as e:
            raise e

    return timestamps
