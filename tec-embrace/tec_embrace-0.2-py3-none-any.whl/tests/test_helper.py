import os
import unittest

import settings as settings
import urllib.request

from helper import InputFiles


class FindOrbitReferenceHelperTest(unittest.TestCase):
    pass
    # def test_find_orbit_reference_default(self):
    #     """ Passing all arguments as default, must return igr18471.sp3.Z """
    #     self.assertEqual(self._find_orbit_reference(), "igr18471.sp3.Z")
    #
    # def test_find_orbit_reference_R(self):
    #     """ Passing the correspondent arguments as chpi1521.15o, 2015, R, must return igl18471.sp3.Z """
    #     self.assertEqual(self._find_orbit_reference(orbit_type="R"), "igl18471.sp3.Z")
    #
    # def test_find_year_orbit_reference_year(self):
    #     """ Passing the correspondent arguments as chpi1521.15o, 2016, G, must return igr18992.sp3.Z """
    #     self.assertEqual(self._find_orbit_reference(year=2016), "igr18992.sp3.Z")
    #
    # def test_find_orbit_reference_R_year(self):
    #     """ Passing the correspondent arguments as chpi1521.15o, 2016, R, must return igl18992.sp3.Z """
    #     self.assertEqual(self._find_orbit_reference(year=2016, orbit_type="R"), "igl18992.sp3.Z")
    #
    # def test_find_orbit_reference_wrong_year_2_digits(self):
    #     """ Passing year 2 digits, must return None """
    #     self.assertEqual(self._find_orbit_reference(year=16), None)
    #
    # def test_find_orbit_reference_wrong_year_5_digits(self):
    #     """ Passing year with 5 digits, must return None """
    #     self.assertEqual(self._find_orbit_reference(year=20164), None)
    #
    # def test_find_orbit_reference_rinex_no_station(self):
    #     """ Passing rinex_name with wrong station iaga code, must return None """
    #     self.assertEqual(self._find_orbit_reference(rinex_name='chp1521.15o'), None)
    #
    # def test_find_orbit_reference_rinex_no_extension(self):
    #     """ Passing rinex_name with no extension, must return None """
    #     self.assertEqual(self._find_orbit_reference(rinex_name='chpi1521'), None)
    #
    # def test_find_orbit_reference_rinex_empty(self):
    #     """ Passing rinex_name empty, must return None """
    #     self.assertEqual(self._find_orbit_reference(rinex_name=''), None)
    #
    # def test_find_orbit_reference_rinex_with_incorrect_doy(self):
    #     """ Passing rinex_name with wrong doy, must return None """
    #     self.assertEqual(self._find_orbit_reference(rinex_name='chpi3681.15o'), None)
    #
    # def test_find_orbit_reference_orbit_type_invalid(self):
    #     """ Passing orbit_type invalid, must return None """
    #     self.assertEqual(self._find_orbit_reference(orbit_type='X'), None)
    #
    # def test_find_orbit_reference_orbit_type_empty(self):
    #     """ Passing rinex_name with no extension, must return None """
    #     self.assertEqual(self._find_orbit_reference(orbit_type=''), None)
    #
    # def _find_orbit_reference(self, **kwargs):
    #     input_files = InputFiles()
    #     default = dict(
    #         rinex_name='chpi1521.15o',
    #         year=2015,
    #         orbit_type='G'
    #     )
    #     data = dict(default, **kwargs)
    #     find = input_files._find_orbit_reference(data['rinex_name'], data['year'], data['orbit_type'])
    #     return find


class ChannelsURLHelperTest(unittest.TestCase):
    def test_download_channels_url_response(self):
        """HTML must contain text """
        response = urllib.request.urlopen(settings.URL_GLONASS_CHANNELS).getcode()
        self.assertEqual(response, 200)


class CheckURLExist(unittest.TestCase):
    pass
    # def test_url_download_exist(self):
    #     url = urlopen(settings.URL_ORBIT + '1847/igr18471.sp3.Z')
    #     if url != URLError:
    #         return True
    #     self.assertEqual(url, True)

# class SetupFileAndDownloadHelperTest(unittest.TestCase):
#     def _setup_file_and_download(self, **kwargs):
#         input_files = InputFiles()
#         default = dict(
#             year=2015,
#             month=6,
#             file='chpi1521.15o',
#             file_type='DCB',
#             rinex_interval=30
#         )
#         data = dict(default, **kwargs)
#         find = input_files._setup_file_and_download(data['year'], data['month'], data['file'], data['file_type'],
#                                                     data['rinex_interval'])
#         return find

class DownloadFileHelperTest(unittest.TestCase):
    pass
    # def test_download_file_default(self):
    #     """ Passing all arguments as default, must return complete path of igl18471.sp3.Z"""
    #     self.assertEqual(self._download_file(), settings.PATH_ORBIT + '2015/igl18471.sp3.Z')
    #
    # def _download_file(self, **kwargs):
    #     input_files = InputFiles()
    #     default = dict(
    #         year=2015,
    #         filename='/home/lotte/embrace/tec/orbit/1847/igl18471.sp3.Z',
    #         orbit_name='igl18471.sp3.Z',
    #         gnss_week='1847',
    #         what_to_download='Orbit',
    #     )
    #     data = dict(default, **kwargs)
    #     find = input_files._download_file(data)
    #     return find

    # def test_download_orbit_default(self):
    #     """ Passing uncompressed orbit_name, must return igl18471.sp3"""
    #     self.assertEqual(self._download_orbit(), settings.PATH_ORBIT + '2015/igl18471.sp3')
    #
    # def test_download_orbit_with_orbit_name_empty(self):
    #     """ Passing orbit_name empty must return None"""
    #     self.assertEqual(self._download_orbit(orbit_name=''), None)
    #
    # def test_download_orbit_with_orbit_name_with_wrong_extension(self):
    #     """ Passing orbit_name with wrong extension must return None """
    #     self.assertEqual(self._download_orbit(orbit_name='igl18471.sp5'), None)
    #
    # def test_download_orbit_with_orbit_name_with_uppercase(self):
    #     """ Passing orbit_name with upper case, must return the same orbit_name in lower case: igl18471.sp3.Z"""
    #     self.assertEqual(self._download_orbit(orbit_name='IGL18471.SP3.Z'), settings.PATH_ORBIT
    #                      + '2015/igl18471.sp3')
    #
    # def test_download_orbit_with_year_empty(self):
    #     """ Passing year empty must return ..."""
    #     self.assertEqual(self._download_orbit(year=''), settings.PATH_ORBIT + '...')
    #
    # def test_download_orbit_with_year_with_1_digit(self):
    #     """ Passing year with one single digit, must return the empty orbit path"""
    #     self.assertEqual(self._download_orbit(year=5), '')
    #
    # def test_download_orbit_with_year_with_3_digits(self):
    #     """ Passing year with three digits, must return the empty orbit path"""
    #     self.assertEqual(self._download_orbit(year=105), '')
    #
    # def test_download_orbit_with_year_with_2_digits(self):
    #     """ Passing year with only two digits, must return the saved orbit path with correct 4-digits year folder"""
    #     self.assertEqual(self._download_orbit(year=15), settings.PATH_ORBIT + '2015/igl18471.sp3.Z')
    #
    # def test_download_orbit_with_year_with_more_than_4_digits(self):
    #     """ Passing year with more than 4 digits, must return the empty orbit path"""
    #     self.assertEqual(self._download_orbit(year=20159), '')
    #
    # def test_download_orbit_with_year_as_string(self):
    #     """ Passing year as string, must return the empty orbit path"""
    #     self.assertEqual(self._download_orbit(year='2015a'), '')


class CheckFilesExistHelperTest(unittest.TestCase):
    pass
    # def delete_all(self, folder):
    #     for the_file in os.listdir(folder):
    #         file_path = os.path.join(folder, the_file)
    #         try:
    #             if os.path.isfile(file_path):
    #                 os.unlink(file_path)
    #         except Exception as e:
    #             print(e)
    #
    # def create_file(self, folder, filename):
    #     tmp_file = os.path.join(folder, filename)
    #     with open(tmp_file, 'w+') as f:
    #         f.write('Python mock testing. Delete me later!')
    #
    # def test_dcb_compressed_and_uncompressed_exists_return_uncompressed(self):
    #     """ Passing default DCB, check if it exists, if so, returns absolute path of the uncompressed file """
    #     self.create_file(settings.PATH_DCB, 'P1C11506.DCB')
    #     self.create_file(settings.PATH_DCB, 'P1C11506.DCB.Z')
    #     self.assertTrue(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB'))
    #     self.assertTrue(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB.Z'))
    #     self.assertEqual(self._check_files_already_exist(), (False, settings.PATH_DCB + 'P1C11506.DCB'))
    #     self.delete_all(settings.PATH_DCB)
    #
    # def test_dcb_only_compressed_exists_return_compressed(self):
    #     """ Passing the DCB only with the P1C11506.DCB.Z file, make sure it exists, if it does,
    #     returns the absolute path of the compressed file """
    #     self.create_file(settings.PATH_DCB, 'P1C11506.DCB.Z')
    #     self.assertTrue(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB.Z'))
    #     self.assertFalse(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB'))
    #     self.assertEqual(self._check_files_already_exist(), (False, settings.PATH_DCB + 'P1C11506.DCB.Z'))
    #     self.delete_all(settings.PATH_DCB)
    #
    # def test_dcb_no_file_exists(self):
    #     """ Passing the DCB without any files, check if there is any file, if so,
    #      returns the absolute path of the compressed file """
    #     self.assertFalse(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB.Z'))
    #     self.assertFalse(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB'))
    #     self.assertEqual(self._check_files_already_exist(), (True, settings.PATH_DCB + 'P1C11506.DCB.Z'))
    #     self.delete_all(settings.PATH_DCB)
    #
    # def test_dcb_only_decompressed_exists_return_decompressed(self):
    #     """ Passing the DCB only with the P1C11506.DCB file, make sure the file exists,
    #     if so, returns the absolute path of the uncompressed file """
    #     self.create_file(settings.PATH_DCB, 'P1C11506.DCB')
    #     self.assertTrue(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB'))
    #     self.assertFalse(os.path.isfile(settings.PATH_DCB + 'P1C11506.DCB.Z'))
    #     self.assertEqual(self._check_files_already_exist(), (False, settings.PATH_DCB + 'P1C11506.DCB'))
    #     self.delete_all(settings.PATH_DCB)
    #
    # def _check_files_already_exist(self, **kwargs):
    #     input_files = InputFiles()
    #     default = dict(
    #         path=settings.PATH_DCB,
    #         filename='P1C11506.DCB.Z',
    #     )
    #     data = dict(default, **kwargs)
    #     find = input_files._check_files_already_exist(data['path'], data['filename'])
    #     return find
