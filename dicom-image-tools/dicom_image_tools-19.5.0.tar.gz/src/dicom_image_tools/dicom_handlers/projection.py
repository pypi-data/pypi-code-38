import numpy as np
from pathlib import Path
import pydicom
from pydicom import FileDataset
from typing import List, Optional

from .dicom_series import DicomSeries
from ..helpers.pixel_data import get_pixel_array
from ..helpers.voxel_data import VoxelData


class ProjectionSeries(DicomSeries):
    """ A class to manage 2D DICOM images, e.g., from conventional X-rays, mammography, panoramic, intraoral etc.

    This class only handles one image per series, as is usually the case for this kind of images.

    Args:
        file: Path object for the file that is to be imported
        dcm: A pydicom FileDataset object containing the file

    Attributes:
        kV: Tube voltage used in the image acquisition in kV
        mA: Tube current used in the image acquisition in mA
        Modality: The modality of the image, e.g., IO, PX, MG, DX, CR, etc.
        Manufacturer: The name of the manufacturer as specified in the DICOM file
        ManufacturersModelName: The model name specified by the manufacturer as given in the DICOM file

    """
    def __init__(self, file: Path, dcm: Optional[FileDataset] = None):
        if dcm is None:
            dcm = pydicom.dcmread(fp=str(file.absolute()), stop_before_pixels=True)

        if 'SeriesInstanceUID' not in dcm:
            raise ValueError("The DICOM file does not contain a series instance UID")

        super().__init__(series_instance_uid=dcm.SeriesInstanceUID)

        self.Modality = dcm.Modality
        self.Manufacturer: Optional[str] = None
        if 'Manufacturer' in dcm:
            self.Manufacturer = dcm.Manufacturer

        self.ManufacturersModelName: Optional[str] = None
        if 'ManufacturerModelName' in dcm:
            self.ManufacturersModelName = dcm.ManufacturerModelName
        if self.Modality == 'IO' and 'DetectorManufacturerModelName' in dcm:
            self.ManufacturersModelName = dcm.DetectorManufacturerModelName

        self.kV: Optional[List[float]] = []
        self.mA: Optional[List[float]] = []
        self.ImageVolume: Optional[List[np.ndarray]] = []

        self.add_file(file=file, dcm=dcm)

    def add_file(self, file: Path, dcm: Optional[FileDataset] = None):
        """ Add a file to the objects list of files

        First performs a check that the file path is of a path object and that it has the same series instance UID as
        the class object

        Args:
            file: Path to where the file to be added is stored on disc
            dcm: The DICOM-file imported to a FileDataset object

        Raises:
            InvalidDicomError: If the given file is not a valid DICOM file
            ValueError: If the file does not have the same study instance UID as the StudyInstanceUID of the object

        """
        if not isinstance(file, Path):
            raise TypeError("file is not a Path-object")

        super().add_file(file=file, dcm=dcm)

        if dcm is None:
            dcm = pydicom.dcmread(fp=str(file.absolute()), stop_before_pixels=True)

        if 'PixelSpacing' in dcm:
            self.VoxelData.append(VoxelData(x=float(dcm.PixelSpacing[1]),
                                            y=float(dcm.PixelSpacing[0]),
                                            z=None))
        else:
            # Assume pixel size is set in Detector Element Spacing tag (0018, 7022)
            self.VoxelData.append(VoxelData(x=float(dcm.DetectorElementSpacing[1]),
                                            y=float(dcm.DetectorElementSpacing[0]),
                                            z=None))
        if 'KVP' in dcm:
            self.kV.append(float(dcm.KVP))

        if 'XRayTubeCurrent' in dcm:
            self.mA.append(float(dcm.XRayTubeCurrent))
        elif 'XRayTubeCurrentInmA' in dcm:
            self.mA.append(float(dcm.XRayTubeCurrentInmA))
        elif 'XRayTubeCurrentInuA' in dcm:
            self.mA.append(float(dcm.XRayTubeCurrentInuA) / 1000)

        # Remove pixel data part of dcm to decrease memory used for the object
        if 'PixelData' in dcm:
            try:
                del dcm[0x7FE00010]
            except Exception as e:
                pass

        self.CompleteMetadata.append(dcm)

    def import_image(self) -> None:
        """ Import the pixel data into the ImageVolume property

        Returns:

        """
        self.ImageVolume = []
        for fp in self.FilePaths:
            dcm = pydicom.dcmread(str(fp.absolute()))
            self.ImageVolume.append(get_pixel_array(dcm=dcm))
