import os

from pkg_resources import parse_requirements
from requirements import parser
from packaging.specifiers import SpecifierSet, Version

from pypi_oldest_requirements import pypi
from pypi_oldest_requirements import misc


def _make_spec_set(req):
    if isinstance(req.specifier, SpecifierSet):
        return req.specifier
    else:
        return SpecifierSet(specifiers=','.join((''.join(s) for s in req.specs)))


def _get_all_versions(req):
    available_versions = pypi.get_versions(req.name)
    # actually a packaging.specifiers.SpecifierSet
    spec_set = _make_spec_set(req)
    return available_versions, spec_set


def _get_oldest_version(req):
    available_versions, spec_set = _get_all_versions(req)
    for av in sorted(available_versions, reverse=False):
        # for some reason 'av' is incompatible 'Version" object that spec_set wants to parse again
        if spec_set.contains(str(av)):
            return av
    raise RuntimeError(f'no matching version for {req.project_name}')


def _get_minimal_restricted_version(req):
    if len(req.specs) == 0:
        # return unconstrained
        return f'{req.name}\n'
    available_versions, spec_set = _get_all_versions(req)
    for av in sorted(available_versions, reverse=False):
        # for some reason 'av' is incompatible 'Version" object that spec_set wants to parse again
        if spec_set.contains(str(av)):
            if getattr(req, 'marker', None):
                return f'{req.name}=={av};{req.marker}\n'
            return f'{req.name}=={av}\n'
    raise RuntimeError(f'no matching version for {req.project_name}')


def _get_minimal_version(req):
    available_versions, spec_set = _get_all_versions(req)
    for av in sorted(available_versions, reverse=False):
        # for some reason 'av' is incompatible 'Version" object that spec_set wants to parse again
        if spec_set.contains(str(av)):
            return av
    raise RuntimeError(f'no matching version for {req.project_name}')


def _get_last_major_versions(req, skip_n_releases=1):
    available_versions, spec_set = _get_all_versions(req)
    last_release = None
    skipped = 0
    for av in sorted(available_versions, reverse=True):
        # for some reason 'av' is incompatible 'Version" object that spec_set wants to parse again
        if not spec_set.contains(str(av)) or av.is_prerelease or av.is_devrelease:
            continue
        if last_release is None:
            last_release = av.release
            continue
        if last_release > av.release:
            skipped += 1
            last_release = av.release
            if skipped >= skip_n_releases:
                return av
        print(f'last release {last_release}')
    # getting skipped version failed, return fallback
    available_versions, spec_set = _get_all_versions(req)
    for av in sorted(available_versions, reverse=True):
        # for some reason 'av' is incompatible 'Version" object that spec_set wants to parse again
        if spec_set.contains(str(av)):
            return av
    raise RuntimeError(f'no matching version for {req.name}')


def _get_compliant_versions(req):
    available_versions, spec_set = _get_all_versions(req)
    compliant = []
    for av in sorted(available_versions, reverse=False):
        # for some reason 'av' is incompatible 'Version" object that spec_set wants to parse again
        if spec_set.contains(str(av)):
            compliant.append(av)
    raise RuntimeError(f'no matching version for {req.project_name}')


def _get_from_req_file(req_file, filter_func):
    # requirements files can contain relative imports
    parsed = []
    with misc.cd(os.path.dirname(os.path.abspath(req_file))):
        for line in open(req_file, 'rt').readlines():
            try:
                gen = list(parse_requirements(line))
            except :
                gen = list(parser.parse(line))
            for req in gen:
                if req.name is None and hasattr(req, 'uri'):
                    # explicit uri dependency cannot install a different version anyway
                    continue
                parsed.append(req)
    for req in parsed:
        yield req.name, filter_func(req)


def get_oldest_from_req_file(req_file):
    return _get_from_req_file(req_file, _get_oldest_version)


def get_compliant_from_req_file(req_file):
    return _get_from_req_file(req_file, _get_compliant_versions)


def get_last_majors_from_req_file(req_file, skip_n_releases=1):
    from functools import partial
    filter_func = partial(_get_last_major_versions, skip_n_releases=skip_n_releases)
    return _get_from_req_file(req_file, filter_func)


def get_minimal_restricted_from_req_file(req_file, skip_n_releases=1):
    parsed = []
    verbatim = []
    # requirements files can contain relative imports
    with misc.cd(os.path.dirname(os.path.abspath(req_file))):
        for line in open(req_file, 'rt').readlines():
            try:
                gen = list(parse_requirements(line))
            except:
                gen = list(parser.parse(line))
            for req in gen:
                if req.name is None and hasattr(req, 'uri'):
                    # explicit uri dependency cannot install a different version anyway
                    verbatim.append(line)
                    continue
                parsed.append(req)
    for req in parsed:
        yield _get_minimal_restricted_version(req)
    yield '# verbatim copies of original lines'
    for line in verbatim:
        yield line



