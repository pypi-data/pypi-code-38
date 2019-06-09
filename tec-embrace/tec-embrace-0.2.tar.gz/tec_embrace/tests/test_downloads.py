import logging
import os
from unittest import TestCase, mock
from urllib.error import HTTPError

import settings
from app.downloads import DownloadDCB, DownloadOrbit, DownloadGlonassChannel

DAY = 16
MONTH = 10
YEAR = 2018


class DownloadGenericAndDCBTest(TestCase):
    def setUp(self):
        self.dcb = DownloadDCB(YEAR, DAY)
        logging.disable(logging.ERROR)

    def test_file_name(self):
        """Must return the name CAS0MGXRAP_2018160000_01D_01D_DCB.BSX.gz"""
        self.assertEqual('CAS0MGXRAP_2018160000_01D_01D_DCB.BSX.gz', self.dcb.file)

    def test_dbd_url(self):
        """Must return the URL
        ftp://cddis.gsfc.nasa.gov/pub/gps/products/mgex/dcb/2018/CAS0MGXRAP_2018160000_01D_01D_DCB.BSX.gz"""
        url = 'ftp://cddis.gsfc.nasa.gov/pub/gps/products/mgex/dcb/2018/CAS0MGXRAP_2018160000_01D_01D_DCB.BSX.gz'
        self.assertEqual(url, self.dcb.dbc_url)

    def test_dcb_path_to_save(self):
        """Must return the path equals to settings.PATH_DCB"""
        self.assertEqual(settings.PATH_DCB, self.dcb._path_to_save)

    def test_is_zipped(self):
        """Must return is_zipped equals True"""
        self.assertTrue(self.dcb.is_zipped)

    def test_file_exist(self):
        """Must return false"""
        self.assertFalse(self.dcb._file_exist)

    def test_file_uncompressed_exist(self):
        """Must return False"""
        self.assertFalse(self.dcb._file_uncompressed_exist)

    @mock.patch('os.path.isfile')
    def test_file_uncompressed__exist(self, filename):
        """Must return True if path exists"""
        filename.return_value = True
        self.assertTrue(self.dcb.file_uncompressed)

    def test_absolute_path(self):
        """Must return the absolute path"""
        path = self.dcb.path_to_save + self.dcb.filename
        self.assertEqual(path, self.dcb.absolute_path)

    @mock.patch('os.remove')
    @mock.patch('os.system')
    @mock.patch('app.downloads.urlopen', autospec=True)
    def test_download(self, urlopen, mock_system, mock_remove):
        """Test the _getting_file function"""
        urlopen.return_value.read.return_value = 'mocked'
        with mock.patch('os.path.exists') as exists:
            exists.return_value = True
            with mock.patch('app.downloads.open', new=mock.mock_open(), create=True) as file:
                self.dcb._getting_file()
                self.assertTrue(mock_system.called)
                self.assertTrue(mock_remove.called)
                mock_system.stop()
                mock_remove.stop()
                file.assert_called_once_with(self.dcb.absolute_path, 'wb+')
                urlopen.assert_called_with(self.dcb.url, timeout=30)
                self.assertEqual(os.path.exists(self.dcb.absolute_path), True)
                exists.stop()

    @mock.patch('os.remove')
    def test_delete_zipped_file(self, mock_remove):
        """Test _delete_zipped_file function"""
        self.dcb._delete_zipped_file()
        self.assertTrue(mock_remove.called)

    @mock.patch('os.remove')
    @mock.patch('os.system')
    def test_unzip_file(self, mock_system, mock_remove):
        """Test _unzip_file function"""
        self.dcb._unzip_file()
        mock_system.assert_called_once_with("uncompress -k " + self.dcb.absolute_path)
        self.assertTrue(mock_system.called)
        self.assertTrue(mock_remove.called)
        mock_system.stop()
        mock_remove.stop()

    def test_str(self):
        """Must return the url when the object is called"""
        self.assertEqual(self.dcb.url, self.dcb.__str__())

    # @mock.patch('app.downloads.urlopen', autospec=True)
    # def test_failed_query(self, mock_get):
    #     mock_get.side_effect = HTTPError(mock.Mock(return_value={'status': 500}), 'server down')
    #     self.dcb._getting_file()
    #     with self.assertRaises(SystemExit) as cm:
    #         self.assertEqual(cm.exception.args[0], 1)


class DownloadGenericErrorTest(TestCase):
    def test_download_fail(self):
        """Must return exit code 1 when given a URL error"""
        dcb = DownloadDCB(YEAR, DAY)
        with mock.patch('os.path.exists') as exists:
            exists.return_value = True
            with mock.patch('app.downloads.open', new=mock.mock_open(), create=True) as file:
                with self.assertRaises(SystemExit) as cm:
                    dcb._file = 'CAS0MGXRAP_{1}{0}0000_01D_01D_DCB.BSX.gz'
                    dcb._getting_file()
                    file.assert_called_once_with(dcb.absolute_path, 'wb+')
                    self.assertEqual(cm.exception.args[0], 1)
                    exists.stop()
                    file.stop()


class DownloadOrbittest(TestCase):
    def setUp(self):
        self.orbit = DownloadOrbit(YEAR, MONTH, DAY)

    def test_api(self):
        """_api Must be equals the settings.URL_ORBIT_MGEX"""
        self.assertEqual(self.orbit._api, settings.URL_ORBIT_MGEX)

    def test_root_path(self):
        """_root_path Must be equals the settings.PATH_ORBIT"""
        self.assertEqual(self.orbit._root_path, settings.PATH_ORBIT)

    def test_epoch(self):
        """EPOCH Must be equals 3657"""
        self.assertEqual(self.orbit.EPOCH, 3657)

    def test_epoch_int(self):
        """EPOCH Must be an int"""
        self.assertIsInstance(self.orbit.EPOCH, int)

    def test_orbit_sufix(self):
        """orbit_sufix must be equals '19842'"""
        self.assertEqual('19842', self.orbit.orbit_sufix)

    def test_orbit_sufix_str(self):
        """orbit_sufix must be an string"""
        self.assertIsInstance(self.orbit.orbit_sufix, str)

    def test_gnss_week_str(self):
        """gnss_week must be an string"""
        self.assertIsInstance(self.orbit.gnss_week, str)

    def test_gnss_week(self):
        """gnss_week must be equals '1984'"""
        self.assertEqual('1984', self.orbit.gnss_week)

    def test_url(self):
        """Must return an URL """
        url = 'ftp://cddis.gsfc.nasa.gov/pub/gps/products/mgex/1984/COD0MGXFIN_2018160000_01D_05M_ORB.SP3.gz'
        self.assertEqual(url, self.orbit._url)

    def test_file(self):
        """Must return de file name"""
        self.assertEqual('COD0MGXFIN_2018160000_01D_05M_ORB.SP3.gz', self.orbit.file)

    def test_path_to_save(self):
        """Must return the path to save the orbit file"""
        path = '%s%s/' % (self.orbit._root_path, self.orbit.gnss_week)
        self.assertEqual(path, self.orbit._path_to_save)


class DownloadGlonassTest(TestCase):
    def setUp(self):
        self.glonass = DownloadGlonassChannel(YEAR, DAY, MONTH)

    def test_api(self):
        """_api Must be equals the settings.URL_GLONASS_CHANNELS"""
        self.assertEqual(self.glonass._api, settings.URL_GLONASS_CHANNELS)

    def test_root_path(self):
        """_root_path Must be equals the settings.PATH_GLONASS_CHANNEL"""
        self.assertEqual(self.glonass._root_path, settings.PATH_GLONASS_CHANNEL)

    def test_epoch(self):
        """EPOCH Must be equals 3657"""
        self.assertEqual(self.glonass.EPOCH, 3657)

    def test_epoch_int(self):
        """EPOCH Must be an int"""
        self.assertIsInstance(self.glonass.EPOCH, int)

    def test_file(self):
        """Must return de file name"""
        self.assertEqual('getCUSMessage.php', self.glonass._file)

    def test_rinex_date(self):
        """Must return rinex date"""
        self.assertEqual('channel-20181016{}', self.glonass.rinex_date)

    def test_url(self):
        """Must return an URL """
        url = 'https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php'
        self.assertEqual(url, self.glonass._url)

    def test_absolute_path(self):
        """Must return the absolute_path to save the glonass channel"""
        path = self.glonass.path_to_save + self.glonass.rinex_date.format('.txt')
        self.assertEqual(path, self.glonass.absolute_path)

    @mock.patch('app.downloads.urlopen', autospec=True)
    def test_download(self, urlopen):
        """Test the _getting_file function"""
        urlopen.return_value.read.return_value = """<font face='Arial' size='3'><pre>                   1.STATUS Information Group
 
                  GLONASS Constellation Status
                      ( March 8, 2019)
  
</pre></font>"""
        with mock.patch('os.path.exists') as exists:
            exists.return_value = True
            with mock.patch('app.downloads.open', new=mock.mock_open(), create=True) as mock_file:
                with mock.patch('app.utils.helpers.fromstring') as utils:
                    utils().itertext.return_value = 'teste'
                    self.glonass._getting_file()
                    mock_file.assert_called_once_with(self.glonass.absolute_path, 'wb+')
                    urlopen.assert_called_once_with(self.glonass.url, timeout=30)
                    self.assertEqual(os.path.exists(self.glonass.absolute_path), True)
                    utils.stop()

    def test_uncompressed_file(self):
        """Glonass file_uncompressed and absolute_path must be equals"""
        self.assertEqual(self.glonass.file_uncompressed, self.glonass.absolute_path)
