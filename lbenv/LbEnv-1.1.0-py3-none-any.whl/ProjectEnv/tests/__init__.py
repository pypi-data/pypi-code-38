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


__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

import os
import sys
import shutil
from tempfile import mkdtemp
from nose import SkipTest


def setup():
    from os.path import join, dirname, pardir, abspath
    # FIXME compatibility py2-py3
    if sys.version_info >= (3, ):
        os.environ['CMAKE_PREFIX_PATH'] = abspath(
            join(
                dirname(__file__), pardir, pardir, pardir, pardir, pardir,
                'python', 'LbEnv', 'ProjectEnv', 'tests', 'data'))
    else:
        os.environ['CMAKE_PREFIX_PATH'] = join(dirname(__file__), 'data')


latest_gaudi = 'v27r1'


def test_platform_sorting():
    from LbEnv.ProjectEnv.lookup import platform_sort_key
    sorted_platforms = [
        'i686-slc5-gcc43-dbg',
        'i686-slc5-gcc43-opt',
        'slc4_amd64_gcc34',
        'slc4_ia32_gcc34',
        'x86_64-centos7-gcc49-dbg',
        'x86_64-centos7-gcc49-opt',
        'x86_64-centos7-gcc62-dbg',
        'x86_64-centos7-gcc62-do0',
        'x86_64-centos7-gcc62-opt',
        'x86_64-centos7-gcc7-dbg',
        'x86_64-centos7-gcc7-do0',
        'x86_64-centos7-gcc7-opt',
        'x86_64-slc5-gcc43-dbg',
        'x86_64-slc5-gcc43-opt',
        'x86_64-slc5-gcc46-dbg',
        'x86_64-slc5-gcc46-opt',
        'x86_64-slc6-gcc46-dbg',
        'x86_64-slc6-gcc46-opt',
        'x86_64-slc6-gcc48-dbg',
        'x86_64-slc6-gcc48-do0',
        'x86_64-slc6-gcc48-opt',
        'x86_64-slc6-gcc49-dbg',
        'x86_64-slc6-gcc49-do0',
        'x86_64-slc6-gcc49-opt',
        'x86_64-slc6-gcc62-dbg',
        'x86_64-slc6-gcc62-do0',
        'x86_64-slc6-gcc62-opt',
        'x86_64+avx2+fma-centos7-gcc62-dbg',
        'x86_64+avx2+fma-centos7-gcc62-opt',
    ]
    expected_order = [
        'x86_64-slc6-gcc48-do0',
        'x86_64-slc6-gcc49-do0',
        'x86_64-slc6-gcc62-do0',
        'x86_64-centos7-gcc62-do0',
        'x86_64-centos7-gcc7-do0',
        'i686-slc5-gcc43-dbg',
        'x86_64-slc5-gcc43-dbg',
        'x86_64-slc5-gcc46-dbg',
        'x86_64-slc6-gcc46-dbg',
        'x86_64-slc6-gcc48-dbg',
        'x86_64-slc6-gcc49-dbg',
        'x86_64-centos7-gcc49-dbg',
        'x86_64-slc6-gcc62-dbg',
        'x86_64-centos7-gcc62-dbg',
        'x86_64-centos7-gcc7-dbg',
        'x86_64+avx2+fma-centos7-gcc62-dbg',
        'slc4_ia32_gcc34',
        'i686-slc5-gcc43-opt',
        'slc4_amd64_gcc34',
        'x86_64-slc5-gcc43-opt',
        'x86_64-slc5-gcc46-opt',
        'x86_64-slc6-gcc46-opt',
        'x86_64-slc6-gcc48-opt',
        'x86_64-slc6-gcc49-opt',
        'x86_64-centos7-gcc49-opt',
        'x86_64-slc6-gcc62-opt',
        'x86_64-centos7-gcc62-opt',
        'x86_64-centos7-gcc7-opt',
        'x86_64+avx2+fma-centos7-gcc62-opt',
    ]
    sorted_platforms.sort(key=platform_sort_key)
    assert sorted_platforms == expected_order


def prepare_tree(base, tree):
    from os import makedirs
    from os.path import dirname, join, exists
    if hasattr(tree, 'items'):
        tree = list(tree.items())
    for k, v in tree:
        k = join(base, k)
        if v:
            d = dirname(k)
            if not exists(d):
                makedirs(d)
            f = open(k, 'w')
            f.write(v)
            f.close()
        else:
            if not exists(k):
                makedirs(k)


class TempDir(object):
    def __init__(self, tree=None):
        self.tmpdir = None
        self.tree = tree

    def __enter__(self):
        self.tmpdir = mkdtemp()
        if self.tree:
            prepare_tree(self.tmpdir, self.tree)
        return self.tmpdir

    def __exit__(self, type_, value, traceback):
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)


def test_import():
    import LbEnv.ProjectEnv
    assert LbEnv.ProjectEnv.path


def test_version():
    from LbEnv.ProjectEnv.version import expandVersionAlias, isValidVersion

    assert expandVersionAlias('Gaudi', 'latest',
                              'x86_64-slc6-gcc46-opt') == 'v25r0'

    assert isValidVersion('Gaudi', 'latest')
    assert isValidVersion('Gaudi', 'HEAD')
    assert isValidVersion('Gaudi', latest_gaudi)
    assert isValidVersion('LHCb', 'v32r5p1')
    assert isValidVersion('LHCb', 'v32r4g1')
    assert isValidVersion('LCGCMT', '64d')
    assert not isValidVersion('Gaudi', 'a random string')


# FIXME this is an integration test...
def _test_compatibility():
    from LbEnv.ProjectEnv.compatibility import getOldEnvironment
    env_bk = dict(os.environ)

    try:
        os.environ['CMTCONFIG'] = 'x86_64-slc6-gcc49-opt'
        if 'BINARY_TAG' in os.environ:
            del os.environ['BINARY_TAG']
        env = getOldEnvironment(['Gaudi', latest_gaudi])
        assert 'GAUDISYSROOT' in env
        assert latest_gaudi in env['GAUDISYSROOT']
    finally:
        os.environ.clear()
        os.environ.update(env_bk)

    try:
        os.environ['BINARY_TAG'] = 'x86_64-slc6-gcc49-opt'
        os.environ['CMTCONFIG'] = 'dummy'
        env = getOldEnvironment(['Gaudi', latest_gaudi])
        assert 'GAUDISYSROOT' in env
        assert latest_gaudi in env['GAUDISYSROOT']
    finally:
        os.environ.clear()
        os.environ.update(env_bk)

    try:
        env = getOldEnvironment(['NotAProject', 'v1r0'])
        assert False, 'exception expected'
    except SystemExit as x:
        assert x.code == 1
    finally:
        os.environ.clear()
        os.environ.update(env_bk)


def parse_args(func, args):
    from optparse import OptionParser
    return func(OptionParser(prog='dummy_program')).parse_args(args)


def test_options_addOutputLevel():
    from LbEnv.ProjectEnv.options import addOutputLevel
    import logging

    opts, _ = parse_args(addOutputLevel, [])
    assert opts.log_level == logging.WARNING

    opts, _ = parse_args(addOutputLevel, ['--debug'])
    assert opts.log_level == logging.DEBUG

    opts, _ = parse_args(addOutputLevel, ['--verbose'])
    assert opts.log_level == logging.INFO

    opts, _ = parse_args(addOutputLevel, ['--quiet'])
    assert opts.log_level == logging.WARNING


def test_options_addPlatform():
    from LbEnv.ProjectEnv.options import addPlatform, checkPlatform

    def parse_args(args):
        from optparse import OptionParser
        parser = addPlatform(OptionParser(prog='dummy_program'))
        opts, args = parser.parse_args(args)
        opts.platform = checkPlatform(parser, opts.platform)
        return opts, args

    # set platform, short optino
    opts, _ = parse_args(['-c', 'platform1'])
    assert opts.platform == 'platform1'

    # set platform, long optino
    opts, _ = parse_args(['--platform', 'platform2'])
    assert opts.platform == 'platform2'

    # take CMTCONFIG
    if 'CMTCONFIG' not in os.environ:
        os.environ['CMTCONFIG'] = 'default'
    if 'BINARY_TAG' in os.environ:
        del os.environ['BINARY_TAG']
    opts, _ = parse_args([])
    assert opts.platform == os.environ['CMTCONFIG']

    # take BINARY_TAG
    if 'BINARY_TAG' not in os.environ:
        os.environ['BINARY_TAG'] = 'default'
    if 'CMTCONFIG' in os.environ:
        del os.environ['CMTCONFIG']
    opts, _ = parse_args([])
    assert opts.platform == os.environ['BINARY_TAG']

    # allow equal BINARY_TAG and CMTCONFIG
    os.environ['BINARY_TAG'] = os.environ['CMTCONFIG'] = 'default'
    opts, _ = parse_args([])
    assert opts.platform == os.environ['BINARY_TAG']

    # fail for inconsistent
    os.environ['BINARY_TAG'] = 'another'
    try:
        opts, _ = parse_args([])
        assert False, 'failure expected'
    except SystemExit:
        pass
    del os.environ['CMTCONFIG']
    del os.environ['BINARY_TAG']

    # pretend we are on an unsupported platform
    import LbEnv
    bk = LbEnv.defaultPlatform

    def force_known():
        return 'known'

    def force_unknown():
        raise RuntimeError('unknown platform')

    try:
        # no environment, something should be selected
        LbEnv.defaultPlatform = force_known
        opts, _ = parse_args([])
        assert opts.platform == 'known'

        LbEnv.defaultPlatform = force_unknown
        opts, _ = parse_args([])
        assert False, 'exception expected'
    except SystemExit:
        pass
    finally:
        LbEnv.defaultPlatform = bk


def test_options_addSearchPath():
    from LbEnv.ProjectEnv.options import addSearchPath
    from LbEnv.ProjectEnv.lookup import InvalidNightlySlotError

    if 'LHCBDEV' not in os.environ:
        os.environ['LHCBDEV'] = '/afs/cern.ch/lhcb/software/DEV'
    opts, _ = parse_args(addSearchPath, ['--dev'])
    assert os.environ['LHCBDEV'] in list(map(str, opts.dev_dirs))

    del os.environ['LHCBDEV']
    try:
        opts, _ = parse_args(addSearchPath, ['--dev'])
        assert False, 'exception expected'
    except SystemExit:
        pass

    opts, _ = parse_args(addSearchPath, ['--dev-dir', '/some/path'])
    assert '/some/path' in list(map(str, opts.dev_dirs))

    if 'User_release_area' in os.environ:
        del os.environ['User_release_area']
    opts, _ = parse_args(addSearchPath, [])
    assert opts.user_area is None

    os.environ['User_release_area'] = '/home/myself/cmtuser'
    opts, _ = parse_args(addSearchPath, [])
    assert opts.user_area == os.environ['User_release_area']
    assert not opts.no_user_area

    opts, _ = parse_args(addSearchPath, ['--user-area', '/tmp/myself'])
    assert opts.user_area == '/tmp/myself'

    opts, _ = parse_args(addSearchPath, ['--no-user-area'])
    assert opts.no_user_area

    try:
        opts, _ = parse_args(addSearchPath, ['--nightly'])
        assert False, 'exception expected'
    except SystemExit:
        pass

    import datetime
    days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    weekday = datetime.date.today().weekday()
    today = 'Today'  # days[weekday]
    yesterday = days[(weekday - 1) % 7]

    with TempDir({
            'lhcb-nightly-slot/%s' % today: None,
            'lhcb-nightly-slot/%s' % yesterday: None
    }) as tmp:
        os.environ['LHCBNIGHTLIES'] = tmp
        opts, _ = parse_args(addSearchPath, ['--nightly', 'lhcb-nightly-slot'])
        assert os.path.join(tmp, 'lhcb-nightly-slot', today) in \
            list(map(str, opts.dev_dirs))
        assert opts.nightly == ('lhcb-nightly-slot', today, tmp), opts.nightly
        opts, _ = parse_args(addSearchPath,
                             ['--nightly', 'lhcb-nightly-slot', yesterday])
        assert os.path.join(tmp, 'lhcb-nightly-slot', yesterday) in \
            list(map(str, opts.dev_dirs))
        assert opts.nightly == ('lhcb-nightly-slot', yesterday,
                                tmp), opts.nightly

        opts, _ = parse_args(addSearchPath, ['--nightly', 'dummy'])
        assert isinstance(opts.nightly, InvalidNightlySlotError)

        opts, _ = parse_args(
            addSearchPath,
            ['--nightly', 'lhcb-nightly-slot', days[(weekday + 1) % 7]])
        assert isinstance(opts.nightly, InvalidNightlySlotError)

    with TempDir({
            'lhcb-nightly-slot/%s/confSummary.py' % today:
            '''cmtProjectPathList = ['/extra/dir']\n'''
    }) as tmp:
        os.environ['LHCBNIGHTLIES'] = tmp
        opts, _ = parse_args(addSearchPath, ['--nightly', 'lhcb-nightly-slot'])
        assert '/extra/dir' in list(map(str, opts.dev_dirs))

    with TempDir({
            'lhcb-nightly-slot/%s/configuration.xml' % today:
            '''<configuration><slot name="lhcb-nightly-slot">
<cmtprojectpath><path value="/extra/xml/dir"/></cmtprojectpath>
</slot></configuration>'''
    }) as tmp:
        os.environ['LHCBNIGHTLIES'] = tmp
        opts, _ = parse_args(addSearchPath, ['--nightly', 'lhcb-nightly-slot'])
        assert '/extra/xml/dir' in list(map(str, opts.dev_dirs))


def test_lookup():
    from LbEnv.ProjectEnv import path
    bk_path = list(path)

    from LbEnv.ProjectEnv.lookup import (
        findProject, MissingProjectError, findDataPackage,
        MissingDataPackageError, getEnvXmlPath, MissingManifestError)

    if 'BINARY_TAG' in os.environ:
        del os.environ['BINARY_TAG']
    os.environ['CMTCONFIG'] = 'x86_64-slc6-gcc46-opt'

    data = {
        'MYPROJECT/MYPROJECT_v1r0/InstallArea/x86_64-slc6-gcc46-opt/manifest.xml':
        '<?xml version="1.0" encoding="UTF-8"?><manifest></manifest>',
        'DERIVEDPROJECT/DERIVEDPROJECT_v1r3/InstallArea/x86_64-slc6-gcc46-opt/manifest.xml':
        '<?xml version="1.0" encoding="UTF-8"?><manifest>'
        '<used_projects>'
        '<project name="MyProject" version="v1r0" />'
        '</used_projects>'
        '<used_data_pkgs>'
        '<package name="MyPackage" version="*"/>'
        '</used_data_pkgs>'
        '</manifest>',
        'OLDPROJECT/OLDPROJECT_v9r0/InstallArea/x86_64-slc6-gcc46-opt':
        None,
        'DBASE/MyPackage/v2r0':
        None,
        'DBASE/MyPackage/v2r1':
        None,
        'DBASE/MyPackage/v10r0':
        None,
        'User/MyProjectDev_v1r0/InstallArea/x86_64-slc6-gcc46-opt/manifest.xml':
        '<?xml version="1.0" encoding="UTF-8"?><manifest>'
        '<used_projects><project name="MyProject" version="v1r0" /></used_projects>'
        '</manifest>',
        'User/MyAnalysis/InstallArea/x86_64-slc6-gcc46-opt/manifest.xml':
        '<?xml version="1.0" encoding="UTF-8"?><manifest>'
        '<used_projects><project name="MyProject" version="v1r0" /></used_projects>'
        '</manifest>'
    }
    with TempDir(data) as tmp:
        path[:] = [tmp] + bk_path

        proj = findProject('MyProject', 'v1r0', os.environ['CMTCONFIG'])
        assert proj == os.path.join(
            tmp, 'MYPROJECT/MYPROJECT_v1r0/InstallArea/x86_64-slc6-gcc46-opt')

        try:
            findProject('AnotherProject', 'v1r0', os.environ['CMTCONFIG'])
            assert False, 'exception expected'
        except MissingProjectError as x:
            assert str(x)

        # test with user area
        path.insert(0, os.path.join(tmp, 'User'))
        proj = findProject('MyProjectDev', 'v1r0', os.environ['CMTCONFIG'])
        assert proj == os.path.join(
            tmp, 'User/MyProjectDev_v1r0/InstallArea/x86_64-slc6-gcc46-opt')

        proj = findProject(
            'MyAnalysis',
            'latest',
            os.environ['CMTCONFIG'],
            allow_empty_version=True)
        assert proj == os.path.join(
            tmp, 'User/MyAnalysis/InstallArea/x86_64-slc6-gcc46-opt')

        try:
            findProject('MyAnalysis', 'v1r0', os.environ['CMTCONFIG'])
            assert False, 'exception expected'
        except MissingProjectError as x:
            assert str(x)

        pkg = findDataPackage('MyPackage', 'v2r0')
        assert pkg == os.path.join(tmp, 'DBASE/MyPackage/v2r0')

        pkg = findDataPackage('MyPackage', 'v2r*')
        assert pkg == os.path.join(tmp, 'DBASE/MyPackage/v2r1')

        pkg = findDataPackage('MyPackage', 'v*')
        assert pkg == os.path.join(tmp, 'DBASE/MyPackage/v10r0')

        pkg = findDataPackage('MyPackage', '*')
        assert pkg == os.path.join(tmp, 'DBASE/MyPackage/v10r0')

        try:
            findDataPackage('NoPackage', '*')
            assert False, 'exception expected'
        except MissingDataPackageError as x:
            assert str(x)

        xml_path = getEnvXmlPath('DerivedProject', 'v1r3',
                                 os.environ['CMTCONFIG'])
        assert os.path.join(
            tmp, 'MYPROJECT/MYPROJECT_v1r0/InstallArea/x86_64-slc6-gcc46-opt'
        ) in xml_path
        assert os.path.join(
            tmp,
            'DERIVEDPROJECT/DERIVEDPROJECT_v1r3/InstallArea/x86_64-slc6-gcc46-opt'
        ) in xml_path

        try:
            xml_path = getEnvXmlPath('OldProject', 'v9r0',
                                     os.environ['CMTCONFIG'])
            assert False, 'exception expected'
        except MissingManifestError as x:
            assert str(x)

    path[:] = bk_path


def test_listVersions():
    from LbEnv.ProjectEnv import path
    bk_path = list(path)
    from os.path import join

    from LbEnv.ProjectEnv.lookup import listVersions

    if 'BINARY_TAG' in os.environ:
        del os.environ['BINARY_TAG']
    os.environ['CMTCONFIG'] = 'x86_64-slc6-gcc48-opt'

    data = {
        'MYPROJECT/MYPROJECT_v1r0/InstallArea/x86_64-slc6-gcc48-opt/manifest.xml':
        '<?xml version="1.0" encoding="UTF-8"?><manifest></manifest>',
        'MYPROJECT/MYPROJECT_v1r2/InstallArea/x86_64-slc6-gcc48-opt/manifest.xml':
        '<?xml version="1.0" encoding="UTF-8"?><manifest></manifest>'
    }
    with TempDir(data) as tmp:
        path[:] = ['/no/where', tmp, tmp]

        expected = [('v1r2', join(tmp, 'MYPROJECT', 'MYPROJECT_v1r2')),
                    ('v1r0', join(tmp, 'MYPROJECT', 'MYPROJECT_v1r0'))]
        observed = list(listVersions('MyProject', os.environ['CMTCONFIG']))
        print('expected', expected)
        print('observed', observed)
        assert expected == observed

    path[:] = bk_path


def _test_profiling():
    from LbEnv.ProjectEnv import profiling

    from io import StringIO

    try:
        sys.stderr = StringIO()
        profiling.run('sys.exit()')
        assert False, 'exception expected'
    except SystemExit:
        print(sys.stderr.getvalue())
    finally:
        sys.stderr = sys.__stderr__

    def dummy():
        raise ImportError()

    import cProfile
    bk1 = cProfile.Profile
    cProfile.Profile = dummy

    try:
        sys.stderr = StringIO()
        profiling.run('sys.exit()')
        assert False, 'exception expected'
    except SystemExit:
        print(sys.stderr.getvalue())
    finally:
        sys.stderr = sys.__stderr__

    import profile
    bk2 = profile.Profile
    profile.Profile = dummy
    try:
        sys.stderr = StringIO()
        profiling.run('sys.exit()')
        assert False, 'exception expected'
    except SystemExit:
        print(sys.stderr.getvalue())
    finally:
        sys.stderr = sys.__stderr__

    cProfile.Profile = bk1
    profile.Profile = bk2


def test_LBCORE_522():
    '''LBCORE-522: lb-run does not expand some variables when falling back on SetupProject
    https://its.cern.ch/jira/browse/LBCORE-522'''
    from LbEnv.ProjectEnv.compatibility import expandAllVars

    original = {'MYDATA': '${DATA}/subdir', 'DATA': '/main/path'}
    expected = {'MYDATA': '/main/path/subdir', 'DATA': '/main/path'}
    assert expandAllVars(original) == expected

    try:
        expandAllVars({'A': '${B}/x', 'B': '${A}/y'})
        assert False, 'exception expected'
    except ValueError:
        pass


def test_SearchPath():
    from LbEnv.ProjectEnv import (SearchPath, SearchPathEntry,
                                  EnvSearchPathEntry)

    if 'DUMMY_ENV_VAR' in os.environ:
        del os.environ['DUMMY_ENV_VAR']
    try:
        EnvSearchPathEntry('DUMMY_ENV_VAR')
        assert False, 'exception expected'
    except ValueError:
        pass

    assert os.environ['PATH'] == str(EnvSearchPathEntry('PATH'))

    path = SearchPath(
        [SearchPathEntry(p) for p in os.environ['PATH'].split(os.pathsep)])
    assert os.environ['PATH'] == str(path)
    assert os.environ['PATH'].split(os.pathsep) == list(path)

    path2 = SearchPath([EnvSearchPathEntry('PATH')])
    assert os.environ['PATH'].split(os.pathsep) == list(path2)

    path3 = SearchPath([SearchPathEntry('b')])
    path3.insert(0, 'a')
    path3.append('c')
    assert os.pathsep.join('abc') == str(path3)

    path4 = path3 + list('123')
    assert os.pathsep.join('abc123') == str(path4)

    path5 = path3 + SearchPath('123')
    assert os.pathsep.join('abc123') == str(path5)

    assert not SearchPath([])
    assert SearchPath(['a'])


def test_incompatibility_report():
    from LbPlatformUtils.inspect import os_id
    if not os_id().endswith('centos7'):
        raise SkipTest()  # only centos7 is incompatible with slc5
    from subprocess import check_output, CalledProcessError, STDOUT
    try:
        check_output([
            'lb-run', '--platform', 'x86_64-slc5-gcc43-opt', 'LHCb/v31r6p1',
            'true'
        ],
                     stderr=STDOUT)
        assert False, 'script failure expected'
    except CalledProcessError as err:
        print(err.output)
        import re
        assert re.search(r'dirac_platform: [^-]+-{}'.format(os_id()),
                         err.output)
