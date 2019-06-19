# -*- coding:utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2013-2018 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import os
import sys
import signal
import logging
import functools
import codecs
import six
import compileall
from datetime import datetime

core_logger = logging.getLogger('core')
core_perf_logger = logging.getLogger('core.perf')

WINDOWS = 'win32'
SY_APPLICATION_DIR = 'SY_APPLICATION_DIR'
SY_PYTHON_EXECUTABLE = 'SY_PYTHON_EXECUTABLE'
SY_PYTHON_SUPPORT = 'SY_PYTHON_SUPPORT'
SY_LAUNCH = 'SY_LAUNCH'
PATH = 'PATH'
PYTHONNOUSERSITE = 'PYTHONNOUSERSITE'
PYTHONHOME = 'PYTHONHOME'
PYTHONPATH = 'PYTHONPATH'

sy_launch = os.path.abspath(__file__)
sy_application_dir = os.path.dirname(sy_launch)
sy_python_executable = sys.executable
sy_python_support = os.path.join(sy_application_dir, 'Python')

# TODO: Fix relative imports (import Sympathy.Gui instead of import Gui)
sys.path.append(sy_application_dir)


startup_file = os.path.join(
    sy_application_dir, 'Python', 'sympathy', 'utils',
    'python_startup.py')


os.environ.update({
    SY_APPLICATION_DIR: sy_application_dir,
    SY_PYTHON_EXECUTABLE: sy_python_executable,
    SY_PYTHON_SUPPORT: sy_python_support,
    SY_LAUNCH: sy_launch
})


def _remove_help_args(args):
    """Filter help arguments from args to avoid early exit."""
    return [arg for arg in args if arg not in ['-h', '--help']]


def perflog(msg, mark, dt=None):
    if dt is None:
        dt = datetime.now()
    assert(mark in '{}')
    core_perf_logger.debug('{} {} {}'.format(dt.isoformat(), msg, mark))


def _pydev_win32process_monkey_patch():
    """
    Enable debugging under PyCharm.
    It does not normally detect calls to win32process.CreateProcess
    which is used by twisted to launch processes on Windows.

    Replaces win32process.CreateProcess with create_process, a wrapper
    function which notifies PyCharm.

    The approach is fragile and has only been tested with PyCharm 2016.3.
    """
    pdm = sys.modules.get('_pydev_bundle.pydev_monkey')

    if pdm:
        import win32process
        win32process.CreateProcessOrg = win32process.CreateProcess

        def create_process(command, process_args, *args):
            try:
                process_args = pdm.patch_arg_str_win(process_args)
            except:
                pass

            res = win32process.CreateProcessOrg(
                command, process_args, *args)
            try:
                pdm.send_process_created_message()
            except:
                pass
            return res

        win32process.CreateProcess = create_process


def setup_environment(environ):
    """Setup base environment required for importing sympathy."""
    sys.path.append(sy_python_support)
    from sympathy.platform import version_support as vs
    environ = vs.environ_wrapper(environ)

    if sys.platform == WINDOWS:
        python_home = os.path.dirname(sy_python_executable)
        environ[PYTHONNOUSERSITE] = 'x'
        environ[PYTHONHOME] = python_home
        environ[PYTHONPATH] = python_home
        paths = [['Lib', 'site-packages', 'pywin32_system32'],
                 ['Lib', 'site-packages', 'numpy', 'core']]
        fq_paths = [vs.py_file(os.path.join(python_home, *path))
                    for path in paths]
        path = environ.get(PATH)
        if path:
            environ[PATH] = os.pathsep.join([path] + fq_paths)
        else:
            environ[PATH] = os.pathsep.join(fq_paths)
        _pydev_win32process_monkey_patch()


def run_sy():
    """Run sy."""
    # from Gui import sy
    # sy.run_binary('sy')
    return run_app('sy')


def run_syg():
    """Run syg."""
    # from Gui import sy
    # sy.run_binary('syg')
    try:
        # Don't allow keyboard interrupt in the GUI application.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except AttributeError:
        pass
    return run_app('syg')


def _install_common():
    from Gui import version
    appname = version.application_name()
    syver = '{}.{}'.format(version.major, version.minor)
    sydata_ext = '.sydata'
    sydata_cls = 'Sympathy.Data'
    syx_ext = '.syx'
    syx_cls = 'Sympathy.Workflow'
    uinstkey = '{}-{}'.format(appname, syver)
    start_menu_root = r'Programs\{}\{}'.format(appname, syver)
    return (appname, syver, sydata_ext, sydata_cls, syx_ext, syx_cls, uinstkey,
            start_menu_root)


def run_install():

    def generate_ply():
        """
        Trigger generation of lexer and parser files.
        """
        print('Generating files.')
        cd = six.moves.getcwd()
        try:
            # Build type parser and lexer.
            os.chdir(os.path.join(
                sy_application_dir, 'Python', 'sympathy', 'types'))
            import sympathy.types.types  # NOQA
            import sympathy.types.types_lexer  # NOQA
            import sympathy.types.types_parser  # NOQA
        finally:
            os.chdir(cd)

    def compile_all():
        """
        Compile pyc-files for Sympathy.
        """
        dir = os.path.abspath(os.path.join(sy_application_dir, os.pardir))
        print('Compiling files in {}.'.format(dir))
        compileall.compile_dir(dir, quiet=True, force=True)

    generate_ply()
    compile_all()

    if sys.platform != WINDOWS:
        return

    from sympathy.platform import os_support as oss
    from sympathy.platform import version_support as vs
    from sympathy.utils import prim
    from Gui import version
    (appname, syver, sydata_ext, sydata_cls, syx_ext, syx_cls, uinstkey,
     start_menu_root) = _install_common()

    spyderico = os.path.join(
        os.path.dirname(sys.executable), 'Scripts', 'spyder.ico')

    launch = vs.fs_decode(sy_launch)
    py = sys.executable.replace('pythonw', 'python')
    pyw = py.replace('python', 'pythonw')
    uinstcli = '"{}" "{}" uninstall'.format(pyw, launch)

    print('Register file associations (syx, sydata).')

    oss.unregister_ext(sydata_ext, sydata_cls)
    oss.register_ext(sydata_ext, sydata_cls, 'Sympathy datafile',
                     '"{}" "{}" viewer "%1"'.format(pyw, launch))
    oss.unregister_ext(syx_ext, syx_cls)
    oss.register_ext(syx_ext, syx_cls, 'Sympathy workflow',
                     '"{}" "{}" syg "%1"'.format(pyw, launch),
                     prim.get_icon_path('syx.ico'))

    print('Create start menu links.')

    oss.delete_start_menu_shortcuts(start_menu_root)
    oss.create_start_menu_shortcuts(
        start_menu_root,
        [
            ('{}.lnk'.format(appname),
             pyw,
             '"{}" syg'.format(launch),
             None,
             prim.get_icon_path('application.ico')),

            ('IPython.lnk'.format(syver),
             py,
             '"{}" ipython'.format(launch),
             None,
             prim.get_icon_path('application.ico')),

            ('Spyder.lnk'.format(syver),
             pyw,
             '"{}" spyder'.format(launch),
             None,
             spyderico),

            ('Viewer.lnk'.format(syver),
             pyw,
             '"{}" viewer'.format(launch),
             None,
             prim.get_icon_path('application.ico'))])

    print('Register application in registry.')

    oss.unregister_app(uinstkey)
    oss.register_app(uinstkey, appname, syver, uinstcli, uinstcli,
                     version.application_copyright())


def run_uninstall():

    if sys.platform != WINDOWS:
        return

    from sympathy.platform import os_support as oss

    (appname, syver, sydata_ext, sydata_cls, syx_ext, syx_cls, uinstkey,
     start_menu_root) = _install_common()

    print('Unregister file associations (syx, sydata).')

    oss.unregister_ext(sydata_ext, sydata_cls)
    oss.unregister_ext(syx_ext, syx_cls)

    print('Remove start menu links.')

    oss.delete_start_menu_shortcuts(start_menu_root)
    oss.unregister_app(uinstkey)

    print('Unregister application in registry.')


def run_app(app):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--benchmark', action='store', type=str, default=None)
    parser.add_argument(
        'filename', action='store', nargs='?', default=None,
        help='File containing workflow.')

    (parsed, _) = parser.parse_known_args(_remove_help_args(sys.argv))

    if parsed.benchmark:
        # Capture output.
        from sympathy.utils import benchmark
        from tempfile import NamedTemporaryFile as ntf

        with ntf() as out, ntf() as err:

            stdout = sys.stdout
            stderr = sys.stderr

            sys.stdout = out
            sys.stderr = err
            result = 1

            try:
                result = run_sympathy(app)

                sys.stdout = stdout
                sys.stderr = stderr

                out.seek(0)
                out_data = out.read()
                err.seek(0)
                err_data = err.read()

                sys.stdout.write(out_data)
                sys.stderr.write(err_data)

                out.write(err_data)

                with open(parsed.benchmark, 'w') as f:
                    out.seek(0)

                    if app == 'sy':
                        if parsed.filename:
                            name = u'Sympathy CLI {}'.format(
                                os.path.basename(parsed.filename))
                        else:
                            name = 'Sympathy CLI'
                    elif app == 'syg':
                        name = 'Sympathy GUI'
                    else:
                        assert(False)

                    bench = benchmark.bench_log(
                        name, out)
                    f.write(bench.renderhtml())
            finally:
                sys.stdout = stdout
                sys.stderr = stderr
                sys.exit(result)
    else:
        sys.exit(run_sympathy(app))


def run_viewer():
    """Run viewer."""
    from Gui import sy
    from Gui import util
    from sympathy.platform import viewer

    # The viewer code is in platform and can therefore not import Gui.util.
    icon_path = util.icon_path('application.png')
    sy.run_function(functools.partial(viewer.run, icon_path))


def worker_environ():
    # Set execution environment.
    # SystemRoot is required for correct behavior on Windows.
    # LD_LIBRARY_PATH is required for correct behavior on Unix.
    # environ['PYTHONPATH'] = os.environ['SY_PYTHON_SUPPORT']
    environ = dict()
    for variable in ['LD_LIBRARY_PATH',
                     'DYLD_LIBRARY_PATH',
                     'PATH',
                     'LANG',
                     'SystemRoot',
                     'TEMP',
                     'TMP',
                     'TMPDIR']:
        if variable in os.environ:
            environ[variable] = os.environ[variable]

    environ['PYTHONPATH'] = os.path.pathsep.join(
        [sy_application_dir, sy_python_support])
    return environ


def run_sympathy(app):
    beg = datetime.now()
    parser = argparse.ArgumentParser()
    from sympathy.platform import version_support as vs

    environ = vs.environ_wrapper()
    environ[u'PYTHONPATH'] = os.path.pathsep.join(
        [environ.get(u'PYTHONPATH', ''),
         sy_application_dir, sy_python_support])

    beg_imports = datetime.now()
    from Gui import sy, settings, task_manager2
    from Gui import execore
    end_imports = datetime.now()

    parser.add_argument(
        '-L', '--loglevel', action='store', type=int, default=0)

    parser.add_argument(
        '-N', '--node-loglevel', '--node_loglevel',
        action='store', type=int, default=4)

    parser.add_argument(
        '--num-worker-processes', '--num_worker_processes',
        action='store', type=int, default=0)

    parser.add_argument(
        '--nocapture', action='store_true', default=False)

    parser.add_argument(
        'filename', action='store', nargs='?', default=None)

    args, unknown = parser.parse_known_args(
        _remove_help_args(sys.argv[1:]))
    sy.setup_loglevel(args.loglevel, args.node_loglevel)

    perflog('run_sympathy', '{', beg)
    perflog('run_sympathy:imports', '{', beg_imports)
    perflog('run_sympathy:imports', '}', end_imports)

    core_logger.info('Sympathy for Data starting')

    core_logger.info('Launch Task Manager')
    if ('--num-worker-processes' in sys.argv or
            '--num_worker_processes' in sys.argv):
        worker_processes = args.num_worker_processes
    else:
        worker_processes = settings.instance()['max_nbr_of_threads']

    nworkers = worker_processes or execore.THREAD_COUNT
    worker_env = worker_environ()
    master_env = os.environ

    session_folder = vs.str_(settings.instance()['session_folder'],
                             vs.fs_encoding)

    master_args = ([sys.executable, '-u',
                    sy_launch.replace('.pyc', '.py'),
                    'launch',
                    session_folder,
                    app] + sys.argv[1:])

    worker_args = 'Gui.task_worker_subprocess:worker'

    return task_manager2.start(
        worker_args=worker_args,
        master_args=master_args,
        nworkers=nworkers,
        worker_environ=worker_env,
        master_environ=master_env,
        nocapture=args.nocapture,
        loglevel=args.loglevel,
        node_loglevel=args.node_loglevel,
        pipe=args.filename == '-' and app == 'sy')


def run_spyder():
    """Run spyder."""
    def execute():
        from sympathy.platform import os_support
        if os_support.has_spyder():
            os_support.run_spyder()
        else:
            print('spyder is not installed')
    from Gui import sy
    sy.run_function(execute)


def run_benchmark_suite():
    from Gui.task_worker import Paths
    from Gui import util, log

    util.create_install_folder()
    getpaths = Paths(sy_application_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename', action='store',
        help='Filename of HTML report to write.')
    parsed, _ = parser.parse_known_args(sys.argv[1:])

    from sympathy.utils import benchmark
    log.setup_loglevel(1, 1)
    bench = benchmark.bench([
        'Test/WorkflowsAuto/locked_subflows/slow.syx',
        'Test/WorkflowsAuto/locked_subflows/slow_locked.syx'],
        os.path.abspath(__file__),
        getpaths)

    with open(parsed.filename, 'w') as f:
        f.write(bench.renderhtml())


def run_ipython():
    """Run ipython."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            from IPython.frontend.terminal.ipapp import launch_new_instance
            os.environ['PYTHONSTARTUP'] = startup_file
            return launch_new_instance()
        except ImportError:
            print('ipython is not installed')
            return 1


def run_nosetests():
    """Run nosetests."""
    from Gui import sy
    from nose import main as nosemain
    from Gui import interactive
    with interactive.load_library().context():
        sy.run_function(nosemain)


def run_tests():
    """Run nosetests on platform and libraries."""
    from nose import main as nosemain
    from Gui import sy
    from Gui import interactive
    from Gui import settings
    lib_paths = interactive.available_libraries()
    lib_test_paths = [os.path.join(lib_path, 'Test', 'Unit')
                      for lib_path in lib_paths]
    test_paths = [path for path in lib_test_paths if os.path.isdir(path)]
    test_paths.append(os.path.join(sy_application_dir, 'Test', 'Unit'))
    if len(settings.instance()['MATLAB/matlab_path']):
        test_paths.append(os.path.join(sy_application_dir, 'Matlab', 'Test'))

    with interactive.load_library().context():
        sy.run_function(functools.partial(nosemain, defaultTest=test_paths))


def run_pylint():
    """Run pylint."""
    args = sys.argv[:]
    sys.argv = sys.argv[:1]

    def execute():
        sys.argv = args
        try:
            from pylint import run_pylint
            run_pylint()
        except:
            os.environ[PYTHONPATH] = os.sep.join(
                [os.environ[PYTHONPATH], args[-1]])
            from pylint import lint
            lint.Run(sys.argv[1:])
    from Gui import sy
    sy.run_function(execute)


def run_pyflakes():
    """Run pyflakes."""
    from pyflakes.scripts.pyflakes import main as pyflakesmain

    def execute():
        try:
            pyflakesmain(sys.argv[-1:])
        except Exception:
            pyflakesmain()
    from Gui import sy
    sy.run_function(execute)


def run_clear():
    from Gui import sy
    import Gui.application

    def clear():
        if not (parsed.sessions or parsed.caches):
            parser.print_help()
        else:
            Gui.application.clear(session=parsed.sessions,
                                  storage=parsed.caches)
    parser = argparse.ArgumentParser(
        prog='{} clear'.format(sys.argv[0]))

    parser.add_argument(
        '--caches',
        action='store_true', default=None,
        help='Clear caches for Sympathy.')

    parser.add_argument(
        '--sessions',
        action='store_true', default=None,
        help='Clear sessions for Sympathy.')

    parsed = parser.parse_args(sys.argv[1:])
    sy.run_function(clear)


def run_launch():
    """
    Extra step of executing python process through a file to get __file__ set
    Correctly. When launch via a string trouble arises when the __file__
    attribute is used.

    __file__ becomes relative in imported modules but it is not obvious to what
    if the working directory changes.

    Otherwise, this would have been done by run_sympathy directly.
    """
    perflog('run_launch', '{')
    perflog('run_launch:imports', '{')
    from Gui import sy, settings
    perflog('run_launch:imports', '}')
    from sympathy.platform import version_support as vs

    iniparser = argparse.ArgumentParser()
    iniparser.add_argument(
        '-I', '--inifile', action='store', default=None)

    argv = vs.SYS.argv
    parsed, _ = iniparser.parse_known_args(_remove_help_args(argv))
    settings.create_settings(parsed.inifile)
    session_folder = argv[1]
    settings.instance()['session_folder'] = session_folder

    app = argv[2]
    argv[:] = argv[:1] + argv[3:]
    sy.run_binary(app)
    perflog('run_launch', '}')


def _stdout_writer(writer, check_enc=True):
    if six.PY2 and sys.stdout and (check_enc and sys.stdout.encoding is None):
        sys.stdout = writer(sys.stdout)


def _stderr_writer(writer, check_enc=True):
    if six.PY2 and sys.stderr and (check_enc and sys.stderr.encoding is None):
        sys.stderr = writer(sys.stderr)


def run(app=None):
    """Run requested app."""
    parser = argparse.ArgumentParser()
    choices = ['sy',
               'cli',
               'syg',
               'gui',
               'viewer',
               'spyder',
               'ipython',
               'nosetests',
               'pylint',
               'pyflakes',
               'launch',
               'client',
               'tests',
               'benchmark',
               'install',
               'uninstall',
               'clear']

    parser.add_argument('application', choices=choices)
    writer = codecs.getwriter(sys.getfilesystemencoding())

    # Wrapping of stdout/stderr.
    # Needs to happen early, before anything is written. Importing modules can
    # trigger output.
    stdout = None
    stderr = None

    if app is None:
        parser.print_help()
        return

    parsed = parser.parse_args([app])

    if parsed.application == 'launch':
        _stdout_writer(writer, False)
        _stderr_writer(writer, False)
    else:
        if sys.stdout is None or sys.stdout.fileno() < 0:
            stdout = open(os.devnull, 'a')
            sys.stdout = stdout

        if sys.stderr is None or sys.stderr.fileno() < 0:
            stderr = open(os.devnull, 'a')
            sys.stderr = stderr

        _stdout_writer(writer)
        _stderr_writer(writer)

    setup_environment(os.environ)
    coverage_tester = None

    if '--coverage' in sys.argv:
        from sympathy.utils import coverage
        index = sys.argv.index('--coverage')
        coverage.prepare_coverage(sys.argv[index + 1:])
        coverage_tester = coverage.CoverageTester()
        coverage_tester.start_coverage()
        sys.argv = sys.argv[:index]

    if (parsed.application in ['sy', 'cli', 'syg', 'gui'] and
            sys.platform == WINDOWS):
        try:
            import colorama
        except ImportError:
            pass
        else:
            if sys.stdout is not None and sys.stdout.fileno() >= 0:
                sys.stdout = colorama.AnsiToWin32(sys.stdout).stream
            if sys.stderr is not None and sys.stderr.fileno() >= 0:
                sys.stderr = colorama.AnsiToWin32(sys.stderr).stream

    if parsed.application == 'launch':
        run_launch()
    else:
        if parsed.application in ['sy', 'cli']:
            action = run_sy
        elif parsed.application in ['syg', 'gui']:
            action = run_syg
        elif parsed.application == 'viewer':
            action = run_viewer
        elif parsed.application == 'spyder':
            action = run_spyder
        elif parsed.application == 'ipython':
            # IPython has no need of pipes, and therefore simply returns.
            return run_ipython()
        elif parsed.application == 'nosetests':
            action = run_nosetests
        elif parsed.application == 'tests':
            action = run_tests
        elif parsed.application == 'pylint':
            action = run_pylint
        elif parsed.application == 'pyflakes':
            action = run_pyflakes
        elif parsed.application == 'benchmark':
            action = run_benchmark_suite
        elif parsed.application == 'install':
            action = run_install
        elif parsed.application == 'uninstall':
            action = run_uninstall
        elif parsed.application == 'clear':
            action = run_clear

        perflog('run:imports', '{')
        from Gui import settings, util
        perflog('run:imports', '}')

        iniparser = argparse.ArgumentParser()
        iniparser.add_argument(
            '-I', '--inifile', action='store', default=None)
        parsed, _ = iniparser.parse_known_args(_remove_help_args(sys.argv))
        # Set the global settings inifile
        settings.create_settings(parsed.inifile)

        util.create_session_folder()
        session_folder = settings.instance()['session_folder']

        close_list = []

        try:
            # Writing missing pipes to files instead.

            if sys.stdin is None or sys.stdin.fileno() < 0:
                stdin_filename = os.path.join(session_folder, 'stdin')
                sys.stdin = open(stdin_filename, 'w+')
                close_list.append(sys.stdin)

            if stdout or sys.stdout is None or sys.stdout.fileno() < 0:
                stdout_filename = os.path.join(session_folder, 'stdout')
                sys.stdout = open(
                    stdout_filename, 'w')
                close_list.append(sys.stdout)

            if stderr or sys.stderr is None or sys.stderr.fileno() < 0:
                stderr_filename = os.path.join(session_folder, 'stderr')
                sys.stderr = open(
                    stderr_filename, 'w')
                close_list.append(sys.stderr)

            _stdout_writer(writer)
            _stderr_writer(writer)

            action()
        finally:
            for f in reversed(close_list):
                f.close()

            if coverage_tester:
                coverage_tester.stop_coverage()
                coverage_tester.report_coverage()


def main():
    """Main."""
    try:
        app = sys.argv[1]
        del sys.argv[1]
    except:
        app = None
    run(app)


if __name__ == '__main__':
    main()
