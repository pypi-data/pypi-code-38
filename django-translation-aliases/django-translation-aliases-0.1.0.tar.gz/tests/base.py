import functools
import os
import re
import shutil
import tempfile

from django.template.engine import Engine
from django.test.utils import override_settings
from django.utils._os import upath

source_code_dir = os.path.dirname(upath(__file__))


def copytree(src, dst):
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))


def setup(templates, *args, **kwargs):
    """
    Runs test method multiple times in the following order:

    debug       cached      string_if_invalid
    -----       ------      -----------------
    False       False
    False       True
    False       False       INVALID
    False       True        INVALID
    True        False
    True        True
    """
    # when testing deprecation warnings, it's useful to run just one test since
    # the message won't be displayed multiple times
    test_once = kwargs.get('test_once', False)

    for arg in args:
        templates.update(arg)

    # numerous tests make use of an inclusion tag
    # add this in here for simplicity
    templates["inclusion.html"] = "{{ result }}"

    loaders = [
        ('django.template.loaders.cached.Loader', [
            ('django.template.loaders.locmem.Loader', templates),
        ]),
    ]

    def decorator(func):
        # Make Engine.get_default() raise an exception to ensure that tests
        # are properly isolated from Django's global settings.
        @override_settings(TEMPLATES=None)
        @functools.wraps(func)
        def inner(self):
            # Set up custom template tag libraries if specified
            libraries = getattr(self, 'libraries', {})

            self.engine = Engine(
                libraries=libraries,
                loaders=loaders,
            )
            func(self)
            if test_once:
                return
            func(self)

            self.engine = Engine(
                libraries=libraries,
                loaders=loaders,
                string_if_invalid='INVALID',
            )
            func(self)
            func(self)

            self.engine = Engine(
                debug=True,
                libraries=libraries,
                loaders=loaders,
            )
            func(self)
            func(self)

        return inner

    return decorator


class POFileAssertionMixin(object):

    def _assertPoKeyword(self, keyword, expected_value, haystack, use_quotes=True):
        q = '"'
        if use_quotes:
            expected_value = '"%s"' % expected_value
            q = "'"
        needle = '%s %s' % (keyword, expected_value)
        expected_value = re.escape(expected_value)
        return self.assertTrue(
            re.search('^%s %s' % (keyword, expected_value), haystack, re.MULTILINE),
            'Could not find %(q)s%(n)s%(q)s in generated PO file' % {'n': needle, 'q': q}
        )

    def assertMsgId(self, msgid, haystack, use_quotes=True):
        return self._assertPoKeyword('msgid', msgid, haystack, use_quotes=use_quotes)


class RunInTmpDirMixin(object):
    """
    Allow i18n tests that need to generate .po/.mo files to run in an isolated
    temporary filesystem tree created by tempfile.mkdtemp() that contains a
    clean copy of the relevant test code.

    Test classes using this mixin need to define a `work_subdir` attribute
    which designates the subdir under `tests/i18n/` that will be copied to the
    temporary tree from which its test cases will run.

    The setUp() method sets the current working dir to the temporary tree.
    It'll be removed when cleaning up.
    """

    def setUp(self):
        self._cwd = os.getcwd()
        self.work_dir = tempfile.mkdtemp(prefix='i18n_')
        # Resolve symlinks, if any, in test directory paths.
        self.test_dir = os.path.realpath(os.path.join(self.work_dir, self.work_subdir))
        copytree(os.path.join(source_code_dir, self.work_subdir), self.test_dir)
        # Step out of the temporary working tree before removing it to avoid
        # deletion problems on Windows. Cleanup actions registered with
        # addCleanup() are called in reverse so preserve this ordering.
        self.addCleanup(self._rmrf, self.test_dir)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.test_dir)

    def _rmrf(self, dname):
        if os.path.commonprefix([self.test_dir, os.path.abspath(dname)]) != self.test_dir:
            return
        shutil.rmtree(dname)

    def rmfile(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
