import numpy as np
from pathlib import Path
import pydicom
from pydicom import FileDataset
from typing import List, Optional
from ..helpers.voxel_data import VoxelData


class DicomSeries:
    """ A class to manage DICOM files connected by a Series Instance UID

    Args:
        series_instance_uid: Series instance UID of the object to be created

    Attributes:
        SeriesInstanceUid: Series instance UID of the object
        FilePaths: Paths to the files added to the object
        CompleteMetadata: The complete set of metadata for the added files
        VoxelData: Voxel size information for included image files
        ImageVolume: The Image volume of the DICOM series
        Mask: A mask of the same dimension as the image volume to apply to the image volume

    """
    def __init__(self, series_instance_uid: str):
        if not isinstance(series_instance_uid, str):
            raise TypeError("series_instance_uid must be a string")
        self.FilePaths: List[Path] = []

        # Metadata
        self.SeriesInstanceUid: str = series_instance_uid
        self.SeriesDescription: Optional[str] = None
        self.CompleteMetadata: List[Optional[FileDataset]] = []
        self.VoxelData: List[VoxelData] = []

        self.ImageVolume: Optional[np.ndarray] = None
        self.Mask: Optional[np.ndarray] = None

    def add_file(self, file: Path, dcm: Optional[FileDataset] = None):
        """ Add a file to the objects list of files

        First performs a check that the file is a valid DICOM file and that it belongs to the object/series

        Args:
            file: Path to where the file to be added is stored on disk
            dcm: The DICOM-file imported to a FileDataset object

        Raises:
            ValueError: if SeriesInstanceUID of the file is not the same as the SeriesInstanceUid attribute

        """
        if any([True if obj == file else False for obj in self.FilePaths]):
            # Return None since the file is alread in hte volume
            return

        if dcm is None:
            dcm = pydicom.dcmread(fp=str(file.absolute()), stop_before_pixels=True)

        if dcm.SeriesInstanceUID != self.SeriesInstanceUid:
            msg = f"Wrong SeriesInstanceUID. Expected: {self.SeriesInstanceUid}; Input: {dcm.SeriesInstanceUID}"
            raise ValueError(msg)

        if 'SeriesDescription' in dcm:
            self.SeriesDescription = dcm.SeriesDescription

        self.FilePaths.append(file)

