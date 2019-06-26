import os
import re
import logging
from packaging.version import parse
from .scm.git import Git
from .scm.base import DEFAULT_TAG_VERSION
from .exception import VersionerError
from .version_string import make_string_pep440_compatible

SCM_TYPES = [Git]
LOG = logging.getLogger(__name__)
RELEASE_FORMAT = "{main_version}"
FORMAT = "{main_version}.dev{commit_count}+{branch}.{scm_change_id}"


def get_version(
    path=os.curdir,
    is_release=False,
    version_format=FORMAT,
    release_version_format=RELEASE_FORMAT,
    version_file="VERSION",
    release_branch_regex=None,
    scm_type=None,
):
    """
    return the version.
    """
    path = os.path.abspath(path)
    version_file_path = os.path.join(path, version_file)

    scm = _get_scm(scm_type, path)
    if not scm:
        existing_version = _read_version_file(version_file_path)
        if existing_version:
            return existing_version

        if scm_type is None:
            msg = "unable to detect scm type."
        else:
            msg = "scm type {0} not found, or is not a valid repo.".format(scm_type)
        raise VersionerError(msg)

    version = determine_version(
        scm,
        version_format=version_format,
        release_version_format=release_version_format,
        is_release=is_release,
    )

    _write_version_file(version_file_path, version)
    return version


def determine_version(
    scm,
    version_format=FORMAT,
    release_version_format=RELEASE_FORMAT,
    release_branch_regex=None,
    is_release=False,
):
    props = scm.get_properties()

    release_branch_regex = release_branch_regex or scm.RELEASE_BRANCH_REGEX
    if not re.match(release_branch_regex, props["branch"]):
        LOG.info(
            "branch {0} does not match regex {1}. Using default tag version.".format(
                props["branch"], release_branch_regex
            )
        )
        props["main_version"] = DEFAULT_TAG_VERSION
    else:
        props["main_version"] = props["tag_version"]

    props["branch"] = make_string_pep440_compatible(props["branch"])

    fmt_to_use = release_version_format if is_release else version_format

    try:
        return str(parse(fmt_to_use.format(**props)))
    except KeyError as ke:
        raise VersionerError(
            "key {0} was not provided by the scm type {1}".format(ke, scm.get_name())
        )


def _read_version_file(version_file):
    if not os.path.exists(version_file):
        return
    with open(version_file) as fh:
        return fh.read()


def _get_scm(scm_type, path):
    for SCMType in SCM_TYPES:
        if scm_type is None or scm_type == SCMType.get_name():
            if SCMType.is_repo(path):
                return SCMType(path)
    return None


def _write_version_file(version_file, version):
    with open(version_file, "w+") as fh:
        fh.write(version)
