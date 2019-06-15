import git

from py_buildsystem.common import logger

from py_buildsystem.Step.Step import Step


class StepGit(Step):

    def __init__(self, step_config, step_name):
        self.configuration = step_config
        self._check_config()

        self.step_name = step_name

    def _check_config(self):
        try:
            self.__repository_location = self.configuration["repo_location"]
        except KeyError:
            logger.error("No repository location given")
            exit(-1)

        try:
            self.__clone_destination = self.configuration["destination"]
        except KeyError:
            logger.error("No clone destination given")
            exit(-1)

        try:
            self.__branch = self.configuration["branch"]
        except KeyError:
            logger.debug("Pulling master branch")
            self.__branch = "master"

    def get_type(self):
        return "git"

    def perform(self):
        logger.info("Cloning " + self.__repository_location + " -- " + self.__branch + " to " + self.__clone_destination)
        try:
            git.Repo.clone_from(self.__repository_location, self.__clone_destination, branch=self.__branch)
        except git.exc.GitCommandError:
            pass
