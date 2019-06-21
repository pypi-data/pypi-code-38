import os
import logging
import gzip
import time
import copy
from tqdm.auto import tqdm
from .utils import run_command
logger = logging.getLogger(__name__)

try:
    import cPickle as pickle
except ImportError:
    import pickle

CONDOR_JOBSTATUS = {
    0: "Unexpanded",
    1: "Idle",
    2: "Running",
    3: "Removed",
    4: "Completed",
    5: "Held",
    6: "Error",
}

class JobMonitor(object):
    def __init__(self, submitter):
        self.submitter = submitter

    def monitor_jobs(self, sleep=5, request_user_input=True):
        jobid_tasks = self.submitter.jobid_tasks
        ntotal = len(jobid_tasks)

        pbar_run = tqdm(total=ntotal, desc="Running ")
        pbar_fin = tqdm(total=ntotal, desc="Finished")

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

        pbar_run = tqdm(total=ntotal, desc="Running ")
        pbar_fin = tqdm(total=ntotal, desc="Finished")
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
                if state not in [4]:
                    all_queried_jobs.extend(queried_jobs)

            jobs_not_queried = {
                jobid: task
                for jobid, task in self.submitter.jobid_tasks.items()
                if jobid not in all_queried_jobs and jobid not in finished
            }
            finished.extend(self.check_jobs(
                jobs_not_queried, results,
                request_user_input=request_user_input,
            ))

            nremaining = ntotal - len(finished)
            # status 2==Running
            yield job_statuses.get(2,{}), results

        # all jobs finished - final loop
        yield {}, results

    def check_jobs(self, jobid_tasks, results, request_user_input=True):
        finished = []
        for jobid, task in jobid_tasks.items():
            pos = int(os.path.basename(task).split("_")[-1])
            try:
                with gzip.open(os.path.join(task, "result.p.gz"), 'rb') as f:
                    pickle.load(f)
                results[pos] = os.path.join(task, "result.p.gz")
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

        for job in self.submitter.schedd.xquery(
            projection=["ClusterId", "ProcId", "JobStatus"],
        ):
            jobid = job["ClusterId"]
            taskid = job["ProcId"]
            state = job["JobStatus"]
            if not '{}.{}'.format(jobid, taskid) in self.submitter.jobid_tasks.keys():
                continue

            if state not in job_status:
                job_status[state] = []
            job_status[state].append('{}.{}'.format(jobid, taskid))

        return job_status
