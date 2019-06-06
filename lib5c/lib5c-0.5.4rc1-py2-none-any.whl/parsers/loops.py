"""
Module for parsing tables containing categorized loop information.
"""


def load_loops(loopsfile):
    """
    Reads categorized loop file into nested dict structure.

    Parameters
    ----------
    loopsfile : str
        String reference to the loop file to parse. Each line in the loop file
        corresponds to one loop. The lines are tab-separated. with four columns.
        These are, in order, the category the loop was categorized into (as a
        string), the region name the loop is in (as a string), the x-coordinate
        of the pixel which represents the loop (as an int), and the y-coordinate
        of the pixel which represent the loop (as an int).

    Returns
    -------
    dict of dicts of dicts
        The outer keys are loop categories as strings. The next level's keys are
        region names as strings. The innermost dicts represent loops. These
        inner loop dicts have the following structure::

            {
                'x': int,
                'y': int
            }

        The ints represent the x and y coordinate, respectively, of the loop
        within the region.
    """
    # dict which will store loop information
    loops_dict = {}

    # parse the file
    with open(loopsfile, 'r') as handle:
        for line in handle:
            # skip comments
            if line.startswith('#'):
                continue

            # split line on tab
            pieces = line.split('\t')

            # parse line information
            category = pieces[0]
            region = pieces[1]
            x_bin = int(pieces[2])
            y_bin = int(pieces[3])

            # create subdict for this category if not present yet
            if category not in loops_dict.keys():
                loops_dict[category] = {}

            # create list for this region if not present yet
            if region not in loops_dict[category].keys():
                loops_dict[category][region] = []

            # append this loop to the correct list
            loops_dict[category][region].append({'x': x_bin, 'y': y_bin})

    return loops_dict
