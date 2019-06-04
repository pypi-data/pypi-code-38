# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from textwrap import dedent
import unittest
import mock
from mock import patch
from six import BytesIO

from diff_cover.violationsreporters import base

from diff_cover.command_runner import CommandError
from diff_cover.violationsreporters.base import QualityReporter
from diff_cover.violationsreporters.java_violations_reporter import (
    Violation, checkstyle_driver,
    CheckstyleXmlDriver, FindbugsXmlDriver)


def _patch_so_all_files_exist():
    _mock_exists = patch.object(base.os.path, 'exists').start()
    _mock_exists.returnvalue = True


def _setup_patch(return_value, status_code=0):
    mocked_process = mock.Mock()
    mocked_process.returncode = status_code
    mocked_process.communicate.return_value = return_value
    mocked_subprocess = mock.patch('diff_cover.command_runner.subprocess').start()
    mocked_subprocess.Popen.return_value = mocked_process
    return mocked_process


class CheckstyleQualityReporterTest(unittest.TestCase):
    """Tests for checkstyle quality violations."""

    def setUp(self):
        """Set up required files."""
        _patch_so_all_files_exist()
        self.addCleanup(patch.stopall)

    def test_no_such_file(self):
        """Expect that we get no results."""
        quality = QualityReporter(checkstyle_driver)

        result = quality.violations('')
        self.assertEqual(result, [])

    def test_no_java_file(self):
        """Expect that we get no results because no Python files."""
        quality = QualityReporter(checkstyle_driver)
        file_paths = ['file1.coffee', 'subdir/file2.js']
        for path in file_paths:
            result = quality.violations(path)
            self.assertEqual(result, [])

    def test_quality(self):
        """Integration test."""
        # Patch the output of `checkstyle`
        _setup_patch((
            dedent("""
            [WARN] ../new_file.java:1:1: Line contains a tab character.
            [WARN] ../new_file.java:13: 'if' construct must use '{}'s.
            """).strip().encode('ascii'), ''
        ))

        expected_violations = [
            Violation(1, 'Line contains a tab character.'),
            Violation(13, "'if' construct must use '{}'s."),
        ]

        # Parse the report
        quality = QualityReporter(checkstyle_driver)

        # Expect that the name is set
        self.assertEqual(quality.name(), 'checkstyle')

        # Measured_lines is undefined for a
        # quality reporter since all lines are measured
        self.assertEqual(quality.measured_lines('../new_file.java'), None)

        # Expect that we get violations for file1.java only
        # We're not guaranteed that the violations are returned
        # in any particular order.
        actual_violations = quality.violations('../new_file.java')
        self.assertEqual(len(actual_violations), len(expected_violations))
        for expected in expected_violations:
            self.assertIn(expected, actual_violations)


class CheckstyleXmlQualityReporterTest(unittest.TestCase):

    def setUp(self):
        _patch_so_all_files_exist()
        # Paths generated by git_path are always the given argument
        _git_path_mock = patch('diff_cover.violationsreporters.java_violations_reporter.GitPathTool').start()
        _git_path_mock.relative_path = lambda path: path
        _git_path_mock.absolute_path = lambda path: path

    def tearDown(self):
        """
        Undo all patches.
        """
        patch.stopall()

    def test_no_such_file(self):
        quality = QualityReporter(CheckstyleXmlDriver())

        # Expect that we get no results
        result = quality.violations('')
        self.assertEqual(result, [])

    def test_no_java_file(self):
        quality = QualityReporter(CheckstyleXmlDriver())
        file_paths = ['file1.coffee', 'subdir/file2.js']
        # Expect that we get no results because no Java files
        for path in file_paths:
            result = quality.violations(path)
            self.assertEqual(result, [])

    def test_quality(self):
        # Patch the output of `checkstyle`
        _setup_patch((
            dedent("""
            <?xml version="1.0" encoding="UTF-8"?>
            <checkstyle version="8.0">
                <file name="file1.java">
                    <error line="1" severity="error" message="Missing docstring"/>
                    <error line="2" severity="error" message="Unused variable 'd'"/>
                    <error line="2" severity="warning" message="TODO: Not the real way we'll store usages!"/>
                    <error line="579" severity="error" message="Unable to import 'rooted_paths'"/>
                    <error line="113" severity="error" message="Unused argument 'cls'"/>
                    <error line="150" severity="error" message="error while code parsing ([Errno 2] No such file or directory)"/>
                    <error line="149" severity="error" message="Comma not followed by a space"/>
                </file>
                <file name="path/to/file2.java">
                    <error line="100" severity="error" message="Access to a protected member"/>
                </file>
            </checkstyle>
            """).strip().encode('ascii'), ''
        ))

        expected_violations = [
            Violation(1, 'error: Missing docstring'),
            Violation(2, "error: Unused variable 'd'"),
            Violation(2, "warning: TODO: Not the real way we'll store usages!"),
            Violation(579, "error: Unable to import 'rooted_paths'"),
            Violation(150, "error: error while code parsing ([Errno 2] No such file or directory)"),
            Violation(149, "error: Comma not followed by a space"),
            Violation(113, "error: Unused argument 'cls'")
        ]

        # Parse the report
        quality = QualityReporter(CheckstyleXmlDriver())

        # Expect that the name is set
        self.assertEqual(quality.name(), 'checkstyle')

        # Measured_lines is undefined for a
        # quality reporter since all lines are measured
        self.assertEqual(quality.measured_lines('file1.java'), None)

        # Expect that we get violations for file1.java only
        # We're not guaranteed that the violations are returned
        # in any particular order.
        actual_violations = quality.violations('file1.java')
        self.assertEqual(len(actual_violations), len(expected_violations))
        for expected in expected_violations:
            self.assertIn(expected, actual_violations)

    def test_quality_error(self):
        # Patch the output stderr/stdout and returncode of `checkstyle`
        _setup_patch((
            dedent("""
            <?xml version="1.0" encoding="UTF-8"?>
            <checkstyle version="8.0">
                <file name="file1.java">
                    <error line="1" severity="error" message="Missing docstring"/>
                </file>
            </checkstyle>
            """), b'oops'), status_code=1)

        # Parse the report
        with patch('diff_cover.violationsreporters.java_violations_reporter.run_command_for_code') as code:
            code.return_value = 0
            quality = QualityReporter(CheckstyleXmlDriver())

            # Expect an error
            self.assertRaises(CommandError, quality.violations, 'file1.java')

    def test_quality_pregenerated_report(self):

        # When the user provides us with a pre-generated checkstyle report
        # then use that instead of calling checkstyle directly.
        checkstyle_reports = [
            BytesIO(dedent("""
                <?xml version="1.0" encoding="UTF-8"?>
                <checkstyle version="8.0">
                    <file name="path/to/file.java">
                        <error line="1" severity="error" message="Missing docstring"/>
                        <error line="57" severity="warning" message="TODO the name of this method is a little bit confusing"/>
                    </file>
                    <file name="another/file.java">
                        <error line="41" severity="error" message="Specify string format arguments as logging function parameters"/>
                        <error line="175" severity="error" message="Operator not preceded by a space"/>
                        <error line="259" severity="error" message="Invalid name '' for type variable (should match [a-z_][a-z0-9_]{2,30}$)"/>
                    </file>
                </checkstyle>
            """).strip().encode('utf-8')),

            BytesIO(dedent("""
            <?xml version="1.0" encoding="UTF-8"?>
            <checkstyle version="8.0">
                <file name="path/to/file.java">
                    <error line="183" severity="error" message="Invalid name '' for type argument (should match [a-z_][a-z0-9_]{2,30}$)"/>
                </file>
                <file name="another/file.java">
                    <error line="183" severity="error" message="Missing docstring"/>
                </file>
            </checkstyle>
            """).strip().encode('utf-8'))
        ]

        # Generate the violation report
        quality = QualityReporter(CheckstyleXmlDriver(), reports=checkstyle_reports)

        # Expect that we get the right violations
        expected_violations = [
            Violation(1, 'error: Missing docstring'),
            Violation(57, 'warning: TODO the name of this method is a little bit confusing'),
            Violation(183, "error: Invalid name '' for type argument (should match [a-z_][a-z0-9_]{2,30}$)")
        ]

        # We're not guaranteed that the violations are returned
        # in any particular order.
        actual_violations = quality.violations('path/to/file.java')
        self.assertEqual(len(actual_violations), len(expected_violations))
        for expected in expected_violations:
            self.assertIn(expected, actual_violations)


class FindbugsQualityReporterTest(unittest.TestCase):

    def setUp(self):
        _patch_so_all_files_exist()
        # Paths generated by git_path are always the given argument
        _git_path_mock = patch('diff_cover.violationsreporters.java_violations_reporter.GitPathTool').start()
        _git_path_mock.relative_path = lambda path: path
        _git_path_mock.absolute_path = lambda path: path

    def tearDown(self):
        """
        Undo all patches.
        """
        patch.stopall()

    def test_no_such_file(self):
        quality = QualityReporter(FindbugsXmlDriver())

        # Expect that we get no results
        result = quality.violations('')
        self.assertEqual(result, [])

    def test_no_java_file(self):
        quality = QualityReporter(FindbugsXmlDriver())
        file_paths = ['file1.coffee', 'subdir/file2.js']
        # Expect that we get no results because no Java files
        for path in file_paths:
            result = quality.violations(path)
            self.assertEqual(result, [])

    def test_quality_pregenerated_report(self):
        # When the user provides us with a pre-generated findbugs report
        # then use that instead of calling findbugs directly.
        findbugs_reports = [
            BytesIO(dedent("""
                <?xml version="1.0" encoding="UTF-8"?>
                <BugCollection sequence="0" release="" analysisTimestamp="1512755361404" version="3.0.1" timestamp="1512755226000">
                    <BugInstance instanceOccurrenceNum="0" instanceHash="1967bf8c4d25c6b964f30356014aa9fb" rank="20" abbrev="Dm" category="I18N" priority="3" type="DM_CONVERT_CASE" instanceOccurrenceMax="0">
                        <ShortMessage>Consider using Locale parameterized version of invoked method</ShortMessage>
                        <LongMessage>Use of non-localized String.toUpperCase() or String.toLowerCase() in org.opensource.sample.file$1.isMultipart(HttpServletRequest)</LongMessage>
                        <Class classname="org.opensource.sample.file$1" primary="true">
                            <SourceLine classname="org.opensource.sample.file$1" start="94" end="103" sourcepath="path/to/file.java" sourcefile="file.java">
                                <Message>At file.java:[lines 94-103]</Message>
                            </SourceLine>
                            <Message>In class org.opensource.sample.file$1</Message>
                        </Class>
                        <Method isStatic="false" classname="org.opensource.sample.file$1" signature="(Ljavax/servlet/http/HttpServletRequest;)Z" name="isMultipart" primary="true">
                            <SourceLine endBytecode="181" classname="org.opensource.sample.file$1" start="97" end="103" sourcepath="file1.java" sourcefile="file1.java" startBytecode="0" />
                            <Message>In method org.opensource.sample.file$1.isMultipart(HttpServletRequest)</Message>
                        </Method>
                        <SourceLine endBytecode="6" classname="org.opensource.sample.file$1" start="97" end="97" sourcepath="path/to/file.java" sourcefile="file.java" startBytecode="6" primary="true">
                            <Message>At file.java:[line 97]</Message>
                        </SourceLine>
                        <SourceLine role="SOURCE_LINE_ANOTHER_INSTANCE" endBytecode="55" classname="org.opensource.sample.file$1" start="103" end="104" sourcepath="another/file.java" sourcefile="file.java" startBytecode="55">
                            <Message>Another occurrence at file.java:[line 103, 104]</Message>
                        </SourceLine>
                    </BugInstance>
                </BugCollection>
            """).strip().encode('utf-8')),

            BytesIO(dedent("""
                <?xml version="1.0" encoding="UTF-8"?>
                <BugCollection sequence="0" release="" analysisTimestamp="1512755361404" version="3.0.1" timestamp="1512755226000">
                    <BugInstance instanceOccurrenceNum="0" instanceHash="1967bf8c4d25c6b964f30356014aa9fb" rank="20" abbrev="Dm" category="I18N" priority="3" type="DM_CONVERT_CASE" instanceOccurrenceMax="0">
                        <ShortMessage>Consider using Locale parameterized version of invoked method</ShortMessage>
                        <LongMessage>Use of non-localized String.toUpperCase() or String.toLowerCase() in org.opensource.sample.file$1.isMultipart(HttpServletRequest)</LongMessage>
                        <Class classname="org.opensource.sample.file$1" primary="true">
                            <SourceLine classname="org.opensource.sample.file$1" start="94" end="103" sourcepath="path/to/file.java" sourcefile="file.java">
                                <Message>At file.java:[lines 94-103]</Message>
                            </SourceLine>
                            <Message>In class org.opensource.sample.file$1</Message>
                        </Class>
                        <Method isStatic="false" classname="org.opensource.sample.file$1" signature="(Ljavax/servlet/http/HttpServletRequest;)Z" name="isMultipart" primary="true">
                            <SourceLine endBytecode="181" classname="org.opensource.sample.file$1" start="97" end="103" sourcepath="file1.java" sourcefile="file1.java" startBytecode="0" />
                            <Message>In method org.opensource.sample.file$1.isMultipart(HttpServletRequest)</Message>
                        </Method>
                        <SourceLine endBytecode="6" classname="org.opensource.sample.file$1" start="183" end="183" sourcepath="path/to/file.java" sourcefile="file.java" startBytecode="6" primary="true">
                            <Message>At file.java:[line 97]</Message>
                        </SourceLine>
                        <SourceLine role="SOURCE_LINE_ANOTHER_INSTANCE" endBytecode="55" classname="org.opensource.sample.file$1" start="183" end="183" sourcepath="another/file.java" sourcefile="file.java" startBytecode="55">
                            <Message>Another occurrence at file.java:[line 183]</Message>
                        </SourceLine>
                    </BugInstance>
                </BugCollection>
            """).strip().encode('utf-8')),

            # this is a violation which is not bounded to a specific line. We'll skip those
            BytesIO(dedent("""
                <?xml version="1.0" encoding="UTF-8"?>
                <BugCollection sequence="0" release="" analysisTimestamp="1512755361404" version="3.0.1" timestamp="1512755226000">
                    <BugInstance instanceOccurrenceNum="0" instanceHash="2820338ec68e2e75a81848c95d31167f" rank="19" abbrev="Se" category="BAD_PRACTICE" priority="3" type="SE_BAD_FIELD" instanceOccurrenceMax="0">
                        <ShortMessage>Non-transient non-serializable instance field in serializable class</ShortMessage>
                        <LongMessage>Class org.opensource.sample.file defines non-transient non-serializable instance field</LongMessage>
                        <SourceLine synthetic="true" classname="org.opensource.sample.file" sourcepath="path/to/file.java" sourcefile="file.java">
                            <Message>In file.java</Message>
                        </SourceLine>
                    </BugInstance>
                </BugCollection>
            """).strip().encode('utf-8'))
        ]

        # Generate the violation report
        quality = QualityReporter(FindbugsXmlDriver(), reports=findbugs_reports)

        # Expect that we get the right violations
        expected_violations = [
            Violation(97, 'I18N: Consider using Locale parameterized version of invoked method'),
            Violation(183, 'I18N: Consider using Locale parameterized version of invoked method')
        ]

        # We're not guaranteed that the violations are returned
        # in any particular order.
        actual_violations = quality.violations('path/to/file.java')
        self.assertEqual(len(actual_violations), len(expected_violations))
        for expected in expected_violations:
            self.assertIn(expected, actual_violations)
