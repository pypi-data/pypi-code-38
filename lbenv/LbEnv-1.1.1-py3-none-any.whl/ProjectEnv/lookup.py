###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
@author: Marco Clemencic <marco.clemencic@cern.ch>
'''

import os
import re
import logging

# FIXME: when we drop Python 2.4, this should become 'from . import path'
from LbEnv.ProjectEnv import path, Error
from LbEnv.ProjectEnv.version import (DEFAULT_VERSION, versionKey as _vkey,
                                      LCGInfoName)

log = logging.getLogger(__name__)

_PLATFORM_ID_RE = re.compile(
    r'((x86_64|i686)-[a-z]+[0-9]+-[a-z]+[0-9]+-[a-z0-9]+)|'
    r'([a-z]+[0-9]+_[a-z]+[0-9]+_[a-z]+[0-9]+(_dbg)?)')

# use uppercase names for case insensitive match
EXTERNAL_PROJECTS = ('ROOT', )


def platform_sort_key(platform):
    '''
    Key function to sort platforms.

    The preferred platform has highest score.
    '''
    if '-' not in platform:
        os_id, arch, comp = platform.split('_')
        arch = {'ia32': 'i686', 'amd64': 'x86_64'}.get(arch, arch)
        opt = 'opt'
    else:
        arch, os_id, comp, opt = platform.split('-')
    os_id = tuple(int(i) for i in os_id if i.isdigit())
    comp = tuple(int(i) for i in comp if i.isdigit())
    return ('0' if opt == 'do0' else opt, arch, comp, os_id)


def isPlatformId(s):
    '''
    Return True if the string looks like a platform id.

    >>> isPlatformId('x86_64-centos7-gcc64-opt')
    True
    >>> isPlatformId('slc4_ia32_gcc34')
    True
    >>> isPlatformId('include')
    False
    '''
    return bool(_PLATFORM_ID_RE.match(s))


def versionKey(x):
    return _vkey(x[0])


class NotFoundError(Error):
    '''
    Generic error for configuration elements that are not found.
    '''

    def __str__(self):
        return 'cannot find {0}'.format(self.args[0])


class MissingManifestError(NotFoundError):
    '''
    The manifest.xml for a project was not found.
    '''


class MissingProjectError(NotFoundError):
    '''
    A project was not found.
    '''

    def __init__(self, *args):
        super(MissingProjectError, self).__init__(*args)
        self.name, self.version, self.platform, self.path = args

    def __str__(self):
        return 'cannot find project {0} {1} for {2} in {3}'.format(*self.args)


class MissingDataPackageError(NotFoundError):
    '''
    A data package was not found.
    '''

    def __init__(self, *args):
        super(MissingDataPackageError, self).__init__(*args)
        self.name, self.version, self.path = args

    def __str__(self):
        return 'cannot find data package {0} {1} in {2}'.format(*self.args)


class InvalidNightlySlotError(NotFoundError):
    '''
    A nightly slot build was not found.
    '''

    def __init__(self, *args):
        super(InvalidNightlySlotError, self).__init__(*args)
        self.slot, self.build_id, self.path = args

    def __str__(self):
        return 'cannot find nightly slot build {0}/{1}{2}.'.format(
            self.args[0], self.args[1], ' in {}'.format(self.args[2])
            if self.args[2] else '')


def findFile(name, search_path=None):
    '''
    Look for a file in the search path.
    '''
    log.debug('looking for file %r', name)
    from LbEnv import which
    fn = which(name, search_path or path)
    if fn:
        log.debug('found %r', fn)
    else:
        raise NotFoundError(name)
    return fn


def findProject(name, version, platform, allow_empty_version=False):
    '''
    Find a Gaudi-based project in the directories specified in the 'path'
    variable.

    @param name: name of the project (case sensitive for local projects)
    @param version: version of the project
    @param platform: binary platform id
    @param allow_empty_version: if True, we allow also the plain project name
                                (without version)

    @return path to the project binary directory

    If name is None, version should be the path to the top directory of the
    project.
    '''
    log.debug('findProject(name=%r, version=%r, platform=%r, '
              'allow_empty_version=%r)', name, version, platform,
              allow_empty_version)

    if name:
        # standard project suffixes
        suffixes = [
            '{0}_{1}'.format(name, version),
            os.path.join(name.upper(), '{0}_{1}'.format(name.upper(),
                                                        version)),
            os.path.join(name.upper(), version)
        ]
        # special case: for the 'latest' version we allow the plain name
        if allow_empty_version:
            suffixes.insert(0, name)
    else:
        # path to project used, no need for suffixes
        suffixes = [os.curdir]

    # if project name is None, version is the path to the top level directory
    # of the project
    for d in [
            os.path.normpath(os.path.join(b, s, bindir))
            for b in (path if name else [version]) for s in suffixes
            for bindir in (os.path.join('InstallArea', platform), os.curdir)
    ]:
        log.debug('check %s', d)
        if os.path.exists(d):
            log.debug('OK')
            return d
    else:
        raise MissingProjectError(name, version, platform, path)


def findNightlyDir(slot, build_id, nightly_bases):
    '''
    Return the directory of the requested build of a nightly slot, looking in
    the directories listed in nightly_bases.

    If not found raise InvalidNightlySlotError
    '''
    # FIXME: we cannot use logging here because this function is called too
    # early in the script

    # log.debug('looking for slot %s %s', slot, build_id)
    for slot_dir in [
            os.path.join(nightly_base, slot_id, build_id)
            for slot_id in (slot, 'lhcb-' + slot)
            for nightly_base in nightly_bases
    ]:
        if os.path.isdir(slot_dir):
            # log.debug('found %s', slot_dir)
            return slot_dir
    # log.warning('not found')
    raise InvalidNightlySlotError(slot, build_id, nightly_bases)


def listVersions(name, platform):
    '''
    Find all instances of a Gaudi-based project in the directories specified in
    the 'path' variable and return the list of versions found.

    @param name: name of the project (case sensitive for local projects)
    @param platform: binary platform id

    @return generator of pairs (version, fullpath)
    '''
    # for special external projects case we delegate to another function
    if name.upper() in EXTERNAL_PROJECTS:
        for entry in listExtVersions(name, platform):
            yield (entry[0], entry[2])
        return
    # FIXME: when we drop Python 2.4, this should become
    # 'from .version import isValidVersion'
    from LbEnv.ProjectEnv.version import isValidVersion
    log.debug('listVersions(name=%r, platform=%r)', name, platform)

    name_u = name.upper()
    prefix = name + '_'
    prefix_u = name_u + '_'
    prefixlen = len(prefix)

    signature = os.path.join('InstallArea', platform, os.curdir)
    if name == 'LCG':
        signature = LCGInfoName(platform)
    log.debug('looking for %s in the search path', signature)

    def matches(path):
        # log.debug('testing %s', path)
        return (os.path.exists(os.path.join(path, signature))
                or platform == 'any')

    found_versions = set()
    for p in [dirname for dirname in path if os.path.isdir(dirname)]:
        files = set(os.listdir(p))
        # the plain project name is taken into account as 'default' version
        if DEFAULT_VERSION not in found_versions and name in files:
            fullpath = os.path.join(p, name)
            if matches(fullpath):
                found_versions.add(DEFAULT_VERSION)
                yield (DEFAULT_VERSION, fullpath)

        # versions like 'Project_vXrY'
        for entry in sorted(
            [(filename[prefixlen:], os.path.join(p, filename))
             for filename in files
             if (filename.startswith(prefix)
                 and isValidVersion(name, filename[prefixlen:]))],
                reverse=True,
                key=versionKey):
            version, fullpath = entry
            if (version not in found_versions and matches(fullpath)):
                found_versions.add(version)
                yield entry

        # versions like PROJECT/PROJECT_vXrY
        project_dir = os.path.join(p, name_u)
        if os.path.isdir(project_dir):
            for entry in sorted(
                [(filename[prefixlen:], os.path.join(project_dir, filename))
                 for filename in os.listdir(project_dir)
                 if (filename.startswith(prefix_u)
                     and isValidVersion(name, filename[prefixlen:]))],
                    reverse=True,
                    key=versionKey):
                version, fullpath = entry
                if (version not in found_versions and matches(fullpath)):
                    found_versions.add(version)
                    yield entry


def listPlatforms(name, version, allow_empty_version=False, quiet=False):
    '''
    Find a version of a Gaudi-based project in the directories specified in
    the 'path' variable and return the list of platforms available.

    @param name: name of the project (case sensitive for local projects)
    @param version: version string
    @allow_empty_version: search also in directories without the version
    @quiet: if true, do not print a warning if the project is not found

    @return list of platform strings

    If name is None, version should be the path to the top directory of the
    project.
    '''
    from os.path import isdir, join, normpath, exists
    # for special external projects case we delegate to another function
    if name.upper() in EXTERNAL_PROJECTS:
        return listExtPlatforms(name, version)
    log.debug('listPlatforms(name=%r, version=%r, allow_empty_version=%r)',
              name, version, allow_empty_version)

    if name:
        # standard project suffixes
        suffixes = [
            '{0}_{1}'.format(name, version),
            join(name.upper(), '{0}_{1}'.format(name.upper(), version)),
            join(name.upper(), version)
        ]
        # special case: for the 'latest' version we allow the plain name
        if allow_empty_version:
            suffixes.insert(0, name)
    else:
        # path to project used, no need for suffixes
        suffixes = [os.curdir]

    platforms = set()
    # if project name is None, version is the path to the top level directory
    # of the project
    for d in [
            normpath(join(b, s)) for b in (path if name else [version])
            for s in suffixes
    ]:
        log.debug('check %s', d)
        inst_area = join(d, 'InstallArea')
        if isdir(inst_area):
            for platform in os.listdir(inst_area):
                p_dir = join(inst_area, platform)
                if (isdir(p_dir) and isPlatformId(platform)
                        or exists(join(p_dir, 'manifest.xml'))):
                    platforms.add(platform)
        elif exists(join(d, 'manifest.xml')):
            platforms.add('<no-platform>')

    if not platforms:
        (log.debug if quiet else log.warning)('could not find %s/%s in %r',
                                              name, version, path)
    return sorted(platforms, key=platform_sort_key, reverse=True)


def findDataPackage(name, version):
    '''
    Find a data package in the directories specified in the 'path' variable,
    using, optionally, the standard suffixes 'DBASE' and 'PARAM'.
    If version is a pattern, the latest version matching the pattern is
    returned.

    @param name: name of the package with "hat" (case sensitive)
    @param version: glob pattern to filter the version

    @return: the path to the data package
    '''
    from fnmatch import fnmatch

    suffixes = ['', 'DBASE', 'PARAM']
    versions = []
    for p in [os.path.join(b, s, name) for b in path for s in suffixes]:
        if os.path.exists(p):
            lst = os.listdir(p)
            if version in lst:
                # stop searching if we find an exact match
                return os.path.join(p, version)
            versions.extend([(v, p) for v in lst if fnmatch(v, version)])
    if not versions:
        raise MissingDataPackageError(name, version, path)
    # sort the versions found
    versions.sort(key=versionKey, reverse=True)
    v, p = versions[0]
    return os.path.join(p, v)


def parseManifest(manifest):
    '''
    Extract the list of required projects and data packages from a manifest.xml
    file.

    @param manifest: path to the manifest file
    @return: tuple with ([projects...], [data_packages...]) as (name, version)
             pairs
    '''
    from xml.dom.minidom import parse
    m = parse(manifest)

    def _iter(parent, child):
        '''
        Iterate over the tags in <parent><child/><child/></parent>.
        '''
        for pl in m.getElementsByTagName(parent):
            for c in pl.getElementsByTagName(child):
                yield c

    # extract the list of used (project, version) from the manifest
    used_projects = [(p.attributes['name'].value,
                      p.attributes['version'].value)
                     for p in _iter('used_projects', 'project')]
    # extract the list of data packages
    data_packages = [(p.attributes['name'].value,
                      p.attributes['version'].value)
                     for p in _iter('used_data_pkgs', 'package')]
    return (used_projects, data_packages)


def getEnvXmlPath(project, version, platform, allow_empty_version=False):
    '''
    Return the list of directories to be added to the Env XML search path for
    a given project.
    '''
    pdir = findProject(
        project, version, platform, allow_empty_version=allow_empty_version)
    search_path = [pdir]
    # manifests to parse
    manifests = [os.path.join(pdir, 'manifest.xml')]
    while manifests:
        manifest = manifests.pop(0)
        if not os.path.exists(manifest):
            raise MissingManifestError(manifest)
        projects, packages = parseManifest(manifest)
        # add the data package directories
        search_path.extend([findDataPackage(p, v) for p, v in packages])
        # add the project directories ...
        pdirs = [findProject(p, v, platform) for p, v in projects]
        search_path.extend(pdirs)
        # ... and their manifests to the list of manifests to parse
        manifests.extend(
            [os.path.join(pdir, 'manifest.xml') for pdir in pdirs])

    def _unique(iterable):
        returned = set()
        for i in iterable:
            if i not in returned:
                returned.add(i)
                yield i

    return list(_unique(search_path))


def findLCG(version, platform):
    '''
    Return the path to the requested LCG version, found in the search path.
    '''
    for p in [
            os.path.join(b, s, n) for b in path
            for s in ('', 'LCG_%s' % version)
            for n in ('LCG_%s_%s.txt' % (version, platform),
                      LCGInfoName(platform))
    ]:
        if os.path.exists(p):
            return os.path.dirname(p)
    for p in [
            os.path.join(b, 'LCGCMT', s) for b in path
            for s in ('LCGCMT_%s' % version, 'LCGCMT-%s' % version)
    ]:
        if os.path.exists(p):
            return p


def getHepToolsInfo(manifest):
    '''
    Extract the hep tools version and platform from a manifest file.
    '''
    from xml.dom.minidom import parse

    log.debug('extracting heptools version from %s', manifest)
    try:
        m = parse(manifest)
        heptools = m.getElementsByTagName('heptools')[0]
        version = (heptools.getElementsByTagName('version')[0]
                   .firstChild.nodeValue)
        platform = (heptools.getElementsByTagName('binary_tag')[0]
                    .firstChild.nodeValue)
        return version, platform
    except (IndexError, AttributeError) as exc:
        # cannot extract heptools version and platform
        raise NotFoundError('heptools info: %s' % exc)


def getLCGRelocation(manifest):
    from os.path import dirname, basename, join, pardir

    try:
        version, platform = getHepToolsInfo(manifest)
    except NotFoundError as exc:
        log.debug(str(exc))
        return {}

    log.debug('looking for LCG %s %s', version, platform)
    lcg_path = findLCG(version, platform)
    if not lcg_path:
        log.debug('cannot find LCG path')
        return {}
    # FIXME: xenv has got problems with unicode filenames
    lcg_path = str(lcg_path)
    log.debug('found LCG at %s', lcg_path)

    if basename(dirname(lcg_path)) == 'LCGCMT':
        # old style
        lcg_root = dirname(dirname(lcg_path))
        return {
            'LCG_releases':
            lcg_root,
            'LCG_external': (lcg_root
                             if lcg_root.endswith('external') else join(
                                 lcg_root, pardir, pardir, 'external'))
        }
    else:
        # new style
        return {
            'LCG_releases':
            lcg_path,
            'LCG_external':
            lcg_path,
            'LCG_releases_base': (dirname(lcg_path) if lcg_path.endswith(
                'LCG_%s' % version) else lcg_path)
        }


def getProjectNameVersion(manifest):
    '''
    Get project name and version from a manifest.xml.
    '''
    from xml.dom.minidom import parse

    log.debug('extracting project name from %s', manifest)
    name, version = None, None
    try:
        m = parse(manifest)
        project = m.getElementsByTagName('project')[0]
        name = project.getAttribute('name')
        version = project.getAttribute('version')
    except (IndexError, AttributeError) as exc:
        log.debug('cannot extract project name or version: %s', exc)
    return name, version


def listExtVersions(ext, platform):
    '''
    @return generator of tuples (ext_version, LCG_version, LCG_path)
    '''
    ext = ext.upper()  # case insensitive check
    found_versions = set()
    for LCG_version, LCG_path in listVersions('LCG', platform):
        for l in open(os.path.join(LCG_path, LCGInfoName(platform))):
            l = l.split(';')
            if l[0].strip().upper() == ext:
                v = l[2].strip()
                if v not in found_versions:
                    found_versions.add(v)
                    yield (l[2].strip(), LCG_version, LCG_path)
                break  # go to next LCG version


def listExtPlatforms(ext, version):
    '''
    @return list of available platforms for a version of an extrenal project
    '''
    import glob
    log.debug('listExtPlatforms(ext=%r, version=%r)', ext, version)

    ext = ext.upper()  # case insensitive check

    info_glob = LCGInfoName('*')
    # transform the glob in a capturing regexp
    platform_exp = re.compile(re.escape(info_glob).replace('\\*', '(.*)'))

    platforms = set()
    for p in [
            os.path.join(b, s, info_glob) for b in path for s in ('', 'LCG_*')
    ]:
        for f in glob.glob(p):
            # it must match if the glob matched
            platform = platform_exp.search(f).group(1)
            # to be sure, check if the external is in the list with the right
            # version
            for l in (l.split(';') for l in open(f)):
                if l[0].strip().upper() == ext and l[2].strip() == version:
                    platforms.add(platform)
                    break
    return sorted(platforms, key=platform_sort_key, reverse=True)


def findLCGForExt(ext, version, platform):
    '''
    Return the (highest) version of LCG containing the required version of
    an external project.
    '''
    for ext_vers, LCG_vers, _path in listExtVersions(ext, platform):
        if ext_vers == version:
            return LCG_vers
    raise MissingProjectError(ext, version, platform, path)


PREFERRED_PLATFORM = (os.environ.get('BINARY_TAG')
                      or os.environ.get('CMTCONFIG') or None)


def _findManifest(path, platform_hint=PREFERRED_PLATFORM):
    '''
    Find a manifest file of the project rooted at 'path'.
    '''
    from os.path import join, exists, isdir
    # try the InstallArea level for the current platform
    inst = join(path, 'InstallArea')

    def candidates():
        if platform_hint:
            yield join(inst, platform_hint, 'manifest.xml')
        if isdir(inst):
            for p in os.listdir(inst):
                yield join(inst, p, 'manifest.xml')
        yield join(path, 'manifest.xml')

    for c in candidates():
        if exists(c):
            return c
    return None


def walkProjectDeps(project, version, platform='any', ignore_missing=False):
    '''
    Return a tuple ((project, version), rootdir, dependencies) for the
    requested project and all its dependencies.

    The dependencies are returned as a list of (project, version) and the list
    can be altered to control which dependency to follow and which not.

    Note that when walking through the dependencies a project may appear more
    than once (for diamond dependency graphs).
    '''
    if project.lower() in ('lcg', 'heptools', 'lcgcmt'):
        return
    try:
        root = findProject(project, version, platform)
    except MissingProjectError as err:
        if ignore_missing:
            log.warning(str(err))
            return
        else:
            raise
    manifest = _findManifest(root)
    if manifest:
        deps = [(p, v) for p, v in parseManifest(manifest)[0]]
        try:
            deps.append(('lcg', getHepToolsInfo(manifest)[0]))
        except NotFoundError:
            pass
    else:
        deps = []
    yield (project, version), root, deps
    for project, version in deps:
        for x in walkProjectDeps(project, version, platform, ignore_missing):
            yield x


def getLHCbGrid(platform):
    '''
    Find the best LHCbGrid version and platform for the requested platform.
    '''
    from LbEnv.ProjectEnv.version import expandVersionAlias
    for version in [DEFAULT_VERSION, 'latest']:
        version = expandVersionAlias('LHCbGrid', 'latest', 'any')
        platforms = listPlatforms('LHCbGrid', version, quiet=True)
        if platforms:
            break
    else:
        raise NotFoundError('LHCbGrid')
    if platform not in platforms:
        log.warning('platform %s not available for LHCbGrid', platform)
        os_id = platform.split('-')[1]
        for platform in platforms:
            if platform.split('-')[1] == os_id:
                log.warning('using %s instead', platform)
                break
    return version, platform
