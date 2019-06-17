from copy import deepcopy
import re

from .definitions import DefinitionError, Definition


COMBINATION_PARC = 'combination'
FS_PARC = 'subject_parc'  # Parcellation that come with every MRI-subject
FSA_PARC = 'fsaverage_parc'  # Parcellation that comes with fsaverage
SEEDED_PARC = 'seeded'
INDIVIDUAL_SEEDED_PARC = 'individual seeded'
SEEDED_PARC_RE = re.compile(r'^(.+)-(\d+)$')


class Parcellation(Definition):
    DICT_ATTRS = ('kind',)
    make = False
    morph_from_fsaverage = False

    def __init__(self, views=None):
        self.views = views

    def _link(self, name):
        out = deepcopy(self)
        out.name = name
        return out


class CombinationParc(Parcellation):
    """Recombine labels from an existing parcellation

    Parameters
    ----------
    base : str
        The name of the parcellation that provides the input labels.
    labels : dict  {str: str}
        New labels to create in ``{name: expression}`` format. All label names
        should be composed of alphanumeric characters (plus underline) and should
        not contain the -hemi tags. In order to create a given label only on one
        hemisphere, add the -hemi tag in the name (not in the expression, e.g.,
        ``{'occipitotemporal-lh': "occipital + temporal"}``).
    views : sequence of str
        Views shown in anatomical plots, e.g. ``("medial", "lateral")``.

    Examples
    --------
    These are pre-defined parcellations::

        parcs = {
            'lobes-op': CombinationParc('lobes', {'occipitoparietal': "occipital + parietal"}),
            'lobes-ot': CombinationParc('lobes', {'occipitotemporal': "occipital + temporal"}),
        }

    An example using a split label. In ``split(superiorfrontal, 3)[2]``, ``3`` indicates a split into
    three parts, and the index ``[2]`` picks the last one. Label are split along their longest axis,
    and ordered posterior to anterior, so ``[2]`` picks the most anterior part of
    ``superiorfrontal``::

        parcs = {
            'medial': CombinationParc('aparc', {
                'medialparietal': 'precuneus + posteriorcingulate',
                'medialfrontal': 'medialorbitofrontal + rostralanteriorcingulate'
                                 ' + split(superiorfrontal, 3)[2]',
                }, views='medial'),
        }
    """
    DICT_ATTRS = ('kind', 'base', 'labels')
    kind = COMBINATION_PARC
    make = True

    def __init__(self, base, labels, views=None):
        Parcellation.__init__(self, views)
        self.base = base
        self.labels = labels


class EelbrainParc(Parcellation):
    "Parcellation that has special make rule"
    kind = 'eelbrain_parc'
    make = True

    def __init__(self, morph_from_fsaverage, views=None):
        Parcellation.__init__(self, views)
        self.morph_from_fsaverage = morph_from_fsaverage


class FreeSurferParc(Parcellation):
    """Parcellation that is created outside Eelbrain for each subject

    Parcs that can not be generated automatically (e.g.,
    parcellation that comes with FreeSurfer). These parcellations are
    automatically scaled for brains based on scaled versions of fsaverage, but
    for individual MRIs the user is responsible for creating the respective
    annot-files.

    Examples
    --------
    Predefined parcellations::

        parcs = {
            'aparc': FreeSurferParc(),
            }
    """
    kind = FS_PARC


class FSAverageParc(Parcellation):
    """Fsaverage parcellation that is morphed to individual subjects

    Parcs that are defined for the fsaverage brain and should be morphed
    to every other subject's brain. These parcellations are automatically
    morphed to individual subjects' MRIs.

    Examples
    --------
    Predefined parcellations::

        parcs = {
            'PALS_B12_Brodmann': FSAverageParc(),
            }
    """
    kind = FSA_PARC
    morph_from_fsaverage = True


class LabelParc(Parcellation):
    """Assemble parcellation from FreeSurfer labels

    Combine one or several ``*.label`` files into a parcellation.

    """
    DICT_ATTRS = ('kind', 'labels')
    kind = 'label_parc'
    make = True

    def __init__(self, labels, views=None):
        Parcellation.__init__(self, views)
        self.labels = labels if isinstance(labels, tuple) else tuple(labels)


class SeededParc(Parcellation):
    """Parcellation that is grown from seed coordinates

    Seeds are defined on fsaverage which is in MNI305 space (`FreeSurfer wiki
    <https://surfer.nmr.mgh.harvard.edu/fswiki/CoordinateSystems>`_).
    For each seed entry, the source space vertex closest to the given coordinate
    will be used as actual seed, and a label will be created including all
    points with a surface distance smaller than a given extent from the seed
    vertex/vertices. The spatial extent is determined when setting the parc as
    analysis parameter as in ``e.set(parc="myparc-25")``, which specifies a
    radius of 25 mm.

    Parameters
    ----------
    seeds : dict
        ``{name: seed(s)}`` dictionary, where names are strings, including
        hemisphere tags (e.g., ``"mylabel-lh"``) and seed(s) are array-like,
        specifying one or more seed coordinate (shape ``(3,)`` or
        ``(n_seeds, 3)``).
    mask : str
        Name of a parcellation to use as mask (i.e., anything that is "unknown"
        in that parcellation is excluded from the new parcellation. For example,
        use ``{'mask': 'lobes'}`` to exclude the subcortical areas around the
        diencephalon.

    Examples
    --------
    Example with multiple seeds::

         parcs = {
             'stg': SeededParc({
                 'anteriorstg-lh': ((-54, 10, -8), (-47, 14, -28)),
                 'middlestg-lh': (-66, -24, 8),
                 'posteriorstg-lh': (-54, -57, 16),
             },
             mask='lobes'),
         }
    """
    DICT_ATTRS = ('kind', 'seeds', 'surface', 'mask')
    kind = SEEDED_PARC
    make = True

    def __init__(self, seeds, mask=None, surface='white', views=None):
        Parcellation.__init__(self, views)
        self.seeds = seeds
        self.mask = mask
        self.surface = surface

    def seeds_for_subject(self, subject):
        return self.seeds


class IndividualSeededParc(SeededParc):
    """Seed parcellation with individual seeds for each subject

    Analogous to :class:`SeededParc`, except that seeds are
    provided for each subject.

    Examples
    --------
    Parcellation with subject-specific seeds::

        parcs = {
            'stg': IndividualSeededParc({
                'anteriorstg-lh': {
                    'R0001': (-54, 10, -8),
                    'R0002': (-47, 14, -28),
                },
                'middlestg-lh': {
                    'R0001': (-66, -24, 8),
                    'R0002': (-60, -26, 9),
                }
                mask='lobes'),
        }
    """
    kind = INDIVIDUAL_SEEDED_PARC
    morph_from_fsaverage = False

    def __init__(self, seeds, mask=None, surface='white', views=None):
        SeededParc.__init__(self, seeds, mask, surface, views)
        labels = tuple(self.seeds)
        label_subjects = {label: sorted(self.seeds[label].keys()) for label in labels}
        subjects = label_subjects[labels[0]]
        if not all(label_subjects[label] == subjects for label in labels[1:]):
            raise DefinitionError("Some labels are missing subjects")
        self.subjects = subjects

    def seeds_for_subject(self, subject):
        if subject not in self.subjects:
            raise DefinitionError(f"Parcellation {self.name} not defined for subject {subject}")
        seeds = {name: self.seeds[name][subject] for name in self.seeds}
        # filter out missing
        return {name: seed for name, seed in seeds.items() if seed}


def parc_from_dict(name, params):
    p = params.copy()
    kind = p.pop('kind', None)
    if kind is None:
        raise KeyError(f"Parcellation {name} does not contain the required 'kind' entry")
    elif kind not in PARC_CLASSES:
        raise ValueError(f"Parcellation {name} contains an invalid 'kind' entry: {kind!r}")
    cls = PARC_CLASSES[kind]
    return cls(**p)


PARC_CLASSES = {
    COMBINATION_PARC:       CombinationParc,
    FS_PARC:                FreeSurferParc,
    FSA_PARC:               FSAverageParc,
    SEEDED_PARC:            SeededParc,
    INDIVIDUAL_SEEDED_PARC: IndividualSeededParc,
}


def assemble_parcs(items):
    parcs = {}
    for name, obj in items:
        if isinstance(obj, Parcellation):
            parc = obj
        elif obj == FS_PARC:
            parc = FreeSurferParc(('lateral', 'medial'))
        elif obj == FSA_PARC:
            parc = FSAverageParc(('lateral', 'medial'))
        elif isinstance(obj, dict):
            parc = parc_from_dict(name, obj)
        else:
            raise DefinitionError(f"parcellation {name!r}: {obj!r}")
        parcs[name] = parc._link(name)
    return parcs
