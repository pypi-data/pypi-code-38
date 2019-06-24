import os
import re


class RegexFileList(object):
    """
    A list of regexes for matching files.

    Examples:

        Get all javascript files in a directory::

            from ievv_opensource.utils import ievvbuildstatic

            filelist = ievvbuildstatic.utils.RegexFileList(include_patterns=['^.*?\.js$'])
            filelist.get_files_as_list('/path/to/javascript/sources/')

        Exclude some files::

            filelist = ievvbuildstatic.utils.RegexFileList(
                include_patterns=['^.*\.js$'],
                exclude_patterns=['^.*\.spec\.js$']
            )
            filelist.get_files_as_list('/path/to/javascript/sources/')
    """
    def __init__(self, include_patterns=None,
                 exclude_patterns=None):
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []

    def matches_include_pattern(self, relative_filepath):
        for pattern in self.include_patterns:
            if re.match(pattern, relative_filepath):
                return True
        return False

    def matches_exclude_pattern(self, relative_filepath):
        for pattern in self.exclude_patterns:
            if re.match(pattern, relative_filepath):
                return True
        return False

    def matches_pattern(self, relative_filepath):
        return (self.matches_include_pattern(relative_filepath) and
                not self.matches_exclude_pattern(relative_filepath))

    def get_files_as_list(self, rootfolder, absolute_paths=False):
        matched_relative_filepaths = []
        for root, dirs, files in os.walk(rootfolder):
            for filename in files:
                filepath = os.path.abspath(os.path.join(root, filename))
                relative_filepath = os.path.relpath(filepath, rootfolder)
                if self.matches_pattern(relative_filepath):
                    if absolute_paths:
                        matched_relative_filepaths.append(filepath)
                    else:
                        matched_relative_filepaths.append(relative_filepath)

        return matched_relative_filepaths

    def prettyformat_patterns(self):
        return 'RegexFileList(include={!r}, exclude={!r})'.format(
            self.include_patterns, self.exclude_patterns)
