""" Unit tests for crackle_api_helpers """
# pylint: disable=relative-import,too-many-instance-attributes
# pylint: disable=too-many-public-methods
from __future__ import print_function
import unittest
from collections import namedtuple
from crackle_api_helpers.api_wrapper import (
    AuthHelpers, APIWrapper, APIWrapperHelpers)


class TestHelpers(unittest.TestCase):
    """ Test all helper methods """

    email_address, password, user_id = '', '', ''

    def setUp(self):
        """ Set up tasks for tests """
        apiconfig = namedtuple('apiconfig',
                               'host partner_id secret geo_code affiliate_id')
        self.config = apiconfig('https://ios-api-us.crackle.com', '22',
                                'KRYDXUKMPKTONARP', 'US',
                                'e2468342-3071-411c-9d3c-7eb8d7cd4d8c')
        self.config_roku = apiconfig('http://roku-v2-api-us.crackle.com', '102',
                                     'MKQUAQNUUWVHGSPG', 'US',
                                     'e2468342-3071-411c-9d3c-7eb8d7cd4d8c')
        self.auth_helpers = AuthHelpers(self.config)
        self.api_wrapper = APIWrapper(self.config)
        self.api_wrapper_helper = APIWrapperHelpers(self.config)
        self.api_wrapper_roku = APIWrapper(self.config_roku)
        self.api_wrapper_helper_roku = APIWrapperHelpers(self.config_roku)

    # Auth
    def test_register_config(self):
        """ Test register_config """
        print('testing register_config')
        self.assertIsNotNone(self.auth_helpers.register_config())

    def test_register_quick(self):
        """ Test register_quick """
        print('testing register_quick')
        message_code, self.email_address, self.password, self.user_id = \
            self.auth_helpers.register_quick()
        assert "OK" in message_code
        assert self.email_address != ''
        assert self.password != ''
        assert self.user_id != ''

    def test_login(self):
        """ Test login """
        print('testing login')
        self.test_register_quick()
        message_code, email_address, password, user_id = \
            self.auth_helpers.login(self.email_address, self.password)
        assert "OK" in message_code
        assert email_address != ''
        assert password != ''
        assert user_id != ''

    def test_logout(self):
        """ Test logout """
        print('testing logout')
        self.test_login()
        assert self.user_id != ''
        print(self.auth_helpers.logout(self.user_id))
        self.assertTrue(self.auth_helpers.logout(self.user_id))

    # Video
    def test_find_media(self):
        """ Test find_media and get_media_id_metadata implicitly """
        print('testing find_media')
        self.assertIsNotNone(self.api_wrapper.find_media())

    def test_find_media_without_adverts(self):
        """ Test find_media_without_adverts """
        print('testing find_media_without_adverts')
        self.assertIsNotNone(self.api_wrapper.find_media_without_adverts())

    def test_find_media_with_preroll(self):
        """ Test find_media_with_preroll """
        print('testing find_media_with_preroll')
        self.assertIsNotNone(self.api_wrapper.find_media_with_preroll())

    def test_find_media_without_preroll(self):
        """ Test find_media_without_preroll """
        print('testing find_media_without_preroll')
        self.assertIsNotNone(self.api_wrapper.find_media_without_preroll())

    def test_find_media_with_two_midrolls(self):
        """ Test find_media_with_two_midrolls """
        print('testing find_media_with_two_midrolls')
        self.assertIsNotNone(self.api_wrapper.find_media_with_two_midrolls())

    def test_find_media_with_preroll_midroll(self):
        """ Test find_media_with_preroll_midroll """
        print('testing find_media_with_preroll_midroll')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_preroll_midroll())

    def test_find_media_with_rating_1(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='Not Rated'))

    def test_find_media_with_rating_2(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='PG'))

    def test_find_media_with_rating_3(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='PG-13'))

    def test_find_media_with_rating_4(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='TV-14'))

    def test_find_media_with_rating_5(self):
        """ Test find_media_with_rating """
        print('testing find_media_with_rating')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_rating(rating='R'))

    def test_find_media_with_min_duration(self):
        """ Test find_media_with_min_duration """
        print('testing find_media_with_min_duration')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_min_duration())

    def test_find_media_with_subtitles(self):
        """ Test find_media_with_subtitles """
        print('testing find_media_with_subtitles')
        self.assertIsNotNone(
            self.api_wrapper.find_media_with_subtitles())

    def test_find_watch_tray_item_with_long_synopsis_1(self):
        """ Test find_media_with_long description """
        print('testing find_watch_tray_item_with_long_synopsis')
        self.assertIsNotNone(
            self.api_wrapper.find_watch_tray_item_with_long_synopsis(
                category='Description', char=150))

    def test_find_watch_tray_item_with_long_synopsis_2(self):
        """ Test find_media_with_long Title """
        print('testing find_watch_tray_item_with_long_synopsis title')
        self.assertIsNotNone(
            self.api_wrapper.find_watch_tray_item_with_long_synopsis(
                category='Title', char=25))

    def test_get_valid_media_ids_type_1(self):
        """ Test test_get_valid_media_ids_type - Promo material """
        print('testing test_get_valid_media_ids_type - Promo material')
        self.assertIsNotNone(
            self.api_wrapper_helper.get_valid_media_ids_type('Promo material'))

    def test_get_valid_media_ids_type_2(self):
        """ Test test_get_valid_media_ids_type - Feature """
        print('testing test_get_valid_media_ids_type - Feature')
        self.assertIsNotNone(
            self.api_wrapper_helper.get_valid_media_ids_type('Feature'))

    def test_get_valid_media_ids_type_3(self):
        """ Test test_get_valid_media_ids_type - Series """
        print('testing test_get_valid_media_ids_type - Series')
        self.assertIsNotNone(
            self.api_wrapper_helper.get_valid_media_ids_type('Series'))

    def test_get_valid_media_ids_type_4(self):
        """ Test test_get_valid_media_ids_type Roku - Promo material """
        print('testing test_get_valid_media_ids_type - Promo material - Roku')
        self.assertIsNotNone(
            self.api_wrapper_helper_roku.get_valid_media_ids_type(
                'Promo material', 'roku'))

    def test_get_valid_media_ids_type_5(self):
        """ Test test_get_valid_media_ids_type Roku - Feature """
        print('testing test_get_valid_media_ids_type - Feature - Roku')
        self.assertIsNotNone(
            self.api_wrapper_helper_roku.get_valid_media_ids_type('Feature', 'roku'))

    def test_get_valid_media_ids_type_6(self):
        """ Test test_get_valid_media_ids_type Roku - Series """
        print('testing test_get_valid_media_ids_type - Series - Roku')
        self.assertIsNotNone(
            self.api_wrapper_helper_roku.get_valid_media_ids_type('Series', 'roku'))

    # Other
    def test_get_watchnow_tray_metadata(self):
        """ Test get_watchnow_tray_metadata """
        print('testing get_watchnow_tray_metadata')
        self.assertIsNotNone(
            self.api_wrapper.get_watchnow_tray_metadata(tray_position=0))

    def test_curation_by_slot_number(self):
        """ Test get_curation  by slot number for Roku """
        print('testing get_curation_by_slot_number for Roku')
        self.assertIsNotNone(
            self.api_wrapper_helper_roku.get_curation_by_slot_number(
                slot_position=1, auth=True, device_type='roku'))

    def test_get_genre_carousel_metadata_1(self):
        """ Test get_genre_carousel_metadata TV """
        print('testing get_genre_carousel_metadata TV')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_carousel_metadata(genre='TV'))

    def test_get_genre_carousel_metadata_2(self):
        """ Test get_genre_carousel_metadata MOVIES """
        print('testing get_genre_carousel_metadata Movies')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_carousel_metadata(genre='Movies'))

    def test_get_genre_all_metadata_1(self):
        """ Test get_genre_all_metadata TV """
        print('testing get_genre_all_metadata TV')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_all_metadata(genre='TV'))

    def test_get_genre_all_metadata_2(self):
        """ Test get_genre_all_metadata MOVIES """
        print('testing get_genre_all_metadata MOVIES')
        self.assertIsNotNone(
            self.api_wrapper.get_genre_all_metadata(genre='Movies'))

    def test_get_show_genres_tv(self):
        """ Test get_genre_all_metadata TV Shows """
        print('testing get_genre_all_metadata using genre_id')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_show_genres_roku(genre='TV'))

    def test_get_show_genres_movies(self):
        """ Test get_genre_all_metadata MOVIES """
        print('testing get_show_genres using genre_id')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_show_genres_roku(genre='Movies'))

    def test_get_genre_metadata_movies(self):
        """ Test get_genre_all_metadata MOVIES """
        print('testing get_genre_metadata_roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_metadata_roku(
                genre='Movies', genre_type='Drama'))

    def test_get_genre_metadata_tv(self):
        """ Test get_genre_all_metadata MOVIES """
        print('testing get_genre_metadata_roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_metadata_roku(
                genre='TV', genre_type='Comedy'))

    def test_get_playlist_metadata_roku(self):
        """ Test get_genre_all_metadata MOVIES """
        print('testing get playlist metadata')
        channel_list = self.api_wrapper_roku.get_genre_metadata_roku(
            genre='TV', genre_type='Comedy')
        channel_id = channel_list[1].get('ID')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_playlist_metadata_roku(
                channel_id=channel_id))

    def test_get_genre_all_metadata_roku_1(self):
        """ Test get_genre_all_metadata TV for Roku alpha-asc"""
        print('testing get_genre_all_metadata '
              'alpha-asc TV for Roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_all_metadata(
                genre='TV', sort='alpha-asc', device_type='roku',
                genre_id='18'))

    def test_get_genre_all_metadata_roku_2(self):
        """ Test get_genre_all_metadata TV for Roku alpha-desc"""
        print('testing get_genre_all_metadata alpha-desc TV for Roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_all_metadata(
                genre='TV', sort='alpha-desc', device_type='roku',
                genre_id='18'))

    def test_get_genre_all_metadata_roku_3(self):
        """ Test get_genre_all_metadata Movies for Roku alpha-asc"""
        print('testing get_genre_all_metadata '
              'alpha-asc Movies for Roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_all_metadata(
                genre='Movies', sort='alpha-asc', device_type='roku',
                genre_id='18'))

    def test_get_genre_all_metadata_roku_4(self):
        """ Test get_genre_all_metadata Movies for Roku alpha-desc"""
        print('testing get_genre_all_metadata alpha-desc Movies for Roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_all_metadata(
                genre='Movies', sort='alpha-desc', device_type='roku',
                genre_id='18'))

    def test_get_genre_all_metadata_roku_5(self):
        """ Test get_genre_all_metadata Movies for Roku date-asc """
        print('testing get_genre_all_metadata date-asc Movies for Roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_all_metadata(
                genre='Movies', sort='date-asc', device_type='roku',
                genre_id='18'))

    def test_get_genre_all_metadata_roku_6(self):
        """ Test get_genre_all_metadata Movies for Roku date-desc """
        print('testing get_genre_all_metadata date-desc Movies for Roku')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_genre_all_metadata(
                genre='Movies', sort='date-desc', device_type='roku',
                genre_id='18'))

    def test_get_series_with_min_episodes(self):
        """ Test get_series_with_min_episodes """
        print('testing get_series_with_min_episodes')
        self.assertIsNotNone(
            self.api_wrapper_roku.get_series_with_min_episodes(min_episodes=1))

if __name__ == '__main__':
    unittest.main()
