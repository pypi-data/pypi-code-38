from shapely.geometry.linestring import LineString

from microlab.geometry.points import create_points

def create_line(signal, verbose=False):
    x_values = signal.y
    y_values = signal.x
    if verbose:
        print('Creating Line |'.format(x_values.__len__()), end=' .....')
    points = create_points(signal=signal, verbose=False)
    line = LineString(points)
    if verbose:
        print('[ OK  ] created {} '.format(line.geom_type))
    return line

