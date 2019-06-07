from __future__ import division
from scipy.stats import norm as normal
import numpy as np
#from sage.all import *
import copy # For deep copying objects

class Ztable(object):
    def __init__(self):
        None

    def get_prob(self, z):
        z = round(z, 2)
        if z > 3.49:
            return 1.0
        elif z < -3.49:
            return 0.0
        else:
            return round(normal.cdf(z, 0, 1), 4)

    def get_zscore(self, p):
        p = round(p, 4)
        return round(normal.ppf(p, 0, 1), 2)

def get_finite_dist(count, precision):
    # Returns a finite probability distribution
    # Returns a finite list, P, of 'count' probabilities rounded to 'precision' decimal places such that sum(P) = 1
    cuts = np.sort(np.random.choice(range(1, 10**precision), size = count - 1, replace = False)/10**precision)
    P = np.zeros(count)
    for i in range(0, count - 1):
        P[i] = cuts[i] - np.sum(P)
    P[-1] = 1 - np.sum(P)
    return P

def partition_set(E, size):
    # Partitions the set E into 'size' non-empty subsets of random length
    if size > len(E):
        raise ValueError('Size cannot be greater than the length of the set.')

    # Randomly select the sizes of the partitions
    cuts = sorted(np.random.choice(range(1,len(E)), size = size - 1, replace = False))
    sizes = [cuts[i] - cuts[i - 1] for i in range(len(cuts))]
    sizes[0] = cuts[0]

    partitions = []
    for size in sizes:
        # Select a random subset from E of length size
        random_subset = set([E.pop() for i in range(size)])
        partitions.append(random_subset)
    partitions.append(E)

    return partitions

def get_set_tex(E):
    elements = ', '.join(map(str, E))
    return r'\{{ {0} \}}'.format(elements)

#########################################################################
############################# My LaTeX ##################################
def my_latex(obj):
    # Wrapper function for Sage's latex function
    # If latex(obj) returns an unsatisfactory string, add a new key:value pair
    # to latex_dict using the output of repr(obj) as the key and the prefered
    # LaTeX representation as the key

    # Dictionary entries should be:
    # output of repr(obj) : 'prefered LaTeX string'
    latex_dict = {"<built-in function le>":'\leq'
                  , "<built-in function ge>":'\geq'
                  , "<built-in function lt>":'<'
                  , "<built-in function gt>":'>'
                  , "<built-in function eq>":'='
                 }
    # The return line is equivalent to this commented code
    #if repr(obj) in latex_dict.keys():
    #    tex = latex_dict[repr(obj)]
    #else:
    #    tex = latex(obj)
    return latex_dict.get(repr(obj), latex(obj))

############################# My LaTeX ##################################
#########################################################################


#########################################################################
###################### cartesian_plane ##################################
class cartesian_plane(object):
    def __init__(self, size):
        # ranges is a dictionary in the form ranges = dict(xmin = -11.5, xmax = 11.5, ymin = -11.5, ymax = 11.5)
        self.ranges = dict(xmin = -1 * size
                      , xmax = size
                      , ymin = -1 * size
                      , ymax = size
                      )
        self.x_range, self.y_range = self.get_implicit_ranges(self.ranges)

        # Define the standard axes. This dictionary should be used when showing the graph
        #     instance.show(**axes_style)
        # OR  \sageplot{instance, **std_axes}
        self.axes_style = dict(axes = True
                      , frame=False
                      , aspect_ratio=1
                      , figsize=(3.5,3.5)
                      , axes_pad = False
                      , gridlines = 'minor'
                      , ticks = [5, 5]
                      , gridlinesstyle = {'linestyle':'solid', 'color':'0.5'}
                     )

        # Define the line style for plotting
        #self.line_style = dict(color = 'black')

        # Test questions should use self.blank_plane
        # Test keys should use self.plot
        self.blank_plane = self.get_plane(**self.ranges)

    def plot(self, expr):
        # Returns a the graph of the expression on the standard cartesian plane
        g = copy.deepcopy(self.blank_plane)
        g += implicit_plot(expr, self.x_range, self.y_range, linestyle = 'solid', color = 'black')

        return g

    def get_plane(self, xmin = -11.5, xmax = 11.5, ymin = -11.5, ymax = 11.5):
        # Returns a graphics object in the style of a textbook cartesian plane

        # Define the style for each axis
        axis_style = dict(width = 1
                        , head = 1
                        , arrowsize = 4
                        , rgbcolor = (0,0,0)
                        , zorder = 8
                        , legend_label = ''
                       )
        g = Graphics()
        g += arrow((xmin, 0), (xmax, 0), **axis_style)
        g += text('$x$', (xmax - 1, 1), rgbcolor=(0, 0, 0), fontsize = 13, fontweight = 'bold')
        g += arrow((0, ymin), (0, ymax), **axis_style)
        g += text('$y$', (1, ymax - 1), rgbcolor=(0, 0, 0), fontsize = 13, fontweight = 'bold')

        return g

    def get_implicit_ranges(self, ranges):
        # ranges is a dictionary in the form ranges = dict(xmin = -11.5, xmax = 11.5, ymin = -11.5, ymax = 11.5)
        var('x y')
        x_range = (x, ranges['xmin'], ranges['xmax'])
        y_range = (y, ranges['ymin'], ranges['ymax'])

        return x_range, y_range
########################## cartesian_plane ################################
###########################################################################

###########################################################################
###################### inequalities_plot ##################################
class inequalities_plot(object):
    def __init__(self, inequalities, ranges):
        # inequalities is a list of statements to plot
        # ranges is a dictionary in the form ranges = dict(xmin = -11.5, xmax = 11.5, ymin = -11.5, ymax = 11.5)
        self.inequalities = inequalities
        self.ranges = ranges
        self.x_range, self.y_range = self.get_implicit_ranges(self.ranges)

        # Find the corner points of the solution set
        self.corners = self.get_corners()

        # Define the standard axes. This dictionary should be when showing the graph
        #     instance.show(**axes_style)
        # OR  \sageplot{instance, **std_axes}
        self.axes_style = dict(axes = True
                      , frame=False
                      , aspect_ratio=1
                      , figsize=(3.5,3.5)
                      , axes_pad = False
                      , gridlines = 'minor'
                      , ticks = [5, 5]
                      , gridlinesstyle = {'linestyle':'solid', 'color':'0.5'}
                     )

        # Define the line style for plotting
        self.line_style = dict(color = 'black')

        # Test questions should use self.blank_plane
        # Test keys should use self.plot
        self.blank_plane = self.get_xy_plane(**self.ranges)
        self.plot = copy.deepcopy(self.blank_plane)
        # Plot the solution set
        self.plot += region_plot(self.inequalities, self.x_range, self.y_range, incol = 'grey', alpha = 0.5)
        # Plot the boundary equations of the inequalities
        for i in self.inequalities:
            boundary_eq = self.get_boundary_eq(i)
            op = i.operator()
            if op == operator.gt or op == operator.lt:
                self.plot += implicit_plot(boundary_eq, self.x_range, self.y_range, linestyle = 'dashed', color = 'black')
            else:
                self.plot += implicit_plot(boundary_eq, self.x_range, self.y_range, linestyle = 'solid', color = 'black')


    def get_xy_plane(self, xmin = -11.5, xmax = 11.5, ymin = -11.5, ymax = 11.5):
        # Returns a graphics object in the style of a textbook cartesian plane

        # Define the style for each axis
        axis_style = dict(width = 1
                        , head = 1
                        , arrowsize = 4
                        , rgbcolor = (0,0,0)
                        , zorder = 8
                        , legend_label = ''
                       )
        g = Graphics()
        g += arrow((xmin, 0), (xmax, 0), **axis_style)
        g += text('$x$', (xmax - 1, 1), rgbcolor=(0, 0, 0), fontsize = 13, fontweight = 'bold')
        g += arrow((0, ymin), (0, ymax), **axis_style)
        g += text('$y$', (1, ymax - 1), rgbcolor=(0, 0, 0), fontsize = 13, fontweight = 'bold')

        return g

    def get_implicit_ranges(self, ranges):
        # ranges is a dictionary in the form ranges = dict(xmin = -11.5, xmax = 11.5, ymin = -11.5, ymax = 11.5)
        var('x y')
        x_range = (x, ranges['xmin'], ranges['xmax'])
        y_range = (y, ranges['ymin'], ranges['ymax'])

        return x_range, y_range

    def get_boundary_eq(self, i):
        var('x y')
        left = i.lhs()
        right = i.rhs()
        eq = left == right
        return eq

    def write_pair(self, pair):
        # Converts a tuple of expressions like (x == 5, y == 7),
        # into and ordered pair of floats like (5, 7)
        var('x y')
        return x.subs(pair), y.subs(pair)

    def get_corners(self):
        var('x y')
        # Get the solutions set
        region = solve_ineq(self.inequalities, [x, y])

        # Identify the corner points of the solution set
        corners = []
        for partition in region:
            # Corner points will be a list of equations
            is_eq = [s.operator() == operator.eq for s in partition]
            if all(is_eq):
                pair = self.write_pair(partition)
                corners.append(pair)
        return corners
###################### inequalities_plot ##################################
###########################################################################


###########################################################################
######################### grid_point ######################################
class grid_point(object):
    def __init__(self, pair, ranges):
        self.pair = pair
        self.x = pair[0]
        self.y = pair[1]

        self.ranges = ranges
        self.xmin = ranges['xmin'] + 1
        self.xmax = ranges['xmax'] - 1
        self.ymin = ranges['ymin'] + 1
        self.ymax = ranges['ymax'] - 1

        # Slope sets contain all integer coordinate points on the line passing through self.pair with the given slope
        # These sets will be stored in a dictionary with key value pairs "slope" : slope_set
        self.slopes = self.get_slopes()
        self.slope_sets = self.get_slope_sets()

    def get_slopes(self):
        slopes = []
        for yint in range(self.ymin, self.ymax + 1):
            slope = Rational((self.y - yint, self.x))
            slopes.append(slope)
        return slopes

    def get_slope_sets(self):
        # Slope sets contain all integer coordinate points on the line passing through self.pair with the given slope
        # These sets will be stored in a dictionary with key value pairs "slope" : slope_set
        slope_sets = {}
        for slope in self.slopes:
            # Include self.pair in the set
            slope_set = {self.pair}
            # Start the crawler at self.pair. The crawler must be mutable.
            crawler = list(self.pair)
            # Use the slope to set the step sizes for the x and y coordinates
            delta = [slope.denominator(), slope.numerator()]
            # Crawl along the line and save points that are in the ranges
            crawler = [c + d for c, d in zip(crawler, delta)]
            while self.xmin <= crawler[0] <= self.xmax and self.ymin <= crawler[1] <= self.ymax:
                # Convert the crawler to a tuple and add it to the slope_set
                slope_set.add(tuple(crawler))
                # Crawl
                crawler = [c + d for c, d in zip(crawler, delta)]

            # Now crawl in the negative x direction
            crawler = list(self.pair)
            crawler = [c - d for c, d in zip(crawler, delta)]
            while self.xmin <= crawler[0] <= self.xmax and self.ymin <= crawler[1] <= self.ymax:
                slope_set.add(tuple(crawler))
                crawler = [c - d for c, d in zip(crawler, delta)]

            # Add 'slope' : slope_set to the dictionary
            slope_sets[str(slope)] = slope_set

        return slope_sets
######################### grid_point ######################################
###########################################################################


###########################################################################
################### system_of_inequalities ################################

class system_of_inequalities(object):
    def __init__(self):
        pass

    def get_system(self, num_of_ineq = 0):
        # Returns a randomly selected system with the appropriate number of inequalities
        num_string = str(num_of_ineq)
        if num_of_ineq < 3:
            raise ValueError('No code has been written for num_of_ineq = {}'.format(str(num_of_ineq)))
        elif num_of_ineq == 3:
            systems = [
                {'K' : [[1, -1], [-3, 1], [1, 2]],
                 'B' : [-3, -1, 2],
                 'R' : [operator.ge, operator.ge, operator.ge],
                 'low' : -5,
                 'high' : 1},
                {'K' : [[1, -2], [3, -1], [-1, 4]],
                 'B' : [-4, 1, 4],
                 'R' : [operator.ge, operator.le, operator.ge],
                 'low' : -5,
                 'high' : 3},
                {'K' : [[1, -3], [3, -1], [1, 3]],
                 'B' : [-9, 0, 3],
                 'R' : [operator.ge, operator.le, operator.ge],
                 'low' : -5,
                 'high' : 2},
                {'K' : [[1, 3], [3, -4], [3, -2]],
                 'B' : [-3, 8, -2],
                 'R' : [operator.le, operator.le, operator.ge],
                 'low' : 0,
                 'high' : 6}
                ]
            return np.random.choice(systems)
        elif num_of_ineq == 4:
            raise ValueError('No code has been written for num_of_ineq = {0}'.format(str(num_of_ineq)))


        return system

################### system_of_inequalities ################################
###########################################################################