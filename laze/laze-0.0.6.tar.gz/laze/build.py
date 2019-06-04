#!/usr/bin/env python3

import copy
import os
import re
import subprocess
import sys
import time
import yaml

import click

from laze.util import uniquify, load_dict, listify, split
from laze.common import determine_dirs, rel_start_dir, dump_args, write_ninja_build_args_file
from laze.deepcopy import deepcopy
import laze.mtimelog

@click.command()
@click.option("--project-file", "-f", type=click.STRING, envvar="LAZE_PROJECT_FILE")
@click.option("--project-root", "-r", type=click.STRING, envvar="LAZE_PROJECT_ROOT")
@click.option(
    "--build-dir", "-B", type=click.STRING, default="build", envvar="LAZE_BUILDDIR"
)
@click.option("--builders", "-b", type=click.STRING, envvar="LAZE_BUILDERS", multiple=True)
@click.option("--tool", "-t", type=click.STRING, envvar="LAZE_TOOL")
@click.option("--no-update", "-n", type=click.BOOL, is_flag=True, envvar="LAZE_NO_UPDATE")
@click.option("--global/--local", "-g/-l", "_global", default=False, envvar="LAZE_GLOBAL")
@click.option("--verbose", "-v", type=click.BOOL, is_flag=True, envvar="LAZE_VERBOSE")

@click.option("--clean", "-c", type=click.BOOL, is_flag=True, envvar="LAZE_CLEAN")
@click.option("--jobs", "-j", type=click.INT, envvar="LAZE_JOBS")
@click.option("--keep-going", "-k", type=click.INT, default=1, envvar="LAZE_JOBS")
@click.option("--dump-data", "-d", is_flag=True, default=False, envvar="LAZE_DUMP_DATA")
@click.argument("targets", nargs=-1)
def build(project_file, project_root, build_dir, tool, targets, builders, no_update, _global, verbose, clean, jobs, keep_going, dump_data):

    targets = split(targets)
    builders = split(builders)

    generate_args = {
            "project_file": project_file,
            "project_root": project_root,
            "build_dir": build_dir,
            "builders": builders,
            "_global": _global,
            "apps": targets,
            "dump_data": dump_data,
            }

    start_dir, build_dir, project_root, project_file = determine_dirs(generate_args)

    ninja_build_file = os.path.join(build_dir, "build.ninja")
    ninja_build_args_file = os.path.join(build_dir, "build-args.ninja")

    laze_binary = sys.argv[0]
    os.chdir(project_root)

    targets = list(targets)
    builders = list(builders)
    if builders:
        builder_set = set(builders)
    if targets:
        target_set = set(targets)

    try:
        if laze.mtimelog.read_log(os.path.join(build_dir, "laze-files.mp"), True) == False:
            print("laze: buildfiles changed")
            laze_args = None
        else:
            laze_args = load_dict((build_dir, "laze-args"))

            if laze_args != generate_args:
                laze_args = None

    except FileNotFoundError as e:
        print("laze-args not found or laze build file removed")
        laze_args = None

    if laze_args == None:
        print("laze: (re-)generating ninja build files")
        laze_args_file = dump_args(build_dir, generate_args)

        ninja_build_file = os.path.join(build_dir, "build.ninja")
        ninja_build_args_file = os.path.join(build_dir, "build-args.ninja")
        ninja_build_file_deps = ninja_build_file + ".d"
        if not os.path.isfile(ninja_build_args_file):
            write_ninja_build_args_file(ninja_build_args_file, ninja_build_file, ninja_build_file_deps, laze_args_file, build_dir)

        try:
            subprocess.check_call(["ninja", "-f", ninja_build_args_file, "relaze"], cwd=project_root)
        except subprocess.CalledProcessError:
            print("laze: re-generation of build files failed.")
            sys.exit(1)

    if tool:
        app_target_map = {}

    #
    # target filtering / selection
    #
    # unless "--global" is specified, all builder / app combinations
    # will be filtered by what's defined in the folder from where
    # laze was launched.
    #
    if _global:
        ninja_targets = targets
        print("laze: global mode")
    else:
        _rel_start_dir = rel_start_dir(start_dir, project_root)

        print("laze: local mode in \"%s\"" % _rel_start_dir)

        try:
            laze_local = load_dict((build_dir, "laze-app-per-folder"))[_rel_start_dir]
        except KeyError:
            print("laze: no targets defined in \"%s\" that match %s" % (_rel_start_dir, targets or "all"))
            sys.exit(1)

        ninja_targets = []
        for app, builder_target in laze_local.items():
            for builder, target in builder_target.items():
                if builders:
                    if not builder in builder_set:
                        continue
                if targets:
                    if not app in targets:
                        continue
                print("laze: building %s for %s" % (app, builder))
                ninja_targets.append(target)
                if tool:
                    app_target_map[target] = (app, builder)

        targets = ninja_targets

    app_builder_tool_target_list = []
    if tool:
        if not ninja_targets:
            print("laze: tool specified but no target given (or locally available).")
            sys.exit(1)

        if len(ninja_targets) > 1:
            print("laze: multiple targets for tool %s specified.")
            print("laze: if this is what you want, add --multi-tool / -m")
            sys.exit(1)

        tools = load_dict((build_dir, "laze-tools"))

        for ninja_target in ninja_targets:
            target_tools = tools.get(ninja_target, {})
            app, builder = app_target_map[ninja_target]


            tool_obj = target_tools.get(tool)
            if not tool_obj:
                print("laze: target %s builder %s doesn't support tool %s" % (ninja_target, builder, tool))
                sys.exit(1)

            app_builder_tool_target_list.append((app, builder, ninja_target, tool_obj))

    if targets and not ninja_targets:
        print("no ninja targets, passing through")
        ninja_targets = targets

    ninja_extra_args = []
    if verbose:
        ninja_extra_args += ["-v"]
    if jobs is not None:
        ninja_extra_args += ["-j", str(jobs)]
    if keep_going is not None:
        ninja_extra_args += ["-k", str(keep_going)]

    try:
        subprocess.check_call(["ninja", "-f", ninja_build_file] + ninja_extra_args + ninja_targets, cwd=project_root)
    except subprocess.CalledProcessError:
        sys.exit(1)

    for app, builder, ninja_target, tool in app_builder_tool_target_list:
        for cmd in tool["cmd"]:
            try:
                subprocess.check_call(cmd, shell=True, cwd=project_root)
            except subprocess.CalledProcessError:
                print("laze: error executing \"%s\" (tool=%s, target=%s, builder=%s)" % (cmd, tool, target, builder))
                sys.exit(1)
