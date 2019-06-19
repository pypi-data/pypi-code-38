from microlab.signals import Signal_2D
from microlab.geometry.lines import create_line
from microlab.plots.__init__ import Plot_Intersection


class Intersection:
    coordinates = [[], []]
    points = []

    def __init__(self, name='' , signal_a=Signal_2D(), signal_b=Signal_2D(), verbose=False):
        self.name = name

        if signal_a is None or signal_b is None:
            print(' Signals is required')
        else:
            self.signal_a = signal_a
            self.signal_b = signal_b
            self.line_a = create_line(signal=self.signal_a, verbose=False)
            self.line_b = create_line(signal=self.signal_b, verbose=False)
            self.points = self.find_intersect_points(verbose=verbose)

    def show_coordinates(self):
        print('[ {}   Intersection'.format(self.name))
        for i, intersection in enumerate(self.coordinates):
            if i == 0:
                print(' X: {}'.format(intersection))
            elif i == 1:
                print(' Y: {}'.format(intersection))

    def show(self, title='Intersection', marker='o'):
        Plot_Intersection(intersection=self, title=title, marker=marker)

    def find_intersect_points(self, verbose=False):
        self.coordinates = [[], []]
        intersection_result = self.line_a.intersection(self.line_b)
        # print('res: {}'.format(res))

        self.points = []
        try:
            # more than one points found
            if len(intersection_result):
                if verbose:
                    print('{} signals has {} intersected points  '.format(self.name,len(intersection_result)))

            # iterate in points
            for point in intersection_result:

                # collect point
                self.points.append(point)
                x, y = point.xy

                # collect coordinates
                self.coordinates[0].append(x)
                self.coordinates[1].append(y)

                # if verbose:
                #     print('+ {}'.format(point), type(point))

        except:
            """ Only one intersection point found """
            if verbose:
                print('one intersection point found')

            # collect point
            point = intersection_result
            self.points.append(point)

            # collect coordinates
            x, y = point.xy
            self.coordinates[0].append(x)
            self.coordinates[1].append(y)

            if verbose:
                print('+ {}'.format(point), type(point))
        return self.points
