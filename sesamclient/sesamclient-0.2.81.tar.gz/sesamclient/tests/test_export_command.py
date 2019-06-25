# -*- coding: utf-8 -*-
# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import contextlib
import io
import json
import os.path
import pprint
import sys
import tempfile
import zipfile
import types
from unittest import mock

from nose.tools import assert_equal, assert_not_in, assert_in, assert_true, assert_false
import sesamclient.main.commands.export


@contextlib.contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield new_out, new_err
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MockConnection:
    def get_config_as_zip(self):
        thezip = io.BytesIO()
        thezipfile = zipfile.ZipFile(thezip, "w")
        thezipfile.writestr("metadata.conf.json", json.dumps({
            "_id": "node"
        }))
        thezipfile.writestr("pipes/pipe1.conf.json", json.dumps({
            "_id": "pipe1"
        }))
        thezipfile.writestr("pipes/pipe2.conf.json", json.dumps({
            "_id": "pipe2"
        }))
        thezipfile.writestr("systems/system1.conf.json", json.dumps({
            "_id": "system1"
        }))
        thezipfile.writestr("systems/system2.conf.json", json.dumps({
            "_id": "system2"
        }))
        thezipfile.close()
        return thezip.getvalue()

    def get_config(self):
        return [
            {
                "_id": "node",
                "type": "metadata"
            },
            {
                "_id": "pipe1",
                "type": "pipe"
            },
            {
                "_id": "pipe2",
                "type": "pipe"
            },
            {
                "_id": "system1",
                "type": "system:sqlite"
            },
            {
                "_id": "system2",
                "type": "system:sqlite"
            },
        ]

    def get_config_as_json_string(self):
        return json.dumps(self.get_config(), indent=4, sort_keys=True)


class InputGuard:
    """This class is used to mock.patch() the input() function in cases where we don't expect the client to
    prompt the user for input."""

    def __init__(self, error_msg="The input() method is not supposed to be called in this test!"):
        self._error_msg = error_msg

    def __call__(self, prompt):
        raise AssertionError(self._error_msg)


def test_export_as_single_file_with_user_prompt():
    do_export_as_single_file(force=False)


def test_export_as_single_file_with_force_flag():
    do_export_as_single_file(force=True)


def do_export_as_single_file(force):
    with tempfile.TemporaryDirectory() as exportdir:
        connection = MockConnection()
        args = types.SimpleNamespace()
        args.exportdir = exportdir
        args.export_filename = None
        args.force = force
        args.expand = False
        args.dry_run = False

        if force:
            # The force-flag is set, so the client shouldn't prompt the user for anything
            input_mock = InputGuard()
        else:
            input_mock = mock.Mock(return_value="yes")

        with captured_output() as (out, err):
            with mock.patch("builtins.input", new=input_mock):
                sesamclient.main.commands.export.export_cmd(connection, args)

                if not force:
                    # Check that the user was asked for a confirmation
                    assert_equal(input_mock.call_count, 1,
                                 "The client should have asked the user to confirm the modifications to the files!")

                filename = "sesam.conf.json"
                assert_true(os.path.exists(os.path.join(exportdir, filename)),
                            "The file '%s' should have been created by the export!" % (filename,))

            out = out.getvalue()
            err = err.getvalue()

            assert_not_in("error", out)
            assert_not_in("error", err)

            assert_in("""\
The following files were added:
  %s/sesam.conf.json""" % (exportdir,), out)
            assert_not_in("The following files were modified", out)
            assert_not_in("The following files were deleted", out)
            assert_not_in("The following files were modified", err)
            assert_not_in("The following files were deleted", err)

        ##################################################################################
        # check that a second run doesn't result in any modified, deleted or added files
        ##################################################################################
        with captured_output() as (out, err):
            with mock.patch("builtins.input",
                            new=InputGuard("The input() method is not supposed to be called in this test, since no "
                                           "changes to the files is supposed to happen in the second export!")):
                args.force = False
                sesamclient.main.commands.export.export_cmd(connection, args)
                filename = "sesam.conf.json"
                assert_true(os.path.exists(os.path.join(exportdir, filename)),
                            "The file '%s' should still exist!" % (filename,))

            out = out.getvalue()
            err = err.getvalue()

            assert_not_in("error", out)
            assert_not_in("error", err)

            assert_in("The existing config-files are up-to-date", out)
            assert_not_in("The following files were added", out)
            assert_not_in("The following files were added", err)
            assert_not_in("The following files were modified", out)
            assert_not_in("The following files were deleted", out)
            assert_not_in("The following files were modified", err)
            assert_not_in("The following files were deleted", err)


def test_export_as_multiple_files_with_user_prompt():
    do_export_as_multiple_files(force=False)


def test_export_as_multiple_files_with_force_flag():
    do_export_as_multiple_files(force=True)


def do_export_as_multiple_files(force):
    with tempfile.TemporaryDirectory() as exportdir:
        connection = MockConnection()
        args = types.SimpleNamespace()
        args.exportdir = exportdir
        args.force = force
        args.expand = True
        args.dry_run = False
        args.export_filename = None

        test_existing_non_config_file_that_should_not_be_touched_filename = os.path.join(exportdir, "test_existing_non_config_file_that_should_not_be_touched.json")
        with open(test_existing_non_config_file_that_should_not_be_touched_filename, "w") as testfile:
            testfile.write("This file should not be touched by the export")
        assert_true(os.path.exists(test_existing_non_config_file_that_should_not_be_touched_filename))

        test_existing_file_that_should_be_deleted_filename = os.path.join(exportdir, "testfilethatshouldbedeleted.conf.json")
        with open(test_existing_file_that_should_be_deleted_filename, "w") as testfile:
            testfile.write("This file should be deleted by the export")
        assert_true(os.path.exists(test_existing_file_that_should_be_deleted_filename))

        test_existing_file_that_should_be_modified_filename = os.path.join(exportdir, "pipes/pipe1.conf.json")
        os.makedirs(os.path.dirname(test_existing_file_that_should_be_modified_filename), exist_ok=True)
        with open(test_existing_file_that_should_be_modified_filename, "w") as testfile:
            testfile.write("This file should be modified by the export")
        assert_true(os.path.exists(test_existing_file_that_should_be_modified_filename))

        if force:
            # The force-flag is set, so the client shouldn't prompt the user for anything
            input_mock = InputGuard
        else:
            input_mock = mock.Mock(return_value="yes")

        with captured_output() as (out, err):
            with mock.patch("builtins.input", new=input_mock):
                sesamclient.main.commands.export.export_cmd(connection, args)

            if not force:
                # Check that the user was asked for a confirmation
                assert_equal(input_mock.call_count, 1,
                             "The client should have asked the user to confirm the modifications to the files!")

            existing_files = []
            for dirpath, dirnames, filenames in os.walk(exportdir):
                for filename in filenames:
                    existing_files.append(os.path.relpath(os.path.join(dirpath, filename), start=exportdir))

            for filename in ["pipes/pipe1.conf.json",
                             "pipes/pipe2.conf.json",
                             "systems/system1.conf.json",
                             "systems/system1.conf.json",
                             "metadata.conf.json"]:
                assert_true(os.path.exists(os.path.join(exportdir, filename)),
                            "The file '%s' should have been created by the export! existing_files:\n%s" % (
                                filename,
                                pprint.pformat(existing_files)))

            assert_false(os.path.exists(test_existing_file_that_should_be_deleted_filename),
                         "The file '%s' should have been deleted by the export!" % (
                             test_existing_file_that_should_be_deleted_filename))

            out = out.getvalue()
            err = err.getvalue()

            assert_not_in("error", out)
            assert_not_in("error", err)

            assert_in("""\
The following files were added:
  %(exportdir)s/metadata.conf.json
  %(exportdir)s/pipes/pipe2.conf.json
  %(exportdir)s/systems/system1.conf.json
  %(exportdir)s/systems/system2.conf.json
""" % {"exportdir": exportdir}, out)
            assert_in("The following files were deleted:\n  %(exportdir)s/testfilethatshouldbedeleted.conf.json" %
                          {"exportdir": exportdir}, out)
            assert_in("The following files were modified:\n  %(exportdir)s/pipes/pipe1.conf.json" %
                          {"exportdir": exportdir}, out)

        # check that the unrelated json-file isn't touched.
        assert_true(os.path.exists(test_existing_non_config_file_that_should_not_be_touched_filename))

        ##################################################################################
        # check that a second run doesn't result in any modified, deleted or added files
        ##################################################################################
        with captured_output() as (out, err):
            with mock.patch("builtins.input",
                            new=InputGuard("The input() method is not supposed to be called in this test, since no "
                                           "changes to the files is supposed to happen in the second export!")):
                args.force = False
                sesamclient.main.commands.export.export_cmd(connection, args)

            out = out.getvalue()
            err = err.getvalue()

            assert_not_in("error", out)
            assert_not_in("error", err)

            assert_in("The existing config-files are up-to-date", out)
            assert_not_in("The following files were added", out)
            assert_not_in("The following files were added", err)
            assert_not_in("The following files were modified", out)
            assert_not_in("The following files were deleted", out)
            assert_not_in("The following files were modified", err)
            assert_not_in("The following files were deleted", err)
