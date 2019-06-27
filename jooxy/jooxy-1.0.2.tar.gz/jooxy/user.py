import json, base64

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            raise Exception('Login required.')
    return checkLogin

class User(object):

    @loggedIn
    def getAllMyPlaylist(self):
        params = dict(reqtype=4, inner=1)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_GETFAV_PATH,
                      params=params, withAuth=True)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    @loggedIn
    def getMyPlaylist(self, myPlaylistId):
        params = dict(reqtype=3, inner=1, listid=myPlaylistId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_GETFAV_PATH,
                      params=params, withAuth=True)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    @loggedIn
    def createPlaylist(self, playlistName):
        playlistName = base64.b64encode(
            bytes(playlistName, "utf-8")).decode("utf-8")
        payload = dict(channel_id=1, from_type=3, items=[
                       dict(gt=0, gl="", mv=0, dv=0, fn=playlistName)])
        r = self._post(self.JOOX_API_DOMAIN + self.JOOX_ADD_DIR_PATH,
                        payload=payload)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    @loggedIn
    def removeMyPlaylist(self, myPlaylistId):
        getMyplaylist = self.getMyPlaylist(myPlaylistId)
        dv = getMyplaylist["detail_ver"]
        payload = dict(
            items=[dict(gt=myPlaylistId, gl="", mv=dv, dv=dv, fn="")])
        r = self._post(self.JOOX_API_DOMAIN + self.JOOX_DEL_DIR_PATH,
                        payload=payload)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    @loggedIn
    def addTracksToMyPlaylist(self, songId, myPlaylistId):
        getMyplaylist = self.getMyPlaylist(myPlaylistId)
        dv = getMyplaylist["detail_ver"]
        payload = dict(
            items=[dict(gt=myPlaylistId, gl=songId, mv=dv, dv=dv, fn="")])
        r = self._post(self.JOOX_API_DOMAIN + self.JOOX_ADD_SONG_PATH,
                        payload=payload)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    @loggedIn
    def removeTracksFromMyPlaylist(self, songId, myPlaylistId):
        getMyplaylist = self.getMyPlaylist(myPlaylistId)
        dv = getMyplaylist["detail_ver"]
        payload = dict(
            items=[dict(gt=myPlaylistId, gl=songId, mv=dv, dv=dv, fn="")])
        
        r = self._post(self.JOOX_API_DOMAIN + self.JOOX_DEL_SONG_PATH,
                        payload=payload)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    @loggedIn
    def getTrackInfo(self, songId):
        params = dict(songid=songId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_GET_SONGINFO_PATH,
                        params=params, withAuth=True)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)