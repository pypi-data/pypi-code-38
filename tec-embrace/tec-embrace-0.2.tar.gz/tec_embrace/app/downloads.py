import logging
import os
import sys

from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import tec_embrace.settings as settings

from tec_embrace.app.utils.helpers import Utils


class DownloadGeneric:
    """
    Download Generic Class
    """
    filename = ''

    def __init__(self, name, url, path, file, is_zipped=True):
        """
        :type is_zipped: True if The files is downloaded zipped
        :param name: A String to be printed on log
        :param url: API to download the file
        :param path: A path to save the files on system
        :param file: Name of the files to download
        """
        self.name = name
        self.url = url
        self.path_to_save = path
        self.filename = file
        self.is_zipped = is_zipped

    @property
    def file_uncompressed(self):
        """
        Returns the current absolute path to the umcompressed file

        :return: The absolute path to the uncompressed file
        """
        file_uncompressed, _ = os.path.splitext(self.absolute_path)
        return file_uncompressed

    @property
    def absolute_path(self):
        """
        Returns the current absolute path

        :return: The absolute path
        """
        return self.path_to_save + self.filename

    @property
    def _file_exist(self):
        """
        The path source download, provides the respective file in compact mode (.Z or .gz) . Thus, in filesystem either
        the compressed or uncompressed file could exist. This method check in which situation the download
        is needed or not

        :return: Absolute file path in filesystem
        """
        file = Path(self.absolute_path)
        return file.exists()

    @property
    def _file_uncompressed_exist(self):
        """
        Check if the path is related to a compressed file. If so, it is uncompressed and the new path is then returned

        :return: True or False, checking if the file is already uncompressed or not
        """
        file = Path(self.file_uncompressed)
        return file.exists()

    def download(self):  # pragma: no cover
        if self._file_exist:
            logging.info(">>>> %s File already exist. Download skipped!", self.name)
        elif self._file_uncompressed_exist:
            logging.info(">>>> %s File uncompressed already exist. Download skipped!", self.name)
        else:
            self._getting_file()

        return self

    def make_dirs(self):  # pragma: no cover
        """
        Make directory if it does not exist yet

        :return: None
        """
        if not os.path.exists(os.path.dirname(self.absolute_path)):
            os.makedirs(os.path.dirname(self.absolute_path))

    def _getting_file(self):
        msg_error = '>>>> %s Data not retrieved because %s - URL: %s'
        try:
            self.make_dirs()
            with urlopen(self.url, timeout=30) as response, open(self.absolute_path, 'wb+') as out_file:
                data = response.read()  # a `bytes` object
                out_file.write(data)
                if self.is_zipped:
                    self._unzip_file()
                response.close()
                out_file.close()
        except HTTPError as error:
            error.close()
            logging.error(msg_error, self.name, error, self.url)
            sys.exit(1)
        except URLError as e:
            logging.error(msg_error, self.name, e, self.url)
            sys.exit(1)
        else:
            logging.info(">>>> File download " + self.filename + " done!")
        return self

    def _unzip_file(self):
        logging.info(">> Uncompressing file " + self.absolute_path)
        os.system("uncompress -k " + self.absolute_path)
        logging.info(">>>> Uncompressing done!")
        self._delete_zipped_file()
        return self

    def _delete_zipped_file(self):
        logging.info(">>>> Deleting Compressed file %s", self.absolute_path)
        os.remove(self.absolute_path)
        logging.info(">>>> Compressed file ws deleted with success!")
        return self

    def __str__(self):
        return self.url


class DownloadDCB(DownloadGeneric):
    """
    Download DCB files
    """
    _api = settings.URL_DCB_MGEX
    _file = 'CAS0MGXRAP_{0}{1}0000_01D_01D_DCB.BSX.gz'
    _path_to_save = ""

    def __init__(self, year, day, path_dcb):
        """
        :param year: A String year on format yyyy
        :param day: A String day on format dd
        """
        self.year = year
        self.day = day
        self._path_to_save = path_dcb
        super().__init__('DCB', self.dbc_url, self._path_to_save, self.file)

    @property
    def dbc_url(self):
        return '%s%s/%s' % (self._api, self.year, self.file)

    @property
    def file(self):
        return self._file.format(self.year, self.day)


class DownloadOrbit(DownloadGeneric):
    """
    Download Orbit files
    """
    _api = settings.URL_ORBIT_MGEX
    _file = "COD0MGXFIN_{0}{1}0000_01D_05M_ORB.SP3.gz"
    _file2 = "com{0}.sp3.Z"
    _root_path = ""
    EPOCH = 3657

    def __init__(self, year, month, day, path_orbit):
        """
        By the rinex's doy, year, and the orbit type desired, return the correspondent GNSS week and day of the week
        to construct the orbit file URL

        :param year: An String year on format yyyy
        :param month: An String month on format mm
        :param day: An String day on format dd
        :param path_orbit: The absolute path for saving the orbit files
        """
        self.year = year
        self.month = month
        self.day = day
        self._root_path = path_orbit
        date = datetime(int(self.year), 1, 1) + timedelta(int(self.day) - 1)
        ms = date.timestamp() * 1000
        self.epoch = ms / (24 * 3600 * 1000)
        super().__init__('Orbit', self._url, self._path_to_save, self.file)

    @property
    def orbit_sufix(self):
        dow = int((self.epoch - self.EPOCH) % 7)
        return str(self.gnss_week) + str(dow)

    @property
    def gnss_week(self):
        return str(int((self.epoch - self.EPOCH) / 7))

    @property
    def _url(self):
        return '%s%s/%s' % (self._api, self.gnss_week, self.file)

    @property
    def _url2(self):
        return '%s%s/%s' % (self._api, self.gnss_week, self.file2)

    @property
    def file(self):
        return self._file.format(self.year, self.day)

    @property
    def file2(self):
        return self._file2.format(self.orbit_sufix)

    @property
    def _file_exist(self):
        """
        The path source download, provides the respective file in compact mode (.Z or .gz) . Thus, in filesystem either
        the compressed or uncompressed file could exist. This method check in which situation the download
        is needed or not

        :return: Absolute file path in filesystem
        """
        file = Path(self.absolute_path)
        file2 = Path(self._path_to_save + self.file2)
        if file.exists():
            return True
        if file2.exists():
            self.filename = self.file2
            return True
        return False

    @property
    def _file_uncompressed_exist(self):
        """
        Check if the path is related to a compressed file. If so, it is uncompressed and the new path is then returned

        :return: True or False, checking if the file is already uncompressed or not
        """
        file = Path(self.file_uncompressed)
        file_uncompressed, _ = os.path.splitext(self._path_to_save + self.file2)
        file2 = Path(file_uncompressed)
        if file.exists():
            return True
        if file2.exists():
            self.filename = self.file2
            return True
        return False

    @property
    def _path_to_save(self):
        return '%s%s/' % (self._root_path, self.gnss_week)

    def _try_url(self):
        with urlopen(self.url, timeout=30) as response, open(self.absolute_path, 'wb+') as out_file:
            data = response.read()  # a `bytes` object
            out_file.write(data)
            if self.is_zipped:
                self._unzip_file()
            response.close()
            out_file.close()

    def _getting_file(self):
        msg_error = '>>>> %s Data not retrieved because %s - URL: %s'
        self.make_dirs()
        try:
            self._try_url()
        except HTTPError as error:
            error.close()
            logging.error(msg_error, self.name, error, self.url)
            sys.exit(1)
        except URLError as e:
            self.filename = self.file2
            self.url = self._url2
            try:
                self._try_url()
            except HTTPError as e:
                logging.error(msg_error, self.name, e, self.url)
                sys.exit(1)
        else:
            logging.info(">>>> File download " + self.filename + " done!")
        return self


class DownloadGlonassChannel(DownloadGeneric):
    """
    Download GLONASS Channel file
    """
    _api = settings.URL_GLONASS_CHANNELS
    _file = "getCUSMessage.php"
    _root_path = ""
    EPOCH = 3657

    def __init__(self, year, day, month, path_glonass_channel):
        """
        :param year: An String year on format yyyy
        :param day: An String day on format dd
        :param month: An String month on format mm
        :param path_glonass_channel: Absolute path for saving the glonass channels
        """
        self.year = year
        self.month = month
        self.day = day
        self._root_path = path_glonass_channel
        super().__init__('Glonass Channel', self._url, self._root_path, self._file, False)

    @property
    def rinex_date(self):
        return 'channel-%s%s%s{}' % (self.year, self.month, self.day)

    @property
    def _url(self):
        return '%s%s' % (self._api, self._file)

    # Overwrite the DownloadGeneric method
    @property
    def absolute_path(self):
        return self.path_to_save + self.rinex_date.format('.txt')

    # Overwrite the DownloadGeneric method
    def _getting_file(self):
        try:
            self.make_dirs()
            with urlopen(self.url, timeout=30) as response, open(self.absolute_path, 'wb+') as out_file:
                data = response.read()
                data = Utils.remove_html_tags(data)
                out_file.write(bytes(data, encoding='utf-8'))
                if self.is_zipped:  # pragma: no cover
                    self._unzip_file()
        except (HTTPError, URLError) as error:  # pragma: no cover
            logging.error('>>>> %s Data not retrieved because %s - URL: %s', self.name, error, self.url)
            sys.exit(1)
        else:
            logging.info(">>>> File download " + self.filename + " done!")
        return self

    @property
    def file_uncompressed(self):
        return self.absolute_path
