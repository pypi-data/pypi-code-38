#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Factory for returning a Archive backend.

New Backends must be added to the
__share_classes list and that class needs to be imported in

Call the factory like the following:
FACTORY = ArchiveBackendFactory()
BACKEND = FACTORY.get_backend_archive(type, prefix)
"""


class ArchiveBackendFactory(object):
    """Factory Class for Archive Backends."""

    share_classes = {}

    def get_backend_archive(self, name, prefix):
        """Method for creating an instance of the backend archive."""
        self.load_backend_archive(name)
        backend_class = self.share_classes.get(name.lower(), None)

        if backend_class:
            return backend_class(prefix)
        raise NotImplementedError(
            'The requested Archive Backend has not been implemented'
        )

    def load_backend_archive(self, name):
        """Method for loading in the correct backend type.

        Only want to load backend type being used.
        """
        if name == 'hpss':  # pragma: no cover licensing issues for testing
            from .hpss.archive import HpssBackendArchive
            self.share_classes = {'hpss': HpssBackendArchive}
        elif name == 'posix':
            from .posix.archive import PosixBackendArchive
            self.share_classes = {'posix': PosixBackendArchive}
        elif name == 'hsmsideband':  # pragma: no cover don't have example database yet
            from .oracle_hsm_sideband.archive import HsmSidebandBackendArchive
            self.share_classes = {'hsmsideband': HsmSidebandBackendArchive}
