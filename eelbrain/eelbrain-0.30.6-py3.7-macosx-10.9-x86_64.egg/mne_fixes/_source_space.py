from functools import reduce

from mne import SourceSpaces
import numpy as np

from .._data_obj import _point_graph


def merge_volume_source_space(sss, name='Volume'):
    """Merge multiple volume source spaces into one

    Notes
    -----
    Only intended to work properly if ``sss`` is the output of a single
    :func:`mne.setup_volume_source_space` call.
    """
    if len(sss) <= 1:
        return sss
    assert all(ss['type'] == 'vol' for ss in sss)
    ss = sss[0]
    ss['vertno'] = np.unique(np.concatenate([ss['vertno'] for ss in sss]))
    ss['inuse'] = reduce(np.logical_or, (ss['inuse'] for ss in sss))
    ss['nuse'] = ss['inuse'].sum()
    ss['seg_name'] = str(name)
    del ss['neighbor_vert']
    return SourceSpaces([ss], sss.info)


def prune_volume_source_space(sss, grade, n=1, mirror=True, remove_midline=False):
    """Remove sources that have ``n`` or fewer neighboring sources"""
    assert len(sss) == 1
    ss = sss[0].copy()
    assert ss['type'] == 'vol'
    if 'neighbor_vert' in ss:
        del ss['neighbor_vert']
    if remove_midline:
        rm = ss['rr'][ss['vertno']][:, 0] == 0
        ss['inuse'][ss['vertno'][rm]] = 0
        ss['vertno'] = ss['vertno'][~rm]
    if mirror:
        coord_tuples = tuple(map(tuple, ss['rr']))
        vertex_list = list(ss['vertno'])
        coord_id = {coord: v for v, coord in enumerate(coord_tuples)}
        for v in ss['vertno']:
            r, a, s = ss['rr'][v]
            v_mirror = coord_id[-r, a, s]
            if v_mirror not in vertex_list:
                vertex_list.append(v_mirror)
        vertex_list.sort()
        ss['vertno'] = np.array(vertex_list, dtype=ss['vertno'].dtype)
        ss['inuse'][ss['vertno']] = 1
    dist = grade * .0011
    while True:
        coords = ss['rr'][ss['vertno']]
        neighbors = _point_graph(coords, dist)
        keep = np.array([np.sum(neighbors == i) > n for i in range(len(coords))])
        if np.all(keep):
            break
        ss['inuse'][ss['vertno'][~keep]] = 0
        ss['vertno'] = ss['vertno'][keep]
    ss['nuse'] = len(ss['vertno'])
    assert ss['inuse'].sum() == ss['nuse']
    assert np.all(np.flatnonzero(ss['inuse']) == ss['vertno'])
    return SourceSpaces([ss], sss.info)
