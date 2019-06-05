class RunJob:
    def __init__(self, host, image, script, job_id, scratch, cores, memory):
        self.host = host
        self.image = image
        self.script = script
        self.job_id = job_id
        self.scratch = scratch
        self.cores = cores
        self.memory = memory
