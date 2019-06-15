import os

from .git import Git
from .parser import Parser


class Reposync:
    def __init__(
        self,
        file="repositories.yaml",
        method="https",
        update=False,
        verbose=False,
        concurrent=False,
    ):
        self.__file = file
        self.__method = method
        self.__update = update
        self.__verbose = verbose
        self.__concurrent = concurrent

        parser = Parser()
        self.__tree = parser.parse(self.__file)

        config = self.build_config()
        self.__git = Git(config)

    def clone(self):
        self.__tree.execute(self.__git.clone, concurrent=self.__concurrent)

    def pull(self):
        self.__tree.execute(self.__git.pull, concurrent=self.__concurrent)

    # private

    def build_config(self):
        return dict(
            gopath=os.getenv("GOPATH"),
            method=self.__method,
            update=self.__update,
            verbose=self.__verbose,
        )
