# -*- coding: utf-8 -*-
from __future__ import division
import codecs
import math
import copy
import json
import numpy as np
from operator import attrgetter
import time

#=======================================================================================================================
class RiverPoint():
    def __init__(self, chainage=0.0, x=0.0, y=0.0):
        self.chainage = chainage
        self.x = x #Geographic x-coordinate in whatever cartesian coordinate system you are using
        self.y = y #Geographic x-coordinate in whatever cartesian coordinate system you are using

    def __eq__(self, other):
        if not isinstance(other, RiverPoint):
            return False
        return self.chainage==other.chainage and self.x == other.x and self.y==other.y


    def __hash__(self):
        return hash((self.chainage,self.x,self.y))
#=======================================================================================================================
class Pp():  #Perimeterpoint
    def __init__(self, dx, dz, marker='', x=None, y=None):
        self.dx = dx #x-distance (positive or nagative) from an abitrary datum (however, usually the center of the river, which could the where the lowest perimeter point is)
        self.dz = dz #distance from the lowest point in the cross section to this point
        self.marker = marker #'left bank' 'right bank' 'center point'
        self.x=x #Geographic x-coordinate (Metadata, not used for any calculation)
        self.y=y #Geographic y-coordinate (Metadata, not used for any calculation)

#=======================================================================================================================
class Xs(): #Cross section
    def __init__(self, x=0.0, y=0.0, z=0.0, chainage=0.0, perimeterpoints=[], name ='', is_closed=False):
        self.name = name
        self.description = ''
        self.chainage = chainage
        self.x = x  #Geographic x-coordinate river midpoint in the cross section (typically the lowest point) (not use for calculations)
        self.y = y  #Geographic z-coordinate river midpoint in the cross section (typically the lowest point) (not use for calculations)
        self.z = z #The level of the lowest point in the cross section
        self.radius_type = 'hydraulic radius'  # must be either 'hydraulic radius' or 'resistance radius'
        self.manning_number = 10.0
        self.is_closed = is_closed
        self.is_weir = False
        self.depth = 1.0 # used as boundary condition, the calculation starts with this cross section
        self.catchmentarea = 0.0 # not used in the calculation.
        self.flow = 0.0
        self.fastmode = False
        self.weighting = 0.0  # weighting must be in interval [0,1]. 0 means only downstream xs properties are used
        if perimeterpoints:
            self.pps = perimeterpoints
        else:
            self.pps = []

        self._dz_table = [] #Internal table updated by the Xs.update method.
        self._surface_widths_table = []  # Internal table updated by the Xs.update method.
        self._areasTable = [] # #Internal table updated by the Xs.update method.

    @property
    def left_bank_pp(self):
        left_bank_pp = self.pps[0]
        for pp in self.pps:
            if pp.marker == 'left bank':
                left_bank_pp = pp
                break
        return left_bank_pp

    @property
    def right_bank_pp(self):
        right_bank_pp = self.pps[-1]
        for pp in reversed(self.pps):
            if pp.marker == 'right bank':
                right_bank_pp = pp
                break
        return right_bank_pp

    @property
    def center_point(self):
        for pp in self.pps:
            if pp.marker == 'center point':
                return pp
        ps1 = self.pps[self.pps.index(self.left_bank_pp):self.pps.index(self.right_bank_pp) + 1]
        return min(ps1, key=attrgetter('dz'))

    def _get_active_perimeter(self):
        """
        Extract the part to the cross sections perimeter, that is within the the range from left bank to
        right bank. Vertical walls are added at the locations of the left bank and the rigth bank. If no banks
        are defined, these walls are added at the first and the last perimeter point.
        :return: <[Pp]> List of perimeter points
        """
        left_bank_pp = self.left_bank_pp
        right_bank_pp = self.right_bank_pp
        max_bank_dz = max(left_bank_pp.dz, right_bank_pp.dz)
        ps1 = self.pps[self.pps.index(left_bank_pp):self.pps.index(right_bank_pp) + 1]
        ps1.insert(0, Pp(left_bank_pp.dx, max_bank_dz + 100.0))  # insert vertical walls
        ps1.append(Pp(right_bank_pp.dx, max_bank_dz + 100.0))  # insert vertical walls
        return ps1

    def update(self):
        """
        Updates the internal tables for the hydraulic functions in order to improve the computational efficiency.
        These table are only used when running in fast mode (the property Xs.fastmode = True)Updates the internal
        tables for the hydraulic functions in order to improve the computational efficiency. These table are only
        used when running in fast mode (the property Xs.fastmode = True)
        """
        modeSettings = self.fastmode
        self.fastmode  = False

        ps1 = self._get_active_perimeter()
        self._dz_table = list(set([p.dz for p in ps1]))  # relative levels into sorted nparray with sorted values
        self._dz_table.sort()
        self._dz_table[-1] = self._dz_table[-1] - 1.0 #to have the perimeter point at bit higher than the table depths


        self._areasTable = np.array([self.get_wetted_area(dz) for dz in self._dz_table])
        # self._perimeter_lengths_table = np.array([self.get_wetted_perimeter_length(dz) for dz in self._dz_table])
        self._surface_widths_table = np.array([self.get_surface_width(dz) for dz in self._dz_table])
        # self._hydraulic_widths_table = np.array([self.get_hydraulic_width(dz) for dz in self._dz_table])

        self.fastmode = modeSettings

    def get_wetted_perimeter_length(self, depth):
        ps1 = self._get_active_perimeter() # insert vertical walls

        if self.is_closed is True:
            depth = min(depth, self.left_bank_pp.dz, self.right_bank_pp.dz)

        wetted_perimeter_length = 0.0
        for n in range(len(ps1) - 1):
            pp1, pp2 = sorted(ps1[n:n+2], key=attrgetter('dz'))
            if pp1.dz == pp2.dz:
                if pp1.dz <= depth:
                    wetted_perimeter_length += math.fabs(pp2.dx - pp1.dx)
            elif pp1.dz < depth:
                length = math.sqrt((pp2.dx - pp1.dx)**2 + (pp2.dz - pp1.dz)**2)
                if pp2.dz <= depth:
                    wetted_perimeter_length += length
                else:
                    wetted_perimeter_length += length * (depth - pp1.dz) / (pp2.dz - pp1.dz)
        return wetted_perimeter_length

    def get_wetted_area(self, depth):
        if self.fastmode:
            if self.is_closed is True and depth >= min(self.left_bank_pp.dz, self.right_bank_pp.dz):
                area = self._areasTable[-1]
            else:
                for n in range(len(self._dz_table)):
                    if self._dz_table[n] > depth:
                        break
                area = self._areasTable[n-1]
                ddt = self._dz_table[n] - self._dz_table[n-1]
                dd = depth - self._dz_table[n-1]

                sw = self._surface_widths_table[n]

                dda = self._areasTable[n] - self._areasTable[n-1]
                da = pow(dd, 2)*(ddt * sw - dda)/pow(ddt, 2) + dd * (2 * dda/ddt - sw)
                area += da
        else:
            if depth <= 0.0:
                area = 0.0
            else:
                wp = self.get_wetted_polygon(depth)
                area = 0
                n = 0
                while n < len(wp) - 1:
                    area += wp[n].dx * wp[n + 1].dz
                    area -= wp[n + 1].dx * wp[n].dz
                    n += 1
                area += wp[-1].dx * wp[0].dz
                area -= wp[-1].dz * wp[0].dx
                area = 0.5 * abs(area)
        return area

    def get_wetted_polygon(self, depth):
        """
        Creating at polygon which covers the wetted perimeter of the cross section
        :param depth: The depth
        :return: List of perimeter points (hymod.Pp)
        """
        if self.is_closed is True:
            depth = min(depth, self.left_bank_pp.dz, self.right_bank_pp.dz)

        ps1 = self._get_active_perimeter()
        ps2 = []
        for n in range(0, len(ps1) - 1):
            ps2.append(ps1[n])
            if (ps1[n].dz < depth and ps1[n+1].dz > depth) or (ps1[n].dz > depth and ps1[n+1].dz < depth):
                if ps1[n].dx == ps1[n+1].dx:
                    px = Pp(ps1[n].dx, depth)
                else:
                    px = Pp(ps1[n].dx + (depth - ps1[n].dz) * (ps1[n + 1].dx - ps1[n].dx) / (ps1[n + 1].dz - ps1[n].dz), depth)
                ps2.append(px)
        ps3 = [p for p in ps2 if p.dz <= depth]
        return ps3

    def get_surface_width(self, depth):
        """
        Calculates the length (width) of the free water surface in the cross section for a given depth. Situations
        where the depth corresponds to at lateral section in the cross section (some internal riverbank) this part is
        not added to the width. However, if this lateral section is part of the lid of the cross section, it added to
        the width.
        :param depth: <float> The depth
        :return: <float> the length (width) of the free water surface
        """
        ps1 = self._get_active_perimeter()

        xcs = []  # list of x-coordinates where the surface crosses as secment of the cross section perimeter
        for n in range(len(ps1) - 1):
            if (ps1[n].dz < depth and ps1[n + 1].dz > depth) or (ps1[n].dz > depth and ps1[n + 1].dz < depth):
                xcs.append((depth - ps1[n].dz) * (ps1[n + 1].dx - ps1[n].dx) / (ps1[n + 1].dz - ps1[n].dz) + ps1[n].dx)
            elif n > 0:
                if ps1[n].dz == depth and ((ps1[n - 1].dz < depth and ps1[n + 1].dz >= depth) or (ps1[n - 1].dz >= depth and ps1[n + 1].dz < depth)):
                    xcs.append(ps1[n].dx)

        xcs.sort()
        width = 0
        for n in range(0, len(xcs) - 1, 2):
            width += xcs[n + 1] - xcs[n]

        return width

    def get_conveyance(self, depth):
        a = self.get_wetted_area(depth)  # the wetted area
        if self.radius_type == 'hydraulic radius':
            p = self.get_wetted_perimeter_length(depth)
            if p > 0:
                k = self.manning_number * a * pow(a/p, 0.66666667)
            else:
                k = 0.0
            return k
        elif self.radius_type == 'resistance radius':
            r = self.get_resistance_radius(depth)
            return self.manning_number * a * pow(r, 0.66666667)
        else:
            raise Exception('Illegal radius type defined for cross section at chainage ' + str(self.chainage))


    def get_critical_depth(self, flow):
        g = 9.82
        criteria = 0.000001
        d1 = 0.0
        d2 = 10.0
        n = 0
        maxIterations = 1000

        while (d2 - d1) > criteria:
            n+= 1
            if n > maxIterations:
                raise Exception('failed to converge, while calculating critical depth')
            d = (d2 + d1)/2.0
            a = self.get_wetted_area(d)
            b = self.get_hydraulic_width(d) #same as surface witdt for simpel crosssections
            hd = a/b #Hydraulic depth
            v = flow/a
            f2 = (v * v) / (g * hd) # froudes number to the power 2
            if f2 > 1.0:
                d1 = d
            else:
                d2 = d
        return d

    def get_normal_depth(self, slope):
        if slope <= 0:
            raise Exception('The slope argument was less or equal to zero. Normal depth is not defined for such bedslopes')
        n = 0
        d1 = 0.01
        d2 = 100.0
        while math.fabs(d1 - d2) > 0.0001:
            n += 1
            if n > 1000:
                raise Exception('failed to converge in get_normal_depth method')
            d = 0.5 * (d1 + d2)
            energy_gradient = pow(self.flow / self.get_conveyance(d), 2)
            if energy_gradient >= slope:
                d1 = d
            else:
                d2 = d

        return d

    def get_resistance_radius(self, depth):
        ps1 = self._get_active_perimeter()
        #TODO: resistance radius can only be calculated for regular cross sections (convex cross section). Find at way to eveluate cross section the check this

        if depth <= 0:
            return 0
        r = 0
        for n in range(len(ps1)-1):
            pp1 = ps1[n]
            pp2 = ps1[n+1]
            if pp1.dz < depth or pp2.dz < depth:
                if pp1.dz >= depth and pp2.dz < depth:
                    d1 = 0
                    d2 = depth - pp2.dz
                    dx = (depth - pp2.dz) * (pp2.dx - pp1.dx) / (pp1.dz - pp2.dz)
                elif pp1.dz < depth and pp2.dz >= depth:
                    d1 = depth - pp1.dz
                    d2 = 0
                    dx = (depth - pp1.dz) * (pp2.dx - pp1.dx) / (pp2.dz - pp1.dz)
                elif pp1.dz < depth and pp2.dz < depth:
                    d1 = depth - pp1.dz
                    d2 = depth - pp2.dz
                    dx = pp2.dx - pp1.dx
                if d1 == d2:
                    r += dx * pow(d1, 1.5)
                else:
                    r += 0.4 * dx * (pow(d2, 2.5) - pow(d1, 2.5))/ (d2 - d1)
        return pow(r/self.get_wetted_area(depth), 2)

    def get_hydraulic_width(self, depth):
        """
        Calculates accumulated width of all wetted bodies. For convex cross sections this corresponds to the surface width
        :param depth:
        :return: The accumulated width of all wetted bodies. For convex cross sections this corresponds to the surface width
        """
        wp = self.get_wetted_polygon(depth)
        pg =[]
        allpgs = []
        for n in range(len(wp)-1):
            pg.append(wp[n])
            if n == len(wp)-2:
                pg.append(wp[-1])
                allpgs.append(pg[:])
            elif wp[n].dz == depth and (wp[n].dz == wp[n+1].dz):
                allpgs.append(pg[:])
                pg = []

        selectedpgs = []
        for n in range(len(allpgs)):
            canAppend = True
            for i in range(len(allpgs)):
                if i != n and max(allpgs[n], key=attrgetter('dx')).dx < max(allpgs[i], key=attrgetter('dx')).dx and min(allpgs[n], key=attrgetter('dx')).dx > min(allpgs[i], key=attrgetter('dx')).dx:
                    canAppend = False
            if canAppend:
                selectedpgs.append(allpgs[n])

        width = 0.0
        for pg in selectedpgs:
            width += max(pg, key=attrgetter('dx')).dx - min(pg, key=attrgetter('dx')).dx
        return width

#======================================================================================================================
class Reach():
    def __init__(self, name='no name'):
        self.xss = []   #list of crosssections
        self.name = name
        self.description = ''
        self.riverPoints = []
        self.calculated_water_levels = []
        self.observations = [] #list of tuples: [(chainage, waterlevel), (chainage, waterlevel).....]

    def calculate_water_levels(self, run_fast_mode=True, show_detailed_progress=False):
        """
        Calculated the water levels in the water levels in the reach. Water levels are calculated at the locations
        of the cross sections and at a number of locations between cross sections. The locations these points are
        determined based in the slope of the energy gradient.
        :return: calculated water levels as a list of tuples. [(chainage, water level), (chainage, water level) .....]
        """


        print('Calculating waterlevel for reach: %s containing %d crosssections' % (self.name, len(self.xss)))

        if run_fast_mode is True:
            for xs in self.xss:
                xs.update()
                xs.fastmode=True

        self.calculated_water_levels = []

        if len(self.xss)==0:
            self.calculated_water_levels.append((0,0))
            return


        self.calculated_water_levels.append((self.xss[0].chainage, self.xss[0].depth + self.xss[0].z))

        for n in range(len(self.xss)-1):
            if show_detailed_progress is True:
                print('calculating water levels for cross section %d of %d cross sections at chainage %.3f' % (n+1, len(self.xss), self.xss[n].chainage))

            ds_xs = self.xss[n]  #downstream cross section
            up_xs = self.xss[n+1] #upstream cross section

            if up_xs.is_weir is True:
                critical_depth = up_xs.get_critical_depth(up_xs.flow)
                if (ds_xs.depth + ds_xs.z) < (critical_depth + up_xs.z):
                    up_xs.depth = critical_depth
                else:
                    up_xs.depth = ds_xs.depth + ds_xs.z - up_xs.z
                continue

            sb = (up_xs.z - ds_xs.z) / (up_xs.chainage - ds_xs.chainage) #river bed slope
            dc = ds_xs.get_critical_depth(ds_xs.flow)  #TODO: Should maybe be moved inside the dx loop.

            if ds_xs.depth < dc:
                ds_xs.depth = dc  # todo

            d1 = ds_xs.depth

            x = ds_xs.chainage
            while x < up_xs.chainage:
                if d1 <= 0:
                    print('zero og negative depth in cross section at chainage: ' + str(ds_xs.chainage))
                    return [] #TODO:
                flow = Tools.interpw(x, ds_xs.chainage, up_xs.chainage, ds_xs.flow, up_xs.flow, ds_xs.weighting)
                wa1 = ds_xs.get_wetted_area(d1)  # Wetted area
                v1 = flow / wa1  # flow velocity
                e1 = (v1 * v1) / (2.0 * 9.82) + d1  # specific energy
                sf1 = pow(flow / ds_xs.get_conveyance(d1), 2)  # Energy gradient (Manning equation)

                idiff = math.fabs(sf1 - sb)

                dx_max = 10.
                dxCriteria = 0.001
                if idiff > 0.0:
                    dx = min(dxCriteria / idiff, up_xs.chainage - x)
                else:
                    dx = min(up_xs.chainage - x, dx_max)

                if dx < 0.001:
                    dx = 0.001

                diff = 1000.
                d_lower = dc  # Critical depth as lower limit for iterations
                d_upper = e1 * 1.1  # 10 % over energy hight used as upper limit for iterations
                n = 0  # iteration counter

                while math.fabs(diff) > 0.00001 and math.fabs(d_upper - d_lower) > 0.00001:

                    n += 1
                    if n > 100:
                        print('failed to converge, while calculating upstream depth (chainage = ' + str(x) + ')')  # Todo: This warning should perhaps not be here (this is actually a normal case when modelling weirs)..
                        d2 = dc
                        break
                    d2 = (d_lower + d_upper) / 2.
                    if True: #ds_xs.weighting == 0: #TODO: For some reason this works better. Needs mere attension.
                        wa2 = ds_xs.get_wetted_area(d2)  # This only to save computational time
                    else:
                        wa2 = Tools.interpw(x, ds_xs.chainage, up_xs.chainage, ds_xs.get_wetted_area(d2), up_xs.get_wetted_area(d2), ds_xs.weighting)
                    v2 = flow / wa2  # flow velocity
                    e2 = (v2 * v2) / (2. * 9.82) + d2  # specific energy
                    if ds_xs.weighting == 0.0:
                        con2 = ds_xs.get_conveyance(d2)  # This only to save computational time.
                    else:
                        con2 = Tools.interpw(x, ds_xs.chainage, up_xs.chainage, ds_xs.get_conveyance(d2), up_xs.get_conveyance(d2), ds_xs.weighting)
                    sf2 = pow(flow / con2, 2.0)  #Energy gradient
                    diff = e2 - e1 - (sf2 - sb) * dx  #TODO: concider if sf1 should be used rather than sf2 or perhaps (sf1 + sf2)/2
                    if diff > 0.0:
                        d_upper = d2
                    elif diff < 0.0:
                        d_lower = d2

                x += dx
                d1 = d2

                self.calculated_water_levels.append((x, d2 + (x - ds_xs.chainage) * sb + ds_xs.z))
            up_xs.depth = self.calculated_water_levels[-1][1] - up_xs.z

    def remove_xs(self,chainage):
        """
        Removes a cross section from the list of cross sections. Exceptions are raised for non existing cross section
        and if multiple cross sections by error has same chainage.
        :param chainage: The chainage property of the cross sections to be removed
        """
        xi = [i for i in range(len(self.xss)) if self.xss[i].chainage == chainage]
        if len(xi) == 0:
            raise Exception('The reach %s does not contain at cross section at chainage: %f' % (self.name, chainage))
        elif len(xi) > 1:
            raise Exception('The reach %s does not contains more than one cross section at chainage: %f' % (self.name, chainage))
        else:
            del self.xss[xi[0]]

    def update_perimeter_points_xy_coords(self, rotate180=False):
        """
        The perimeter point properties x and y (Pp.x and Pp.y) are assigned geographical coordinates under the
        assumption that the cross section is perpendicular to the reach. The coordinates are calculated based on
        coordinates of closest downstream and upstream river points. At the most upstream and downstream locations, an
        upstream og downstream river point way not exist. In this case the perimeter point coordinates are based only on
        cross section coordinates and one river point.
        :param rotate180: <bool> IF True, perimeter point coordinates are calculated for a situation, where the
        cross section is rotated 180 degrees. This has no effect on water level calculations.
        :return: no return value
        """

        get_unit_vec = lambda a: (a[0] / math.sqrt(a[0] * a[0] + a[1] * a[1]), a[1] / math.sqrt(a[0] * a[0] + a[1] * a[1]))
        get_normal_vec = lambda pa, pb: (pa[1] - pb[1], pb[0] - pa[0])


        for xs in self.xss:
            ds_p = None # Point at the location of the river point just downstream to the cross section
            us_p = None # Point at the location of the river point just upstream to the cross section

            for rp in self.riverPoints:
                if rp.chainage > xs.chainage:
                    us_p = (rp.x, rp.y)
                    break

            for rp in reversed(self.riverPoints):
                if rp.chainage < xs.chainage:
                    ds_p = (rp.x, rp.y)
                    break

            xs_p = (xs.x, xs.y)
            v = None

            if ds_p is not None and us_p is not None:
                us_v = get_unit_vec(get_normal_vec(xs_p, us_p))
                ds_v = get_unit_vec(get_normal_vec(ds_p, xs_p))
                v = get_unit_vec((0.5 * (us_v[0] + ds_v[0]), 0.5 * (us_v[1] + ds_v[1])))

            elif us_p is not None and ds_p is None:
                v = get_unit_vec(get_normal_vec(xs_p, us_p))

            elif ds_p is not None and us_p is None:
                v = get_unit_vec(get_normal_vec(ds_p, xs_p))

            if rotate180 is True:
                s = 1.
            else:
                s = -1.

            if v is not None:
                center_dx = xs.center_point.dx
                for p in xs.pps:
                    p.x = xs.x + s * v[0] * (p.dx - center_dx)
                    p.y = xs.y + s * v[1] * (p.dx - center_dx)

    def validate(self):
        """
        Validates the reach for inconsistencies. If such inconsistencies are found, an error message
        is printed to standard output.
        """
        for i in range(len(self.xss) - 1): #Cross sections
            xs = self.xss[i]
            if self.xss[i].chainage == self.xss[i+1].chainage:
                print('two cross sections are located chainage ' + str(self.xss[i].chainage) + '\n')
            if self.xss[i].chainage > self.xss[i + 1].chainage:
                print('cross section chainages are decreasing in upstream direction between cross sections at (index, chainage): ')
                print('(' + str(i) + ', '+ (str(self.xss[i].chainage)) + ') and ')
                print('(' + str(i+1) + ', ' + (str(self.xss[i+1].chainage)) + ')\n')
            if xs.radius_type != 'hydraulic radius' and xs.radius_type != 'resistance radius':
                print('Illegal radius type specified for cross section at chainage %f at index %d in reach %s\n' % (xs.chainage, i, self.name))
                print('The type must be either "hydraulic radius" or "resistance radius"\n')
            if xs.flow <= 0.0:
                print('zero or negative flow detected in xs at chainage %.3f in reach: %s' % (xs.chainage, self.name))
            for pp in xs.pps:
                if len([p for p in xs.pps if pp.dx == p.dx and pp.dz == p.dz]) > 1:
                    print('duplicate perimeter ponts were found in cross section at chainage %.3f in reach %s. (dx = %.3f, dz = %.3f)' % (xs.chainage, self.name, pp.dx, pp.dz))


        if len(self.riverPoints) < 2:
            print('The number of river points are: ' + str(len(self.riverPoints)) + ' a minimum of two riverpoints are required\n')

        for i in range(len(self.riverPoints) - 1): #River points
            if self.riverPoints[i].chainage == self.riverPoints[i+1].chainage:
                print('two river points are located chainage ' + str(self.riverPoints[i].chainage))
                print(' (x1 = ' + str(self.riverPoints[i].x) + ' y1= ' + str(self.riverPoints[i].y) + ') ')
                print(' (x2 = ' + str(self.riverPoints[i].x) + ' y2= ' + str(self.riverPoints[i].y) + ')\n ')
            if self.riverPoints[i].chainage > self.riverPoints[i + 1].chainage:
                print('river point chainages are decreasing in upstream direction between river points sections at (index, chainage): ')
                print('(' + str(i) + ', '+ (str(self.riverPoints[i].chainage)) + ') and ')
                print('(' + str(i+1) + ', ' + (str(self.riverPoints[i+1].chainage)) + ')\n')


#=======================================================================================================================
class Reach_network():
    def __init__(self, reaches=[], name=''):
        if reaches:
            self.reaches = reaches
        else:
            self.reaches = []
        self.name = name
        self.description = ''
        self.connections = []  #list of Connections

    def get_reach(self,name):
        """
        Finding and returning the reach object with the name as defined in param name.
        :param name: The reach name (Reach.name)
        :return: Reach object
        """
        reaches = [reach for reach in self.reaches if reach.name == name]
        if len(reaches) == 0:
            raise Exception('There is no reach with the name: ' + name)
        elif len(reaches) > 1:
            raise Exception('There are more than on reach in the reach network with the name: ' + name)
        else:
            return reaches[0]

    def remove_reach(self, name):
        """
        Removes a reach from the Reach_network
        :param name: The name of the reach to be removed (Reach.name)
        """
        reach = self.get_reach(name)
        cons = [con for con in self.connections if con.downstream_reach_name == reach.name or con.upstream_reach_name == reach.name]
        for con in cons:
            self.connections.remove(con)
        self.reaches.remove(reach)

    def calculate_water_levels(self, run_fast_mode=True, show_detailed_progress=False):
        """
        Calculates the water levels in all reaches in the reach network. The method invokes the
        Reach.calculate_water_levels() method for all reaches. The order of calculations depends on the connections
        defined for the reach network. The result from the calculations are assigned to
        the Reach.calculated_water_levels property for each reach in the network. These calculated water levels
        are organized as lists of tuples ([(chainage, water level), (chainage, water level)]
        """
        print('calculation started')
        computation_time_start = time.time()
        for reach in self.reaches:
            reach.calculated_water_levels = []

        for reach in self.reaches:
            if not [con.upstream_reach_name for con in self.connections].__contains__(reach.name): #no connection is defined
                reach.calculate_water_levels(run_fast_mode=run_fast_mode, show_detailed_progress=show_detailed_progress)

        while len([reach for reach in self.reaches if len(reach.calculated_water_levels) == 0]) > 0: #run until waterlevels in all reaches has been calculated.
            for con in self.connections:
                downstream_reach = self.get_reach(con.downstream_reach_name)
                upstream_reach = self.get_reach(con.upstream_reach_name)
                if len(upstream_reach.calculated_water_levels) == 0:
                    if len(downstream_reach.calculated_water_levels) > 0:  #meaning that water levels has already been calculated for the down stream river
                        boundary_water_level = np.interp(con.chainage, [a[0] for a in downstream_reach.calculated_water_levels], [a[1] for a in downstream_reach.calculated_water_levels])
                        upstream_reach.xss[0].depth = boundary_water_level - upstream_reach.xss[0].z
                        upstream_reach.calculate_water_levels(run_fast_mode=run_fast_mode, show_detailed_progress=show_detailed_progress)
        print('calculation completed. Computation time was %.3f seconds.' % (time.time() - computation_time_start))

    def save_as_json(self, filename, save_calculated_water_levels=False):
        """
        Saves geometry data, connections, hydraulic and numeric parameter in JSON text format. Observed water
        levels and water levels calculated between cross sections are not saved.
        :param filename: path and filename of the output JSON file
        """
#        with open(filename, 'w', encoding='utf-8') as file:
        file = codecs.open(filename, encoding='utf-8', mode='w')
        if True:
            file.write('{\n')
            file.write('  "reach network name": "%s",\n' % (self.name))
            file.write('  "description": "%s",\n' % (self.description))
            file.write('   "connections" : [\n')
            con_count = 0
            for con in self.connections:
                con_count += 1
                file.write('     {"downstream river name": "%s", "upstream river name": "%s", "chainage": %.3f}' % (con.upstream_reach_name, con.downstream_reach_name, con.chainage))
                if con_count == len(self.connections):
                    file.write('\n')
                else:
                    file.write(',\n')
            file.write('   ],\n')

            file.write('  "reaches": [\n')
            reach_count = 0
            for reach in self.reaches:
                reach_count += 1
                file.write('    {\n')  #Reach start
                file.write('      "reach name": "%s",\n' % (reach.name))
                file.write('      "description": "%s",\n' % (reach.description))
                file.write('      "xss": [\n')
                xs_count = 0
                for xs in reach.xss:
                    xs_count += 1
                    if xs.is_closed is True:
                        is_closed_str = 'true'
                    else:
                        is_closed_str = 'false'
                    if xs.is_weir is True:
                        is_weir_str = 'true'
                    else:
                        is_weir_str = 'false'

                    file.write('        {\n')
                    file.write('         "xs name": "%s",\n' % (xs.name))
                    file.write('         "description": "%s",\n' % (xs.description))
                    file.write('         "chainage": %.3f,  "x": %.3f, "y": %.3f, "z": %.3f, "manning number": %.3f,\n' % (xs.chainage, xs.x, xs.y, xs.z, xs.manning_number))
                    file.write('         "catchment area": %.3f, "flow": %.6f, "depth": %.3f, "weighting": %.3f, "is closed": %s,\n' % (xs.catchmentarea, xs.flow, xs.depth, xs.weighting, is_closed_str))
                    file.write('         "is weir": %s, "radius type": "%s",\n' % (is_weir_str, xs.radius_type))
                    file.write('         "pps": [\n')
                    pp_count = 0
                    for p in xs.pps:
                        pp_count += 1
                        if p.x is not None and p.y is not None:
                            file.write('            {"dx": %8.3f, "dz": %8.3f, "x": %.3f, "y": %.3f, "marker": "%s" }' % (p.dx, p.dz, p.x, p.y, p.marker))
                        else:
                            file.write('            {"dx": %8.3f, "dz": %8.3f, "x": null, "y": null, "marker": "%s" }' % (p.dx, p.dz, p.marker))
                        if pp_count == len(xs.pps):
                            file.write('\n')
                        else:
                            file.write(',\n')

                    file.write('         ]\n')
                    file.write('        }')
                    if xs_count == len(reach.xss):
                        file.write('\n')
                    else:
                        file.write(',\n')
                file.write('      ],\n')

                file.write('      "observations": [\n')
                obs_count = 0
                for observation in reach.observations:
                    obs_count += 1
                    file.write('         {"chainage": %.3f, "water level": %.3f}' % (observation[0], observation[1]))
                    if obs_count == len(reach.observations):
                        file.write('\n')
                    else:
                        file.write(',\n')
                file.write('      ],\n')


                file.write('      "calculated water levels": [\n')
                obs_count = 0
                if save_calculated_water_levels is True:
                    for wl in reach.calculated_water_levels:
                        obs_count += 1
                        file.write('         {"chainage": %.3f, "water level": %.3f}' % (wl[0], wl[1]))
                        if obs_count == len(reach.calculated_water_levels):
                            file.write('\n')
                        else:
                            file.write(',\n')
                file.write('      ],\n')

                file.write('      "river points": [\n')
                rp_count = 0
                for riverPoint in reach.riverPoints:
                    rp_count += 1
                    file.write('         {"chainage": %.3f, "x": %.3f, "y": %.3f}' % (riverPoint.chainage, riverPoint.x, riverPoint.y))
                    if rp_count == len(reach.riverPoints):
                        file.write('\n')
                    else:
                        file.write(',\n')
                file.write('      ]\n')
                file.write('    }')
                if reach_count == len(self.reaches):
                    file.write('\n')
                else:
                    file.write(',\n')
            file.write('  ]\n')
            file.write('}')
        file.close()

    def import_json_file(self,filename):
        """
        Imports geometry data, connections, hydraulic and numeric parameter in JSON text format. Observed water levels
        and water levels calculated between cross sections are not imported.
        :param filename: path and filename for the JSON file
        """
#        with open(filename, 'r', encoding='utf-8') as file:
        file = codecs.open(filename, encoding='utf-8', mode='r')
        data = json.load(file)
        file.close()

        self.name = data['reach network name']
        self.description = data['description']
        for jcon in data['connections']:
            self.connections.append(Connection(jcon['downstream river name'], jcon['upstream river name'], jcon['chainage']))
        for jreach in data['reaches']:
            reach = Reach()
            reach.name = jreach['reach name']
            reach.description = jreach['description']
            for jxs in jreach['xss']:
                xs = Xs()
                xs.name = jxs['xs name']
                xs.description = jxs['description']
                xs.x = jxs['x']
                xs.y = jxs['y']
                xs.z = jxs['z']
                xs.chainage = jxs['chainage']
                xs.catchmentarea = jxs['catchment area']
                xs.depth = jxs['depth']
                xs.flow = jxs['flow']
                xs.weighting = jxs['weighting']
                xs.is_closed = jxs['is closed']
                if jxs.get('is weir'): #TODO: to be removed when all json files are opdated with the is_weir property
                    xs.is_weir = jxs['is weir']
                xs.manning_number = jxs['manning number']
                xs.radius_type = jxs['radius type']
                pps = []
                for jpp in jxs['pps']:
                    pps.append(Pp(jpp['dx'], jpp['dz'], jpp['marker'], jpp['x'], jpp['y']))
                xs.pps = pps
                reach.xss.append(copy.deepcopy(xs))

            if jreach.get('calculated water levels'): #TODO: to be removed when all json files are opdated with the observations property
                reach.calculated_water_levels = []
                for jcalculated_water_levels in jreach['calculated water levels']:
                    reach.calculated_water_levels.append((jcalculated_water_levels['chainage'], jcalculated_water_levels['water level']))

            if jreach.get('observations'): #TODO: to be removed when all json files are opdated with the observations property
                observations = []
                for jobservation in jreach['observations']:
                    observations.append((jobservation['chainage'], jobservation['water level']))
                reach.observations = observations

            riverpoints = []
            for jriverPoint in jreach['river points']:
                riverpoints.append(RiverPoint(jriverPoint['chainage'], jriverPoint['x'], jriverPoint['y']))
            reach.riverPoints = riverpoints
            self.reaches.append(copy.deepcopy(reach))

    def validate(self):
        """
        Validates the whole system for inconsistencies. If such inconsistencies are found, an error message
        is printed to standard output. (error does not stop the execution)
        """
        print('Validating...\n')
        for reach in self.reaches:
            print('validating reach: ' + reach.name)
            reach.validate()

        # checking connections:
        for con in self.connections:
            if not [reach.name for reach in self.reaches].__contains__(con.upstream_reach_name):
                print('specified upstream_reach_name: ' + con.upstream_reach_name + ' in connections does not exist\n')

            if not [reach.name for reach in self.reaches].__contains__(con.downstream_reach_name):
                print('specified downstream_reach_name: ' + con.upstream_reach_name + ' in connections does not exist\n')

            downstream_reach = self.get_reach(con.downstream_reach_name)
            if con.chainage < downstream_reach.xss[0].chainage or con.chainage > downstream_reach.xss[-1].chainage:
                print('connection chainage: ' + str(con.chainage) +' is outside the range of chainage in downstream reach: ' + con.downstream_reach_name)


#=======================================================================================================================
class Connection():
    """
    Defines the connection between an upstream reach and a downstream reach. The connection is between the most
    downstream cross section (index zero) in the upstream reach and any location (defined be chainage) in the
    downstream reach. When a connection is defined, the upstream reach will use the calculated water level in the
    downstream reach at the connection point as boundary condition. This means that water levels in a reach connected
    to a downstream reach cannot be calculated before the water levels are calculated in the downstream reach.
    When using the Reach.calculate_water_levels() method this is taken care of. The downstream water level is obtained
    using linear interpolation between locations where the water levels has been calculated.
    """
    def __init__(self, upstream_reach_name=None, downstream_reach_name=None, chainage=None, distance=None):
        self.upstream_reach_name = upstream_reach_name
        self.downstream_reach_name = downstream_reach_name
        self.chainage = chainage  #The chainage in the downstream river at which the upstream river is connected
        self.distance = distance  #Optional informativ, the distance from the first point in upstream river to the connection point

#=======================================================================================================================
class Observation():
    def __init__(self, chainage_waterlevels=[], name=''):
        self.name = name                      #eg. shown as label in plots
        self.chainage_waterlevels = chainage_waterlevels  #This is assumed to be at list of tuples [(chainage, waterlevel), (chainage, waterlevel)....]

#=======================================================================================================================
class Factory():
    """
    The Factory class has methods for convenient creation of populated objects. The purpose of this class is only to
    save some programming code for creation of often used class types.
    """
    @staticmethod
    def get_trapezoidal_xs(bottom_width=3.0, side_slope=1.0, hight=2.0, z=0.0, manning_number=8.0, x=0.0, y=0.0, chainage=0.0):
        """
        Creates a trapezoidal cross section if type Xs (a cross section with four perimeter points).
        :param bottom_width: The width of the lateral bottom
        :param side_slope: Slope of the side of the cross section
        :param hight: Distance from the lowest point to the highest point
        :param z: level of the lowest point
        :param manning_number: Manning number
        :param x: Geographical x coordinate for the cross section midpoint
        :param y: Geographical y coordinate for the cross section midpoint
        :param chainage: Chainage
        :return: The populated cross section (Xs) object
        """
        pps = []
        pps.append(Pp(-(hight / side_slope + bottom_width / 2.0), hight))
        pps.append(Pp(-bottom_width / 2., 0.0))
        pps.append(Pp(bottom_width / 2., 0.0))
        pps.append(Pp(hight / side_slope + bottom_width / 2.0, hight))
        xs = Xs(perimeterpoints=pps)
        xs.manning_number = manning_number
        xs.chainage = chainage
        xs.x = x
        xs.y = y
        xs.z = z
        return xs

    @staticmethod
    def get_circular_xs(chainage=0.0, radius=0.5, n_pp = 36, x=0.0, y=0.0, z=0.0):
        """
        Creates a circular cross section (used for e.g. culverts).
        :param radius: The radius of the circular cross section
        :param n_pp: The number of perimeter points used the define the perimeter
        :param x: Geographical x-coordinate of the cross section midpoint
        :param y: Geographical y-coordinate of the cross section midpoint
        :param z: The level of the lowest point in the cross section
        :return: Circular cross section (type: Xs).
        """
        pps = []
        dv = (2.0 * math.pi) / n_pp   #Angle increment
        v = 0.5 * math.pi + 0.5 * dv
        for n in range(n_pp):
            pps.append(Pp(radius * math.cos(v), radius * math.sin(v) + radius + z))
            v = v + dv

        pps[0].marker = 'left bank'
        pps[-1].marker = 'right bank'

        xs = Xs(x=x, y=y, z=z, chainage=chainage, perimeterpoints=pps)
        xs.is_closed = True

        return xs

#=======================================================================================================================
class Tools():
    """"
    Contains various tools as static methods for more efficient (less code to write) creation of Python scripts for
    setting up a reach network.
    """
    @staticmethod
    def create_connections(reach_network, maxium_distance=None):
        """
        Creates a list of connections (hymod.connection), which can be assigned to the Reach_nework.connections
        property. For each reach a connection is created from this reach to the reach containing the cross section
        closest to the most downstream cross section. Connections are only created if the distance is smaller
        than the maximum_distance defined in the parameters. Note, that this method may provide wrong connections,
        depending on the geometry of the network. So, connections should always be inspected (e.g. by saving the reach
        network to a JSON file and subsequently inspecting this file). ). Also note, that the list of connections are
        not assigned to the reach_network.connections property. This must be done subsequently in your own
        Python script.
        :param reach_network: The reach network for which connections are created
        :param maxium_distance: The maximum allowed distance for creation of a connection
        :return: list of connections (list of hymod.Connection)
        """
        #TODO: Finds the closest river point. Should actually find river point between cross sections
        connections = []

        for n in range(len(reach_network.reaches)):
            if maxium_distance != None:
                min_dist = maxium_distance * maxium_distance
            else:
                min_dist = 1000000.0

            reach_name = None
            chainage = None
            crp = reach_network.reaches[n].riverPoints[0]  #most downstream river point for the river for which the connection is about to be found
            for j in range(len(reach_network.reaches)):
                if j != n:
                    for rp in reach_network.reaches[j].riverPoints:
                        dist = math.pow(crp.x - rp.x, 2) + math.pow(crp.y - rp.y, 2)
                        if dist < min_dist:
                            min_dist = dist
                            reach_name = reach_network.reaches[j].name
                            chainage = rp.chainage
            if chainage != None and reach_name != None:
                connections.append(Connection(upstream_reach_name=reach_network.reaches[n].name, downstream_reach_name=reach_name, chainage=chainage, distance=math.sqrt(min_dist)))
        return connections

    @staticmethod
    def remove_reach(reach, network):
        network.reaches.remove(reach)

    @staticmethod
    def get_sub_reach(reach, from_chainage=None, to_chainage=None):
        if from_chainage is None:
            from_chainage = reach.xss[0].chainage
        if to_chainage is None:
            to_chainage = reach.xss[-1].chainage

        sub_reach = Reach(name= 'subset of ' + reach.name)
        sub_reach.riverPoints = [rp for rp in reach.riverPoints if rp.chainage >= from_chainage and rp.chainage <= to_chainage]
        sub_reach.xss = [xs for xs in reach.xss if xs.chainage >= from_chainage and xs.chainage <= to_chainage]
        sub_reach.observations = [obs for obs in reach.observations if obs[0] >= from_chainage and obs[0] <= to_chainage]
        sub_reach.calculated_water_levels = [wl for wl in reach.calculated_water_levels if wl[0] >= from_chainage and wl[0] <= to_chainage]

        return sub_reach

    @staticmethod
    def remove_duplicate_river_points(river_points):
        """
        E.g. when importing digitized river points, some points may have the same geographical location. This method
        will remove such river points from list of river points if chainage, x and y are identical to another
        river point in the list.
        :param river_points:
        """
        rp_copy = river_points[:]
        for rpc in rp_copy:
            dups = [rp for rp in river_points if rp.chainage == rpc.chainage and rp.x == rpc.x and rp.y == rpc.y]
            for i in range(len(dups) - 1):
                river_points.remove(dups[i])

    @staticmethod
    def interpw(x, x1, x2, y1, y2, weight=0.5):
        if not (x1<= x <= x2 or x1 >= x >= x2):
            raise Exception('method: hymod.Tools.interpw was passed an argument outside allowed interval (extrapolation is not allowed) x = %f x1 = %f x2 = %f' % (x, x1, x2))
        if weight == 0:
            return y1
        elif weight == 1:
            return y2
        else:
            r = (x - x1) / (x2 - x1)
            return y1 * (1 - r) + y2 * r

    @staticmethod
    def make_xs_convex(xs):
        """
        For some applications e.g. mike11 and HECRAS concave cross sections are not allowed
        This method will make modications to concave cross sections in order to make these convex
        :param xs: The cross section to be changed
        """

        index = 0
        for n in range(len(xs.pps)): #find index of the deepest perimeter point:
            if xs.pps[n].dz < xs.pps[index].dz:
                index = n
        for n in range(0,index):
            if xs.pps[n+1].dx < xs.pps[n].dx:
                xs.pps[n+1].dx = xs.pps[n].dx

        for n in range(len(xs.pps) - 2, index, -1):
            if xs.pps[n+1].dx < xs.pps[n].dx:
                xs.pps[n].dx = xs.pps[n+1].dx

        Tools.remove_duplicate_perimeter_points(xs)

    @staticmethod
    def remove_duplicate_perimeter_points(xs):
        pps_copy = xs.pps[:]
        for pp in pps_copy:
            ppc = [p for p in xs.pps if p.dx == pp.dx and p.dz == pp.dz]
            for n in range(1, len(ppc)):
                xs.pps.remove(ppc[n])

    @staticmethod
    def center_xs(xs):
        """
        Changes the perimenter points dx value, so the center point (deepest point) has dx value zero
        :param xs: <hymod.Xs> Cross section
        """
        dx_center = min(xs.pps, key=attrgetter('dz')).dx
        for pp in xs.pps:
            pp.dx = pp.dx - dx_center


    @staticmethod
    def RemoveUnnecessaryPerimeterPoints(networkOrXs):
        """
        Remove points in between points that have the same level
        """
        if isinstance(networkOrXs, Xs):
            i = len(networkOrXs.pps)-3
            while i > 1:
                if (networkOrXs.pps[i].dz == networkOrXs.pps[i-1].dz and networkOrXs.pps[i].dz == networkOrXs.pps[i+1].dz):
                    networkOrXs.pps.remove(networkOrXs.pps[i])
                i-=1

        elif isinstance(networkOrXs, Reach_network):
            for r in networkOrXs.reaches:
                for xs in r.xss:
                    Tools.RemoveUnnecessaryPerimeterPoints(xs)

    @staticmethod
    def remove_duplicated_cross_sections(reach):
        """
        Removes cross sections that have the same chainages
        """
        xs_chainages = [xs.chainage for xs in reach.xss]
        for xs_chainage in xs_chainages:
            dups = [xs for xs in reach.xss if xs.chainage == xs_chainage]
            for i in range(len(dups) - 1):
                reach.xss.remove(dups[i])















