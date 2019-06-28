import cray.jobs as jobs
import cray.config as config
import cray.s3 as cs3

# import cray.sqs as csqs
import json


def stdout(jobID, taskID):
    return jobs.job_file_prefix(jobID, "logs/{}_out.txt".format(taskID))


def stderr(jobID, taskID):
    return jobs.job_file_prefix(jobID, "logs/{}_err.txt".format(taskID))


def has_executed(jobID, taskID):
    return cs3.file_exists(config.bucket(), stdout(jobID, taskID))


def logs(jobID, taskID):
    return {
        "out": cs3.load_file(config.bucket(), stdout(jobID, taskID)),
        "err": cs3.load_file(config.bucket(), stderr(jobID, taskID)),
    }


def count_executed(jobID):
    return int(
        cs3.count_files(config.bucket(), jobs.job_file_prefix(jobID, "logs/")) / 2
    )


def get_job_tasks(job):
    cfg = jobs.get_job_config(job)
    return (json.dumps(t) for t in cfg["targets"]["raw"])


def count(jobID):
    return len(list(get_job_tasks(jobID)))
