""" Crackle API Wrapper """
# pylint: disable=too-few-public-methods,no-member,too-many-lines
# pylint: disable=super-init-not-called,too-many-locals
# pylint: disable=too-many-arguments
from __future__ import print_function
import time
from datetime import datetime
from random import shuffle
from collections import namedtuple
import json
import requests
from crackle_api_helpers.authentication.authentication import (
    Authentication)
from crackle_api_helpers.authentication.authentication_helpers import (
    generate_username)
from crackle_api_helpers import AuthKeyMissingError, SESSION


def default_configuration():
    """ Get a default configuration """
    host = ''
    affiliate_id = ''
    partner_id = ''
    secret = ''
    geo_code = 'US'

    apiconfig = namedtuple('apiconfig',
                           'host partner_id secret geo_code affiliate_id')
    return apiconfig(
        host=host,
        partner_id=partner_id,
        secret=secret,
        geo_code=geo_code,
        affiliate_id=affiliate_id)


class AuthHelpers(object):
    """
    Authentication methods
    """
    def __init__(self, configuration=None):
        if not configuration:
            self.configuration = default_configuration()
        else:
            self.configuration = configuration

    def register_config(self):
        """
        GET /Service.svc/register/config
        """
        endpoint = '/Service.svc/register/config'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            return response
        except ValueError as exception:
            print(exception)

    def register_quick(self, **kwargs):
        """
        POST /Service.svc/register/quick
        optional args: prefix, email_domain,
              password, dob, email_address newsletter
        on success:
            return data(message_code, email_address, password, user_id)
        on failure:
            return data(message_code, "", "", "", "")

        """
        endpoint = '/Service.svc/register/quick'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        prefix = kwargs.get('prefix', 'cracklebddautomation+AUTO_JAN_API_')
        email_address = kwargs.get('email_address', None)
        password = kwargs.get('password', 'kyqkuBmn4')
        dob = kwargs.get('dob', '01012000')
        if email_address is None:
            email_domain = kwargs.get('email_domain', 'gmail.com')
            email_address = generate_username(prefix) + '@' + email_domain

        data = {
            "emailAddress": email_address,
            "password": password,
            "dob": dob,
            "sendNewsletter": True
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            data = namedtuple(
                "data", ["message_code", "email", "password", "user_id"])
            response_text = json.loads(response.content)
            user_id = response_text['userID']
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return data(message_code, email_address, password, user_id)
            return data(message_code, "", "", "")
        except ValueError as exception:
            print(exception)

    def login(self, email_address, password):
        """
        POST /Service.svc/login
        on success:
            return data(message_code, email_address, password, user_id)
        on failure:
            return data(message_code, "", "", "", "")
        """
        endpoint = '/Service.svc/login'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        data = {
            "emailAddress": email_address,
            "password": password,
            "geoCode": self.configuration.geo_code,
            "AffiliateUserId": self.configuration.affiliate_id
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            data = namedtuple(
                "data", ["message_code", "email", "password", "user_id"])
            response_text = json.loads(response.content)
            user_id = response_text['userID']
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return data(message_code, email_address, password, user_id)
            return data(message_code, "", "", "")
        except ValueError as exception:
            print(exception)

    def logout(self, user_id):
        """
        POST /Service.svc/logout
        on success:
            return True
        """
        endpoint = '/Service.svc/logout?userId={}'.format(user_id)
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.post(path)
        try:
            response_text = json.loads(response.content)
            message_code = response_text['messageCodeDescription']
            if 'OK' in message_code:
                return True
            return False
        except ValueError as exception:
            print(exception)

    def deactivate(self, user_id):
        """
        POST /Service.svc/deactivate
        on success:
            return True
        """
        endpoint = '/Service.svc/deactivate'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        data = {
            "userId": user_id,
            "reason": 0,
            "comment": ""
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            response_text = json.loads(response.content)
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return True
            return False
        except ValueError as exception:
            print(exception)

    def activate_device(self, user_id, activation_code):
        """
        POST /Service.svc/externaluser/activate
        on success:
            return True
        """
        endpoint = '/Service.svc/externaluser/activate'
        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        data = {
            "RegistrationCode": activation_code,
            "CrackleUserId": user_id
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            response_text = json.loads(response.content)
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return True
            return False
        except ValueError as exception:
            print(exception)

    def deactivate_device(self, user_id):
        """
        POST /Service.svc/externaluser/deactivate
        on success:
            return True
        """
        endpoint = '/Service.svc/externaluser/deactivate'
        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)

        data = {
            "CrackleUserId": user_id,
            "AffiliateUserId": self.configuration.affiliate_id,
            "PartnerId": int(self.configuration.partner_id)
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            response_text = json.loads(response.content)
            message_code = response_text['status']['messageCodeDescription']
            if 'OK' in message_code:
                return True
            return False
        except ValueError as exception:
            print(exception)


class UserHelpers(object):
    """
    User methods
    """
    def __init__(self, configuration):
        self.configuration = configuration

    def continue_watching_remove(self, user_id, media_id):
        """
        Remove a specific item for a user from continue watching
        """
        endpoint = '/Service.svc/user/{0}/continue/watch/{1}/remove'.format(
            user_id, media_id)
        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")
        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        response.raise_for_status()

    def remove_playback_history(self, user_id, media_id):
        """
        Remove playback history from a specific item
        for a user
        """
        endpoint = '/Service.svc/history/remove'
        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        body = ('{{"UserId": "{0}","MediaId": "{1}"}}'
                .format(user_id, media_id))
        response = SESSION.post(path, data=body)
        response.raise_for_status()


class APIWrapperHelpers(object):
    """
    Helper methods for API wrapper
    """

    def __init__(self, configuration):
        self.configuration = configuration

    @staticmethod
    def wait_between_requests():
        """ time to wait in seconds between HTTP requests """
        time.sleep(0.25)

    def get_valid_curations(self, device_type=None, preview=True):
        """ Returns a list of valid curations """
        if device_type == "roku":
            if preview:
                endpoint = '/Service.svc/curation/preview/homepage/{}/1000'.format(
                    self.configuration.geo_code)
            else:
                endpoint = '/Service.svc/curation/homepage/{}'.format(
                    self.configuration.geo_code)
        else:
            endpoint = '/Service.svc/curation/homepage/false/{}'.format(
                self.configuration.geo_code)

        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            curations = response_text['Result']['Slots']
            return [curation['Id'] for curation in curations]
        except ValueError as exception:
            print(exception)

    def get_curation_by_slot_number(self, slot_position, auth=True,
                                    device_type=None):
        """ Returns the curation metadata at a given slot position """
        if device_type == "roku":
            endpoint = '/Service.svc/curation/preview/homepage/{}/1000'.format(
                self.configuration.geo_code)
        else:
            endpoint = '/Service.svc/curation/homepage/false/{}'.format(
                self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            curations = response_text['Result']['Slots']
            return ([curation for curation in curations if
                     curation['SlotPosition'] == slot_position][0])
        except ValueError as exception:
            print(exception)

    def get_assets_metadata(self, curation_id, auth=True):
        """ Returns the metadata of all assets for a given curation
        return: List of assets metadata
        """
        endpoint = '/Service.svc/curation/{0}/{1}'.format(
            curation_id, self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            media_items = response_text['Result']['Items']
            return [media_item['MediaInfo'] for media_item in media_items]
        except ValueError as exception:
            print(exception)

    def get_valid_media_ids(self, device_type=None):
        """ Returns a randomised list of valid media IDs """
        curation_ids = self.get_valid_curations(device_type=device_type)
        media_ids = []

        for curation_id in curation_ids:
            endpoint = '/Service.svc/curation/{0}/{1}'.format(
                curation_id, self.configuration.geo_code)

            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                response_text = json.loads(response.content)
                media_items = response_text['Result']['Items']
                for media_item in media_items:
                    media_ids.append(media_item['MediaInfo'].get('Id'))
            except ValueError as exception:
                print(exception)
            APIWrapperHelpers.wait_between_requests()
        shuffle(media_ids)
        return media_ids

    def get_valid_media_ids_type(self, media_type, device_type=None):
        """ Returns a list of media ids of the specified type
        media_type: 'Promo material', 'Feature', 'Series'
        """
        curation_ids = self.get_valid_curations(device_type=device_type)
        media_ids = []

        for curation_id in curation_ids:
            endpoint = '/Service.svc/curation/{0}/{1}'.format(
                curation_id, self.configuration.geo_code)

            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                response_text = json.loads(response.content)
                media_items = response_text['Result']['Items']
                for media_item in media_items:
                    if media_item['MediaInfo'].get('Type') == media_type:
                        media_ids.append(media_item['MediaInfo'].get('Id'))
            except ValueError as exception:
                print(exception)
            APIWrapperHelpers.wait_between_requests()
        shuffle(media_ids)
        return set(media_ids)

    def get_media_id_metadata(self, media_id):
        """
        Get the metadata for a video (media_id)
        return: json response if successful
                False if the video does not exist or has expired
        """
        endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                    .format(media_id, self.configuration.geo_code))

        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print("HTTP Error: Call to {0} responded with HTTP status: "
                      "{1}".format(path, response.status_code))
                return False
            response_text = json.loads(response.content)
            expiry_time = response_text['RightsExpirationDate']
            if not expiry_time:
                expiry_time = response_text['ExpirationDate']
            expiry_time = (datetime.strptime(expiry_time,
                                             "%m/%d/%Y %I:%M:%S %p"))
            if expiry_time < datetime.now():
                print('Asset has expired')
                return False
            return response_text if response_text else False
        except ValueError as exception:
            print(exception)


class APIWrapper(AuthHelpers):
    """
    Crackle API Wrapper methods
    """
    def __init__(self, configuration=None, device_type=None):
        if not configuration:
            self.configuration = default_configuration()
        else:
            self.configuration = configuration
        self.api_helpers = APIWrapperHelpers(self.configuration)
        self.media_ids = self.api_helpers.get_valid_media_ids(
            device_type=device_type)

    def find_media(self):
        """
        Find any media item
        returns: ('media_id', 'short_name', 'media_duration')
        """
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))
            auth = Authentication(self.configuration, endpoint)

            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                duration_in_seconds = response_text['DurationInSeconds']
                print('found media item')
                data = namedtuple(
                    "data", ["media_id", "short_name", "duration_in_seconds"])
                return data(media_id, short_name, duration_in_seconds)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media item was found')
        return None

    def find_media_without_adverts(self):
        """
        Find a media item without any adverts
        returns: ('media_id', 'short_name', 'media_duration')
        """
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                duration_in_seconds = response_text['DurationInSeconds']
                chapters = response_text['Chapters']
                if not chapters:
                    print('found media with no adverts')
                    data = namedtuple(
                        "data",
                        ["media_id", "short_name", "duration_in_seconds"])
                    return data(media_id, short_name, duration_in_seconds)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items without adverts were found')
        return None

    def find_media_with_preroll(self):
        """
        Find a media item with a preroll
        returns: ('media_id', 'short_name')
        """
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                chapters = response_text['Chapters']
                if not chapters:
                    continue
                pre_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'pre-roll']
                if not pre_rolls:
                    continue
                print('found media with pre-roll')
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items with a preroll were found')
        return None

    def find_media_without_preroll(self):
        """
        Find a media item without a preroll
        returns: ('media_id', 'short_name')
        """
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                chapters = response_text['Chapters']
                if not chapters:
                    print('found media with no pre-roll (no adverts)')
                    return data(media_id, short_name)
                pre_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'pre-roll']
                if not pre_rolls:
                    print('found media with no pre-roll (has mid-rolls)')
                    return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items without a preroll were found')
        return None

    def find_media_with_two_midrolls(self):
        """
        Find a media item with at least two midrolls
        returns: ('media_id', 'short_name', [midroll timestamps (seconds)])
        """
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = (response_text['ParentChannelDetailsSummary']
                              ['ShortName'])
                chapters = response_text['Chapters']
                if not chapters:
                    continue
                mid_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'']
                if not len(mid_rolls) >= 2:
                    continue
                print('found media with at least two midrolls')
                mid_roll_timestamps = \
                    [ad['StartTimeInMilliSeconds'] / 1000 for ad in mid_rolls]
                data = namedtuple(
                    "data", ["media_id", "short_name", "mid_roll_timestamps"])
                return data(media_id, short_name, mid_roll_timestamps)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items with at least two midrolls were found')
        return None

    def find_media_with_preroll_midroll(self):
        """
        Find a media item with a preroll and at least one midroll
        returns: ('media_id', 'short_name', [advert timestamps])
        """
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = (response_text['ParentChannelDetailsSummary']
                              ['ShortName'])
                chapters = response_text['Chapters']
                if not chapters:
                    continue
                pre_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'pre-roll']
                if not pre_rolls:
                    continue
                mid_rolls = \
                    [ad for ad in chapters if ad['Name'] == u'']
                if not len(mid_rolls) >= 1:
                    continue
                print('found media with a preroll and at least one midroll')
                mid_roll_timestamps = \
                    [ad['StartTimeInMilliSeconds'] / 1000 for ad in mid_rolls]
                advert_timestamps = [0] + mid_roll_timestamps
                data = namedtuple(
                    "data", ["media_id", "short_name", "advert_timestamps"])
                return data(media_id, short_name, advert_timestamps)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items with a preroll and at least one midroll found')
        return None

    def find_media_with_rating(self, rating='Not Rated'):
        """
        Find a media item with the given rating
        rating: 'Not Rated', 'PG' 'PG-13', 'TV-14', 'R'
        returns: ('media_id', 'short_name', 'name')

        """
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = \
                    response_text['ParentChannelDetailsSummary']['ShortName']
                name = response_text['ParentChannelDetailsSummary']['Name']
                rating_result = response_text['Rating']
                if rating != rating_result:
                    continue
                print('found media matching the provided rating')
                data = namedtuple(
                    "data", ["media_id", "short_name", "name"])
                return data(media_id, short_name, name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items matching the provided rating were found')
        return None

    def find_media_with_min_duration(self, min_duration_mins=1):
        """
        Find a media item with the minimum duration
        min_duration: minimum duration in minutes
        returns: ('media_id', 'short_name')

        """
        min_duration = min_duration_mins * 60
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with"
                        " HTTP status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                short_name = (response_text['ParentChannelDetailsSummary']
                              ['ShortName'])
                media_duration = response_text['DurationInSeconds']
                if int(media_duration) < min_duration:
                    continue
                print('found media item matching the minimum duration')
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items matching the minimum required duration found')
        return None

    def find_media_with_subtitles(self):
        '''
        Find a media item with subtitles
        returns: ('media_id', 'short_name')

        '''
        shuffle(self.media_ids)
        for media_id in self.media_ids:
            endpoint = ('/Service.svc/details/media/{0}/{1}?format=json'
                        .format(media_id, self.configuration.geo_code))

            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

            path = '{0}{1}'.format(self.configuration.host, endpoint)
            response = SESSION.get(path)
            try:
                if not response.status_code == requests.codes.ok:
                    print(
                        "HTTP Error: Call to {0} responded with HTTP"
                        " status: {1}".format(
                            path, response.status_code))
                    continue
                response_text = json.loads(response.content)
                subtitles = response_text['ClosedCaptionFiles']
                if not subtitles:
                    continue
                print('found media with subtitles')
                short_name = (response_text['ParentChannelDetailsSummary']
                              ['ShortName'])
                data = namedtuple(
                    "data", ["media_id", "short_name"])
                return data(media_id, short_name)
            except ValueError as exception:
                print(exception)
            self.api_helpers.wait_between_requests()
        print('no media items with subtitles were found')
        return None

    def find_watch_tray_item_with_long_synopsis(
            self, content_type='Feature', category='Title', char=50):
        '''
        Get all the data from Watch Tray
        '''
        data_list = self.api_helpers.get_curation_by_slot_number(
            slot_position=1, auth=True, device_type='roku')

        # Variables to hold the final values
        filtered_data = []

        # Iterate over data_list and filter it based on the 'Type'
        for i, item in enumerate(data_list.get('Items')):
            media = item.get('MediaInfo')
            if media.get('Type') == content_type and i != 0:
                data_paylaod = {}
                data_paylaod['Media Info'] = media
                data_paylaod['Position'] = i + 1
                filtered_data.append(data_paylaod)

        # Iterate over the filtered data, to further
        # filter based on 'Category'
        data_required = {}
        for item in filtered_data:
            media = item.get('Media Info')
            # Capture the media that fits the character criteria
            if len(media.get(category).encode('utf8')) > char:
                data_required = item
                break
        if not filtered_data:
            raise Exception(
                'No media found for the category {0}. '
                '\n{1}'.format(category, data_list))
        return data_required

    def get_watchnow_tray_metadata(self, tray_position=0):
        """ Get metatdata for all items in a Watch Now tray (slot)
        Platforms - iOS
        returns: list of dictionaries. one dictionary per item.
        """
        curation = self.api_helpers.get_curation_by_slot_number(
            tray_position + 1)
        if curation:
            return self.api_helpers.get_assets_metadata(curation['Id'])
        return None

    def get_genre_carousel_metadata(self, genre='TV', auth=False):
        """ Get metadata for all items in a Genre page (TV, Movie) Spotlight carousel
        Platforms - iOS
        genres: TV, Movies
        returns: list of dictionaries. one dictionary per item.
        """
        if genre and 'TV' in genre:
            genre = 'Shows'
        elif genre and 'Movies' in genre:
            pass
        else:
            raise Exception('Invalid genre value passed to method')
        endpoint = '/Service.svc/curation/{0}/{1}'.format(
            genre, self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print("HTTP Error: Call to {0} responded with HTTP status: "
                      "{1}".format(path, response.status_code))
                return None
            response_text = json.loads(response.content)
            return response_text['Result']['Slots']
        except ValueError as exception:
            print(exception)
            return None

    def get_genre_all_metadata(self, genre='TV', auth=False, sort=None,
                               device_type=None, genre_id=None):
        """ Get the metadata for all items on a TV or Movies page.
        Platforms - iOS, Cavendish, Roku
        genre: TV, Movies
        device_type: None or roku
        Roku only:
            sort: alpha-asc, alpha-desc, date-asc, date-desc
            genre_id: the integer ID of the sub-genre (eg: Comedy)
        returns: list of dictionaries. one dictionary per item.
        """
        if genre and 'TV' in genre:
            genre = 'shows'
        elif genre and 'Movies' in genre:
            genre = 'movies'
        else:
            raise Exception('Invalid genre value passed to method')

        if device_type == 'roku':
            if not genre_id:
                raise Exception('Genre Id is missing. '
                                'Please provide genre id.')
            endpoint = '/Service.svc/browse/{0}/full/{1}/{2}/{3}'.format(
                genre, genre_id, sort, self.configuration.geo_code)
        else:
            endpoint = (
                '/Service.svc/browse/{0}/all/all/alpha/{1}/500/1'.format(
                    genre, self.configuration.geo_code))

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print("HTTP Error: Call to {0} responded with HTTP status: "
                      "{1}".format(path, response.status_code))
                return None
            response_text = json.loads(response.content)
            return response_text['Entries']
        except ValueError as exception:
            print(exception)
            return None

    def get_series_with_min_episodes(self, min_episodes=1, auth=False):
        """ Get the metadata for all TV episodes that have at least
        min_episodes episodes
        returns: list of dictionaries. one dictionary per item
        """
        endpoint = '/Service.svc/curation/Shows/{}'.format(
            self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print("HTTP Error: Call to {0} responded with HTTP status: "
                      "{1}".format(path, response.status_code))
                return None
            shows = []
            response_text = json.loads(response.content)
            # 'Curation' is 'show' in this context
            curations = response_text['Result']['Slots']
            curation_ids = [curation['Id'] for curation in curations]
            for curation_id in curation_ids:
                episodes = self.api_helpers.get_assets_metadata(curation_id)
                if len(episodes) > min_episodes:
                    curation_metadata = ([curation for curation in curations
                                          if curation['Id'] == curation_id][0])
                    shows.append(curation_metadata)
            print('Found {0} shows with at least {1} episodes'.format(
                len(shows), min_episodes))
            return shows
        except ValueError as exception:
            print(exception)
            return None

    def get_genre_metadata(
            self, genre='TV', sub_genre='Comedy', sort='alpha-asc'):
        """ Get metadata based on genre, sub genre and sorting
        :returns list of dictionaries. One dictionary per item"""
        return self.get_genre_metadata_roku(
            genre=genre, genre_type=sub_genre, sort=sort)

    def get_sub_genres(self, genre='TV', auth=True):
        """ Get a list of all known Show/Movie sub genres
        returns: list of dictionaries. one dictionary per item
        """
        return self.get_show_genres_roku(genre=genre, auth=auth)

    def get_genre_metadata_roku(
            self, genre='TV', genre_type='Comedy', sort='alpha-asc'):
        """ Get metadata based on genre type and correspondent id
        for Roku
        :returns list of dictionaries. One dictionary per item"""
        genre_type_id = None
        response = self.get_show_genres_roku(genre=genre)
        for item in response:
            api_genre_type = item.get('Name')
            if api_genre_type == genre_type:
                genre_type_id = item.get('ID')
                break
        if not genre_type_id:
            raise Exception(
                "Genre type {0} is not found from the "
                "list {1}".format(genre_type, str(response)))

        metadata_based_on_id = self.get_genre_all_metadata(
            genre=genre, auth=True, genre_id=genre_type_id,
            sort=sort, device_type='roku')
        return metadata_based_on_id

    def get_show_genres_roku(self, genre='TV', auth=True):
        """ Get a list of all known Show genres for Roku
        returns: list of dictionaries. one dictionary per item
        """
        if genre and 'TV' in genre:
            genre = 'shows'
        elif genre and 'Movies' in genre:
            genre = 'movies'
        else:
            raise Exception('Invalid genre value passed to method')

        endpoint = '/Service.svc/genres/{0}/all/{1}?format=json'.format(
            genre, self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print("HTTP Error: Call to {0} responded with HTTP status: "
                      "{1}".format(path, response.status_code))
                return None
            response_text = json.loads(response.content)
            return response_text['Items']
        except ValueError as exception:
            print(exception)
            return None

    def get_playlist_metadata_roku(self, auth=True, channel_id=None):
        """ Get list of videos associated with the selected video i.e
        for TV shows, list of seasons and episodes will be returned """
        endpoint = (
            '/Service.svc/channel/{0}/playlists/all/{1}?format=json'.format(
                channel_id, self.configuration.geo_code))

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            if not response.status_code == requests.codes.ok:
                print("HTTP Error: Call to {0} responded with HTTP status: "
                      "{1}".format(path, response.status_code))
                return None
            response_text = json.loads(response.content)
            return response_text['Playlists']
        except ValueError as exception:
            print(exception)
            return None


class APIWrapperAnimaxPin(AuthHelpers):
    """
    Animax send-pin endpoint wrapper
    """
    def __init__(self, configuration):
        self.configuration = configuration

    def get_auth_pin(self, dialing_code, phone_number, country_code):
        """ Get the four digit pin from the send-pin endpoint
        platforms - Animax web
        returns: four digit pin
        """
        auth = Authentication(self.configuration)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        number = phone_number[len(dialing_code):]
        body = ('{{"Phone": "{0}","CountryCode": "{1}",'
                '"DialingCode": "{2}","Number": "{3}"}}'
                .format(phone_number, country_code, dialing_code, number))
        response = SESSION.post(self.configuration.host, data=body)
        try:
            response_text = json.loads(response.content)
            return response_text['status']['message']
        except ValueError as exception:
            print(exception)
            return None


class APIWrapperAnimax(AuthHelpers):
    """
    Animax-specific API Wrapper methods
    """
    def __init__(self, configuration=None):
        if not configuration:
            self.configuration = default_configuration()
        else:
            self.configuration = configuration

    def get_homepage_slideshow_metadata(self, auth=False):
        """ Get metadata for all items in the homepage top slideshow
        platforms - Animax web
        ui component - Homepage slideshow
        returns: list of dictionaries. one dictionary per item
        """
        endpoint = '/Service.svc/slideshow/home/{0}?format=json'.format(
            self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            return response_text['slideList']
        except ValueError as exception:
            print(exception)
            return None

    def get_show_genres(self, auth=False):
        """ Get a list of all known Show genres
        returns: list of dictionaries. one dictionary per item
        """
        endpoint = '/Service.svc/genres/shows/all/{0}?format=json'.format(
            self.configuration.geo_code)

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            return response_text['Items']
        except ValueError as exception:
            print(exception)
            return None

    def get_shows_metadata(self, video_type='full', genre='all',
                           sort='date-desc', count=20, auth=False):
        """ Get metadata for all Shows
        platforms - Animax web
        ui component - Show page media grid
        video_type: 'all', full', 'clips', 'trailers'
        genre: 'all' or an integer genre id returned from get_shows_genres()
        sort: date-desc, date-asc, alpha-asc, alpha-desc
        count: max number of items to retrieve
        returns: list of dictionaries. one dictionary per item
        """
        endpoint = ("/Service.svc/browse/shows/{0}/{1}/"
                    "{2}/{3}/{4}/1?format=json"
                    .format(video_type, genre, sort,
                            self.configuration.geo_code, count))

        if auth:
            auth = Authentication(self.configuration, endpoint)
            if not auth.key:
                raise AuthKeyMissingError(
                    "API access requires generation of an auth key")

            SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        try:
            response_text = json.loads(response.content)
            return response_text['Entries']
        except ValueError as exception:
            print(exception)
            return None
