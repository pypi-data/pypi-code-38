import contextlib
import numpy as np

import config
from eppy.modeleditor import IDF
import json

from functools import partial
import warnings

from errors import ModeError

"""This file is a collection of functions to interact with eppy.
They could do with some sorting and refactoring."""


def convert_format(s: str, place, mode):
    """Converts energyPlus names to their Eppy equivalents

    :param s: name to convert
    :param place: the type of place that is being used 'field' or 'class'
    :param mode: whether to convert to idf or json formating
    :return: the converted name
    """
    # TODO: Find an authoritative source for the naming conventions
    if mode == 'idf':
        if place == 'field':
            return s.replace(' ', '_').replace('-', '')
        if place == 'class':
            return s.upper()
    if mode == 'json':
        if place == 'field':
            return s.replace(' ', '_').replace('-', '_').lower()
        if place == 'class':
            # uses camel case, s.title() removes some of the capitals and does not work
            return s
    raise ModeError(message=f'no format defined for place:{place} and mode:{mode}')


def get_mode(building):
    if isinstance(building, IDF):
        return 'idf'
    if isinstance(building, dict):
        return 'json'
    raise ModeError(message=f'Cannot find a valid mode for {building}')


def get_idf(idf_file: str = config.files.get('idf'),
            idd_file: str = config.files.get('idd'),
            output_directory=config.out_dir) -> IDF:
    """Uses eppy to read an idf file and generate the corresponding idf object"""
    # Trying to change the idd file inside a program will cause an error
    IDF.setiddname(idd_file)
    # TODO: Fix this rather than hiding it.
    # calling IDF causes a warning to appear, currently redirect_stdout hides this.
    with contextlib.redirect_stdout(None):
        idf = IDF(idf_file)
        # override the output location so I stop messing up
        idf.run = partial(idf.run, output_directory=output_directory)
        return idf


def get_building(building=None,
                 data_dict=None,
                 output_directory=config.out_dir,
                 mode=None):
    if mode is None and building is None:
        building = config.files.get('building')
        mode = config.energy_plus_mode
    if mode is None:
        ending = building.split('.')[-1]
        if ending == 'idf':
            mode = 'idf'
        elif ending == 'epJSON':
            mode = 'json'
        else:
            warnings.warn(f'expected "idf" or "epJSON" file. building has extension {ending}')
    if building is None:
        building = config.files[mode]
    if mode == 'idf':
        data_dict = data_dict or config.files['idd']
        return get_idf(idf_file=building, idd_file=data_dict, output_directory=output_directory)
    elif mode == 'json':
        with open(building) as f:
            return json.load(f)
    ModeError(mode)


def get_windows(building):
    mode = get_mode(building)
    if mode == 'idf':
        return ((window.Name, window) for window in building.idfobjects['FENESTRATIONSURFACE:DETAILED'])
    elif mode == 'json':
        return building['FenestrationSurface:Detailed'].items()
    else:
        raise ModeError(mode)


def wwr_all(building, wwr: float) -> None:
    """Sets the wwr for all walls that have a window.
    Will malfunction if there are multiple windows on one wall
    """
    mode = get_mode(building)
    windows = get_windows(building)
    for window_name, window in windows:
        wwr_single(window, wwr, building, mode)


def set_vertex(idfObj, vertexNum: int, x: float = 0, y: float = 0, z: float = 0):
    """Sets a single vertex of the passed idfObject (idfObj)
     to the specified x,y and z coordinates."""
    for val, name in zip((x, y, z), 'XYZ'):
        idfObj['Vertex_{}_{}coordinate'.format(vertexNum, name)] = round(val, 2)


def one_window(building):
    """Removes some windows so that each wall has no more than one"""
    mode = get_mode(building)
    walls = set()
    toRemove = []
    windows = get_windows(building)
    for window_name, window in windows:
        if mode == 'idf':
            wall_name = window.Building_Surface_Name
        elif mode == 'json':
            wall_name = window['building_surface_name']
        else:
            raise ModeError(mode)
        if wall_name in walls:
            toRemove.append((window_name, window))
        else:
            walls.add(wall_name)
    if mode == 'idf':
        for window_name, window in toRemove:
            building.idfobjects['FENESTRATIONSURFACE:DETAILED'].remove(window)
    elif mode == 'json':
        for window_name, window in toRemove:
            building['FenestrationSurface:Detailed'].pop(window_name)


def wwr_single(window, wwr: float, building, mode):
    """Sets `window` to have the window to wall ratio specified by `wwr`"""

    # will not work for some orientations
    # multiple windows on a single wall will break this
    if mode == 'idf':
        def coordinates(ax):
            return [window[f'Vertex_{n}_{ax.upper()}coordinate'] for n in range(1, 5)]

        wall = building.getobject('BUILDINGSURFACE:DETAILED', window.Building_Surface_Name)
    elif mode == 'json':
        def coordinates(ax):
            return [window[f'vertex_{n}_{ax.lower()}_coordinate'] for n in range(1, 5)]

        wall = building['BuildingSurface:Detailed'][window['building_surface_name']]
    else:
        raise ModeError(mode)

    xs = coordinates('X')
    ys = coordinates('Y')
    zs = coordinates('Z')

    if max(ys) == min(ys):
        axis = 'x'
        axs = xs
    elif max(xs) == min(xs):
        axis = 'y'
        axs = ys
    else:
        raise ValueError('The window is not aligned with the x or y axes')
    width = max(axs) - min(axs)
    scale_factor = np.sqrt(wwr)
    new_width = width * scale_factor
    height = max(zs) - min(zs)
    new_height = height * scale_factor

    startW = (width - new_width) / 2
    endW = startW + new_width
    startH = (height - new_height) / 2
    endH = startH + new_height

    # Maintains vertex order by mimicking the current order
    s = [0] * 4
    for vertex in range(0, 4):
        if zs[vertex] == max(zs):
            # vertex on the top
            if axs[vertex] == max(axs):
                # TOP RIGHT
                s[0] += 1
                set_vertex(window, vertex + 1, z=endH, **{axis: endW})
            else:
                # TOP LEFT
                s[1] += 1
                set_vertex(window, vertex + 1, z=endH, **{axis: startW})
        else:
            if axs[vertex] == max(axs):
                # BOTTOM RIGHT
                s[2] += 1
                set_vertex(window, vertex + 1, z=startH, **{axis: endW})
            else:
                # BOTTOM LEFT
                s[3] += 1
                set_vertex(window, vertex + 1, z=startH, **{axis: startW})
    assert s == [1] * 4, ('verticesS are wrong:', s)
