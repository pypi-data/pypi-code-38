from microlab.signals import Signal_1D, Signal_2D
from microlab.methods.intersection import Intersection
from microlab.types import is_1d_signal, is_2d_signal, is_point, is_polygon, is_intersection
from microlab.geometry.points import Point
from microlab.geometry.polygons import Polygon

if __name__ == "__main__":
    print('\n~ TEST DATA TYPES')
    print('[  I  ]   Signal 1D ', end=".....")
    if is_1d_signal(object=Signal_1D()):
        print('[ OK ] identify Signal 1D')

    print('[  I  ]   Signal 2D ', end=".....")
    if is_2d_signal(object=Signal_2D()):
        print('[ OK ] identify Signal 2D')

    print('\n~ TEST CORE TYPES')
    print('[  I  ]   Intersection', end=" ..")
    if is_intersection(object=Intersection()):
        print('[ OK ] identify Intersection')


    print('\n~ TEST GEOMETRY TYPES')
    print('[  I  ]   Point', end=" .........")
    if is_point(object=Point()):
        print('[ OK ] identify Point')

    print('[  I  ]   Polygon', end=" .......")
    if is_polygon(object=Polygon()):
        print('[ OK ] identify Polygon')



