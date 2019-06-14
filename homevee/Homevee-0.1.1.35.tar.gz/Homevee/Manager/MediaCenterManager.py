#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.parse
import urllib.request

from Homevee.DeviceAPI import kodi_api
from Homevee.DeviceAPI.kodi_api import KodiAPI
from Homevee.Exception import NoSuchTypeException
from Homevee.Helper import Logger
from Homevee.Utils.Database import Database

TYPE_KODI = "KODI"

class MediaCenterManager:
    def __init__(self):
        self.kodi_api = KodiAPI()
        return

    def get_media_centers(self, user, db: Database = None):
        if db is None:
            db = Database()
        media_centers = []

        results = db.select_all("SELECT *, MEDIA_CENTER.NAME as MEDIA_CENTER_NAME, ROOMS.NAME as ROOM_NAME FROM MEDIA_CENTER, ROOMS WHERE ROOMS.LOCATION = MEDIA_CENTER.LOCATION", {})

        for result in results:
            if(user.has_permission(result['LOCATION'])):
                item = {'name': result['MEDIA_CENTER_NAME'], 'type': result['TYPE'], 'id': result['ID'],
                        'location': result['LOCATION'], 'value': result['ROOM_NAME']}
                media_centers.append(item)

        return media_centers

    def media_remote_action(self, type, id, remoteaction, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            return self.kodi_api.media_remote_action(self.get_data(id), remoteaction)

    def send_text(self, type, id, text, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            return self.kodi_api.send_text(self.get_data(id), text)

        raise NoSuchTypeException

    def get_music(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_music(self.get_data(id), limit, offset)

            result = json.loads(result)

            songs = []

            song_array = result['result']['songs']

            for song in song_array:
                item = {'title': song['label'], 'artists': song['artist'], 'id': song['songid'], 'album': song['album']}
                songs.append(item)

            return songs

        raise NoSuchTypeException

    def get_artists(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_artists(self.get_data(id), limit, offset)

            result = json.loads(result)

            artists = []

            artist_array = result['result']['artists']

            for artist in artist_array:
                item = {'artist': artist['artist'], 'id': artist['artistid'], 'thumbnail': artist['thumbnail']}
                artists.append(item)

            return artists

        raise NoSuchTypeException

    def get_albums(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_albums(self.get_data(id), limit, offset)

            result = json.loads(result)

            albums = []

            album_array = result['result']['albums']

            for album in album_array:
                item = {'title': album['label'], 'artists': album['artist'], 'id': album['albumid'], 'thumbnail': album['thumbnail']}
                albums.append(item)

            return albums

        raise NoSuchTypeException

    def get_music_genres(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_music_genres(self.get_data(id), limit, offset)

            result = json.loads(result)

            genres = []

            genre_array = result['result']['genres']

            for genre in genre_array:
                item = {'title': genre['label'], 'id': genre['genreid'], 'thumbnail': genre['thumbnail']}
                genres.append(item)

            return genres

        raise NoSuchTypeException

    def get_movie_genres(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_movie_genres(self.get_data(id), limit, offset)

            Logger.log(result)

            result = json.loads(result)

            genres = []

            genre_array = result['result']['genres']

            for genre in genre_array:
                item = {'title': genre['label'], 'id': genre['genreid'], 'thumbnail': genre['thumbnail']}
                genres.append(item)

            return genres

        raise NoSuchTypeException

    def get_shows(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_tv_show(self.get_data(id), limit, offset)

            result = json.loads(result)

            tvshows = []

            tvshow_array = result['result']['tvshows']

            for tvshow in tvshow_array:

                thumbnail = tvshow['thumbnail']
                thumbnail = thumbnail.replace('image://', '')
                thumbnail = urllib.parse.unquote(thumbnail).decode('utf8')

                item = {'title': tvshow['label'], 'genres': tvshow['genre'], 'id': tvshow['tvshowid'],
                        'year': ['year'], 'thumbnail': thumbnail}
                tvshows.append(item)

            return tvshows

        raise NoSuchTypeException

    def get_show_seasons(self, type, id, limit, offset, showid, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_tv_show_seasons(self.get_data(id), showid, limit, offset)

            result = json.loads(result)

            seasons = []

            season_array = result['result']['tvshows']

            for season in season_array:

                thumbnail = season['thumbnail']
                thumbnail = thumbnail.replace('image://', '')
                thumbnail = urllib.parse.unquote(thumbnail).decode('utf8')

                item = {'title': season['label'], 'id': season['seasonid'], 'thumbnail': thumbnail}
                seasons.append(item)

            return seasons

        raise NoSuchTypeException

    def get_show_episodes(self, type, id, limit, offset, showid, seasonid, db: Database = None):
        if db is None:
            db = Database()
        return []

    def get_movies(self, type, id, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        if type == TYPE_KODI:
            result = self.kodi_api.get_movies(self.get_data(id), limit, offset)

            result = json.loads(result)

            movies = []

            movie_array = result['result']['movies']

            for movie in movie_array:

                thumbnail = movie['thumbnail']
                thumbnail = thumbnail.replace('image://', '')
                thumbnail = urllib.parse.unquote(thumbnail).decode('utf8')

                item = {'title': movie['label'], 'genres': movie['genre'], 'id': movie['movieid'],
                        'year': movie['year'], 'thumbnail': thumbnail}
                movies.append(item)

            return movies

        raise NoSuchTypeException

    def get_playing(self, type, id, db: Database = None):
        if db is None:
            db = Database()
        return []

    def get_data(self, id, db: Database = None):
        if db is None:
            db = Database()
        result = db.select_one("SELECT * FROM MEDIA_CENTER WHERE ID == :id", {'id': id})
        return result