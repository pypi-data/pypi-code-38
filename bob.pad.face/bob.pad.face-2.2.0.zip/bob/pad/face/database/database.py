from bob.pad.base.database import PadFile
import bob.bio.video


class VideoPadFile(PadFile):
    """A simple base class that defines basic properties of File object for the
    use in face PAD experiments.
    """

    def __init__(self, attack_type, client_id, path, file_id=None):
        super(VideoPadFile, self).__init__(
            attack_type=attack_type,
            client_id=client_id,
            path=path,
            file_id=file_id,
        )

    def load(self, directory=None, extension='.avi',
             frame_selector=bob.bio.video.FrameSelector(selection_style='all')):
        """Loads the video file and returns in a :any:`bob.bio.video.FrameContainer`.

        Parameters
        ----------
        directory : :obj:`str`, optional
            The directory to load the data from.
        extension : :obj:`str`, optional
            The extension of the file to load.
        frame_selector : :any:`bob.bio.video.FrameSelector`, optional
            Which frames to select.

        Returns
        -------
        :any:`bob.bio.video.FrameContainer`
            The loaded frames inside a frame container.
        """
        return frame_selector(self.make_path(directory, extension))
