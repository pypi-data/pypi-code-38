class CommitHashNotFound(Exception):
    """
    Exception thrown when commit hash not found
    """

    def __init__(self, repo, version):
        """
        Inits CommitHashNotFound

        :param repo: url of the repository
        :param version: version of the archive
        """
        self.repo = repo
        self.version = version

    def __str__(self):
        return "Commit hash not found: {repo}@{version}".format(
            repo=self.repo,
            version=self.version)


class ArchiveNotFound(Exception):
    """
    Exception thrown when archive not found
    """

    def __init__(self, repo, version):
        """
        Inits ArchiveNotFound

        :param repo: url of the repository
        :param version: version of the archive
        """
        self.repo = repo
        self.version = version

    def __str__(self):
        return "Archive not found: {repo}@{version}".format(
            repo=self.repo,
            version=self.version)


class RepoNotFound(Exception):
    """
    Exception thrown when repository not found
    """

    def __init__(self, repo):
        """
        Inits RepoNotFound

        :param repo: url of the repository
        """
        self.repo = repo

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Repository not found: {repo}".format(repo=self.repo)


class ValidationError(Exception):
    """
    Exception thrown when authentication error with source
    """

    def __init__(self, errors):
        """
        Inits ValidationError

        :param errors: errors as dict
        """
        self.errors = errors

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Validation errors: {errors}".format(errors=self.errors)


class AuthenticationError(Exception):
    """
    Exception thrown when authentication error with source
    """

    def __init__(self, url):
        """
        Inits AuthenticationError

        :param url: url of the server
        """
        self.url = url

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Authentication error with: {url}".format(url=self.url)


class HttpError(Exception):
    """
    Exception thrown when the return code is not 2xx
    """

    def __init__(self, url, code=None):
        """
        Inits HttpError

        :param url: url of the request
        """
        self.url = url
        self.code = code

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Request could not complete for: {url}".format(url=self.url)


class DirectoryDoesNotExist(Exception):
    """
    Exception thrown when directory does not exist
    """

    def __init__(self, directory):
        """
        Inits DirectoryDoesNotExist

        :param directory: path of non existing directory
        """
        self.directory = directory

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Directory does not exist: {directory}".format(
            directory=self.directory
        )


class DirectoryNotEmpty(Exception):
    """
    Exception thrown when directory not empty
    """

    def __init__(self, directory):
        """
        Inits DirectoryNotEmpty

        :param directory: path of not empty directory
        """
        self.directory = directory

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Directory not empty: {directory}".format(
            directory=self.directory
        )


class ParserError(Exception):
    """
    Exception thrown when parsing does not complete
    """

    def __init__(self, file, error):
        """
        Inits ParserError

        :param file: path to file which has errors
        :param error: error message of parser
        """
        self.file = file
        self.error = error

    def __str__(self):
        """
        Get error message

        :return: Error message as string
        """
        return "Parsing failed for {file} due to {error}".format(
            file=self.file,
            error=self.error)
