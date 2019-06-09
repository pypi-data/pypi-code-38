import numpy as np
import scipy.spatial

def connect_line_segments(lines):
    """ Create polygons from unsorted line segments """
    points = np.unique([p for pp in lines for p in pp])

    # map from points to lines segments
    l_dict = dict([(p,list()) for p in points])
    for i, (p0, p1) in enumerate(lines):
        l_dict[p0].append(i)
        l_dict[p1].append(i)

    polygons = []
    polygon = []
    while True:
        if len(l_dict) == 0:
            break

        # pop a point, and a line segment that contains the point
        p0, l_dict_entry = l_dict.popitem()

        l0 = l_dict_entry[0]

        # find the other point in that line segment
        p1 = [p for p in lines[l0] if p != p0][0]

        # start the polygon
        polygon.append(p0)
        polygon.append(p1)

        # next
        p0 = p1

        while True:
            # check if we're finished
            if p0 not in l_dict:
                polygons.append(polygon)
                polygon = []
                break

            # check if we've hit the end of a chain
            if len(l_dict[p0]) < 2:
                # check if we've already done both ends
                if l_dict_entry is None:
                    polygons.append(polygon)
                    polygon = []
                    break

                # try the other end of the chain
                l_dict[polygon[-1]] = l_dict_entry
                p0 = polygon[0]
                polygon = list(reversed(polygon))
                l_dict_entry = None
                continue

            # get both lines
            l0 = l_dict[p0][0]
            l1 = l_dict[p0][1]

            # get the point we don't already have in the chain
            p1 = [p for l in [lines[l0], lines[l1]] for p in l if (p != p0) and (p != polygon[-2])][0]

            # next
            polygon.append(p1)
            del l_dict[p0]
            p0 = p1

    return polygons

def _simplex_intersections(samples, levels, simplices):
    """ Compute the simplex intersections of a iso-lines for a scalar field in a 2d space """

    # to simplify the problem each point has an index
    # and each line has an index

    simplex_lines = np.zeros((len(levels),0)).tolist() # lines between the simplex edges that cross the levels
    lines = [] # the lines that compose the simplex edges
    li_to_si = dict() # maps line index -> simplex indices
    l_to_li = dict() # maps line -> line index
    for si, points in enumerate(simplices):
        points = sorted(points)
        # points and lines are ordered so lx does not contain px (px is opposite lx)
        p0, p1, p2 = points
        these_lines = [(p1,p2), (p0,p2), (p0,p1)]

        # fill the maps
        for l in these_lines:
            if l not in l_to_li:
                li_to_si[len(lines)] = []
                l_to_li[l] = len(lines)
                lines.append(l)
            li = l_to_li[l]
            li_to_si[li].append(si)

        for level_i, level in enumerate(levels):
            # which points are above / below the level
            b = np.array([samples[p] >= level for p in points]).astype(bool)
            b_sum = np.sum(b)

            # skip triangles thar are all above or all below the level
            # for triangles spanning the level, get the lines that cross the level
            if b_sum == 1:
                line_indices = np.array([l_to_li[l] for l in these_lines])[np.array([i for i in range(3) if i != np.argmax(b)])]
            elif b_sum == 2:
                line_indices = np.array([l_to_li[l] for l in these_lines])[np.array([i for i in range(3) if i != np.argmin(b)])]
            else:
                continue
            simplex_lines[level_i].append(tuple(sorted(line_indices)))

    simplex_intersections_by_level = []
    for level_i, level in enumerate(levels):
        connected_line_segments = connect_line_segments(simplex_lines[level_i])
        simplex_intersections_by_level.append([np.array([lines[li] for li in index_contour]) for index_contour in connected_line_segments])

    return simplex_intersections_by_level

def _planar_geodesic(p0, p1, x):
    # This function describes the geodesic between p0 and p1 in a 2d cartesian space
    # p0 and p1 are assumed to be of the form (x0, y0) and (x1, y1)
    assert(x >= 0.0 and x <= 1.0)
    p = np.asarray(p0) * (1.0-x) + np.asarray(p1) * x
    return p

def _spherical_geodesic(p0, p1, x):
    # This function describes the geodesic between p0 and p1 on a unit sphere
    # p0 and p1 are assumed to be of the form (theta0, phi0) and (theta1, phi1)
    # where theta and phi are the polar and azimuthal angles respectively measured in radians
    assert(x >= 0.0 and x <= 1.0)
    v0, v1 = [np.array((np.cos(phi)*np.sin(theta), np.sin(phi)*np.sin(theta), np.cos(theta))) for theta, phi in [p0, p1]]
    v5 = v0*(1.-x) + v1*x
    v5 = v5 / np.sqrt(np.sum(v5*v5))
    p = (np.arccos(v5[2]), np.arctan2(v5[1], v5[0]))

    return p
"""
def _spherical_geodesic(p0, p1, x):
    # This function describes the geodesic between p0 and p1 on a unit sphere
    # p0 and p1 are assumed to be of the form (theta0, phi0) and (theta1, phi1)
    # where theta and phi are the polar and azimuthal angles respectively measured in radians
    assert(x >= 0.0 and x <= 1.0)
    v0, v1 = [np.array((np.cos(phi)*np.sin(theta), np.sin(phi)*np.sin(theta), np.cos(theta))) for theta, phi in [p0, p1]]
    c = np.sqrt(np.sum((v1-v0)**2))
    theta = 2.0*np.arcsin(c/2.0)
    theta0 = x*theta
    theta1 = theta * (1.0 - x)
    theta2 = (np.pi - theta) / 2.0
    theta4 = np.pi - (theta1 + theta2)
    c0 = np.sin(theta0) / np.sin(theta4)

    v2 = v1 - v0
    v2 = v2 / np.sqrt(np.sum(v2**2.0))
    v3 = v0 + v2*c0
    v3 = v3 / np.sqrt(np.sum(v3**2.0))

    p = (np.arccos(v3[2]), np.arctan2(v3[1], v3[0]))

    v4 = v0*x + v1*(1.-x)
    v4 = v4 / np.sqrt(np.sum(v4*v4))
    pp = (np.arccos(v4[2]), np.arctan2(v4[1], v4[0]))
    v5 = v0*(1.-x) + v1*x
    v5 = v5 / np.sqrt(np.sum(v5*v5))
    ppp = (np.arccos(v5[2]), np.arctan2(v5[1], v5[0]))

    print(p, pp, ppp)
    return p
"""

def _interpolate_simplex_intersections(sample_points, samples, levels, simplex_intersections_by_level, geodesic=_planar_geodesic):
    contours_by_level = []
    for level_i, level in enumerate(levels):
        connected_line_segments = simplex_intersections_by_level[level_i]
        lines_in_contours = np.unique([line for index_contour in connected_line_segments for line in index_contour], axis=0)

        line_ps = dict()

        for line in lines_in_contours:
            line = tuple(line)
            p0, p1 = line
            (p0, y0), (p1, y1) = sorted([(p0, samples[p0]), (p1, samples[p1])], key=lambda x: x[1])
            x = (level-y0) / (y1-y0)
            p = geodesic(sample_points[p0], sample_points[p1], x)
            line_ps[line] = p

        contours_by_level.append([np.array([line_ps[tuple(li)] for li in index_contour]) for index_contour in connected_line_segments])
    return contours_by_level

def _compute_planar_simplices(sample_points):
    tri = scipy.spatial.Delaunay(sample_points)
    simplices = tri.simplices
    return simplices

def _compute_spherical_simplices(sample_points):
    sample_points = [(np.cos(phi)*np.sin(theta), np.sin(phi)*np.sin(theta), np.cos(theta)) for theta, phi in sample_points]
    hull = scipy.spatial.ConvexHull(sample_points)
    simplices = hull.simplices
    return simplices

def _compute_simplices(geodesic, simplex_function, sample_points):
    try:
        simplex_array = np.asarray(simplex_function)
        simplices_shape = simplex_array.shape
        assert(len(simplices_shape) == 2)
        n_samples = len(sample_points)
        if simplices_shape[0] == n_samples:
            assert(simplices_shape[1] == 3)
            return simplex_array
        elif simplices_shape[1] == n_samples:
            assert(simplices_shape[0] == 3)
            return simplex_array.T
    except:
        pass

    if callable(simplex_function):
        try:
            simplices = simplex_function(sample_points)
            return simplices
        except:
            pass

    if simplex_function is None:
        if type(geodesic) is str:
            simplex_function = geodesic

    if simplex_function == 'planar':
        return _compute_planar_simplices(sample_points)
    elif simplex_function == 'spherical':
        return _compute_spherical_simplices(sample_points)
    else:
        raise ValueError("Not sure what to do with simplex_function = %s" % str(simplex_function))

def _get_geodesic_function(geodesic):
    if callable(geodesic):
        return geodesic
    elif geodesic == 'planar':
        return _planar_geodesic
    elif geodesic == 'spherical':
        return _spherical_geodesic
    else:
        raise ValueError("Not sure what to do with geodesic = %s" % str(geodesic))

def compute_contours(sample_points, samples, levels, geodesic='planar', simplices=None):
    """ Compute contours (iso-lines of a scalar field) in a 2d space

        Parameters
        ----------
        sample_points : array_like
            The points in the 2d space for which there are samples
            of the scalar field. This should be structured as
            [(x0,y0), (x1,y1), ...]
        samples : array_like
            The values of the scalar field at the locations of sample_points
        levels : array_like
            The values of the scalar field at which the contours are computed
        geodesic : str or callable, optional
            The geodesic of the space in which the sample_points exist.
            If geodesic is a str, it can have values ['planar', 'spherical']
            to specify if the points exist in a planar space or on the surface
            of a sphere.
            If geodesic is callable it should have the form geodesic(p0, p1, x)
            where p0 and p1 are points in the space and x is a number between 0
            and 1 that describes a point between p0 and p1 along the geodesic. In
            this case geodesic should return the point corresponding to x.
            The default is 'planar'.
        simplices : None or array_like or callable, optional
            If None, the simplices are computed via the Delaunay triangulation
            on either a planar or spherical surface depending on the geodesic
            If array_like, the simplices are assumed to be of the form
            [(pi0, pj0, pk0), (pi1, pj1, pk1), ...] where the pi,pj,pk refer to indices
            in sample_points that specify the points that compose each simplex
            If callable, simplices is assumed to take the sample_points and return the
            an array_like version of simplices
            The default is None
        Returns
        -------
        contours_by_level : list(list(list(point)))
            The contours for each level
            Outermost list indexes by level
            Second list indexes by contours at a particular level
            Third list indexes by points in each contour
            Points are of the same form as sample_points
    """

    simplices = _compute_simplices(geodesic, simplices, sample_points)

    simplex_intersections_by_level = _simplex_intersections(samples, levels, simplices)

    geodesic_function = _get_geodesic_function(geodesic)

    contours_by_level = _interpolate_simplex_intersections(sample_points, samples, levels, simplex_intersections_by_level, geodesic=geodesic_function)

    return contours_by_level

def planar_contours(sample_points, samples, levels, simplices=None):
    """ Compute contours (iso-lines of a scalar field) in a 2d planar space
        See compute_contours for more information.
        compute_contours(sample_points, samples, levels, geodesic='planar', simplices=simplices)
    """
    return compute_contours(sample_points, samples, levels, geodesic='planar', simplices=simplices)

def spherical_contours(sample_points, samples, levels, simplices=None):
    """ Compute contours (iso-lines of a scalar field) in a 2d space on the surface of a unit sphere
        See compute_contours for more information.
        compute_contours(sample_points, samples, levels, geodesic='spherical', simplices=simplices)
    """
    return compute_contours(sample_points, samples, levels, geodesic='spherical', simplices=simplices)

