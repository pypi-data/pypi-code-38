from setuptools.command.test import test as TestCommand
import os
import setuptools
import shutil
import sys


# From here: http://pytest.org/2.2.4/goodpractises.html
class TestCommand(TestCommand):
    DIRECTORY = 'test'

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [self.DIRECTORY]
        self.test_suite = True

    def run_tests(self):
        # Import here, because outside the eggs aren't loaded.
        import pytest

        errno = pytest.main(self.test_args)
        if errno:
            raise SystemExit(errno)


class CoverageCommand(TestCommand):
    def run_tests(self):
        import coverage

        cov = coverage.Coverage(config_file=True)

        cov.start()
        super().run_tests()
        cov.stop()

        cov.report(file=sys.stdout)
        coverage = cov.html_report(directory='htmlcov')
        fail_under = cov.get_option('report:fail_under')
        if coverage < fail_under:
            print(
                'ERROR: coverage %.2f%% was less than fail_under=%s%%'
                % (coverage, fail_under)
            )
            raise SystemExit(1)


class ApplicationCommand(setuptools.Command):
    description = 'Build the application'
    user_options = []
    MAIN = 'scripts/main/hardback'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from PyInstaller import __main__

        old_argv = sys.argv[:]
        try:
            sys.argv[:] = 'pyapplication', '--onefile', '-y', self.MAIN
            code = __main__.run()
            if code:
                raise SystemExit(code)

        finally:
            sys.argv[:] = old_argv


class CleanCommand(setuptools.Command):
    description = 'Clean generated files'
    user_options = []
    TO_CLEAN = 'dist/', 'build/', 'hardback.spec'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for f in self.TO_CLEAN:
            if f.endswith('/'):
                shutil.rmtree(f, ignore_errors=True)
            else:
                os.remove(f)


NAME = 'hardback'
OWNER = 'timedata-org'
VERSION_FILE = os.path.join(os.path.dirname(__file__), NAME, 'VERSION')
VERSION = open(VERSION_FILE).read().strip()
URL = 'http://github.com/%s/%s' % (OWNER, NAME)

setuptools.setup(
    name=NAME,
    version=VERSION,
    description='Hardcopy backups of digital data',
    long_description=open('README.rst').read(),
    author='Tom Ritchford',
    author_email='tom@swirly.com',
    url=URL,
    download_url='%s/archive/%s.tar.gz' % (URL, VERSION),
    license='MIT',
    packages=setuptools.find_packages(exclude=['test']),
    install_requires=open('requirements.txt').read().splitlines(),
    tests_require=open('test_requirements.txt').read().splitlines(),
    include_package_data=True,
    cmdclass={
        'application': ApplicationCommand,
        'clean': CleanCommand,
        'coverage': CoverageCommand,
        'test': TestCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
