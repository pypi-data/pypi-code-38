import os
import logging
import lz4.frame
import time
import copy
from tqdm import tqdm
from .utils import run_command
logger = logging.getLogger(__name__)

try:
    import cPickle as pickle
except ImportError:
    import pickle

SGE_JOBSTATUS = {
    1: "Running",
    2: "Pending",
    3: "Suspended",
    4: "Error",
    5: "Deleted",
    6: "Finished",
}

# https://gist.github.com/cmaureir/4fa2d34bc9a1bd194af1
SGE_JOBSTATE_CODES = {
    # Running
    "r": 1,
    "t": 1,
    "Rr": 1,
    "Rt": 1,

    # Pending
    "qw": 2,
    "hqw": 2,
    "hRwq": 2,

    # Suspended
    "s": 3, "ts": 3,
    "S": 3, "tS": 3,
    "T": 3, "tT": 3,
    "Rs": 3, "Rts":3, "RS":3, "RtS":3, "RT":3, "RtT": 3,

    # Error
    "Eqw": 4, "Ehqw": 4, "EhRqw": 4,

    # Deleted
    "dr": 5, "dt": 5, "dRr": 5, "ds": 5, "dS": 5, "dT": 5, "dRs": 5, "dRS": 5, "dRT": 5,
}

class JobMonitor(object):
    def __init__(self, submitter):
        self.submitter = submitter

    def monitor_jobs(self, sleep=5, request_user_input=True):
        jobid_tasks = self.submitter.jobid_tasks
        ntotal = len(jobid_tasks)

        pbar_run = tqdm(total=ntotal, desc="Running ", dynamic_ncols=True)
        pbar_fin = tqdm(total=ntotal, desc="Finished", dynamic_ncols=True)

        for running, results in self.return_finished_jobs(request_user_input=request_user_input):
            pbar_run.n = len(running)
            pbar_fin.n = len([r for r  in results if r is not None])
            pbar_run.refresh()
            pbar_fin.refresh()
            time.sleep(sleep)

        pbar_run.close()
        pbar_fin.close()
        print("")
        return results

    def request_jobs(self, sleep=5, request_user_input=True):
        jobid_tasks = self.submitter.jobid_tasks
        ntotal = len(jobid_tasks)

        pbar_run = tqdm(total=ntotal, desc="Running ", dynamic_ncols=True)
        pbar_fin = tqdm(total=ntotal, desc="Finished", dynamic_ncols=True)
        try:
            for running, results in self.return_finished_jobs(request_user_input=request_user_input):
                pbar_run.n = len(running)
                pbar_fin.n = len([r for r  in results if r is not None])
                pbar_run.refresh()
                pbar_fin.refresh()
                time.sleep(sleep)
                yield results
        except KeyboardInterrupt as e:
            self.submitter.killall()

        pbar_run.close()
        pbar_fin.close()
        print("")
        yield results

    def return_finished_jobs(self, request_user_input=True):
        jobid_tasks = self.submitter.jobid_tasks
        ntotal = len(jobid_tasks)
        nremaining = ntotal

        finished, results = [], [None]*ntotal

        while nremaining>0:
            job_statuses = self.query_jobs()
            all_queried_jobs = []
            for state, queried_jobs in job_statuses.items():
                all_queried_jobs.extend(queried_jobs)

            jobs_not_queried = {
                jobid: task
                for jobid, task in self.submitter.jobid_tasks.items()
                if jobid not in all_queried_jobs and jobid not in finished
            }
            finished.extend(self.check_jobs(jobs_not_queried, results, request_user_input=request_user_input))

            nremaining = ntotal - len(finished)
            yield job_statuses.get(1, {}), results

        # all jobs finished - final loop
        yield {}, results

    def check_jobs(self, jobid_tasks, results, request_user_input=True):
        finished = []
        for jobid, task in jobid_tasks.items():
            pos = int(os.path.basename(task).split("_")[-1])
            try:
                with lz4.frame.open(os.path.join(task, "result.p.lz4"), 'rb') as f:
                    pickle.load(f)
                results[pos] = os.path.join(task, "result.p.lz4")
                finished.append(jobid)
            except (IOError, EOFError, pickle.UnpicklingError) as e:
                logger.info('Resubmitting {}: {}'.format(jobid, task))
                self.submitter.submit_tasks(
                    [task], start=pos, request_user_input=request_user_input,
                )
                self.submitter.jobid_tasks.pop(jobid)

        return finished

    def query_jobs(self):
        job_status = {}
        out, err = run_command("qstat -g d")

        for l in out.decode('utf-8').splitlines():
            if l.startswith("job-ID") or l.startswith("-----"):
                continue
            ws = l.split()
            jobid = ws[0]
            taskid = int(ws[-1])

            if not '{}.{}'.format(jobid, taskid) in self.submitter.jobid_tasks.keys():
                continue

            state = SGE_JOBSTATE_CODES[ws[4]]
            if state not in job_status:
                job_status[state] = []
            job_status[state].append('{}.{}'.format(jobid, taskid))

        return job_status
