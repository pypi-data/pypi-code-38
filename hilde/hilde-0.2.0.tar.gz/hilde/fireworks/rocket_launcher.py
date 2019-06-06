"""This module contains a modified rapid-fire mode."""
# coding: utf-8
from __future__ import unicode_literals
from datetime import datetime
import os
import time


from fireworks.fw_config import RAPIDFIRE_SLEEP_SECS
from fireworks.core.rocket_launcher import launch_rocket, get_fworker
from fireworks.utilities.fw_utilities import (
    get_fw_logger,
    create_datestamp_dir,
    log_multi,
    redirect_local,
)

from .combined_launcher import get_ordred_fw_ids

__author__ = "Anubhav Jain, Modified by Thomas Purcell Nov 2, 2018"
__copyright__ = "Copyright 2013, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Anubhav Jain"
__email__ = "ajain@lbl.gov"
__date__ = "Feb 22, 2013"


def rapidfire(
    launchpad,
    fworker=None,
    m_dir=None,
    nlaunches=0,
    max_loops=-1,
    sleep_time=None,
    strm_lvl="CRITICAL",
    timeout=None,
    local_redirect=False,
    pdb_on_exception=False,
    fw_ids=None,
    wflow_id=None,
):
    """
    Keeps running Rockets in m_dir until we reach an error. Automatically creates subdirectories
    for each Rocket. Usually stops when we run out of FireWorks from the LaunchPad.

    Args:
        launchpad (LaunchPad)
        fworker (FWorker object)
        m_dir (str): the directory in which to loop Rocket running
        nlaunches (int): 0 means 'until completion', -1 or "infinite" means to loop until max_loops
        max_loops (int): maximum number of loops (default -1 is infinite)
        sleep_time (int): secs to sleep between rapidfire loop iterations
        strm_lvl (str): level at which to output logs to stdout
        timeout (int): of seconds after which to stop the rapidfire process
        local_redirect (bool): redirect standard input and output to local file
        pdb_on_exception (bool): if set to True,
                                 python will start the debugger on a firework exception
        fw_ids (list of ints): list of FireWorks to run
        wflow_id (list of ints): list of ids of the root nodes of a workflow
    """
    if fw_ids and len(fw_ids) != nlaunches:
        print("WARNING: Setting nlaunches to the length of fw_ids.")
        nlaunches = len(fw_ids)
    sleep_time = sleep_time if sleep_time else RAPIDFIRE_SLEEP_SECS
    curdir = m_dir if m_dir else os.getcwd()
    l_logger = get_fw_logger(
        "rocket.launcher", l_dir=launchpad.get_logdir(), stream_level=strm_lvl
    )
    nlaunches = -1 if nlaunches == "infinite" else int(nlaunches)
    fworker = get_fworker(fworker)

    num_launched = 0
    start_time = datetime.now()
    num_loops = 0

    def time_ok():
        """ Determines if the rapidfire run has timed out"""
        return (
            timeout is None or (datetime.now() - start_time).total_seconds() < timeout
        )

    while num_loops != max_loops and time_ok():
        skip_check = False  # this is used to speed operation
        if wflow_id:
            wflow = launchpad.get_wf_by_fw_id(wflow_id[0])
            nlaunches = len(wflow.fws)
            fw_ids = get_ordred_fw_ids(wflow)
        while (skip_check or launchpad.run_exists(fworker, ids=fw_ids)) and time_ok():
            os.chdir(curdir)
            launcher_dir = create_datestamp_dir(curdir, l_logger, prefix="launcher_")
            os.chdir(launcher_dir)
            if local_redirect:
                with redirect_local():
                    if fw_ids or wflow_id:
                        rocket_ran = launch_rocket(
                            launchpad,
                            fworker,
                            strm_lvl=strm_lvl,
                            pdb_on_exception=pdb_on_exception,
                            fw_id=fw_ids[num_launched],
                        )
                    else:
                        rocket_ran = launch_rocket(
                            launchpad,
                            fworker,
                            strm_lvl=strm_lvl,
                            pdb_on_exception=pdb_on_exception,
                        )
            else:
                if fw_ids or wflow_id:
                    rocket_ran = launch_rocket(
                        launchpad,
                        fworker,
                        strm_lvl=strm_lvl,
                        pdb_on_exception=pdb_on_exception,
                        fw_id=fw_ids[num_launched],
                    )
                else:
                    rocket_ran = launch_rocket(
                        launchpad,
                        fworker,
                        strm_lvl=strm_lvl,
                        pdb_on_exception=pdb_on_exception,
                    )
            if wflow_id:
                wflow = launchpad.get_wf_by_fw_id(wflow_id[0])
                nlaunches = len(wflow.fws)
                fw_ids = get_ordred_fw_ids(wflow)
            if rocket_ran:
                num_launched += 1
            elif not os.listdir(launcher_dir):
                # remove the empty shell of a directory
                os.chdir(curdir)
                os.rmdir(launcher_dir)
            if nlaunches > 0 and num_launched == nlaunches:
                break
            if launchpad.run_exists(fworker, ids=fw_ids):
                skip_check = True  # don't wait, pull the next FW right away
            else:
                # add a small amount of buffer breathing time for DB to refresh in case we have a
                # dynamic WF
                time.sleep(0.15)
                skip_check = False
        if nlaunches == 0:
            if not launchpad.future_run_exists(fworker, ids=fw_ids):
                break
        elif num_launched == nlaunches:
            break
        log_multi(l_logger, "Sleeping for {} secs".format(sleep_time))
        time.sleep(sleep_time)
        num_loops += 1
        log_multi(l_logger, "Checking for FWs to run...")
    os.chdir(curdir)
