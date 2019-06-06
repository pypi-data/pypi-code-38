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
import sys
import traceback
import xenv

import LbPlatformUtils.describe
from LbPlatformUtils import host_supports_tag, get_viable_containers

from LbEnv.ProjectEnv.lookup import (
    getEnvXmlPath, findProject, findDataPackage, getLCGRelocation,
    getHepToolsInfo, NotFoundError, getProjectNameVersion, findLCGForExt,
    listVersions, listPlatforms, EXTERNAL_PROJECTS, InvalidNightlySlotError)
from LbEnv.ProjectEnv.version import (isValidVersion, expandVersionAlias,
                                      DEFAULT_VERSION, LCGInfoName)
from LbEnv import fixProjectCase, __version__

HOST_INFO = LbPlatformUtils.describe.platform_info()
HOST_PLATFORM = HOST_INFO['dirac_platform']
SUPPORTED_CONTAINERS = [
    c for c in HOST_INFO['container_technology']
    if HOST_INFO['container_technology'][c]
]

auto_override_projects = []


def decodePkg(s):
    '''
    Translate a string declaring a data package into a pair (package, version).

    The user can specify the data package they want to use in different ways
    and in all cases we need to return the package name with "hat" (also when
    the hat is implied) and the version pattern.

    >>> decodePkg('Hat/Package')
    ('Hat/Package', '*')
    >>> decodePkg('Package v7r*')
    ('Package', 'v7r*')
    >>> decodePkg('Package v1r0 Hat')
    ('Hat/Package', 'v1r0')
    >>> decodePkg('Hat/Package.v1r0')
    ('Hat/Package', 'v1r0')
    >>> decodePkg('Hat.Package.v1r0')
    ('Hat/Package', 'v1r0')
    >>> decodePkg('a b c d')
    Traceback (most recent call last):
       ...
    ValueError: too many words in package declaration 'a b c d'
    '''
    # split on spaces
    l = s.split()
    if len(l) == 2:
        pkg, vers = l
    elif len(l) == 3:
        pkg, vers, hat = l
        pkg = '{0}/{1}'.format(hat, pkg)
    elif len(l) == 1:
        if '.' in s:
            pkg, vers = s.rsplit('.', 1)
            pkg = pkg.replace('.', '/')
        else:
            pkg = s
            vers = '*'
    else:
        raise ValueError('too many words in package declaration %r' % s)

    return pkg, vers


def projectExtraPath(projroot):
    '''
    Return any extra search path required by the project at 'projroot'.
    '''
    from LbEnv.ProjectEnv.options import SearchPath, NightlyPathEntry
    extra_path = SearchPath([])
    # drop the 'InstallArea' part of the path
    while 'InstallArea' in projroot:
        projroot = os.path.dirname(projroot)

    # check for the Python digested search path
    spFile = os.path.join(projroot, 'searchPath.py')
    if os.path.exists(spFile):
        data = {}
        with open(spFile) as fp:
            exec(fp.read(), data)
        extra_path = data['path']

    # check for a requested nightly slot
    build_conf = os.path.join(projroot, 'build.conf')
    if os.path.exists(build_conf):
        vals = dict(l.strip().split('=', 1)
                    for l in map(str.strip, open(build_conf))
                    if l and not l.startswith('#'))
        slot = vals.get('nightly_slot')
        day = vals.get('nightly_day')
        base = vals.get('nightly_base') or os.environ.get('LHCBNIGHTLY', '')
        if slot and day and base:
            for p in extra_path:
                if isinstance(p, NightlyPathEntry):
                    p.base, p.slot, p.day = base, slot, day
                    break
            else:  # else clause for the 'for' statement
                extra_path.insert(0, NightlyPathEntry(base, slot, day))

    return extra_path


LOCAL_NIGHTLY_HELP = '''It can be installed locally and used with:

  lbn-install --verbose --projects {project} --platforms {platform} --dest {install_root}/{err.slot}/{err.build_id} {err.slot} {build_id}
  {prog} --nightly-base {install_root} {args}

(you can replace '{install_root}' with any directory)'''


def localNightlyHelp(prog, err, project, platform, args, error=True):
    '''
    Help message instructing on how to get and use a local installation of
    a nightly slot.
    '''
    try:
        from shlex import quote
    except ImportError:
        from pipes import quote

    import re
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from ssl import SSLError
    from json import load
    from difflib import get_close_matches
    from datetime import date, timedelta
    from LbEnv.Info import COUCHDB_ROOT

    class SlotError(Exception):
        pass

    class BadName(SlotError):
        def __str__(self):
            typename, name, all_slots = self.args
            msg = ['I do not know {} "{}"'.format(typename, name)]
            candidates = get_close_matches(name, all_slots)
            if candidates:
                candidates.sort()
                msg[0] += ', did you mean any of:'
                msg.extend('  - {}'.format(c) for c in candidates)
            return '\n'.join(msg)

    class NotReady(SlotError):
        def __str__(self):
            typename, name = self.args
            return '{} "{}" not built yet'.format(typename, name)

    # default message
    msg = LOCAL_NIGHTLY_HELP
    # build_id is meant to contain the numeric build id for the requested build
    build_id = err.build_id
    # check if the user request make any sense
    try:
        # does the slot name exist?
        all_slots = set(entry['key'] for entry in load(
            urlopen(
                COUCHDB_ROOT + '_design/names/_view/slots?group=true',
                timeout=5)).get('rows', []))
        # if err.slot not in all_slots:
        #     if ('lhcb-' + err.slot) in all_slots:
        #         err.slot = 'lhcb-' + err.slot
        if err.slot not in all_slots:
            raise BadName('slot', err.slot, all_slots)

        # if the user asked for a non numeric id, we need to find the actual id
        if not build_id.isdigit():
            build_id_alias = build_id.lower()
            # we allow day name, today, yesterday or a date, and we map it to a
            # ISO date (yyyy-mm-dd)
            DAYS = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
            if build_id_alias == 'today':
                build_date = str(date.today())
            elif build_id_alias == 'yesterday':
                build_date = str(date.today() - timedelta(1))
            elif build_id_alias in DAYS:
                build_date = str(date.today() - timedelta(
                    date.today().weekday() - DAYS.index(build_id_alias)))
            elif re.match(r'^\d{4}-\d\d-\d\d$', build_id_alias):
                build_date = build_id_alias
            else:
                # none of the allowed options
                raise BadName('build id', build_id, [])
            # let's check against all builds in the requested day
            rows = load(
                urlopen(
                    COUCHDB_ROOT + '_design/summaries/_view/byDay?key="{}"'.
                    format(build_date),
                    timeout=5)).get('rows', [])
            # was the slot built on that date?
            names = set(row['value']['slot'] for row in rows)
            if err.slot not in names:
                raise BadName('slot (for {})'.format(build_id), err.slot,
                              names)
            # if OK we get the highest numeric id in the day for that slot
            build_id = max(row['value']['build_id'] for row in rows
                           if row['value']['slot'] == err.slot)

        # at this point we have a numeric id, we try to get the build info
        try:
            slot_info = load(
                urlopen(
                    '{}{}.{}'.format(COUCHDB_ROOT, err.slot, build_id),
                    timeout=5))
        except HTTPError:
            # the numeric id is not known in the DB
            raise BadName('build id', build_id, [])

        if slot_info and slot_info.get('config', {}).get('platforms'):
            if platform not in slot_info['config']['platforms']:
                raise BadName('platform', platform,
                              slot_info['config']['platforms'])
            if platform not in slot_info.get('builds', {}):
                raise NotReady('platform', platform)
            if not slot_info['builds'][platform].get(project,
                                                     {}).get('completed'):
                raise NotReady('project', project)

    except SlotError as reason:
        msg = str(reason)
    except SSLError:
        # ignore connection problems and assume it's OK
        pass

    # format the final message
    if msg:
        msg += '\n\n'
    return '\n'.join(['{prog}: error: {err}\n' if error else '', msg]).format(
        prog=prog,
        err=err,
        build_id=build_id,
        project=project,
        platform=platform,
        args=' '.join(map(quote, args)),
        install_root='$TMPDIR' if os.environ.get('TMPDIR') else '/tmp')


class LbRun(xenv.Script):
    __usage__ = ('Usage: %prog [OPTION]... [NAME=VALUE]... '
                 'PROJECT[/VERSION] [COMMAND [ARG]...]')

    def _prepare_parser(self):
        from .options import addSearchPath, addPlatform, addListing
        from optparse import OptionValueError

        super(LbRun, self)._prepare_parser()
        parser = self.parser

        parser.version = '%prog {}'.format(__version__)

        parser.add_option(
            '--version',
            action='version',
            help="show program's version number and exit")

        parser.add_option(
            "--use",
            action="append",
            help="add a data package to the environment")
        parser.add_option(
            "--ext",
            action="append",
            help="add an external lcg tool environment")

        addPlatform(parser)
        addSearchPath(parser)
        addListing(parser)

        def extract_project_version(opt_str, rargs):
            if not rargs:
                raise OptionValueError(
                    '%s must be followed by the project'
                    ' name and optionally by the version' % opt_str)
            if '/' in rargs[0]:
                p_name, v = rargs.pop(0).split('/')
                p_name = fixProjectCase(p_name)
            else:
                p_name = fixProjectCase(rargs.pop(0))
                if rargs and isValidVersion(p_name, rargs[0]):
                    v = rargs.pop(0)
                else:
                    v = DEFAULT_VERSION
            return p_name, v

        def runtime_project_option(_option, opt_str, _value, parser):
            pv = extract_project_version(opt_str, parser.rargs)
            parser.values.runtime_projects.append(pv)

        parser.add_option(
            "--runtime-project",
            action="callback",
            metavar="PROJECT[/VERSION]",
            type="string",
            callback=runtime_project_option,
            nargs=0,
            help="Add a project to the runtime environment")

        def overriding_project_option(_option, opt_str, _value, parser):
            pv = extract_project_version(opt_str, parser.rargs)
            parser.values.overriding_projects.append(pv)

        parser.add_option(
            "--overriding-project",
            action="callback",
            metavar="PROJECT[/VERSION]",
            type="string",
            callback=overriding_project_option,
            nargs=0,
            help="Add a project to override packages")

        parser.add_option(
            "--no-auto-override",
            action="store_false",
            dest="auto_override",
            help="Do not automatically prepend the "
            "projects %s" % auto_override_projects)

        parser.add_option(
            "--grid-override",
            action="store_true",
            dest='grid_override',
            help="Override grid middleware versions [default]")

        parser.add_option(
            "--no-grid-override",
            action="store_false",
            dest='grid_override',
            help="Prevent override grid middleware versions")

        parser.add_option(
            "--grid-override-map",
            help="Use specific grid middleware override map")

        parser.add_option(
            "--use-grid",
            action="store_true",
            help="ignored, kept for backward compatibility")

        parser.add_option(
            "--use-sp",
            action="store_true",
            dest="use_setupproject",
            help="Force fallback on SetupProject even if the "
            "project have manifest.xml and a .xenv files")

        parser.add_option(
            "--no-sp",
            action="store_true",
            dest="no_setupproject",
            help="Prevent fallback on SetupProject in case of "
            "problems")

        # Note: the profile is not used in the script class, but in the wrapper
        #       it is added to the parser to appear in the help and for
        #       checking
        parser.add_option(
            "--profile",
            action="store_true",
            help="Print some profile informations about the "
            "execution.")

        parser.add_option(
            '--path-to-project',
            action='store_true',
            help='Interpret the first argument as path to a '
            'project top-level directory instead of as a '
            'project name')

        parser.add_option(
            '--container',
            choices=SUPPORTED_CONTAINERS,
            help='wrap the command to run in a container supporting the '
            'requested platform [allowed values: %s]' %
            ', '.join(SUPPORTED_CONTAINERS))

        parser.add_option(
            "--allow-containers",
            action="store_true",
            help="Allow a container technology to be automatically chosen if "
                 "native support is not available")

        parser.add_option(
            "--prefer-container",
            action="store_true",
            help="Prefer running inside containers to natively "
            "(implies --allow-containers)")

        parser.set_defaults(
            use=[],
            ext=[],
            runtime_projects=[],
            overriding_projects=[],
            auto_override=True,
            grid_override=True,
            use_grid=False,
            use_setupproject=False)
        self.allow_empty_version = False

    def _parse_args(self, args=None):
        super(LbRun, self)._parse_args(args)
        if len(self.cmd) < 1:
            self.parser.error("missing project " + (
                'path' if self.opts.path_to_project else 'name'))
        if self.opts.path_to_project:
            self.project = None
            self.version = os.path.abspath(self.cmd.pop(0))
        elif '/' in self.cmd[0]:
            self.project, self.version = self.cmd.pop(0).split('/')
            self.project = fixProjectCase(self.project)
        else:
            self.project = fixProjectCase(self.cmd.pop(0))
            if self.cmd and isValidVersion(self.project, self.cmd[0]):
                self.version = self.cmd.pop(0)
                self.log.warning('deprecated version specification: '
                                 'use "lb-run ... %s/%s ..." instead',
                                 self.project, self.version)
            else:
                # if no version is specified, we want to allow just the
                # project name
                self.allow_empty_version = True
                self.version = DEFAULT_VERSION
        if (self.opts.platform is None
                and str(self.project.lower()) == 'lhcbdirac'):
            self.opts.platform = 'best'
        else:
            from .options import checkPlatform
            self.opts.platform = checkPlatform(self.parser, self.opts.platform)

        if self.opts.prefer_container:
            self.opts.allow_containers = True

        if isinstance(self.opts.nightly, InvalidNightlySlotError):
            sys.stderr.write(
                localNightlyHelp(self.parser.prog, self.opts.nightly,
                                 self.project, self.opts.platform
                                 if self.opts.platform not in ('best', None)
                                 else '$CMTCONFIG', args or sys.argv[1:]))
            sys.exit(64)
        if self.opts.help_nightly_local:
            if not self.opts.nightly:
                self.parser.error('--help-nightly-local must be specified in '
                                  'conjunction with --nightly')
            sys.stdout.write(
                localNightlyHelp(
                    self.parser.prog,
                    InvalidNightlySlotError(self.opts.nightly[0],
                                            self.opts.nightly[1], []),
                    self.project,
                    self.opts.platform
                    if self.opts.platform not in ('best', None) else
                    '$CMTCONFIG', [
                        a for a in args or sys.argv[1:]
                        if not '--help-nightly-local'.startswith(a)
                    ],
                    error=False))
            sys.exit()

    def _add_ext_dir_to_env(self, path):
        def prepend(k, v):
            self.log.debug('prepending %s to %s', v, k)
            self.opts.actions.append(('prepend', (k, v)))

        def with_python(files):
            for f in files:
                if f.endswith('.py'):
                    return True
            return False

        for root, dirs, files in os.walk(path):
            base = os.path.basename(root)
            if base == 'bin':
                prepend('PATH', os.path.join(root))
                dirs[:] = []  # no not recurse
            elif base.startswith('lib'):
                prepend('LD_LIBRARY_PATH', root)
                if with_python(files):
                    prepend('PYTHONPATH', root)
                # let recurse
            elif base.startswith('python'):
                if with_python(files):
                    prepend('PYTHONPATH', root)
                # let recurse
            elif base == 'site-packages':
                prepend('PYTHONPATH', root)
                dirs[:] = []  # no not recurse
            dirs[:] = [
                d for d in dirs
                if d in ['bin', 'site-packages', 'lib', 'lib64']
                or d.startswith('python')
            ]

    def _handle_externals(self, lcg_path, manifest):
        if not self.opts.ext:
            return
        if not lcg_path:
            self.log.warning('no LCG found: ignoring --ext option')
            return

        if manifest:
            _version, platform = getHepToolsInfo(manifest)
        else:
            platform = self.opts.platform
        ext_info_file = os.path.join(lcg_path, LCGInfoName(platform))
        if not os.path.isfile(ext_info_file):
            self.log.warning('no LCG_externals_<>.txt found: '
                             'ignoring --ext option')
            return

        def parse_deps_list(s):
            s = s.strip()
            if s:
                return [x.rsplit('-', 1)[0].lower() for x in s.split(',')]
            else:
                return []

        self.log.debug('handling required externals')
        # get list of ext dirs from LCG_externals_<platform>.txt
        # the result is a dictionary {name: (path, deps)}
        exts_info = dict(
            (x[0].lower(), (os.path.join(lcg_path, x[3]),
                            parse_deps_list(x[4]))) for x in
            [list(map(str.strip, x.split(';'))) for x in open(ext_info_file)]
            if len(x) == 5)

        # we want case insensitive lookup and the use may specify
        #  --ext A --ext B,C
        exts = set(
            map(str.lower, sum([x.split(',') for x in self.opts.ext], [])))
        if exts - set(exts_info):
            self.log.warning('ignored unknown externals: %s',
                             ', '.join(exts - set(exts_info)))
            exts = exts.intersection(exts_info)

        # expand dependencies
        count = -1
        while len(exts) != count:  # expand until we get the full list
            count = len(exts)  # size before expansion
            exts.update(sum([exts_info[ext][1] for ext in exts], []))

        if self.project == 'LCG':
            # for LCG we need to explicitly pick up the compiler
            for l in open(ext_info_file):
                if l.startswith('COMPILER:'):
                    name, version = l[9:].strip().split(';')
                    exts.add(name)
                    exts_info[name] = (os.path.join(
                        lcg_path, name, version, '-'.join(
                            platform.split('-')[:2])), None)
                    break
            else:  # this 'else' matches the 'for'
                raise NotFoundError('compiler in %s' % ext_info_file)

        # add all externals to the environment
        for ext in exts:
            path = exts_info[ext][0]
            if os.path.isdir(path):
                self._add_ext_dir_to_env(path)
                # special cases
                if ext == 'root':
                    self.opts.actions.append(('set', ('ROOTSYS', path)))
            else:
                self.log.warning('unusable path for %s: %s', ext, path)

    def _findPlatformAndContainer(self):
        '''
        Find the best combination of platform and container to use.
        '''
        if self.opts.platform.lower() == 'best':
            platforms = listPlatforms(self.project, self.version)
        else:
            platforms = [self.opts.platform]

        container_types = []

        if self.opts.container:
            container_types.append(self.opts.container)
        else:
            if self.opts.allow_containers:
                container_types += SUPPORTED_CONTAINERS
            if self.opts.prefer_container:
                container_types.append(None)
            else:
                container_types.insert(0, None)

        for container_type in container_types:
            for platform in platforms:
                if not host_supports_tag(HOST_INFO, platform, container_type):
                    continue
                if self.opts.platform.lower() == 'best':
                    self.log.warning('Decided best platform to use is {0}'
                                     .format(platform))
                if self.opts.allow_containers:
                    self.log.warning('Decided best container to use is {0}'
                                     .format(container_type))
                return platform, container_type

        if self.opts.platform.lower() == 'best':
            self.log.error('current host does not support any of %s/%s '
                           'available platforms', self.project, self.version)
            self._print_viable_containers()
            raise SystemExit(64)
        elif self.opts.container:
            msg = ('container technology {1} does not support platform {0}'
                   ).format(self.opts.platform, self.opts.container)
        else:
            msg = ('current host does not support platform {0} '
                   '(dirac_platform: {1}, required: {2}').format(
                       self.opts.platform, HOST_PLATFORM,
                       LbPlatformUtils.requires(self.opts.platform))
            if not HOST_PLATFORM.endswith('-' + HOST_INFO['os_id']):
                msg += ', os_id: {0}'.format(HOST_INFO['os_id'])
            msg += ')'

        if self.opts.force_platform:
            self.log.warning(msg)
        else:
            self.log.error(msg)

        self.log.info('CPU model: %s', HOST_INFO['model'])
        self.log.info('microarch flags: %s', HOST_INFO['flags'])
        if not self.opts.force_platform:
            self._print_viable_containers()
            sys.exit(66)

    def _print_viable_containers(self):
        if not self.opts.container:
            viable_containers = get_viable_containers(HOST_INFO,
                                                      self.opts.platform)
            if viable_containers:
                self.log.warning('you may try adding to the options:')
                for container in viable_containers:
                    self.log.warning('  --container %s', container)

    def overrideGridMiddleware(self):
        '''
        Modify the environment to override middleware libraries.
        '''
        if not self.opts.grid_override:
            self.log.debug('not overriding grid middleware')
            return

        from json import load
        from re import sub, error as re_error
        from hashlib import sha1
        from itertools import chain

        try:
            if not self.opts.grid_override_map:
                self.opts.grid_override_map = os.path.join(
                    findDataPackage('LbEnvFix', 'prod'), 'override_map.json')
            override_map = load(open(self.opts.grid_override_map, 'rt'))

            substitutions = override_map.get('substitutions', [])

            checksum = sha1()
            for x in chain.from_iterable(substitutions):
                checksum.update(x.encode('utf-8'))

            self.log.info('using override map version %s (sha1: %s)',
                          override_map.get('version', 'unknown'),
                          checksum.hexdigest())

            for varname in self.env:
                value = '{0}={1}'.format(varname, self.env[varname])
                for entry in substitutions:
                    a, b = entry[:2]
                    before = value
                    value = sub(a, b, value)
                    if value != before:
                        comment = '' if len(entry) < 3 else \
                                  ' ({})'.format(entry[2])
                        self.log.info('replaced %s with %s in %s%s', a, b,
                                      varname, comment)
                value = value.split('=', 1)
                if value[0] == varname:
                    self.env[varname] = value[1]
                else:
                    self.log.warning('variable rename not supported in '
                                     'override map (%s -> %s)', varname,
                                     value[0])
        except (NotFoundError, IOError, ValueError, re_error) as err:
            self.log.warning('%s: %s, not overriding grid middleware',
                             type(err).__name__, err)

    def _makeEnv(self):
        # FIXME: when we drop Python 2.4, this should become
        #        'from . import path'
        from LbEnv.ProjectEnv import path, SearchPathEntry

        try:
            if self.project.lower() == 'lhcbdirac':
                self.log.debug('try new LHCbDirac environment tool')
                from LbEnv.ProjectEnv.LHCbDirac import (getLHCbDiracEnv,
                                                        LHCbDiracEnvError)
                # different convention between lb-run and lhcbdirac
                for item in list(getLHCbDiracEnv('pro' if self.version ==
                                            'prod' else self.version).items()):
                    self.opts.actions.append(('set', item))
                # FIXME: this section is a copy of the code at the end of the
                #        function, but it's not factored out because this is
                #        anyway a temporary workaround
                try:
                    super(LbRun, self)._makeEnv()
                    return
                except SystemExit as exc:
                    raise SystemExit(exc.code | 64)
        except LHCbDiracEnvError:
            # Could not use new LHCbDirac environment tool, use old style
            self.log.debug('fall back to legacy LHCbDirac environment')

        if self.opts.use_grid:
            self.log.warning('the option --use-grid is ignored (deprecated)')

        # prepend dev dirs to the search path
        if self.opts.dev_dirs:
            path[:] = self.opts.dev_dirs + path

        if self.opts.user_area and not self.opts.no_user_area:
            path.insert(0, SearchPathEntry(self.opts.user_area))

        if self.opts.path_to_project:
            if self.opts.list:
                self.parser.error('options --list and --path-to-project '
                                  'are incompatible')
            elif self.opts.use_setupproject:
                self.parser.error('options --use-sp and --path-to-project '
                                  'are incompatible')

        # FIXME: we need to handle common options like --list in a single place
        if self.opts.list:
            for entry in listVersions(self.project, self.opts.platform):
                print('%s in %s' % entry)
            sys.exit(0)
        if self.opts.list_platforms:
            platforms = listPlatforms(self.project, self.version)
            if platforms:
                print('\n'.join(platforms))
            sys.exit(0)

        self.opts.platform, self.opts.container = self._findPlatformAndContainer()

        # special handling of external projects
        # (unless we only want to list)
        if self.project.upper() in EXTERNAL_PROJECTS:
            self.opts.ext.append(self.project)
            if self.allow_empty_version:  # no version specified
                # for LCG the version DEFAULT_VERSION does not make sense
                self.version = 'latest'
            else:
                self.version = findLCGForExt(self.project, self.version,
                                             self.opts.platform)
            self.project = 'LCG'

        self.version = expandVersionAlias(self.project, self.version,
                                          self.opts.platform)

        # prepare the list of projects to use
        projects = []
        if self.opts.auto_override:
            explicit = set([p[0] for p in self.opts.overriding_projects])
            projects.extend(
                [p for p in auto_override_projects if p[0] not in explicit])
        projects.extend(self.opts.overriding_projects)
        projects.append((self.project, self.version))
        projects.extend(self.opts.runtime_projects)

        # Check if the main project needs a special search path
        self.log.debug('check if we need extra search path')
        project_path = findProject(
            self.project,
            self.version,
            self.opts.platform,
            allow_empty_version=self.allow_empty_version)
        extra_path = projectExtraPath(project_path)
        if extra_path:
            self.log.debug('the project requires an extra search path')
            # we add the extra search path between the command line entries
            # and the default
            idx = len(self.opts.dev_dirs)
            if self.opts.user_area:
                idx += 1
                path[:] = path[:idx] + extra_path + path[idx:]
        self.log.debug('final search path: %r', path)
        # Make sure the wrapped commands sees the same search path as us
        self.opts.actions.append(('set', ('CMAKE_PREFIX_PATH', str(path))))
        self.opts.actions.append(('set', ('CMTPROJECTPATH', str(path))))

        # set the environment XML search path
        env_path = []
        for p, v in projects:
            if p == 'LCG':
                continue
            if p:
                v = expandVersionAlias(p, v, self.opts.platform)
            self.log.info('using %s/%s %s', p, v, self.opts.platform)
            env_path.extend(
                getEnvXmlPath(p, v, self.opts.platform,
                              self.allow_empty_version and p == self.project))

        # ensure that we do not have unicode strings
        # FIXME: xenv has got problems with unicode in the search path
        env_path = list(map(str, env_path))
        xenv.path.extend(env_path)

        # set LCG relocation roots
        if self.project == 'LCG':
            self.log.debug('project is LCG, using externals from %s',
                           project_path)
            lcg_relocation = {'LCG_external': project_path}
            manifest = None
        else:
            manifest = os.path.join(project_path, 'manifest.xml')
            lcg_relocation = getLCGRelocation(manifest)
        self.opts.actions.extend(
            ('set', (k, v)) for k, v in list(lcg_relocation.items()))

        self._handle_externals(lcg_relocation.get('LCG_external'), manifest)

        # now we can expand project name and version if --path-to-project
        if self.opts.path_to_project:
            self.project, self.version = \
                getProjectNameVersion(os.path.join(project_path,
                                                   'manifest.xml'))
            # FIXME: xenv has got problems with unicode in the search path
            self.project, self.version = list(map(str, (self.project, self.version)))

        # extend the prompt variable (bash, sh)
        if self.cmd and os.path.basename(self.cmd[0]) in ('bash', 'sh'):
            prompt = os.environ.get('PS1', r'\W \$ ')
        # extend the prompt variable (zsh)
        elif self.cmd and os.path.basename(self.cmd[0]) in ('zsh', ):
            prompt = os.environ.get('PS1', r'%1d%# ')
        else:
            prompt = '> '

        self.opts.actions.append(('set', ('PS1', r'[{0} {1}] {2}'.format(
            self.project, self.version, prompt))))

        # instruct the script to load the projects environment XML
        for p, _ in projects[::-1]:
            if p == 'LCG':
                continue
            if not p:  # this flags the main project (when --path-to-project)
                p = self.project
            self.opts.actions.append(('loadXML', (p + '.xenv', )))

        # handle the extra data packages
        for pkg_name, pkg_vers in map(decodePkg, self.opts.use):
            xml_name = pkg_name.replace('/', '_') + '.xenv'
            xml_path = os.path.join(
                findDataPackage(pkg_name, pkg_vers), xml_name)
            if not os.path.exists(xml_path):
                # fall back on the old conventional name
                xml_path = xml_path[:-5] + 'Environment.xml'
            # FIXME: xenv has got problems with unicode filenames
            self.opts.actions.append(('loadXML', (str(xml_path), )))

        # Set the CMTCONFIG and BINARY_TAG as they could different from the env
        self.opts.actions.append(('set', ('CMTCONFIG', self.opts.platform)))
        self.opts.actions.append(('set', ('BINARY_TAG', self.opts.platform)))

        try:
            super(LbRun, self)._makeEnv()
        except SystemExit as exc:
            # make sure that an exit from underlying _makeEnv has the right
            # bit set
            raise SystemExit(exc.code | 64)

        self.overrideGridMiddleware()

    def compatMain(self, reason=None):
        '''
        Fall-back function to call the old SetupProject code.
        '''
        from .compatibility import getOldEnvironment
        if reason:
            self.log.warning('trying old SetupProject (%s)', reason)

        # fix command line to fit old SetupProject
        if self.cmd:
            args = sys.argv[1:-len(self.cmd)]
        else:
            args = sys.argv[1:]

        if self.opts.allow_containers and self.opts.container:
            args.insert(0, '--container='+self.opts.container)

        project_idx = len(args) - 1
        while (project_idx >= 0 and not args[project_idx].lower()
               .startswith(self.project.lower())):
            project_idx -= 1

        # if we ran "best platform match", pass the result to SetupProject
        args.insert(project_idx, '--platform=' + self.opts.platform)
        os.environ['CMTCONFIG'] = self.opts.platform

        split_platform = self.opts.platform.split('-')
        if len(split_platform) < 2:
            raise ValueError('Platform appears to be invalid', split_platform)
        args.insert(project_idx, '--tag_add=host-' + split_platform[1])

        self.log.debug('invoking SetupProject with arguments: %s', args)
        self.env = getOldEnvironment(args)

        self.overrideGridMiddleware()

        if self.cmd:
            return self.runCmd()
        else:
            self.dump()
            return 0

    def runCmd(self):
        if self.opts.container == 'singularity':
            self.log.debug('preparing singularity wrapper command')
            # wrap command in container
            wrapper = [
                'singularity', 'exec', '--home', '$HOME:/home', '--bind',
                '/cvmfs'
            ]
            from LbPlatformUtils.inspect import SINGULARITY_ROOTS
            supported_roots = HOST_INFO['container_technology']['singularity']
            for root, _ in SINGULARITY_ROOTS:
                if self.opts.platform in supported_roots[root]:
                    self.log.debug('selected singularity root %s', root)
                    wrapper.append(root)
                    break
            else:
                # We should have failed earlier, but better be sure
                self.log.error('platform not supported by container')
                sys.exit(66)
            # Note: singularity (or cernvm) strips PATH and LD_LIBRARY_PATH
            # - LD_LIBRARY_PATH can be propagated with this trick
            self.env['SINGULARITYENV_LD_LIBRARY_PATH'] = \
                self.env['LD_LIBRARY_PATH']
            # - this is the only way to propagate PATH
            wrapper.extend(['env', 'PATH=' + self.env['PATH']])
            self.cmd = wrapper + self.cmd
            self.log.debug('final command: %s', self.cmd)
        elif self.opts.container:
            self.log.error(
                'container technology %s is currently not supported by %s',
                self.opts.container, self.parser.prog)
            sys.exit(66)

        return super(LbRun, self).runCmd()

    def main(self):
        try:
            try:
                if not self.opts.use_setupproject:
                    super(LbRun, self).main()
                else:
                    sys.exit(self.compatMain())
            except (NotFoundError, IOError, OSError) as err:
                if self.opts.path_to_project or self.opts.no_setupproject:
                    # SetupProject does not support --path-to-project
                    self.log.error('%s', err)
                    sys.exit(64)
                sys.exit(self.compatMain(err))
        except SystemExit:
            # pass through SystemExit exceptions (sys.exit)
            raise
        except:
            # force a special exit code for unhandled exceptions
            traceback.print_exc()
            raise SystemExit(65)


def main():
    # special handling of the option --profile
    if '--profile' in sys.argv:
        from LbEnv.ProjectEnv.profiling import run
        run('LbRun().main()')
    else:
        # special handling of the '#!' case (LBCORE-782)
        # - we must have at least one argument and the first one must be a file
        if len(sys.argv) >= 2 and os.path.isfile(sys.argv[1]):
            # - the second line of the file must start with '# args: '
            argline = ''
            with open(sys.argv[1]) as scriptfile:
                next(scriptfile)  # skip first line
                argline = scriptfile.next().strip()
            import re
            args = re.match(r'#\s*args\s*:\s*(\S+.*)', argline)
            if args:
                # FIXME: we should improve the argument splitting
                sys.argv = sys.argv[:1] + args.group(1).split() + sys.argv[1:]
        LbRun().main()
