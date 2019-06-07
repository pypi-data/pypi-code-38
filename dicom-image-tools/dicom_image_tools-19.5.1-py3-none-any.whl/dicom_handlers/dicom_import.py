from pathlib import Path
import pydicom
from pydicom.errors import InvalidDicomError
from typing import Dict, Optional

from .dicom_study import DicomStudy


def import_dicom_from_folder(folder: Path, recursively: bool = True) -> Dict[str, DicomStudy]:
    """ Go through a folder and import all valid DICOM images found

    Args:
        folder: Path object of the folder to search for DICOM files
        recursively: Specification if the folder should be search recursively. Defaults to True

    Raises:
        TypeError: If the given folder is not a Path object
        ValueError: If the given folder is not a directory
        ValueError: If no valid DICOM files were found in the search of the given folder

    Returns:
        A dictionary on the form {<study-instance-uid>: <DicomStudy object>}

    """
    if not isinstance(folder, Path):
        raise TypeError("folder must be a Path object")
    if not folder.is_dir():
        raise ValueError("The given folder is not a directory")

    files = folder.iterdir()
    if recursively:
        files = folder.rglob("*")

    dicom_study_list = dict()

    for fp in files:
        if not fp.is_file():
            continue

        try:
            dcm = pydicom.dcmread(fp=str(fp.absolute()), stop_before_pixels=True)
        except InvalidDicomError as e:
            continue

        if dcm.StudyInstanceUID not in dicom_study_list:
            dicom_study_list[dcm.StudyInstanceUID] = DicomStudy(study_instance_uid=dcm.StudyInstanceUID)

        dicom_study_list[dcm.StudyInstanceUID].add_file(fp, dcm=dcm)

    if not len(dicom_study_list):
        raise ValueError("The given folder contains no valid DICOM files")

    return dicom_study_list


def import_dicom_file(file: Path) -> DicomStudy:
    """ Import a DICOM file into a DicomStudy object

    Args:
        file: Path to the file to import

    Raises:
        TypeError: If the given file is not a Path object
        ValueError: If the given file path is not a valid file
        InvalidDicomError: If the given file is not a valid DICOM file

    Returns:
        DicomStudy object with the file added to it

    """
    if not isinstance(file, Path):
        raise TypeError("file must be a Path object")
    if not file.is_file():
        raise ValueError("File is not a valid file")

    try:
        dcm = pydicom.dcmread(fp=str(file.absolute()), stop_before_pixels=True)
    except InvalidDicomError:
        raise

    output = DicomStudy(study_instance_uid=dcm.StudyInstanceUID)
    output.add_file(file=file, dcm=dcm)

    return output
