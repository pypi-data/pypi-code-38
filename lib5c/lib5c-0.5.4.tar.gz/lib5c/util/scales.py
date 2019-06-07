"""
Module for determining various scales for visualization purposes.
"""

from copy import copy

import numpy as np

from lib5c.parsers.bed import load_features
from lib5c.util.counts import flatten_regional_counts


def compute_regional_obs_scale(counts_superdict, region, top_percentile=98):
    """
    Computes a typical scale for visualizing observed for a specified region.

    Parameters
    ----------
    counts_superdict : dict of dicts of 2d numpy arrays
        The keys of the outer dict are replicate names. The values are dicts
        corresponding to counts dicts (see
        ``lib5c.parsers.counts.load_counts()``), whose keys are region names and
        whose values are the arrays of counts values for that region. These
        arrays are square and symmetric.
    region : str
        The region for which the scale should be computed.
    top_percentile : int
        The upper percentile to use when determinig the max of the scale.

    Returns
    -------
    list of float
        The first element of this list is the minimum value of the computed
        scale. The second element of this list is the maximum value of the
        computed scale.

    Notes
    -----
    The returned scale is computed as ranging from 0 to the average of the 98th
    percentiles across the replicates.
    """
    mins = []
    top_percentiles = []
    for rep in counts_superdict.keys():
        flattened_counts = flatten_regional_counts(
            counts_superdict[rep][region], discard_nan=True)
        mins.append(np.min(flattened_counts))
        top_percentiles.append(np.percentile(flattened_counts, top_percentile))
    return [np.mean(mins), np.mean(top_percentiles)]


def compute_regional_obs_over_exp_scale(counts_superdict, region):
    """
    Computes a typical scale for visualizing observed over expected counts for a
    specified region.

    Parameters
    ----------
    counts_superdict : dict of dicts of 2d numpy arrays
        The keys of the outer dict are replicate names. The values are dicts
        corresponding to counts dicts (see
        ``lib5c.parsers.counts.load_counts()``), whose keys are region names and
        whose values are the arrays of counts values for that region. These
        arrays are square and symmetric.
    region : str
        The region for which the scale should be computed.

    Returns
    -------
    list of float
        The first element of this list is the minimum value of the computed
        scale. The second element of this list is the maximum value of the
        computed scale.

    Notes
    -----
    The returned scale is computed as the mean of the observed over expected
    counts for the selected region across all replicates, plus and minus two and
    a half times the mean of the standard deviations for the selected region
    across all replicates for the maximum and the minimum, respectively.
    """
    means = []
    stds = []
    for rep in counts_superdict.keys():
        flattened_counts = flatten_regional_counts(
            counts_superdict[rep][region], discard_nan=True)
        means.append(np.mean(flattened_counts))
        stds.append(np.std(flattened_counts))
    mean_of_means = np.mean(means)
    mean_of_stds = np.mean(stds)
    return [mean_of_means - 2.5*mean_of_stds, mean_of_means + 2.5*mean_of_stds]


def compute_track_scales(tracks, pixelmap, conditions=(),
                         filename_generator=lambda x: '%s.bed' % x):
    """
    Computes regional zero-to-max scales for visualizing ChIP-seq tracks.

    Parameters
    ----------
    tracks : list of str
        List of string identifiers for the tracks to compute scales for. The
        identifiers will be used to find the appropriate BED files on the disk
        according to filename_generator.
    pixelmap : pixelmap
        The pixelmap to use when identifying the region names and boundaries.
        See ``lib5c.parsers.bed.get_pixelmap()``.
    conditions : list of str
        List of string identifiers for the conditions. If this kwarg is passed,
        the tracks will be grouped by condition, and tracks that differ only in
        the condition identifier will be assigned the same scale. If this list
        is empty (as it is by default), no such grouping of tracks is performed.
    filename_generator : function str -> str
        When passed any string from tracks, this function should return a string
        reference to the BED file on the disk containing the BED features for
        that track.

    Returns
    -------
    dict of dict of numeric
        The keys of the outer dict are the elements of tracks. The values are
        dicts whose keys are region names and whose values are the maximum
        values within that region for that track.

    Notes
    -----
    Since this function computes a zero-to-max scale, the minimum of the scale
    is always implicitly taken to be zero.

    When conditions is not empty, the tracks are grouped by removing all
    instances of all condition identifiers from the track identifiers and then
    comparing them for equality. When the sequence of characters defined by a
    condition identifier appears elsewhere in the track name in a location not
    intended to identify the condition of the track, this may lead to failure to
    correctly group tracks by condition.
    """
    # load features for all tracks
    features = {track: load_features(filename_generator(track))
                for track in tracks}

    # compute regional maxima for all tracks
    maxima = {track: {region: max(
        [feature['value']
         for feature in features[track][pixelmap[region][0]['chrom']]
         if
         feature['chrom'] == pixelmap[region][0]['chrom'] and
         feature['end'] >= pixelmap[region][0]['start'] and
         feature['start'] <= pixelmap[region][-1]['end']])
        for region in pixelmap.keys()}
        for track in tracks}

    # trim conditions from track names
    trimmed_tracks = {}
    for track in tracks:
        trimmed_track = copy(track)
        for condition in conditions:
            trimmed_track = trimmed_track.replace(condition, '')
        trimmed_tracks[track] = trimmed_track

    # build comparison sets
    comparison_sets = []
    comparison_set_map = {}
    for track in tracks:
        assigned_flag = False
        for comparison_set in comparison_sets:
            for element in comparison_set:
                if trimmed_tracks[track] == trimmed_tracks[element]:
                    comparison_set_map[track] = \
                        comparison_sets.index(comparison_set)
                    comparison_set.append(track)
                    assigned_flag = True
                    break
        if not assigned_flag:
            comparison_set_map[track] = len(comparison_sets)
            comparison_sets.append([track])

    # set the track scale to the maximum of the appropriate comparison set
    track_scales = {track: {region: max(
        [maxima[compared_track][region]
         for compared_track in comparison_sets[comparison_set_map[track]]])
        for region in pixelmap.keys()}
        for track in tracks}
    return track_scales


# test client
def main():
    from lib5c.parsers.primers import get_pixelmap
    from lib5c.parsers.counts import load_counts

    # hardcode replicates
    replicates = ['ES_Rep1',
                  'NPC_Rep31']

    # hardcode conditions
    conditions = ['ES', 'NPC']

    # hardcode tracktypes
    tracktypes = ['Smc1', 'CTCF', 'H3K4me1', 'H3K27ac']

    # compute tracks
    tracks = ['%s_%s' % (tracktype, condition)
              for tracktype in tracktypes
              for condition in conditions]

    # get pixelmap
    pixelmap = get_pixelmap('test/bins_nuc.bed')

    # load counts
    counts_superdict = {
        replicate: load_counts('test/%s_obs_over_exp.counts' % replicate)
        for replicate in replicates}

    print('colorscales')
    for region in pixelmap.keys():
        print('%s: %s' %
              (region,
               compute_regional_obs_over_exp_scale(counts_superdict, region)))

    print('')
    print('track scales')
    track_scales = compute_track_scales(
        tracks, pixelmap, conditions,
        filename_generator=lambda x: 'test/tracks/%s.bed' % x)
    for track in track_scales.keys():
        print('%s:' % track)
        for region in track_scales[track].keys():
            print('\t%s: %s' % (region, track_scales[track][region]))


if __name__ == "__main__":
    main()
