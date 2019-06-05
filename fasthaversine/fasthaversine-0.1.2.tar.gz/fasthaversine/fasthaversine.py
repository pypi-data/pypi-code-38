import numpy as np

# mean earth radius - https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
_AVG_EARTH_RADIUS_KM = 6371.0088

# Unit values taken from http://www.unitconversion.org/unit_converter/length.html
_CONVERSION_TO_KILOMETERS = 1.0
_CONVERSION_TO_METERS = 1000.0
_CONVERSION_TO_MILES = 0.621371192
_CONVERSION_TO_NAUTICAL_MILES = 0.539956803
_CONVERSION_TO_FEETS = 3280.839895013
_CONVERSION_TO_INCHES = 39370.078740158


def haversine(points1, points2, unit='km'):
	points1 = np.asarray(points1)
	points2 = np.asarray(points2)

	if points1.shape[0] != points2.shape[0] or points1.shape[1] != 2 or points2.shape[1] != 2:
		raise ValueError('Dimension of input arrays should be the same.')

	avg_earth_radius = _get_avg_earth_radius(unit)

	# convert angles from degrees to radians.
	points1 = np.radians(points1)
	points2 = np.radians(points2)

	lat1, lon1 = points1[:, 0], points1[:, 1]
	lat2, lon2 = points2[:, 0], points2[:, 1]

	lat_diff = lat1 - lat2
	lon_diff = lon1 - lon2

	d = np.sin(lat_diff * 0.5) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lon_diff * 0.5) ** 2

	return 2 * avg_earth_radius * np.arcsin(np.sqrt(d))


def _get_avg_earth_radius(unit):
	if unit == 'km':
		return _AVG_EARTH_RADIUS_KM
	elif unit == 'm':
		return _AVG_EARTH_RADIUS_KM * _CONVERSION_TO_METERS
	elif unit == 'mile':
		return _AVG_EARTH_RADIUS_KM * _CONVERSION_TO_MILES
	elif unit == 'nmile':
		return _AVG_EARTH_RADIUS_KM * _CONVERSION_TO_NAUTICAL_MILES
	elif unit == 'feet':
		return _AVG_EARTH_RADIUS_KM * _CONVERSION_TO_FEETS
	elif unit == 'inch':
		return _AVG_EARTH_RADIUS_KM * _CONVERSION_TO_INCHES
	else:
		raise ValueError('unit should be "km", "m", "mile", "nmile", "feet" or "inch". Found {0}.'.format(unit))

