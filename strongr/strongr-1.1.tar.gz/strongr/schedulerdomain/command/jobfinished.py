class JobFinished(object):
    def __init__(self, job_id, ret, retcode):
        self.job_id = job_id
        self.ret = ret
        self.retcode = retcode
