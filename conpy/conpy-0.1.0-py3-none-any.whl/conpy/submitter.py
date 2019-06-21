import os
import re
import logging
import time
from builtins import input
from multiprocessing import Pool
from tqdm.auto import tqdm
import htcondor

from .utils import run_command

logger = logging.getLogger(__name__)

class CondorTaskSubmitter(object):
    regex_submit = re.compile('submitted to cluster (?P<clusterid>[0-9]+)')
    def __init__(self, job_options):
        self.job_options = job_options
        self.jobid_tasks = {}

        self.schedd = htcondor.Schedd()

    def submit_tasks(
        self, tasks, start=0, dryrun=False, request_user_input=False,
        quiet=False,
    ):
        if tasks is None or len(tasks) <= 0:
            return

        curdir = os.getcwd()
        njobs = len(tasks)
        executable = run_command("which conpy_worker.sh")[0].rstrip("\n")

        job_opts = self.job_options
        if request_user_input:
            job_opts = input(
                "Using job options '{}'. Insert new options (comma delimited "
                "key=val) or nothing to use the default\n:".format(job_opts)
            )
            job_opts = job_opts if job_opts != "" else self.job_options
        job_opts = [
            kv.split("=")
            for kv in job_opts.split(",")
            if kv != ""
        ]

        wd = os.path.dirname(tasks[0])
        job = [
            ("executable", executable),
            ("pkg_index", "$(ProcId) + {}".format(start)),
            ("Iwd", os.path.join(wd, "task_$INT(pkg_index,%05d)")),
            ("log", os.path.join(wd, "log.$(ClusterId).txt")),
            ("output", "stdout.$(ClusterId).$(ProcId).txt"),
            ("error", "stderr.$(ClusterId).$(ProcId).txt"),
            ("getenv", "true"),
            ("transfer_input_files", "task.p.gz"),
            ("should_transfer_files", "YES"),
            ("when_to_transfer_output", "ON_EXIT"),
        ]
        input_ = (
            "\n".join(["{} = {}".format(k, v) for k, v in job+job_opts])
            + "\nqueue {}".format(len(tasks))
        )

        if not dryrun:
            out, err = run_command("condor_submit", input_=input_)
            match = self.regex_submit.search(out)
            if match is None:
                logger.error("Malformed condor_submit config:\n{}".format(input_))
                assert RuntimeError
            jobid = int(match.group("clusterid"))
            logger.info('Submitted {}.{}-{}:1'.format(jobid, start, len(tasks)+start-1))
        else:
            print(input_)
            jobid = 0

        for aid in range(njobs):
            self.jobid_tasks['{}.{}'.format(jobid, aid+start)] = tasks[aid]

    def killall(self):
        jids = []
        for jobid, _ in self.jobid_tasks.items():
            tjid = jobid.split(".")[0]
            if tjid not in jids:
                jids.append(tjid)
        run_command("condor_rm {}".format(" ".join(jids)))

class MPTaskSubmitter(object):
    def submit_tasks(self, tasks, ncores=4, sleep=1, quiet=False):
        if tasks is None or len(tasks) <= 0:
            return

        results = []
        pool = Pool(processes=ncores)
        pbar = tqdm(total=len(tasks), desc="Finished", disable=quiet)

        try:
            for task in tasks:
                results.append(
                    pool.apply_async(task['task'], task['args'], task['kwargs'])
                )

            nremaining = len(tasks)
            while nremaining > 0:
                nfinished = sum(r.ready() for r in results)
                nremaining = len(tasks) - nfinished
                pbar.n = nfinished
                pbar.refresh()
                time.sleep(sleep)

            results = [r.get() for r in results]
        except KeyboardInterrupt:
            pool.terminate()
            results = []
        pool.close()
        pbar.close()
        print("")

        return results
