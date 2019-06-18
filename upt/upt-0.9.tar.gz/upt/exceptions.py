# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.


class InvalidPackageNameError(Exception):
    """Invalid package name or non-existing package."""
    def __init__(self, backend, pkg_name):
        self.backend = backend
        self.pkg_name = pkg_name

    def __str__(self):
        return (f'The package {self.pkg_name} could not be found by backend '
                f'{self.backend}')


class UnhandledFrontendError(Exception):
    """Frontend not supported by backend."""
    def __init__(self, backend, frontend):
        self.backend = backend
        self.frontend = frontend

    def __str__(self):
        return (f'The {self.backend} backend does not work well with the '
                f'{self.frontend} frontend (yet!). Unable to generate a '
                f'package definition.')
