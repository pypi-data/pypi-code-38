# coding: utf-8

from __future__ import unicode_literals

"""
A runnable script for launching rockets (a command-line interface to queue_launcher.py)
"""

from argparse import ArgumentParser
import os
import sys
import time

try:
    import fabric

    if int(fabric.__version__.split(".")[0]) < 2:
        raise ImportError
except ImportError:
    HAS_FABRIC = False
else:
    HAS_FABRIC = True

from fireworks.fw_config import (
    QUEUEADAPTER_LOC,
    CONFIG_FILE_DIR,
    FWORKER_LOC,
    LAUNCHPAD_LOC,
)
from fireworks.core.fworker import FWorker
from fireworks.queue.queue_launcher import launch_rocket_to_queue
from fireworks.utilities.fw_serializers import load_object_from_file

from hilde import DEFAULT_CONFIG_FILE
from hilde.fireworks.combined_launcher import rapidfire
from hilde.fireworks.launchpad import LaunchPadHilde as LaunchPad
from hilde.settings import Settings
from hilde.tasks import fireworks as fw

settings = Settings()
remote_setup = settings.remote_setup if "remote_setup" in settings else {}
remote_host_auth = settings.remote_host_auth if "remote_host_auth" in settings else {}
remote_queue_param = (
    settings.remote_queue_param if "remote_queue_param" in settings else {}
)
launch_params = settings.launch_params if "launch_params" in settings else {}

fw_defaults = {
    "launch_dir": (remote_setup.launch_dir if "launch_dir" in remote_setup else "."),
    "remote_host": (remote_setup.remote_host if "remote_host" in remote_setup else None),
    "remote_config_dir": (
        remote_setup.remote_config_dir if "remote_config_dir" in remote_setup else ["~/.fireworks"]
    ),
    "remote_user": (
        remote_host_auth.remote_user if "remote_user" in remote_host_auth else None
    ),
    "remote_password": (
        remote_host_auth.remote_password
        if "remote_password" in remote_host_auth
        else None
    ),
    "njobs_queue": (
        remote_queue_param.njobs_queue if "njobs_queue" in remote_queue_param else 0
    ),
    "njobs_block": (
        remote_queue_param.njobs_block
        if "njobs_block" in remote_queue_param
        else 500
    ),
    "nlaunches": (launch_params.nlaunches if "nlaunches" in launch_params else 0),
    "sleep_time": (launch_params.sleep_time if "sleep_time" in launch_params else None),
    "tasks2queue": (
        launch_params.tasks2queue if "tasks2queue" in launch_params else []
    ),
}


def claunch():
    """Defines the command claunch_hidle"""
    m_description = (
        "This program is used to submit jobs to a queueing system. "
        "Details of the job and queue interaction are handled by the "
        'mandatory queue adapter file parameter. The "rapidfire" option '
        "can be used to maintain a certain number of jobs in the queue by "
        "specifying the n_loops parameter to a large number. If n_loops is "
        "set to 1 (default) the queue launcher will quit after submitting "
        "the desired number of jobs. For more help on rapid fire options, "
        "use qlauncher.py rapidfire -h"
    )

    parser = ArgumentParser(description=m_description)

    parser.add_argument(
        "-rh",
        "--remote_host",
        default=fw_defaults["remote_host"],
        nargs="*",
        help="Remote host to exec qlaunch. Right now, "
        "only supports running from a config dir.",
    )
    parser.add_argument(
        "-rc",
        "--remote_config_dir",
        nargs="+",
        default=fw_defaults["remote_config_dir"],
        help="Remote config dir location(s). Defaults to "
        "~/.fireworks. You can specify multiple "
        "locations if you have multiple configurations "
        "on the same cluster e.g., multiple queues or FireWorkers. "
        "Note that this may have to come before the -ru"
        "argument (or other single arg) options as "
        "argparse may not be able to find "
        "the find command while it consumes args.",
    )
    parser.add_argument(
        "-ru",
        "--remote_user",
        default=fw_defaults["remote_user"],
        help="Username to login to remote host.",
    )
    parser.add_argument(
        "-rp",
        "--remote_password",
        default=fw_defaults["remote_password"],
        help="Password for remote host (if necessary). For "
        "best operation, it is recommended that you do "
        "passwordless ssh.",
    )
    parser.add_argument(
        "-rsh",
        "--remote_shell",
        help="Shell command to use on remote host for running submission.",
        default="/bin/bash -l -c",
    )

    parser.add_argument(
        "-rs",
        "--remote_setup",
        help="Setup the remote config dir using files in "
        "the directory specified by -c.",
        action="store_true",
    )
    parser.add_argument(
        "-rgss", "--gss_auth", help="use gss_api authorization", action="store_true"
    )
    parser.add_argument(
        "-rro",
        "--remote_recover_offline",
        action="store_true",
        help="recover offline jobs from remote host",
    )
    parser.add_argument(
        "-d",
        "--daemon",
        help="Daemon mode. Command is repeated every x "
        "seconds. Defaults to 0, which means non-daemon "
        "mode.",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--launch_dir", help="directory to launch the job / rapid-fire", default="."
    )
    parser.add_argument(
        "--logdir", help="path to a directory for logging", default=None
    )
    parser.add_argument(
        "--loglvl", help="level to print log messages", default="CRITICAL", type=str
    )
    parser.add_argument(
        "-s", "--silencer", help="shortcut to mute log messages", action="store_true"
    )
    parser.add_argument("-r", "--reserve", help="reserve a fw", action="store_true")
    parser.add_argument("-l", "--launchpad_file", help="path to launchpad file")
    parser.add_argument("-w", "--fworker_file", help="path to fworker file")
    parser.add_argument("-q", "--queueadapter_file", help="path to queueadapter file")
    parser.add_argument(
        "-c",
        "--config_dir",
        help="path to a directory containing the config file (used if -l, -w, -q unspecified)",
        default=CONFIG_FILE_DIR,
    )
    parser.add_argument(
        "-fm",
        "--fill_mode",
        help="launch queue submissions even when there is nothing to run",
        action="store_true",
    )
    parser.add_argument(
        "-ids",
        "--firework_ids",
        nargs="+",
        help="A list of specific ids to run",
        type=int,
        default=[],
    )
    parser.add_argument(
        "-wf",
        "--wflow",
        nargs="+",
        help="A list of the root fw ids of a workflow",
        type=int,
        default=[],
    )
    parser.add_argument(
        "-m",
        "--maxjobs_queue",
        help="maximum jobs to keep in queue for this user",
        default=fw_defaults["njobs_queue"],
        type=int,
    )
    parser.add_argument(
        "-b",
        "--maxjobs_block",
        help="maximum jobs to put in a block",
        default=fw_defaults["njobs_block"],
        type=int,
    )
    parser.add_argument(
        "--nlaunches",
        help='num_launches (int or "infinite"; default 0 is all jobs in DB)',
        default=fw_defaults["nlaunches"],
    )
    parser.add_argument(
        "--timeout",
        help="timeout (secs) after which to quit (default None)",
        default=None,
        type=int,
    )
    parser.add_argument(
        "--sleep",
        help="sleep time between loops",
        default=fw_defaults["sleep_time"],
        type=int,
    )
    parser.add_argument(
        "-tq",
        "--tasks_to_queue",
        nargs="+",
        type=str,
        default=fw_defaults["tasks2queue"],
        help="list of tasks to be sent to the queue",
    )

    try:
        import argcomplete

        argcomplete.autocomplete(parser)
        # This supports bash autocompletion. To enable this, pip install
        # argcomplete, activate global completion, or add
        #      eval "$(register-python-argcomplete qlaunch)"
        # into your .bash_profile or .bashrc
    except ImportError:
        pass

    args = parser.parse_args()
    print(args)
    if not args.launchpad_file and os.path.exists(
        os.path.join(args.config_dir, "my_launchpad.yaml")
    ):
        args.launchpad_file = os.path.join(args.config_dir, "my_launchpad.yaml")
    elif not args.launchpad_file:
        args.launchpad_file = LAUNCHPAD_LOC

    if not args.fworker_file and os.path.exists(
        os.path.join(args.config_dir, "my_fworker.yaml")
    ):
        args.fworker_file = os.path.join(args.config_dir, "my_fworker.yaml")
    elif not args.fworker_file:
        args.fworker_file = FWORKER_LOC

    launchpad = (
        LaunchPad.from_file(args.launchpad_file)
        if args.launchpad_file
        else LaunchPad(strm_lvl=args.loglvl)
    )
    fworker = FWorker.from_file(args.fworker_file) if args.fworker_file else FWorker()

    if args.remote_host == "localhost":
        if not args.queueadapter_file and os.path.exists(
            os.path.join(args.config_dir, "my_qadapter.yaml")
        ):
            args.queueadapter_file = os.path.join(args.config_dir, "my_qadapter.yaml")
        elif not args.queueadapter_file:
            args.queueadapter_file = QUEUEADAPTER_LOC
        queueadapter = load_object_from_file(args.queueadapter_file)
    else:
        queueadapter = None

    rapidfire(
        launchpad,
        fworker=fworker,
        qadapter=queueadapter,
        launch_dir=args.launch_dir,
        nlaunches=args.nlaunches,
        njobs_queue=args.maxjobs_queue,
        njobs_block=args.maxjobs_block,
        sleep_time=args.sleep,
        reserve=args.reserve,
        strm_lvl=args.loglvl,
        timeout=args.timeout,
        fill_mode=args.fill_mode,
        fw_ids=args.firework_ids,
        wflow=args.wflow,
        tasks2queue=args.tasks_to_queue,
        gss_auth=args.gss_auth,
        remote_host=args.remote_host,
        remote_config_dir=args.remote_config_dir,
        remote_user=args.remote_user,
        remote_password=args.remote_password,
        remote_shell=args.remote_shell,
        remote_recover_offline=args.remote_recover_offline,
        daemon=args.daemon,
    )


if __name__ == "__main__":
    claunch()
