

class DeployVException(Exception):
    msg = None

    def __init__(self, message, *args, **kwargs):
        self.msg = message
        super(DeployVException, self).__init__(message, *args, **kwargs)

    def __str__(self):
        return self.msg


class NotRunning(DeployVException):
    def __init__(self, container):
        super(NotRunning, self).__init__('Container {} is not running'.format(container))


class NoSuchContainer(DeployVException):
    def __init__(self, container):
        super(NoSuchContainer, self).__init__('No such container or id: {}'.format(container))


class FileNotFoundInContainer(DeployVException):
    def __init__(self, container, filename):
        super(FileNotFoundInContainer, self).__init__('File {0} not found in the {1} container'
                                                      .format(filename, container))


class ErrorPort(DeployVException):
    def __init__(self, message):
        super(ErrorPort, self).__init__(message)


class BuildError(DeployVException):
    def __init__(self, message):
        super(BuildError, self).__init__(message)


class NoSuchBranch(DeployVException):
    def __init__(self, branch, repo):
        super(NoSuchBranch, self).__init__(('Could not find the specified remote branch'
                                            ' {branch} in repo: {repo}').format(branch=branch,
                                                                                repo=repo))


class MethodNotImplemented(DeployVException):
    def __init__(self, message):
        super(MethodNotImplemented, self).__init__(message)


class NoSuchImage(DeployVException):
    def __init__(self, image_name):
        super(NoSuchImage, self).__init__('Image not found: {image}'
                                          .format(image=image_name))


class DumpError(DeployVException):
    def __init__(self, message):
        super(DumpError, self).__init__(message)


class GracefulExit(DeployVException):
    def __init__(self, message):
        super(GracefulExit, self).__init__(message)


class CommandError(DeployVException):
    def __init__(self, cmd, error):
        super(CommandError, self).__init__(('Failed to execute the command {cmd}: {error}'
                                            .format(cmd=cmd, error=error)))


class SupervisorStatusError(DeployVException):
    def __init__(self, message):
        super(SupervisorStatusError, self).__init__(message)


class ClientAPIError(DeployVException):
    def __init__(self, message):
        super(ClientAPIError, self).__init__(message)


class ParameterError(DeployVException):
    def __init__(self, message):
        super(ParameterError, self).__init__(message)
