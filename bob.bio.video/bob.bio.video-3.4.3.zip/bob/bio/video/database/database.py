#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Wed 20 July 14:43:22 CEST 2016

from bob.bio.base.database.file import BioFile
from ..utils import FrameSelector


class VideoBioFile(BioFile):
    def __init__(self, client_id, path, file_id, **kwargs):
        """
        Initializes this File object with an File equivalent for
        VoxForge database.
        """
        super(VideoBioFile, self).__init__(client_id=client_id, path=path, file_id=file_id, **kwargs)

    def load(self, directory=None, extension='.avi', frame_selector=FrameSelector()):
        return frame_selector(self.make_path(directory, extension))
