# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import io
import json
import os
import pprint
import sys
import zipfile

import collections

from .. import utils
from ..utils import print_message, exit_with_error
from ...exceptions import ConfigUploadFailed


def _get_humanreadable_filename(filename):
    if not os.path.isabs(filename):
        # The user specified a relative path, so use a relative path when printing the message, too.
        filename = os.path.relpath(filename, start=os.getcwd())
    return filename


def _get_filenames_as_humanreadable_list(filenames):
    result = ""
    for filename in filenames:
        filename = _get_humanreadable_filename(filename)
        result += "  " + filename + "\n"
    return result


def import_cmd(connection, args):
    for config_file_or_folder in args.config_file_or_folder:
        if not os.path.exists(config_file_or_folder):
            exit_with_error("The specified path '%s' doesn't exist!" % (config_file_or_folder,))

    config_files = []
    for config_file_or_folder in args.config_file_or_folder:
        if os.path.isfile(config_file_or_folder):
            config_files.append(config_file_or_folder)
        elif os.path.isdir(config_file_or_folder):
            # Search for all *.conf.json files in the folder
            for dirpath, dirnames, filenames in os.walk(config_file_or_folder):
                for testfilename in filenames:
                    if utils.is_valid_configfile_name(testfilename):
                        if utils.is_valid_but_deprecated_configfile_name(testfilename):
                            print_message(("Warning: The config filename '%s' is deprecated. "
                                           "Configfiles should have names on the form '*.conf.json'.") % (
                                os.path.join(dirpath, testfilename),))
                        testfilename = os.path.join(dirpath, testfilename)
                        config_files.append(testfilename)
        else:
            exit_with_error("The specified path '%s' is neither a file nor a folder!" % (config_file_or_folder,))

    if not config_files:
        exit_with_error("No '*.conf.json' configfiles were found!")

    config_files.sort()

    configentity_id2filename = collections.OrderedDict()

    for config_filename in config_files:
        humanreadable_config_filename = _get_humanreadable_filename(config_filename)
        with open(config_filename, "rt") as config_file:
            config_file_content = None
            try:
                config_file_content = json.load(config_file)
            except Exception as e:
                exit_with_error("Failed to parse the content of the file '%s': %s" % (
                                humanreadable_config_filename, e))

            if not isinstance(config_file_content, list):
                config_file_content = [config_file_content]

            for configentity in config_file_content:
                if "_id" not in configentity:
                    exit_with_error("The file '%s' contains an configentity that doesn't have an '_id' attribute: %s"
                                    % (humanreadable_config_filename, configentity))

                # Check that the ids are unique
                configentity_id = configentity["_id"]
                if configentity_id in configentity_id2filename:
                    otherfilename = configentity_id2filename[configentity_id]
                    if otherfilename == config_filename:
                        exit_with_error("The file '%s' contains two config entities with the id '%s'! "
                                        "The '_id'-values must be unique!"
                                        % (humanreadable_config_filename, configentity_id))
                    else:
                        exit_with_error("The config entity id '%s' was found in both in '%s' and in '%s'! "
                                        "The '_id'-values must be unique!"
                                        % (configentity_id, _get_humanreadable_filename(otherfilename),
                                           humanreadable_config_filename))

                configentity_id2filename[configentity_id] = config_filename

    def print_validation_errors(validation_errors, file=None):
        # validation_errors is a list on this format:
        # [{'config-errors': [{'elements': '$', 'level': 'error',
        #            'msg': "Unknown component id 'longrunningdummytask' of type 'task'"}],
        #      'is-valid-config': False,
        #      'json-schema': {'properties': {'type': {'enum': ['pipe', 'system:sqlite', 'system:sesam-node', ... },
        #      'posted-config': {'_id': 'task:longrunningdummytask1', 'schedule_interval': 60000, ...}}]
        for validation_error in validation_errors:
            parse_error = False
            posted_config = validation_error.get("posted-config")
            if not isinstance(posted_config, dict):
                parse_error = True
                origin_configentity_id = "*unknown*"
                origin_filename = "*unknown*"
            else:
                origin_configentity_id = posted_config.get("_id") or "*unknown*"
                origin_filename = configentity_id2filename.get(origin_configentity_id)
                if origin_filename:
                    origin_filename = _get_humanreadable_filename(origin_filename)
                else:
                    origin_filename = "*unknown*"

            print_message("Issues with the config entity '%s' from the file '%s':" % (origin_configentity_id,
                                                                                      origin_filename, ),
                          file=file,
                          indent=4)
            for error in validation_error["config-errors"]:
                level = error["level"]
                msg = error["msg"]
                elements = error.get("elements")
                elements_term = ""
                if elements:
                    elements_term = " (path: %s)" % (elements,)
                print_message("%s: %s%s" % (level, msg, elements_term),
                              file=file,
                              indent=8)

            if args.verbose or parse_error:
                print_message("Raw validation error:", file=file, indent=6)
                print_message(pprint.pformat(validation_error), file=file, indent=8)

    print_message("Read %d config entities from these config-files:" % (len(configentity_id2filename), ))
    print_message(_get_filenames_as_humanreadable_list(config_files))

    if args.dry_run:
        print_message("\nThe '--dry-run' parameter was specified, so no changes will be done to the configuration. ")
    else:
        if len(config_files) == 1:
            # There is just the one config-file, so just upload that
            config_to_upload = config_files[0]
        else:
            # There is more than one configfile, so upload them all in a ziparchive
            zipped_config = io.BytesIO()
            ziparchive = zipfile.ZipFile(zipped_config, "w")
            for config_filename in config_files:
                humanreadable_config_filename = _get_humanreadable_filename(config_filename)
                ziparchive.write(config_filename, humanreadable_config_filename)
            ziparchive.close()
            config_to_upload = zipped_config

        try:
            response = connection.upload_config(config_to_upload,
                                                force=args.force)
            response_validation_errors = response["validation_errors"]
            if response_validation_errors:
                print_message("The configuration was applied, but these errors/warnings were detected:")
                print_validation_errors(response_validation_errors)

        except ConfigUploadFailed as e:
            response = e.parsed_response
            response_validation_errors = response["validation_errors"]
            if response_validation_errors:
                print_message("Failed to apply the configuration. These errors were detected:", file=sys.stderr)
                print_validation_errors(response_validation_errors, file=sys.stderr)
                exit_with_error(None)
