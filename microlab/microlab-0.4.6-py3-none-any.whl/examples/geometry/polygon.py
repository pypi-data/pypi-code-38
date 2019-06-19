from microlab.signals import Signal_2D
from microlab.samples.__init__ import dataset_npArray
from microlab.geometry.polygons import create_polygon

if __name__ == '__main__':
    signal = Signal_2D(values=dataset_npArray, verbose=True)
    polygon = create_polygon(signal=signal, verbose=True)
    print(polygon)
    print(polygon.exterior.xy)
