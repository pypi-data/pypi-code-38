from strongr.clouddomain.command import DeployVms, RunJob, DestroyVms, JobFinished

from strongr.core.exception import InvalidParameterException

class CommandFactory:
    """ This factory instantiates command objects to be sent to a cloud commandbus. """

    def newJobFinishedCommand(self, job_id, ret, retcode):
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

    def newDestroyVms(self, names):
        """ Generates a new DestroyVm command

        :param name: The name of the VM to be destroyed
        :type name: string

        :returns: A DestroyVm command object
        :rtype: DestroyVm
        """
        if not isinstance(names, list) or len(names) <= 0:
            raise InvalidParameterException('names is invalid')

        return DestroyVms(names=names)

    def newDeployVms(self, names, profile, cores, ram):
        """ Generates a new DeployVms command

        :param names: A list of names
        :type names: list

        :param profile: the vm profile to be used
        :type profile: string

        :param cores: the number of cores per vm
        :type cores: int

        :param ram: the amount of ram per vm in GiB
        :type ram: int

        :returns: A DeployVms command object
        :rtype: DeployVms
        """

        if not isinstance(names, list) or len(names) <= 0:
            raise InvalidParameterException('names is inavlid')

        if not isinstance(cores, int) or cores <= 0:
            raise InvalidParameterException('cores is inavlid')

        if not isinstance(ram, int) or ram <= 0:
            raise InvalidParameterException('ram is invalid')

        if len(profile) <= 0:
            raise InvalidParameterException('profile is invalid')

        return DeployVms(names, profile, cores, ram)

    def newRunJob(self, host, image, script, job_id, scratch, cores, memory):
        """ Generates a new RunShellCode command

        :param host: where host where te command should be ran
        :type host: string
        :param image: the docker image the script should run under
        :type image: string
        :param script: array of strings, the shellcode to be ran in the docker container
        :type script: list
        :param job_id: the name of the job to be used
        :type job_id: string
        :param scratch: should a scratch be mounted?
        :type scratch: bool
        :param cores: how many cores for this job?
        :type cores: int
        :param memory: how much memory for this job?
        :type memory: int

        :returns: A new RunJob command object
        :rtype: RunJob
        """

        if not len(host) > 0:
            raise InvalidParameterException('host is invalid')
        elif not len(image) > 0:
            raise InvalidParameterException('image is invalid')
        elif not len(script) > 0:
            raise InvalidParameterException('script is invalid')
        elif not len(job_id) > 0:
            raise InvalidParameterException('job_id is invalid')
        elif cores <= 0:
            raise InvalidParameterException('cores is invalid')
        elif memory <= 0:
            raise InvalidParameterException('memory is invalid')

        return RunJob(host=host, image=image, script=script, job_id=job_id, scratch=scratch, cores=cores, memory=memory)
