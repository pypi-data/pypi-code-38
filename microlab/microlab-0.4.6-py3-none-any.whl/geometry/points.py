from shapely.geometry.point import Point


def create_points(signal, verbose=False):
    '''

    :param signal:
    :param verbose:
    :return:             a tuple of Points    e.x: (  Point(x1,y1), Point(x2,y2) , ... Point(xn,yn) )
    '''
    x_values = signal.y
    y_values = signal.x
    points = []
    if verbose:
        print('Creating Points |'.format(x_values.__len__()), end=' .....')
    for x, y in zip(x_values, y_values):
        point = Point(x, y)
        points.append(point)
    if verbose:
        print('[ OK  ] created {} points'.format(points.__len__()))
    return points
