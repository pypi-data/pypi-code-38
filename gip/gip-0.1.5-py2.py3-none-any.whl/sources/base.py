import pathlib
import tarfile

from gip import logger
from gip import exceptions

LOG = logger.get_logger(__name__)


class Source():
    """
    Superclass which interfaces all the sources
    """

    def get_commit_hash(self):
        raise NotImplementedError

    def get_archive(self, dest):
        raise NotImplementedError

    def extract_archive(self, src, dest, name, remove_src=True):
        """
        Extract archive to destination, zip and tar supported

        :param src: path to archive to extract
        :param dest: directory where to extract the archive to
        :param name: name of the folder of the extracted archive
        :param remove_src: boolean to enable removal of the source file
        :raise exceptions.DirectoryDoesNotExist: directory does not exist
        :raise FileNotFoundError: source does not exist
        :raise TypeError: archive is of an unsupported type
        """
        src = pathlib.Path(src)
        dest = pathlib.Path(dest)

        # Raise error when destination directory does not exists
        if not dest.is_dir():
            raise exceptions.DirectoryDoesNotExist(dest)

        # Raise error when archive does not exists
        if not src.is_file():
            raise FileNotFoundError("Archive not found: {archive}".format(
                            archive=src
                        ))

        if tarfile.is_tarfile(src):
            archive = tarfile.open(src)
            archive.extractall(path=dest)
            if remove_src:
                # No need for try/except only raises on directory.
                src.unlink()

            # Rename extracted folder when name is passed
            if name:
                extracted_folder_name = archive.getmembers()[0].name
                dest = pathlib.PurePath(dest)
                extracted_archive = pathlib.Path(
                                        dest.joinpath(extracted_folder_name))

                # Thrown error when for some reaseon the extraction has failed
                if not extracted_archive.is_dir():
                    raise exceptions.DirectoryDoesNotExist(extracted_archive)

                extracted_archive.rename(dest.joinpath(name))
        else:
            raise TypeError("Downloaded archive is of a non supported \
                            archive type: {archive}".format(
                                archive=src
                            ))
