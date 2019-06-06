"""
Module containing utility functions for filtering 5C interaction matrices.
"""


def filter_selector(array, nearby_x, nearby_y):
    """
    Create a list of dicts that describes the "neighborhood" around a point
    given an array of values and lists of the nearby entities along both the x-
    and y-axes.

    Parameters
    ----------
    array : np.ndarray
        The array of values at each point in the region.
    nearby_x, nearby_y : List[Dict[str, int]]
        A list of nearby entities (bins or fragments) along the x- or y-axis,
        respectively, represented as dicts of the form::

            {
                'index': int,
                'distance': int
            }

        where 'index' is the index of the entity within the region, and
        'distance' is the distance from this entity to the query point in base
        pairs. A list of this form can be created by functions like
        ``find_nearby_bins()`` or ``find_nearby_fragments()``.

    Returns
    -------

    """
    return [{'index' : (i['index'], j['index']),
             'value' : array[i['index'], j['index']],
             'x_dist': i['distance'],
             'y_dist': j['distance']}
            for i in nearby_x
            for j in nearby_y]
