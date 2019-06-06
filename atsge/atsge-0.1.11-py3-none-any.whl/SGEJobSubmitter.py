#!/usr/bin/env python
import os, sys
import subprocess
import collections
import time
import textwrap
import getpass
import re
import gzip
import pickle
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

import alphatwirl
from alphatwirl.concurrently.condor.exec_util import try_executing_until_succeed, compose_shortened_command_for_logging

##__________________________________________________________________||
SGE_JOBSTATUS = {
    1: "Running",
    2: "Pending",
    3: "Suspended",
    4: "Error",
    5: "Deleted",
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

##__________________________________________________________________||
class SGEJobSubmitter(object):
    def __init__(self, queue="hep.q", walltime=7200, vmem=6,
                 vmem_dict={}, walltime_dict={}):
        self.job_desc_template = "qsub -N {name} -t 1-{njobs}:1 -o /dev/null -e /dev/null -cwd -V -q {queue} -l h_rt={walltime} -l h_vmem={vmem}G {job_script}"
        self.clusterprocids_outstanding = [ ]
        self.clusterprocids_finished = [ ]
        self.queue = queue
        self.walltime = walltime # 1h
        self.vmem = vmem
        self.wallmax = 172800 # 48h
        self.vmemmax = 32
        self.vmem_dict = vmem_dict
        self.walltime_dict = walltime_dict

    def run(self, workingArea, package_index):
        return self.run_multiple(workingArea, [package_index])[0]

    def run_multiple(self, workingArea, package_indices):

        if not package_indices:
            return [ ]

        cwd = os.getcwd()
        os.chdir(workingArea.path)

        package_paths = [workingArea.package_relpath(i) for i in package_indices]
        resultdir_basenames = [os.path.splitext(p)[0] for p in package_paths]
        resultdir_basenames = [os.path.splitext(n)[0] for n in resultdir_basenames]
        resultdirs = [os.path.join('results', n) for n in resultdir_basenames]

        for d in resultdirs:
            alphatwirl.mkdir_p(d)

        # Get list of task names
        task_name = None
        for p in package_paths:
            with gzip.open(p, 'rb') as f:
                package = pickle.load(f)
            if hasattr(package.task, 'progressbar_label'):
                if task_name is None:
                    task_name = package.task.progressbar_label
                elif package.task.progressbar_label != task_name:
                    logger = logging.getLogger(__name__)
                    logger.warning("Task name changed somehow")
            else:
                task_name = "task"

        job_desc = self.job_desc_template.format(
            name = task_name,
            job_script = 'job_script.sh',
            njobs = len(package_paths),
            queue = self.queue,
            walltime = self.walltime_dict[task_name] if task_name in self.walltime_dict else self.walltime,
            vmem = self.vmem_dict[task_name] if task_name in self.vmem_dict else self.vmem,
        )

        s = "#!/bin/bash\n\nulimit -c 0\n\n"
        for idx, package_path in enumerate(package_paths):
            s += "cmd1[{index}]='cd {path}'\n".format(
                index=idx+1,
                path=resultdirs[idx],
            )
            s += "cmd2[{index}]='python {job_script} {args}'\n".format(
                index=idx+1,
                job_script="../../run.py",
                args=package_path,
            )
        s += "\n${{cmd1[$SGE_TASK_ID]}} > {out} 2> {err}\n".format(
            out="stdout.txt",
            err="stderr.txt",
        )
        s += "${{cmd2[$SGE_TASK_ID]}} >> {out} 2>> {err}".format(
            out="stdout.txt",
            err="stderr.txt",
        )
        with open("job_script.sh",'w') as f:
            f.write(s)

        proc = subprocess.Popen(
            job_desc.split(),
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()

        regex = re.compile("Your job-array (\d+).1-(\d+):1 \(\"{}\"\) has been submitted".format(task_name))
        try:
            njobs = int(regex.search(stdout).groups()[1])
            clusterid = regex.search(stdout).groups()[0]
            # e.g., '2448770'
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(stdout)
            logger.error(stderr)
            raise AttributeError(e)

        #change_job_priority([clusterid], 10) ## need to make configurable

        procid = ['{}'.format(i+1) for i in range(njobs)]
        # e.g., ['1', '2', '3', '4']

        clusterprocids = ['{}.{}'.format(clusterid, i) for i in procid]
        # e.g., ['2448770.1', '2448770.2', '2448770.3', '2448770.4']

        self.clusterprocids_outstanding.extend(clusterprocids)

        os.chdir(cwd)

        return clusterprocids

    def poll(self):
        """check if the jobs are running and return a list of cluster IDs for
        finished jobs

        """

        clusterids = clusterprocids2clusterids(self.clusterprocids_outstanding)
        clusterprocid_status_list = query_status_for(clusterids)
        # e.g. [('2448775.1',2), ('2448775.2',2), ('2448775.3',2), ('2448775.4',2), ('2448769.1',6), ('2448769.2',6), ('2448769.3',6)


        if clusterprocid_status_list:
            clusterprocids, statuses = zip(*clusterprocid_status_list)
        else:
            clusterprocids, statuses = (), ()

        clusterprocids_finished = [i for i in self.clusterprocids_outstanding if i not in clusterprocids]
        self.clusterprocids_finished.extend(clusterprocids_finished)
        self.clusterprocids_outstanding[:] = clusterprocids

        # logging
        counter = collections.Counter(statuses)
        messages = [ ]
        if counter:
            messages.append(', '.join(['{}: {}'.format(SGE_JOBSTATUS[k], counter[k]) for k in counter.keys()]))
        if self.clusterprocids_finished:
            messages.append('Finished {}'.format(len(self.clusterprocids_finished)))
        logger = logging.getLogger(__name__)
        logger.info(', '.join(messages))

        return clusterprocids_finished

    def wait(self):
        """wait until all jobs finish and return a list of cluster IDs
        """
        sleep = 5
        while self.clusterprocids_outstanding:
            self.poll()
            time.sleep(sleep)
        return self.clusterprocids_finished

    def failed_runids(self, runids):
        # remove failed clusterprocids from self.clusterprocids_finished
        # so that len(self.clusterprocids_finished)) becomes the number
        # of the successfully finished jobs
        for i in runids:
            try:
                self.clusterprocids_finished.remove(i)
            except ValueError:
                pass

    def terminate(self):
        clusterids = clusterprocids2clusterids(self.clusterprocids_outstanding)
        ids_split = split_ids(clusterids)
        statuses = [ ]
        for ids_sub in ids_split:
            procargs = ['qdel'] + ids_sub
            command_display = compose_shortened_command_for_logging(procargs)
            logger = logging.getLogger(__name__)
            logger.debug('execute: {}'.format(command_display))
            proc = subprocess.Popen(
                procargs,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()

##__________________________________________________________________||
def clusterprocids2clusterids(clusterprocids):
    return list(set([i.split('.')[0] for i in clusterprocids]))

##__________________________________________________________________||
def query_status_for(ids, n_at_a_time=500):

    ids_split = split_ids(ids, n=n_at_a_time)
    ret = [ ]
    for ids_sub in ids_split:
        procargs = ['qstat','-g','d']
        result = try_executing_until_succeed(procargs)
        # e.g.,
        # job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID 
        # -----------------------------------------------------------------------------------------------------------------
        # 2448775 0.12500 job.sh     sdb15        qw    02/14/2018 04:15:59                                    1 1
        # 2448775 0.12500 job.sh     sdb15        qw    02/14/2018 04:15:59                                    1 2
        # 2448775 0.12500 job.sh     sdb15        qw    02/14/2018 04:15:59                                    1 3
        # 2448775 0.12500 job.sh     sdb15        qw    02/14/2018 04:15:59                                    1 4
        ret.extend([
            ["{}.{}".format(l.split()[0], l.split()[-1]), SGE_JOBSTATE_CODES[l.split()[4]]]
            for l in result
            if "job-ID" not in l and "-----" not in l and l.split()[0] in ids
        ])
        # e.g. [('2448775.1',2), ('2448775.2',2), ('2448775.3',2), ('2448775.4',2), ('2448769.1',6), ('2448769.2',6), ('2448769.3',6)

    return ret

##__________________________________________________________________||
def split_ids(ids, n=500):
    # e.g.,
    # ids = [3158174', '3158175', '3158176', '3158177', '3158178']
    # n = 2
    # return [[3158174', '3158175'], ['3158176', '3158177'], ['3158178']]
    return [ids[i:(i + n)] for i in range(0, len(ids), n)]

##__________________________________________________________________||
