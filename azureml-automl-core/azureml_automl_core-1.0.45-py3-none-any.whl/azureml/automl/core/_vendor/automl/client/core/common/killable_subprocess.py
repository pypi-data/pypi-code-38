# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to kill process trees."""
from typing import Dict, List
import os
import re
import subprocess


# Returns pids of all descendents of root_process_pid. Doesn't include the
# root_process_pid.
# Returns None if root_process_pid < 0
def get_all_descendents_in_linux(root_process_pid):
    """
    Get all child processes.

    :param root_process_pid: pid of the root process
    :return:
    """
    if root_process_pid < 0:
        return None

    # First we are getting all processes' pids and ppids. [0] is for reading
    # the stdout
    # Setting universal_newlines=True for default string encoding.
    output = subprocess.check_output(['ps', '-eo', 'pid,ppid'],
                                     universal_newlines=True)
    all_process_list = output.splitlines()
    # Skipping the first line, as that is the column header, precisely, PID,
    # PPID.
    all_process_list = all_process_list[1:]

    # A dictionary in which a key is a ppid, and the value is a list of
    # children's pids.
    parent_to_child_dict = {}   # type: Dict[int, List[int]]
    for item in all_process_list:
        # Removing leading, trailing and multiple spaces
        if len(item) > 0:
            item = re.sub(' +', ' ', item.strip())
            pid_string, ppid_string = item.split(" ")
            pid_int = int(pid_string)
            ppid_int = int(ppid_string)

            if ppid_int in parent_to_child_dict:
                parent_to_child_dict[ppid_int].append(pid_int)
            else:
                child_list = [pid_int]
                parent_to_child_dict[ppid_int] = child_list

    # Parent to child dictionary creation complete.

    # We just iteratively adding each pid's children to the output list.
    # We start from root_process_pid, and continue iteratively from there,
    # thereby performing a breadth-first traversal of a tree.

    all_descendant_list = []    # type: List[int]
    child_list = []

    # If root_process_pid is not in parent_to_child_dict, then it means
    # root_process_pid has no children
    if root_process_pid in parent_to_child_dict:
        child_list = parent_to_child_dict[root_process_pid]

    while len(child_list) > 0:
        # Adding the current chidren to the output list.
        all_descendant_list = all_descendant_list + child_list

        next_list = []  # type: List[int]
        for child_pid in child_list:
            if child_pid in parent_to_child_dict:
                next_list = next_list + parent_to_child_dict[child_pid]

        child_list = next_list

    # All descendants computation complete
    return all_descendant_list


def kill_ignoring_dead_process_in_linux(kill_arguments):
    """
    Kill a process in linux ignoring the errors if the specified process has already died.

    :param kill_arguments: arguments to pass to the subprocess
    :return:
    """
    try:
        subprocess.check_call(kill_arguments, stdout=subprocess.DEVNULL)
    except OSError as e:
        if not e.strerror == "No such file or directory":
            raise e


def kill_process_tree_in_linux(root_pid, is_sudo=False):
    """
    Kill the process tree for linux like environments.

    :param root_pid: the pid of the root process of the process tree
    :param is_sudo: flag whether the root process was started using sudo,
    false otherwise.
    :return:
    """
    # Computing the list of all descendants.
    all_descendants = get_all_descendents_in_linux(root_pid)

    # All processes to kill, parent and all its descendants.
    all_processes = all_descendants

    # The logic here handles the case if the parent process was not started
    # using
    # sudo, but some of its children were started using sudo.
    for pid in all_processes:
        try:
            if is_sudo:
                kill_ignoring_dead_process_in_linux(
                    ["sudo", "kill", "-SIGKILL", str(pid)])
            else:
                kill_ignoring_dead_process_in_linux(
                    ["kill", "-SIGKILL", str(pid)])
        except BaseException as e:
            # Catching all exceptions here in the case a process was not
            # successfully killed.
            # Printing a warning and continuing with the killing of other
            # processes.
            try:
                # 0 is a no-op for the pid
                os.kill(pid, 0)
            except OSError:
                pass
            else:
                print(
                    "WARNING: Unable to kill process with pid={}. The "
                    "exception is={}".format(
                        pid, e))
    if is_sudo:
        kill_ignoring_dead_process_in_linux(
            ["sudo", "kill", "-SIGKILL", str(root_pid)])
    else:
        kill_ignoring_dead_process_in_linux(
            ["kill", "-SIGKILL", str(root_pid)])


def kill_process_tree_in_windows(root_pid):
    """
    Kill the subprocess tree in Windows.

    :param root_pid: the pid of the root process of the process tree
    :return:
    """
    try:
        subprocess.check_call(
            ["TASKKILL", "/F", "/T", "/PID", str(root_pid)],
            stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        # 128 is the taskkill return code in windows for "no such process",
        # which happens when a process has already died.
        if not e.returncode == 128:
            raise e
