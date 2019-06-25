# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.


import collections
import io
import json
import os
import zipfile

from .. import utils


def export_cmd(connection, args):
    original_exportdir = args.exportdir or "."

    exportdir = os.path.abspath(original_exportdir)

    files_that_will_be_deleted = []  # filenames
    files_that_will_be_added = collections.OrderedDict()  # filename => filecontent
    files_that_will_be_modified = collections.OrderedDict()   # filename => new filecontent
    os.makedirs(exportdir, exist_ok=True)

    source_files = collections.OrderedDict()  # filename => filecontent
    if args.expand:
        if args.export_filename:
            utils.exit_with_error("The '--expand' and '--export_filename' are mutually exclusive! They can't both be specified.")

        for dirpath, dirnames, filenames in os.walk(exportdir):
            for filename in filenames:
                if not utils.is_valid_configfile_name(filename):
                    continue
                files_that_will_be_deleted.append(os.path.abspath(os.path.join(dirpath, filename)))

        config_as_zip = connection.get_config_as_zip()
        config_zipfile = zipfile.ZipFile(io.BytesIO(config_as_zip))
        for filename in config_zipfile.namelist():
            source_file_content = config_zipfile.read(filename)
            source_files[filename] = source_file_content
    else:
        # export everything together as one file
        source_filename = args.export_filename or "sesam.conf.json"
        assert utils.is_valid_configfile_name(source_filename)
        source_files[source_filename] = connection.get_config_as_json_string().encode("utf-8")

        target_filename = os.path.abspath(os.path.join(exportdir, source_filename))
        if os.path.exists(target_filename):
            files_that_will_be_deleted.append(target_filename)

    for source_filename, source_file_content in source_files.items():
        target_filename = os.path.abspath(os.path.join(exportdir, source_filename))
        if target_filename in files_that_will_be_deleted:
            files_that_will_be_deleted.remove(target_filename)
            # check if the file will be modified
            with open(target_filename, "rb") as target_file:
                target_file_content = target_file.read()
                if target_file_content != source_file_content:
                    # the raw file-content has been changed, but if both files are valid json and the parsed
                    # content is identical we ignore the change, since the files are functionally identical.
                    try:
                        source_file_content_parsed = json.loads(source_file_content.decode("utf-8"))
                        target_file_content_parsed = json.loads(target_file_content.decode("utf-8"))
                        is_changed = target_file_content_parsed != source_file_content_parsed
                    except:
                        # failed to parse at least one of the files, so we will assume the files are functionally
                        # different.
                        is_changed = True
                    if is_changed:
                        files_that_will_be_modified[target_filename] = source_file_content
        else:
            files_that_will_be_added[target_filename] = source_file_content

    def get_filenames_as_humanreadable_list(filenames):
        result = ""
        for filename in filenames:
            if not os.path.isabs(original_exportdir):
                # The user specified a relative path, so use a relative path when printing the message, too.
                filename = os.path.relpath(filename, start=os.getcwd())
            result += "  " + filename + "\n"
        return result

    def get_filelist_output(verb):
        result = ""
        if files_that_will_be_deleted:
            result += "The following files %s deleted:\n" % (verb,)
            result += get_filenames_as_humanreadable_list(files_that_will_be_deleted)

        if files_that_will_be_modified:
            result += "The following files %s modified:\n" % (verb,)
            result += get_filenames_as_humanreadable_list(files_that_will_be_modified)

        if files_that_will_be_added:
            result += "The following files %s added:\n" % (verb,)
            result += get_filenames_as_humanreadable_list(files_that_will_be_added)
        return result

    if files_that_will_be_deleted or files_that_will_be_modified or files_that_will_be_added:
        if args.dry_run:
            utils.print_message("The '--dry-run' parameter was specified, so no files will be touched. "
                                "Otherwise, the following changes would have been made:")
            utils.print_message(get_filelist_output("would have been"))
        else:
            if not args.force:
                prompt = get_filelist_output("will be")

                prompt += "Are you sure you want to do this (yes/no)"

                answer = input(prompt)
                if answer.lower() not in ("y", "yes"):
                    utils.print_message("Exiting without making any changes.")
                    return

            for filename, filecontent in files_that_will_be_added.items():
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "wb") as targetfile:
                    targetfile.write(filecontent)

            for filename, filecontent in files_that_will_be_modified.items():
                with open(filename, "wb") as targetfile:
                    targetfile.write(filecontent)

            for filename in files_that_will_be_deleted:
                os.remove(filename)

            utils.print_message(get_filelist_output("were"))

    else:
        utils.print_message("The existing config-files are up-to-date.")
