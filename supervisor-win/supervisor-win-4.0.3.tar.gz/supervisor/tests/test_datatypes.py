"""Test suite for supervisor.datatypes"""

import os
import signal
import socket
import unittest

from supervisor import datatypes
from supervisor.compat import maxint


class ProcessOrGroupName(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.process_or_group_name(arg)

    def test_strips_surrounding_whitespace(self):
        name = " foo\t"
        self.assertEqual(self._callFUT(name), "foo")

    def test_disallows_inner_spaces(self):
        name = "foo bar"
        self.assertRaises(ValueError, self._callFUT, name)

    def test_disallows_colons(self):
        name = "foo:bar"
        self.assertRaises(ValueError, self._callFUT, name)


class IntegerTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.integer(arg)

    def test_converts_numeric(self):
        self.assertEqual(self._callFUT('1'), 1)

    def test_converts_numeric_overflowing_int(self):
        self.assertEqual(self._callFUT(str(maxint + 1)), maxint + 1)

    def test_raises_for_non_numeric(self):
        self.assertRaises(ValueError, self._callFUT, 'abc')


class BooleanTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.boolean(arg)

    def test_returns_true_for_truthy_values(self):
        for s in datatypes.TRUTHY_STRINGS:
            self.assertEqual(self._callFUT(s), True)

    def test_returns_true_for_upper_truthy_values(self):
        for s in map(str.upper, datatypes.TRUTHY_STRINGS):
            self.assertEqual(self._callFUT(s), True)

    def test_returns_false_for_falsy_values(self):
        for s in datatypes.FALSY_STRINGS:
            self.assertEqual(self._callFUT(s), False)

    def test_returns_false_for_upper_falsy_values(self):
        for s in map(str.upper, datatypes.FALSY_STRINGS):
            self.assertEqual(self._callFUT(s), False)

    def test_braises_value_error_for_bad_value(self):
        self.assertRaises(ValueError,
                          self._callFUT, 'not-a-value')


class ListOfStringsTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.list_of_strings(arg)

    def test_returns_empty_list_for_empty_string(self):
        self.assertEqual(self._callFUT(''), [])

    def test_returns_list_of_strings_by_comma_split(self):
        self.assertEqual(self._callFUT('foo,bar'), ['foo', 'bar'])

    def test_returns_strings_with_whitespace_stripped(self):
        self.assertEqual(self._callFUT(' foo , bar '), ['foo', 'bar'])

    def test_raises_value_error_when_comma_split_fails(self):
        self.assertRaises(ValueError,
                          self._callFUT, 42)


class ListOfIntsTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.list_of_ints(arg)

    def test_returns_empty_list_for_empty_string(self):
        self.assertEqual(self._callFUT(''), [])

    def test_returns_list_of_ints_by_comma_split(self):
        self.assertEqual(self._callFUT('1,42'), [1, 42])

    def test_returns_ints_even_if_whitespace_in_string(self):
        self.assertEqual(self._callFUT(' 1 , 42 '), [1, 42])

    def test_raises_value_error_when_comma_split_fails(self):
        self.assertRaises(ValueError,
                          self._callFUT, 42)

    def test_raises_value_error_when_one_value_is_bad(self):
        self.assertRaises(ValueError,
                          self._callFUT, '1, bad, 42')


class ListOfExitcodesTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.list_of_exitcodes(arg)

    def test_returns_list_of_ints_from_csv(self):
        self.assertEqual(self._callFUT('1,2,3'), [1, 2, 3])

    def test_returns_list_of_ints_from_one(self):
        self.assertEqual(self._callFUT('1'), [1])

    def test_raises_for_invalid_exitcode_values(self):
        self.assertRaises(ValueError, self._callFUT, 'a,b,c')
        self.assertRaises(ValueError, self._callFUT, '1024')
        self.assertRaises(ValueError, self._callFUT, '-1,1')


class DictOfKeyValuePairsTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.dict_of_key_value_pairs(arg)

    def test_returns_empty_dict_for_empty_str(self):
        actual = self._callFUT('')
        self.assertEqual({}, actual)

    def test_returns_dict_from_single_pair_str(self):
        actual = self._callFUT('foo=bar')
        expected = {'foo': 'bar'}
        self.assertEqual(actual, expected)

    def test_returns_dict_from_multi_pair_str(self):
        actual = self._callFUT('foo=bar,baz=qux')
        expected = {'foo': 'bar', 'baz': 'qux'}
        self.assertEqual(actual, expected)

    def test_returns_dict_even_if_whitespace(self):
        actual = self._callFUT(' foo = bar , baz = qux ')
        expected = {'foo': 'bar', 'baz': 'qux'}
        self.assertEqual(actual, expected)

    def test_returns_dict_even_if_newlines(self):
        actual = self._callFUT('foo\n=\nbar\n,\nbaz\n=\nqux')
        expected = {'foo': 'bar', 'baz': 'qux'}
        self.assertEqual(actual, expected)

    def test_handles_commas_inside_apostrophes(self):
        actual = self._callFUT("foo='bar,baz',baz='q,ux'")
        expected = {'foo': 'bar,baz', 'baz': 'q,ux'}
        self.assertEqual(actual, expected)

    def test_handles_commas_inside_quotes(self):
        actual = self._callFUT('foo="bar,baz",baz="q,ux"')
        expected = {'foo': 'bar,baz', 'baz': 'q,ux'}
        self.assertEqual(actual, expected)

    def test_handles_newlines_inside_quotes(self):
        actual = datatypes.dict_of_key_value_pairs('foo="a\nb\nc"')
        expected = {'foo': 'a\nb\nc'}
        self.assertEqual(actual, expected)

    def test_handles_quotes_inside_quotes(self):
        actual = datatypes.dict_of_key_value_pairs('foo="\'\\""')
        expected = {'foo': '\'"'}
        self.assertEqual(actual, expected)

    def test_handles_empty_inside_quotes(self):
        actual = datatypes.dict_of_key_value_pairs('foo=""')
        expected = {'foo': ''}
        self.assertEqual(actual, expected)

    def test_handles_unquoted_non_alphanum(self):
        actual = self._callFUT(
            'HOME=/home/auser,FOO=/.foo+(1.2)-_/,'
            'SUPERVISOR_SERVER_URL=http://127.0.0.1:9001')
        expected = {'HOME': '/home/auser', 'FOO': '/.foo+(1.2)-_/',
                    'SUPERVISOR_SERVER_URL': 'http://127.0.0.1:9001'}
        self.assertEqual(actual, expected)

    def test_allows_trailing_comma(self):
        actual = self._callFUT('foo=bar,')
        expected = {'foo': 'bar'}
        self.assertEqual(actual, expected)

    def test_raises_value_error_on_too_short(self):
        self.assertRaises(ValueError,
                          self._callFUT, 'foo')
        self.assertRaises(ValueError,
                          self._callFUT, 'foo=')
        self.assertRaises(ValueError,
                          self._callFUT, 'foo=bar,baz')
        self.assertRaises(ValueError,
                          self._callFUT, 'foo=bar,baz=')

    def test_raises_when_comma_is_missing(self):
        kvp = 'KEY1=no-comma KEY2=ends-with-comma,'
        self.assertRaises(ValueError,
                          self._callFUT, kvp)


class LogfileNameTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.logfile_name(arg)

    def test_returns_none_for_none_values(self):
        for thing in datatypes.LOGFILE_NONES:
            actual = self._callFUT(thing)
            self.assertEqual(actual, None)

    def test_returns_none_for_uppered_none_values(self):
        for thing in datatypes.LOGFILE_NONES:
            if hasattr(thing, 'upper'):
                thing = thing.upper()
            actual = self._callFUT(thing)
            self.assertEqual(actual, None)

    def test_returns_automatic_for_auto_values(self):
        for thing in datatypes.LOGFILE_AUTOS:
            actual = self._callFUT(thing)
            self.assertEqual(actual, datatypes.Automatic)

    def test_returns_automatic_for_uppered_auto_values(self):
        for thing in datatypes.LOGFILE_AUTOS:
            if hasattr(thing, 'upper'):
                thing = thing.upper()
            actual = self._callFUT(thing)
            self.assertEqual(actual, datatypes.Automatic)

    def test_returns_existing_dirpath_for_other_values(self):
        func = datatypes.existing_dirpath
        datatypes.existing_dirpath = lambda path: path
        try:
            path = '/path/to/logfile/With/Case/Preserved'
            actual = self._callFUT(path)
            self.assertEqual(actual, path)
        finally:
            datatypes.existing_dirpath = func


class RangeCheckedConversionTests(unittest.TestCase):
    def _getTargetClass(self):
        return datatypes.RangeCheckedConversion

    def _makeOne(self, conversion, min=None, max=None):
        return self._getTargetClass()(conversion, min, max)

    def test_below_lower_bound(self):
        conversion = self._makeOne(lambda *arg: -1, 0)
        self.assertRaises(ValueError, conversion, None)

    def test_above_upper_lower_bound(self):
        conversion = self._makeOne(lambda *arg: 1, 0, 0)
        self.assertRaises(ValueError, conversion, None)

    def test_passes(self):
        conversion = self._makeOne(lambda *arg: 0, 0, 0)
        self.assertEqual(conversion(0), 0)


class OctalTypeTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.octal_type(arg)

    def test_success(self):
        self.assertEqual(self._callFUT('10'), 8)

    def test_raises_for_non_numeric(self):
        try:
            self._callFUT('bad')
            self.fail()
        except ValueError as e:
            expected = 'bad can not be converted to an octal type'
            self.assertEqual(e.args[0], expected)

    def test_raises_for_unconvertable_numeric(self):
        try:
            self._callFUT('1.2')
            self.fail()
        except ValueError as e:
            expected = '1.2 can not be converted to an octal type'
            self.assertEqual(e.args[0], expected)


class ExistingDirectoryTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.existing_directory(arg)

    def test_dir_exists(self):
        path = os.path.dirname(__file__)
        self.assertEqual(path, self._callFUT(path))

    def test_dir_does_not_exist(self):
        path = os.path.join(os.path.dirname(__file__), 'nonexistent')
        try:
            self._callFUT(path)
            self.fail()
        except ValueError as e:
            expected = "%s is not an existing directory" % path
            self.assertEqual(e.args[0], expected)

    def test_not_a_directory(self):
        path = __file__
        try:
            self._callFUT(path)
            self.fail()
        except ValueError as e:
            expected = "%s is not an existing directory" % path
            self.assertEqual(e.args[0], expected)

    def test_expands_home(self):
        home = os.path.expanduser('~')
        if os.path.exists(home):
            path = self._callFUT('~')
            self.assertEqual(home, path)

class ExistingDirpathTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.existing_dirpath(arg)

    def test_returns_existing_dirpath(self):
        self.assertEqual(self._callFUT(__file__), __file__)

    def test_returns_dirpath_if_relative(self):
        self.assertEqual(self._callFUT('foo'), 'foo')

    def test_raises_if_dir_does_not_exist(self):
        path = os.path.join(os.path.dirname(__file__), 'nonexistent', 'foo')
        try:
            self._callFUT(path)
            self.fail()
        except ValueError as e:
            expected = ('The directory named as part of the path %s '
                        'does not exist.' % path)
            self.assertEqual(e.args[0], expected)

    def test_raises_if_exists_but_not_a_dir(self):
        path = os.path.join(os.path.dirname(__file__),
                            os.path.basename(__file__), 'foo')
        try:
            self._callFUT(path)
            self.fail()
        except ValueError as e:
            expected = ('The directory named as part of the path %s '
                        'does not exist.' % path)
            self.assertEqual(e.args[0], expected)

    def test_expands_home(self):
        home = os.path.expanduser('~')
        if os.path.exists(home):
            path = self._callFUT(os.path.join('~', 'foo'))
            self.assertEqual(os.path.join(home, 'foo'), path)

class LoggingLevelTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.logging_level(arg)

    def test_returns_level_from_name_case_insensitive(self):
        from supervisor.loggers import LevelsByName
        self.assertEqual(self._callFUT("wArN"), LevelsByName.WARN)

    def test_raises_for_bad_level_name(self):
        self.assertRaises(ValueError,
                          self._callFUT, "foo")


class UrlTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.url(arg)

    def test_accepts_urlparse_recognized_scheme_with_netloc(self):
        good_url = 'http://localhost:9001'
        self.assertEqual(self._callFUT(good_url), good_url)

    def test_rejects_urlparse_recognized_scheme_but_no_netloc(self):
        bad_url = 'http://'
        self.assertRaises(ValueError, self._callFUT, bad_url)

    def test_accepts_unix_scheme_with_path(self):
        good_url = "unix://somepath"
        self.assertEqual(good_url, self._callFUT(good_url))

    def test_rejects_unix_scheme_with_no_slashes_or_path(self):
        bad_url = "unix:"
        self.assertRaises(ValueError, self._callFUT, bad_url)

    def test_rejects_unix_scheme_with_slashes_but_no_path(self):
        bad_url = "unix://"
        self.assertRaises(ValueError, self._callFUT, bad_url)


class InetStreamSocketConfigTests(unittest.TestCase):
    def _getTargetClass(self):
        return datatypes.InetStreamSocketConfig

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_url(self):
        conf = self._makeOne('127.0.0.1', 8675)
        self.assertEqual(conf.url, 'tcp://127.0.0.1:8675')

    def test___str__(self):
        cfg = self._makeOne('localhost', 65531)
        self.assertEqual(str(cfg), 'tcp://localhost:65531')

    def test_repr(self):
        conf = self._makeOne('127.0.0.1', 8675)
        s = repr(conf)
        self.assertTrue('supervisor.datatypes.InetStreamSocketConfig' in s)
        self.assertTrue(s.endswith('for tcp://127.0.0.1:8675>'), s)

    def test_addr(self):
        conf = self._makeOne('127.0.0.1', 8675)
        addr = conf.addr()
        self.assertEqual(addr, ('127.0.0.1', 8675))

    def test_port_as_string(self):
        conf = self._makeOne('localhost', '5001')
        addr = conf.addr()
        self.assertEqual(addr, ('localhost', 5001))

    def test_create_and_bind(self):
        conf = self._makeOne('127.0.0.1', 8675)
        sock = conf.create_and_bind()
        reuse = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.assertTrue(reuse)
        self.assertEqual(conf.addr(), sock.getsockname())  # verifies that bind was called
        sock.close()

    def test_same_urls_are_equal(self):
        conf1 = self._makeOne('localhost', 5001)
        conf2 = self._makeOne('localhost', 5001)
        self.assertTrue(conf1 == conf2)
        self.assertFalse(conf1 != conf2)

    def test_diff_urls_are_not_equal(self):
        conf1 = self._makeOne('localhost', 5001)
        conf2 = self._makeOne('localhost', 5002)
        self.assertTrue(conf1 != conf2)
        self.assertFalse(conf1 == conf2)

    def test_diff_objs_are_not_equal(self):
        conf1 = self._makeOne('localhost', 5001)
        conf2 = 'blah'
        self.assertTrue(conf1 != conf2)
        self.assertFalse(conf1 == conf2)


class InetAddressTests(unittest.TestCase):
    def _callFUT(self, s):
        return datatypes.inet_address(s)

    def test_no_port_number(self):
        self.assertRaises(ValueError, self._callFUT, 'a:')

    def test_bad_port_number(self):
        self.assertRaises(ValueError, self._callFUT, 'a')

    def test_default_host(self):
        host, port = self._callFUT('*:8080')
        self.assertEqual(host, '')
        self.assertEqual(port, 8080)

    def test_boring(self):
        host, port = self._callFUT('localhost:80')
        self.assertEqual(host, 'localhost')
        self.assertEqual(port, 80)


class SocketAddressTests(unittest.TestCase):
    def _getTargetClass(self):
        return datatypes.SocketAddress

    def _makeOne(self, s):
        return self._getTargetClass()(s)

    def test_inet_socket(self):
        addr = self._makeOne('localhost:8080')
        self.assertEqual(addr.family, socket.AF_INET)
        self.assertEqual(addr.address, ('localhost', 8080))


class SignalNumberTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.signal_number(arg)

    def test_converts_number(self):
        self.assertEqual(self._callFUT(signal.SIGTERM), signal.SIGTERM)

    def test_converts_name(self):
        self.assertEqual(self._callFUT(' term '), signal.SIGTERM)

    def test_converts_signame(self):
        self.assertEqual(self._callFUT('SIGTERM'), signal.SIGTERM)

    def test_raises_for_bad_number(self):
        try:
            self._callFUT('12345678')
            self.fail()
        except ValueError as e:
            expected = "value '12345678' is not a valid signal number"
            self.assertEqual(e.args[0], expected)

    def test_raises_for_bad_name(self):
        try:
            self._callFUT('BADSIG')
            self.fail()
        except ValueError as e:
            expected = "value 'BADSIG' is not a valid signal name"
            self.assertEqual(e.args[0], expected)


class AutoRestartTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.auto_restart(arg)

    def test_converts_truthy(self):
        for s in datatypes.TRUTHY_STRINGS:
            result = self._callFUT(s)
            self.assertEqual(result, datatypes.RestartUnconditionally)

    def test_converts_falsy(self):
        for s in datatypes.FALSY_STRINGS:
            self.assertFalse(self._callFUT(s))

    def test_converts_unexpected(self):
        for s in ('unexpected', 'UNEXPECTED'):
            result = self._callFUT(s)
            self.assertEqual(result, datatypes.RestartWhenExitUnexpected)

    def test_raises_for_bad_value(self):
        try:
            self._callFUT('bad')
            self.fail()
        except ValueError as e:
            self.assertEqual(e.args[0], "invalid 'autorestart' value 'bad'")


class ProfileOptionsTests(unittest.TestCase):
    def _callFUT(self, arg):
        return datatypes.profile_options(arg)

    def test_empty(self):
        sort_options, callers = self._callFUT('')
        self.assertEqual([], sort_options)
        self.assertFalse(callers)

    def test_without_callers(self):
        sort_options, callers = self._callFUT('CUMULATIVE,calls')
        self.assertEqual(['cumulative', 'calls'], sort_options)
        self.assertFalse(callers)

    def test_with_callers(self):
        sort_options, callers = self._callFUT('cumulative, callers')
        self.assertEqual(['cumulative'], sort_options)
        self.assertTrue(callers)
