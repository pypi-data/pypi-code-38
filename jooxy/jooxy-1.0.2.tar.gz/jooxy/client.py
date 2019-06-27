import json

class Client(object):

    def search(self, q, type, limit, offset):
        params = dict(search_input=q, sin=offset, ein=limit, type=type)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_SEARCH_PATH,
                      params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def searchTracks(self, q, limit=30, offset=0):
        return self.search(q, None, limit, offset)

    def searchArtists(self, q, limit=30, offset=0):
        return self.search(q, 2, limit, offset)

    def searchAlbums(self, q, limit=30, offset=0):
        return self.search(q, 1, limit, offset)

    def searchPlaylist(self, q, limit=30, offset=0):
        return self.search(q, 3, limit, offset)

    def getPlaylistTaglist(self):
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_TAG_LIST_PATH)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getAllPlaylist(self, tagId=None, limit=50, offset=0):
        params = dict(sin=offset, ein=limit, req_type=5, tag_id=tagId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_RECOMMENDED_MORE_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getCategoryPlaylist(self, tagId, limit=50, offset=0):
        return self.getAllPlaylist(tagId, limit, offset)

    def getPlaylist(self, playlistId):
        params = dict(qryDissID=playlistId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_GET_DISS_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getAllAlbum(self, limit=50, offset=0):
        params = dict(sin=offset, ein=limit, req_type=4)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_RECOMMENDED_MORE_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getAlbumInfo(self, albumId):
        params = dict(all=1, albumid=albumId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_GET_ALBUMINFO_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getHotTracksAndArtists(self):
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_HOT_QUERY_PATH)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getTopChartList(self):
        params = dict(song_num=1)

        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_GET_TOPLIST_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getTopChart(self, topId=33, limit=100, offset=0):
        params = dict(sin=offset, ein=limit, topid=topId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_TOPLIST_DETAIL_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getAllArtist(self, limit=49, offset=0):
        params = dict(sin=offset, ein=limit, is_all=1)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_ALL_SINGER_LIST_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getArtistCategory(self):
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_SINGER_CATEGORY_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getCategoryArtists(self, categoryId, limit=49, offset=0):
        params = dict(sin=offset, ein=limit, category_id=categoryId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_ALL_SINGER_LIST_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getArtistTracks(self, singerId, limit=29, offset=0):
        params = dict(sin=offset, ein=limit, cmd=2, singerid=singerId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_ALBUM_SINGER_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getArtistAlbums(self, singerId, limit=29, offset=0):
        params = dict(sin=offset, ein=limit, cmd=1, singerid=singerId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_ALBUM_SINGER_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)

    def getTrackLyric(self, musicId):
        params = dict(musicid=musicId)
        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_LYRIC_PATH,
                        params=params)
        if r.status_code != 200:
            raise("Failed to fetch data.")
        return json.loads(r.text)