from strongr.schedulerdomain.command import ScheduleJob, RunEnqueuedJobs,\
                                            StartJobOnVm, CheckJobsRunning,\
                                            EnsureMinAmountOfNodes, ScaleOut,\
                                            JobFinished, VmDestroyed,\
                                            VmReady, VmCreated, VmNew, CheckScaling,\
                                            CleanupNodes, ScaleIn, LogStats, CleanupOldJobs

from strongr.core.exception import InvalidParameterException

# try-except for py 2 / 3 compatibility
try:
    basestring
except NameError:
    basestring = str

class CommandFactory:
    """ This factory instantiates command objects to be sent to a scheduler commandbus. """

    def newCleanupOldJobs(self):
        return CleanupOldJobs()

    def newLogStats(self):
        """Generates a new LogStats command"""
        return LogStats()

    def newCleanupNodes(self):
        """ Generates a new Cleanupnodes command

        :return: A CleanupNodes command object
        :rtype: CleanupNodes
        """
        return CleanupNodes()

    def newCheckScaling(self):
        """ Generates a new CheckScaling command

        :returns: A CheckScaling command object
        :rtype: CheckScaling
        """
        return CheckScaling()

    def newVmNew(self, vm_id, cores, ram):
        """ Generates a new VmNew command

        :param vm_id: An identifier token for the job
        :type vm_id: string

        :param cores: the amount of cores assigned to the vm
        :type cores: int

        :param ram: the amount of ram in GiB assigned to the vm
        :type ram: int

        :returns: A VmNew command object
        :rtype: VmNew
        """
        if not isinstance(vm_id, basestring) or len(vm_id.strip()) == 0:
            raise InvalidParameterException('vm_id is invalid')
        elif not isinstance(cores, int) or cores <= 0:
            raise InvalidParameterException('cores is invalid')
        elif not isinstance(ram, int) or ram <= 0:
            raise InvalidParameterException('ram is invalid')

        return VmNew(vm_id, cores, ram)

    def newVmReady(self, vm_id):
        """ Generates a new VmReady command

        :param vm_id: An identifier token for the job
        :type job_id: string

        :returns: A VmReady command object
        :rtype: VmReady
        """
        if not isinstance(vm_id, basestring) or len(vm_id.strip()) == 0:
            raise InvalidParameterException('job_id is invalid')
        return VmReady(vm_id)

    def newVmDestroyed(self, vm_id):
        """ Generates a new VmDestroyed command

        :param vm_id: An identifier token for the job
        :type vm_id: string

        :returns: A VmDestroyed command object
        :rtype: VmDestroyed
        """
        if not isinstance(vm_id, basestring) or len(vm_id.strip()) == 0:
            raise InvalidParameterException('vm_id is invalid')
        return VmDestroyed(vm_id)

    def newVmCreated(self, vm_id):
        """ Generates a new VmCreated command

        :param vm_id: An identifier token for the job
        :type vm_id: string

        :returns: A VmCreated command object
        :rtype: VmCreated
        """
        if not isinstance(vm_id, basestring) or len(vm_id.strip()) == 0:
            raise InvalidParameterException('vm_id is invalid')
        return VmCreated(vm_id)

    def newJobFinished(self, job_id, ret, retcode):
        """ Generates a new JobFinished command

        :param job_id: An identifier token for the job
        :type job_id: string

        :param ret: Usually the stdout of the job
        :type ret: string

        :param retcode: The exit code of the job
        :type ret: int

        :returns: A JobFinished command object
        :rtype: JobFinished
        """
        if not isinstance(job_id, basestring) or len(job_id.strip()) == 0:
            raise InvalidParameterException('jid is invalid')
        elif not isinstance(ret, basestring) or len(ret.strip()) == 0:
            raise InvalidParameterException('ret is invalid')
        elif not isinstance(retcode, int):
            raise InvalidParameterException('retcode is invalid')

        return JobFinished(job_id, ret, retcode)

    def newScaleIn(self):
        return ScaleIn()

    def newScaleOut(self, cores, ram):
        if not cores > 0:
            raise InvalidParameterException('Cores should be higher than 0')
        elif not ram > 0:
            raise InvalidParameterException('Ram should be higher than 0')

        return ScaleOut(cores, ram)

    def newEnsureMinAmountOfNodes(self):
        return EnsureMinAmountOfNodes()

    def newRunEnqueuedJobs(self):
        """ Generates a new RunEnqueuedJobs command

        :returns: A RunEnqueuedJobs command object
        :rtype: RunEnqueuedJobs
        """
        return RunEnqueuedJobs()

    def newScheduleJobCommand(self, image, script, job_id, scratch, cores, memory, secrets):
        """ Generates a new ScheduleTask command

        :param image: the docker image used for running the job
        :type image: string

        :param script: a list of strings with shellcode
        :type script: list

        :param job_id: the jobs id (max 32 characters)
        :type job_id: string

        :param scratch: should a scratch volume be mounted?
        :type scratch: bool

        :param cores: The amount of cores in the VM
        :type cores: int

        :param ram: The amount of RAM in GiB in the VM
        :type ram: int

        :param secrets: List of keys of secrets that should be injected into the process
        :type secrets: list

        :returns: A ScheduleJob command object
        :rtype: ScheduleJob
        """

        if not len(image) > 0:
            raise InvalidParameterException('image is invalid')
        elif not len(script) > 0:
            raise InvalidParameterException('script is invalid')
        elif not len(job_id) > 0:
            raise InvalidParameterException('job_id is invalid')
        elif cores <= 0:
            raise InvalidParameterException('cores is invalid')
        elif memory <= 0:
            raise InvalidParameterException('memory is invalid')
        elif not isinstance(secrets, list):
            raise InvalidParameterException('List of secrets is invalid')

        return ScheduleJob(image=image, script=script, job_id=job_id, scratch=scratch, cores=cores, memory=memory, secrets=secrets)

    def newStartJobOnVm(self, vm_id, job_id):
        """ Generates a new StartJobOnVm command

        :param vm_id: the node name
        :type vm_id: string
        :param job_id: the taskid to be started
        :type job_id: string

        :returns: A StartJobOnVm command object
        :rtype: StartJobOnVm
        """
        if not len(vm_id) > 0:
            raise InvalidParameterException('node is invalid')
        elif not len(job_id) > 0:
            raise InvalidParameterException('taskid is invalid')

        return StartJobOnVm(vm_id=vm_id, job_id=job_id)

    def newCheckJobsRunning(self):
        """ Generates a new CheckJobsRunning command

        :returns: A CheckJobRunning command object
        :rtype: CheckJobsRunning
        """

        return CheckJobsRunning()
