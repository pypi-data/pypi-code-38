#
#  job/job.py
#  bxtorch
#
#  Created by Oliver Borchert on May 15, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from abc import ABC, abstractmethod
import argparse
import json

class Job(ABC):
    """
    An abstract class which should be subclassed to provide an implementation
    for a specific job to be run.
    """

    # MARK: Initialization
    def __init__(self, description, arguments):
        """
        Initializes a new job with the given arguments.

        Parameters:
        -----------
        - description: str
            The description of the job on the command line.
        - arguments: list of bxtorch.job._Argument
            The arguments for the job.
        """
        parser = argparse.ArgumentParser(
            description=description
        )
        identifiers = []
        for arg in arguments:
            arg.register_on(parser)
            identifiers.append(arg.identifier)
        self._args = parser.parse_args()
        self._identifiers = identifiers

    # MARK: Instance Methods
    @abstractmethod
    def run(self):
        pass

    def save_config(self, file):
        """
        Saves the configuration parameters passed to this job into the given
        file.

        Parameters:
        -----------
        - file: str
            The file to save the parameters to as JSON.
        """
        config = {i: getattr(self, i) for i in self._identifiers}
        with open(file, 'w+') as f:
            json.dump(config, f)

    # MARK: Special Methods
    def __getattr__(self, name):
        return getattr(self._args, name)
