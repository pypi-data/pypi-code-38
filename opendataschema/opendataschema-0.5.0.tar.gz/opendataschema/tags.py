from datetime import date
from distutils.version import LooseVersion

from . import GitRef


def by_commit_date(tag: GitRef):
    return tag.commit.committed_date if tag.commit else date.min


def by_semver(ref):
    """Helps sorting againt semantic versioning"""

    if isinstance(ref, str):
        ref_val = ref
    elif isinstance(ref, GitRef):
        ref_val = ref.name
    else:
        raise NotImplementedError(ref)

    return LooseVersion(ref_val)
