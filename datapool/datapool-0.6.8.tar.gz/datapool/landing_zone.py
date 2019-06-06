#  encoding: utf-8
from __future__ import absolute_import, division, print_function

import contextlib
import fnmatch
import glob
import os
import shutil
import time
from os.path import exists, join, relpath

from .errors import DataPoolIOError, InvalidLandingZone, InvalidOperationError
from .instance.landing_zone_structure import (lock_file,
                                              ordered_fnmatch_patterns_for_update,
                                              raw_file_pattern_for_script,
                                              scripts_pattern,
                                              source_type_based_scripts_pattern)
from .utils import (copy, here, hexdigest_file, iter_to_list,
                    list_folder_recursive)


def disable_write(path):
    os.chmod(path, 0o444)


def enable_write(path):
    os.chmod(path, 0o744)


def _lock_file_path(root_folder):
    return join(root_folder, lock_file)


def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            return True
        except IOError as e:
            raise DataPoolIOError(
                "coulnd not create folder {}. Please check permissions".format(path)
            )
    return False


@contextlib.contextmanager
def write_lock(landing_zone_folder):
    got_lock = not is_locked(landing_zone_folder)

    lock_file_path = _lock_file_path(landing_zone_folder)
    if got_lock:
        with open(lock_file_path, "w"):
            pass
    try:
        yield got_lock
    finally:
        if got_lock:
            os.remove(lock_file_path)


def is_locked(landing_zone_folder):
    lock_file_path = _lock_file_path(landing_zone_folder)
    return os.path.exists(lock_file_path)


class LandingZone:
    def __init__(self, root_folder):
        self.root_folder = root_folder
        if exists(root_folder):
            self._check_landing_zone()

    def _check_landing_zone(self):
        self._check_start_state()

    @property
    def path_to_start_state(self):
        return self.p(".start_state")

    def _load_start_state_file(self):
        result = {}
        start_state = self.path_to_start_state
        try:
            fh = open(start_state, "r")
            lines = fh.readlines()
        except IOError as e:
            raise InvalidLandingZone(
                "reading from {} failed. reason: {}".format(start_state, e)
            )
        for line in lines:
            path, checksum = line.rstrip().rsplit(" ", 1)
            result[path] = checksum
        return result

    def _check_start_state(self):
        if not exists(self.path_to_start_state):
            raise InvalidLandingZone(
                "landing zone at {} does not contain .start_state file".format(
                    self.root_folder
                )
            )

        missing = []
        for rel_path in self._load_start_state_file():
            path = self.p(rel_path)
            if not exists(path):
                missing.append(path)
        if missing:
            n = len(missing)
            if len(missing) > 5:
                mm = ", ".join(missing[:5])
                msg = "files {}, ... ({} in total) are missing from landing zone".format(
                    mm, n
                )
            else:
                mm = ", ".join(missing)
                msg = "files {} are missing from landing zone".format(mm, n)
            raise InvalidLandingZone(msg)

    def check_if_foreing_is_in_sync(self, folder):
        if not exists(self.path_to_start_state):
            raise InvalidLandingZone(
                "landing zone at {} does not contain .start_state file".format(
                    self.root_folder
                )
            )

        missing = []
        for rel_path in self._load_start_state_file():
            path = os.path.join(folder, rel_path)
            if not exists(path):
                missing.append(path)
        return missing

    @staticmethod
    def create_empty(root_folder):
        lz = LandingZone(root_folder)
        try:
            os.makedirs(root_folder)
        except IOError as e:
            raise InvalidLandingZone(e)
        open(lz.path_to_start_state, "w").close()

    def _remove_from_start_state(self, path):
        files = self._load_start_state_file()
        if path in files:
            del files[path]
        self.update_start_state_file(files.keys())

    @staticmethod
    def create_from(new_landing_zone, existing_landing_zone):
        assert not exists(new_landing_zone)
        lz = LandingZone(new_landing_zone)
        shutil.copytree(existing_landing_zone, lz.root_folder)

        already_exists = list_folder_recursive(
            existing_landing_zone, also_folders=False
        )
        lz.write_start_state_file(already_exists)

        for rel_path in already_exists:
            path = lz.p(rel_path)
            disable_write(path)

        return lz

    def write_start_state_file(self, rel_pathes):
        with open(self.path_to_start_state, "w") as fh:
            for rel_path in rel_pathes:
                full_path = self.p(rel_path)
                print(rel_path, hexdigest_file(full_path), file=fh)
        disable_write(self.path_to_start_state)

    def p(self, relative_path):
        return join(self.root_folder, relative_path)

    def rp(self, path):
        return relpath(path, self.root_folder)

    def add_file(self, path_in_landing_zone, file_path):
        full_path = self.p(path_in_landing_zone)
        folder = os.path.dirname(full_path)
        create_folder_if_not_exists(folder)
        shutil.copy(file_path, folder)

    def overwrite_file(self, path_in_landing_zone, file_path):
        full_path = self.p(path_in_landing_zone)
        shutil.copy(file_path, full_path)

    def remove_file(self, path_in_landing_zone):
        full_path = self.p(path_in_landing_zone)
        os.remove(full_path)
        self._remove_from_start_state(path_in_landing_zone)

    def remove_folder(self, folder, force=False):
        abs_folder = self.p(folder)
        assert os.path.isdir(abs_folder)
        files = list(list_folder_recursive(folder, also_folders=False))
        if files and not force:
            raise InvalidOperationError("folder {} is not empty".format(folder))
        shutil.rmtree(abs_folder)

        for file in files:
            self._remove_from_start_state(self.p(file))

    @iter_to_list
    def check_before_update_operational(self, operational_landing_zone):
        """
        check if saved state is valid:
        check if operational_landing_zone is super set of saved state
        """
        operational_files = set(
            list_folder_recursive(
                operational_landing_zone, also_folders=False, check=True
            )
        )
        saved_start_files = set(self._load_start_state_file().keys())
        if saved_start_files - operational_files:
            raise InvalidLandingZone(
                "development landing zone invalid: {} contains files which "
                "are not in {}".format(
                    self.path_to_start_state, operational_landing_zone
                )
            )
        new_files = self.list_new_files()
        for new_file in sorted(new_files):
            target = join(operational_landing_zone, new_file)
            if os.path.isfile(target):
                if exists(target):
                    yield (
                        "development zone contains new file {} which already exists "
                        "in {}".format(self.p(new_file), operational_landing_zone)
                    )

    @iter_to_list
    def list_all_files(self):
        """lists new files, this are files which are not listed in the start_state_file"""
        for rel_path in list_folder_recursive(self.root_folder):
            yield rel_path

    @iter_to_list
    def list_new_files(self):
        """lists new files, this are files which are not listed in the start_state_file"""
        rel_path_to_hexdigest = self._load_start_state_file()
        for rel_path in list_folder_recursive(self.root_folder):
            if rel_path not in rel_path_to_hexdigest.keys():
                yield rel_path

    @iter_to_list
    def list_new_and_changed_files(self):
        """lists new and edited files. edit change is determined based on hexdigest"""
        yield from self.list_new_files()
        rel_path_to_hexdigest = self._load_start_state_file()
        for rel_path in list_folder_recursive(self.root_folder):
            path = self.p(rel_path)
            tobe = rel_path_to_hexdigest.get(rel_path)
            if tobe is not None:
                if hexdigest_file(path) != tobe:
                    yield rel_path

    def update_operational(
        self, operational_landing_zone, copy_raw, raw_file_patterns, delay=1.1
    ):
        saved_state = self._load_start_state_file()
        files_in_state_file = set(saved_state.keys())
        all_changed_files = set(self.list_new_and_changed_files())

        allowed_changes_in_correct_order, __ = self.separate_allowed_files(
            all_changed_files
        )

        for new_file in allowed_changes_in_correct_order:
            if not copy_raw and any(
                fnmatch.fnmatch(new_file, pattern) for pattern in raw_file_patterns
            ):
                continue
            target = join(operational_landing_zone, new_file)
            if os.path.isdir(self.p(new_file)):  # eg raw_data folder
                if create_folder_if_not_exists(target):
                    yield "created folder", new_file
            else:
                copy(self.p(new_file), target)
                files_in_state_file.add(new_file)
                yield "copied file", new_file
            time.sleep(
                delay
            )  # we sleep so that dispatcher gets the changes in the right order

        self.update_start_state_file(files_in_state_file)

    @staticmethod
    def separate_allowed_files(
        rel_paths,
        ordered_fnmatch_patterns_for_update=ordered_fnmatch_patterns_for_update,
    ):
        left_overs = set(rel_paths)
        allowed_changes_in_correct_order = []
        for pattern in ordered_fnmatch_patterns_for_update():
            for rel_path in sorted(left_overs):
                if fnmatch.fnmatch(rel_path, pattern):
                    left_overs.remove(rel_path)
                    allowed_changes_in_correct_order.append(rel_path)
        return allowed_changes_in_correct_order, sorted(left_overs)

    def update_start_state_file(self, rel_pathes):
        enable_write(self.path_to_start_state)
        self.write_start_state_file(rel_pathes)
        disable_write(self.path_to_start_state)

    def conversion_scripts_and_data(
        self,
        scripts_pattern=scripts_pattern,
        raw_file_pattern_for_script=raw_file_pattern_for_script,
    ):
        script_pattern = self.p(scripts_pattern)
        for script_path in sorted(glob.glob(script_pattern, recursive=True)):
            raw_file_pattern = raw_file_pattern_for_script(script_path)
            raw_file_paths = sorted(glob.glob(raw_file_pattern))
            if not raw_file_paths:
                yield self.rp(script_path), None
            else:
                for raw_file_path in raw_file_paths:
                    yield self.rp(script_path), self.rp(raw_file_path)

    def source_type_based_conversion_scripts_and_data(
        self,
        source_type_based_scripts_pattern=source_type_based_scripts_pattern,
        raw_file_pattern_for_script=raw_file_pattern_for_script,
    ):
        yield from self.conversion_scripts_and_data(
            source_type_based_scripts_pattern, raw_file_pattern_for_script
        )
