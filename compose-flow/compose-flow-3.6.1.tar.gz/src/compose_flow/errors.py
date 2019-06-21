class CommandError(Exception):
    """
    Raised when a problem with the command run is encountered
    """


class DockerError(CommandError):
    """
    Raised when a problem running a docker command is encountered
    """


class ErrorMessage(Exception):
    """
    Subclass to print out error message instead of entire stack trace
    """


class AlreadyConnected(ErrorMessage):
    """
    Error raised when already connected to remote
    """


class EnvError(ErrorMessage):
    """
    Error for when environment variables are not found
    """


class NoSuchConfig(Exception):
    """
    Raised when a requested config is not in the docker swarm
    """


class NoSuchProfile(Exception):
    """
    Raised when a requested profile is not listed in dc.yml
    """


class NotConnected(Exception):
    """
    Raised when not connected to a remote host
    """


class NoContainer(Exception):
    """
    Raised when a desired container is not found
    """


class ProfileError(ErrorMessage):
    """
    Raised when there is a problem with a Profile
    """


class RemoteUndefined(ErrorMessage):
    """
    Raised when no remote is defined
    """


class RuntimeEnvError(ErrorMessage):
    """
    Raised when variable substitution at runtime fails
    """


class TagVersionError(Exception):
    """
    Raised when there is a problem running tag-version
    """

    def __init__(
            self, message: str, shell_exception: Exception, tag_version: str = None
    ):
        self.message = message
        self.shell_exception = shell_exception
        self.tag_version = tag_version


class InvalidTargetCluster(ErrorMessage):
    """
    Raised when a profile is provided with the -e flag
    which would target an invalid Rancher cluster,
    such as the local cluster where Rancher itself runs
    """


class MissingManifest(ErrorMessage):
    """
    Raised when a YAML manifest path is specified but not found
    """


class ManifestCheck(ErrorMessage):
    """
    Raised when a rendered YAML manifest fails to pass a check
    """


class MissingKubeContext(ErrorMessage):
    """
    Raised when a kubeconfig context is missing.
    """


class MissingRancherProject(ErrorMessage):
    """
    Raised when no Rancher project is configured or the configured project is not found.
    """


class RancherNamespaceAlreadyExists(ErrorMessage):
    """
    Raised when a namespace is specified for creation but that namespace already exists.
    """


class PodNotFound(ErrorMessage):
    """Raised when no pod is found matching a certain set of criteria."""


class PublishMajorMinorTagsError(ErrorMessage):
    """Raised when publish_with_major_minor_tags is called on an invalid PrivateImage"""
