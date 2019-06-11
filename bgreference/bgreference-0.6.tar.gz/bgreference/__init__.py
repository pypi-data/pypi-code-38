import mmap
import os

import bgdata

from os.path import join


REF_PATHS = {}
REF_MMAPS = {}

HUMAN_GENOME_SEQUENCE_MAPS = {'{}'.format(c): 'chr{}'.format(c) for c in range(1, 23)}
HUMAN_GENOME_SEQUENCE_MAPS.update({'X': 'chrX', '23': 'chrX', 'chr23': 'chrX', 'Y': 'chrY', '24': 'chrY', 'chr24': 'chrY'})
HUMAN_GENOME_SEQUENCE_MAPS.update({'M': 'chrM', 'MT': 'chrM', 'chrMT': 'chrM'})

MOUSE_GENOME_SEQUENCE_MAPS = {'{}'.format(c): 'chr{}'.format(c) for c in range(1, 22)}
MOUSE_GENOME_SEQUENCE_MAPS.update({'X': 'chrX', 'Y': 'chrY'})
MOUSE_GENOME_SEQUENCE_MAPS.update({'M': 'chrM'})

SEQUENCE_NAME_MAPS = {
    'hg19': HUMAN_GENOME_SEQUENCE_MAPS,
    'hg38': HUMAN_GENOME_SEQUENCE_MAPS,
    'hg18': HUMAN_GENOME_SEQUENCE_MAPS,
    'c3h':  MOUSE_GENOME_SEQUENCE_MAPS,
    'mm10': MOUSE_GENOME_SEQUENCE_MAPS,
    'cast': MOUSE_GENOME_SEQUENCE_MAPS,
    'car': MOUSE_GENOME_SEQUENCE_MAPS,
    'f344': MOUSE_GENOME_SEQUENCE_MAPS
}


def _get_dataset(build_name, release=None):
    global REF_PATHS, REF_MMAPS

    if build_name not in REF_PATHS:
        # Done in an if clause to retain compatibility with bgdata 1.5 that used the LATEST as build
        if release is None:
            path_ = bgdata.get_path('datasets', 'genomereference', build_name)
        else:
            path_ = bgdata.get_path('datasets', 'genomereference', build_name, build=release)
        REF_PATHS[build_name] = path_
        REF_MMAPS[build_name] = {}

    return REF_PATHS[build_name]


def _get_mmap(build_name, sequence_name, release=None):
    global REF_MMAPS, REF_PATHS

    if build_name not in REF_PATHS or sequence_name not in REF_MMAPS[build_name]:
        path = join(_get_dataset(build_name, release=release), "{0}.txt".format(sequence_name))

        if not os.path.exists(path):
            raise RuntimeError("Sequence '{}' not found in genome build '{}' ({})".format(sequence_name, build_name, path))

        fd = open(path, 'rb')
        REF_MMAPS[build_name][sequence_name] = mmap.mmap(fd.fileno(), 0, access=mmap.ACCESS_READ)

    return REF_MMAPS[build_name][sequence_name]


def refseq(build_name, sequence_name, start, size=1, release=None):

    # Convert to string
    sequence_name = str(sequence_name)

    # Transform sequence_name
    if build_name in SEQUENCE_NAME_MAPS:
        if sequence_name in SEQUENCE_NAME_MAPS[build_name]:
            sequence_name = SEQUENCE_NAME_MAPS[build_name][sequence_name]

    mm_file = _get_mmap(build_name, sequence_name, release=release)
    mm_file.seek(start - 1)
    return mm_file.read(size).decode().upper()


def hg19(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('hg19', chromosome, start, size=size)


def hg38(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('hg38', chromosome, start, size=size)


def hg18(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('hg18', chromosome, start, size=size)


def c3h(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('c3h', chromosome, start, size=size)


def mm10(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('mm10', chromosome, start, size=size)


def f344(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('f344', chromosome, start, size=size)


def car(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('car', chromosome, start, size=size)


def cast(chromosome, start, size=1):
    """

    Args:
        chromosome (str): chromosome identifier
        start (int): starting position
        size (int): amount of bases. Default to 1.

    Returns:
        str: bases in the reference genome
    """

    return refseq('cast', chromosome, start, size=size)
