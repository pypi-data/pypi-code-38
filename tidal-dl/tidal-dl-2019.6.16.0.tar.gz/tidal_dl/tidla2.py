import os
import re
import uuid
import requests

NUM_GET_RETRY = 3
TIDAL_TOKEN = '4zx46pyr9o8qZNRw'
TIDAL_PHONE_TOKEN = 'kgsOOmYk3zShYrNP'
VERSION = '1.9.1'
URL_PRE = 'https://api.tidalhifi.com/v1/'

class TidalAccount(object):
    def __init__(self, user, pwd, byphone=False):
        self.username = None
        self.password = None
        self.sessionid = None
        self.userid = None
        self.countrycode = None
        self.islogin = True
        self.token = TIDAL_TOKEN
        if byphone:
            self.token = TIDAL_PHONE_TOKEN

        self.err = self._login(user, pwd)
        if self.err is not None:
            self.islogin = False

    def _login(self, username, password):
        try:
            postParams = {
                'username': username,
                'password': password,
                'token': self.token,
                'clientUniqueKey': str(uuid.uuid4()).replace('-', '')[16:],
                'clientVersion': VERSION,
            }
            ret = requests.post(URL_PRE + 'login/username',data=postParams).json()
            if 'status' in ret and ret['status'] == 401:
                return "Uername or password err!"
            if 'status' in ret:
                return "Get sessionid err!"

            self.username = username
            self.password = password
            self.userid = ret['userId']
            self.countrycode = ret['countryCode']
            self.sessionid = ret['sessionId']

            ret = requests.get(URL_PRE + 'users/' + str(self.userid),params={'sessionId': self.sessionid}).json()
            if 'status' in ret and not ret['status'] == 200:
                return "Sessionid is unvalid!"
            return None
        except:
            return "Login err!"

class TidalTool(object):
    def __init__(self, account_pc, account_phone):
        self.account_pc = account_pc
        self.account_phone = account_phone

    def _getAccount(self, quality=None):
        if quality == 'LOSSLESS':
            if self.account_phone.islogin:
                return self.account_phone
        if self.account_pc.islogin:
            return self.account_pc
        if self.account_phone.islogin:
            return self.account_phone
        return None

    def _get(self, path, params={}):
        quality = None
        if 'soundQuality' in params:
            quality = params['soundQuality']
        account = self._getAccount(quality)

        for i in range(NUM_GET_RETRY):
            try:
                params['countryCode'] = account.countrycode
                resp = requests.get(
                    URL_PRE + path,
                    headers={'X-Tidal-SessionId': account.sessionid},
                    params=params).json()

                errmsg = None
                if 'status' in resp and resp['status'] == 404 and resp['subStatus'] == 2001:
                    errmsg = '{}. This might be region-locked.'.format(resp['userMessage'])
                elif 'status' in resp and not resp['status'] == 200:
                    errmsg = '{}. Get operation err!'.format(resp['userMessage'])
                return resp, errmsg
            except:
                if i == NUM_GET_RETRY - 1:
                    return None,'Function `Http-Get` Err!'

    def _getList(self, path):
        ret, err = self._get(path, {'limit': 0})
        count   = ret['totalNumberOfItems']
        offset  = 0
        limit   = 100
        retList = []
        while offset < count:
            items, err = self._get(path, {'offset': offset, 'limit': limit})
            if err and err.find('Too big page') >= 0:
                limit = limit - 10
                continue
            if err:
                return retList
            offset = offset + limit
            retList.extend(items['items'])
        return retList

    def _diffAlbumTracks(self, data):
        same = {}
        for item in data['items']:
            if item['version'] is not None:
                item['title'] = item['title'] + '(' + item['version']+')'
            if item['title'] in same:
                same[item['title']] += 1
            else:
                same[item['title']] = 1
        for item in same:
            if same[item] <= 1:
                continue
            index = 1
            for track in data['items']:
                if track['title'] != item:
                    continue
                track['title'] += str(index)
                index += 1
        return data

    def setAccount(self, account_pc, account_phone):
        self.account_pc = account_pc
        self.account_phone = account_phone

    def getAlbum(self, album_id):
        return self._get('albums/' + str(album_id))
    def getTrack(self, track_id):
        return self._get('tracks/' + str(track_id))
    def getVideo(self, video_id):
        return self._get('videos/' + str(video_id))
    def getStreamUrl(self, track_id, quality):
        return self._get('tracks/' + str(track_id) + '/streamUrl', {'soundQuality': quality})
    def getAlbumCoverUrl(self, coverid, size=1280):
        return 'https://resources.tidal.com/images/{0}/{1}x{1}.jpg'.format(coverid.replace('-', '/'), size)
    def getAlbumTracks(self, album_id):
        data, errmsg = self._get('albums/' + str(album_id) + '/tracks')
        if errmsg is None:
            data = self._diffAlbumTracks(data)
        return data,errmsg

    def getPlaylist(self, playlist_id):
        return self._get('playlists/' + playlist_id)
    def getPlaylistItems(self, playlist_id):
        return self._getList('playlists/' + playlist_id + '/items')
    def getPlaylistCoverUrl(self, playlist_uuid, size=1280):
        return 'http://images.tidalhifi.com/im/im?w={1}&h={2}&uuid={0}&rows=2&cols=3&noph'.format(playlist_uuid, size, size)
   
    def getFavorite(self, user_id):
        trackList = self._getList('users/' + str(user_id) + '/favorites/tracks')
        videoList = self._getList('users/' + str(user_id) + '/favorites/videos')
        return trackList, videoList
    def getArtistAlbum(self, artist_id):
        return self._getList('artists/' + str(artist_id) + '/albums')
