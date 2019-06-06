"""
Module containing functions for assisting in assessing the degree of convergency
in orientation of transcription factors.
"""

import numpy as np

from lib5c.contrib.interlap.util import features_to_interlaps, query_interlap
from lib5c.algorithms.enrichment import get_fold_change_all, \
    get_fisher_exact_pvalue_all


def compute_convergency(loops, pixelmap, peaks, motifs,
                        loop_classes=('constitutive',), margin=0):
    # prepare annotationmaps
    annotationmaps = prepare_convergency_annotations(pixelmap, peaks, motifs)

    # modify loops
    loops = {region: np.copy(loops[region]) for region in loops}
    for region in loops:
        for loop_class in loop_classes:
            loops[region][loops[region] == loop_class] = 'target'

    # assemble fixed args and kwargs
    fixed_args = ['target', annotationmaps, loops]
    kwargs = {'margin': margin, 'asymmetric': True}

    # prepare mapping
    types = {
        '+-': ['forward', 'reverse'],
        '-+': ['reverse', 'forward'],
        '++': ['forward', 'forward'],
        '--': ['reverse', 'reverse']
    }

    return {
        k: {'foldchange': get_fold_change_all(*(v + fixed_args), **kwargs),
            'pvalue': get_fisher_exact_pvalue_all(*(v + fixed_args), **kwargs)}
        for k, v in types.items()
    }


def prepare_convergency_annotations(pixelmap, peaks, motifs):
    # prepare interlaps for chroms covered by the pixelmap
    chroms = {region: pixelmap[region][0]['chrom'] for region in pixelmap}
    chroms_list = list(set(chroms.values()))
    peaks_ilap = features_to_interlaps(peaks, chroms=chroms_list)
    motifs_ilap = features_to_interlaps(motifs, chroms=chroms_list)

    # collect orientations
    orientations = {
        region: [
            [motif['id']
             for peak in query_interlap(peaks_ilap[chroms[region]], pixel)
             for motif in query_interlap(motifs_ilap[chroms[region]], peak)]
            for pixel in pixelmap[region]]
        for region in pixelmap
    }

    # decide classes
    classes = {
        region: np.array([
            ' ' if not len(orientations[region][i])
            else '+' if all([e == '+' for e in orientations[region][i]])
            else '-' if all([e == '-' for e in orientations[region][i]])
            else '?'
            for i in range(len(pixelmap[region]))
        ], dtype='|S1')
        for region in pixelmap
    }

    # make simple boolean annotationmaps
    return {
        'forward': {region: (classes[region] == '+') for region in pixelmap},
        'reverse': {region: (classes[region] == '-') for region in pixelmap},
        'ambiguous': {region: (classes[region] == '?') for region in pixelmap},
        'empty': {region: (classes[region] == ' ') for region in pixelmap}
    }
