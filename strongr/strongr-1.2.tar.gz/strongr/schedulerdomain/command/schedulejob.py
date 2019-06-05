class ScheduleJob:
    def __init__(self, image, script, job_id, scratch, cores, memory, secrets):
        self.image = image
        self.script = script
        self.job_id = job_id
        self.scratch = scratch
        self.cores = cores
        self.memory = memory
        self.secrets = secrets
