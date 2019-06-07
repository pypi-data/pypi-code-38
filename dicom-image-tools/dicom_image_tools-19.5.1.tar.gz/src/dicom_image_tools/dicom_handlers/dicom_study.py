from pathlib import Path
import pydicom
from pydicom import FileDataset
from typing import List, Optional, Union

from .dicom_series import DicomSeries
from .ct import CtSeries
from .projection import ProjectionSeries


class DicomStudy:
    """ A class to manage DICOM files connected by a Study Instance UID

    Args:
        study_instance_uid : The study instance UID of the DICOM study object that is to be created

    Attributes:
        StudyInstanceUid: The study instance UID of the DICOM study object
        Series: List of DicomSeries objects containing detailed information abouts series included in the study
        Manufacturer: The manufacturer of the machine used in acquiring the image/-s
        ManufacturerModelName: The name of the machine, as given by the manufacturer, used in acquiring the image/-s

    Raises:
        TypeError: if study_instance_uid is not a string

    """
    def __init__(self, study_instance_uid: str):
        if not isinstance(study_instance_uid, str):
            raise TypeError("study_instance_uid must be a string")
        # Metadata
        self.StudyInstanceUid: str = study_instance_uid
        self.Series: List[Union[DicomSeries, CtSeries, ProjectionSeries]] = []
        self.Manufacturer: Optional[str] = None
        self.ManufacturerModelName: Optional[str] = None

    def add_file(self, file: Path, dcm: Optional[FileDataset] = None) -> None:
        """ Add the DICOM file to the DicomStudy object after validating the study instance UID

        Args:
            file: Path to where the file to be added is stored on disc
            dcm: The DICOM-file imported to a FileDataset object

        Raises:
            InvalidDicomError: If the given file is not a valid DICOM file
            ValueError: If the file does not have the same study instance UID as the StudyInstanceUID of the object

        """
        if dcm is None:
            dcm = pydicom.dcmread(fp=str(file.absolute()), stop_before_pixels=True)

        if dcm.StudyInstanceUID != self.StudyInstanceUid:
            raise ValueError(f"The given DICOM file is not part of the study {self.StudyInstanceUid}")

        self.Manufacturer = dcm.Manufacturer
        self.ManufacturerModelName = dcm.ManufacturerModelName

        try:
            index = [obj.SeriesInstanceUid for obj in self.Series].index(dcm.SeriesInstanceUID)
            self.Series[index].add_file(file=file, dcm=dcm)
        except ValueError:
            if dcm.Modality == "CT":
                self.Series.append(CtSeries(series_instance_uid=dcm.SeriesInstanceUID))
            else:
                self.Series.append(ProjectionSeries(file=file, dcm=dcm))
