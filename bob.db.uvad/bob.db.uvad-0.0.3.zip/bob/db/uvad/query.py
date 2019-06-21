from . import UVAD_FRAME_SHAPE
from bob.extension import rc
from bob.io.video import reader
from bob.db.base.annotations import read_annotation_file
from bob.pad.base.database import FileListPadDatabase
from bob.pad.face.database import VideoPadFile
from pkg_resources import resource_filename
import numpy


class File(VideoPadFile):
    """The file objects of the OULU-NPU dataset."""

    @property
    def frames(self):
        """Yields the frames of the biofile one by one.

        Yields
        ------
        :any:`numpy.array`
            A frame of the video. The size is (3, 1920, 1080).
        """
        vfilename = self.make_path(directory=self.original_directory)
        for frame in reader(vfilename):
            # crop frames to 720 x 1024
            h, w = numpy.shape(frame)[-2:]
            dh, dw = (h - 720) // 2, (w - 1024) // 2
            if dh != 0:
                frame = frame[:, : -2 * dh, :]
            if dw != 0:
                frame = frame[:, :, : -2 * dw]
            assert frame.shape == self.frame_shape, frame.shape
            yield frame

    @property
    def number_of_frames(self):
        """Returns the number of frames in a video file.

        Returns
        -------
        int
            The number of frames.
        """
        vfilename = self.make_path(directory=self.original_directory)
        return reader(vfilename).number_of_frames

    @property
    def frame_shape(self):
        """Returns the size of each frame in this database.

        Returns
        -------
        (int, int, int)
            The (#Channels, Height, Width) which is :any:`UVAD_FRAME_SHAPE`.
        """
        return UVAD_FRAME_SHAPE

    @property
    def annotations(self):
        # The annotations shipped with uvad are totally wrong. We load custom
        # annotations here
        path = self.make_path(self.annotation_directory, self.annotation_extension)
        annotations = read_annotation_file(path, annotation_type=self.annotation_type)
        return annotations


class Database(FileListPadDatabase):
    """The database interface for the OULU-NPU dataset."""

    def __init__(
        self,
        original_directory=rc["bob.db.uvad.directory"],
        name="uvad",
        pad_file_class=None,
        original_extension=None,
        annotation_directory=rc["bob.db.uvad.annotation_dir"],
        annotation_extension=".json",
        annotation_type="json",
        **kwargs
    ):
        if pad_file_class is None:
            pad_file_class = File
        filelists_directory = resource_filename(__name__, "lists")
        super(Database, self).__init__(
            filelists_directory=filelists_directory,
            name=name,
            original_directory=original_directory,
            pad_file_class=pad_file_class,
            original_extension=original_extension,
            annotation_directory=annotation_directory,
            annotation_extension=annotation_extension,
            annotation_type=annotation_type,
            **kwargs
        )

    def objects(
        self,
        groups=None,
        protocol=None,
        purposes=None,
        model_ids=None,
        classes=None,
        **kwargs
    ):
        """overrides the parent method to add attributes to the files.
        """
        files = super(Database, self).objects(
            groups=groups,
            protocol=protocol,
            purposes=purposes,
            model_ids=model_ids,
            classes=classes,
            **kwargs
        )
        for f in files:
            f.original_directory = self.original_directory
            f.annotation_directory = self.annotation_directory
            f.annotation_extension = self.annotation_extension
            f.annotation_type = self.annotation_type
        return files

    def frames(self, padfile):
        return padfile.frames

    def number_of_frames(self, padfile):
        return padfile.number_of_frames

    @property
    def frame_shape(self):
        return UVAD_FRAME_SHAPE

    def annotations(self, padfile):
        """Reads the annotations for the given padfile.

        Parameters
        ----------
        padfile : :any:`File`
            The file object for which the annotations should be read.

        Returns
        -------
        dict
            The annotations as a dictionary, e.g.:
            ``{'0': {'reye':(re_y,re_x), 'leye':(le_y,le_x)}, ...}``
        """
        return padfile.annotations
