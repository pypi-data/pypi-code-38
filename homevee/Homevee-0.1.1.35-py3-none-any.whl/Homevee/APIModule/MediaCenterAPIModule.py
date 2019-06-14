from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.MediaCenterManager import MediaCenterManager

ACTION_KEY_GET_MEDIA_CENTERS = "getmediacenters"
ACTION_KEY_CONTROL = "mediacentercontrol"
ACTION_KEY_SEND_TEXT = "mediacentersendtext"
ACTION_KEY_MUSIC = "mediacentermusic"
ACTION_KEY_ARTISTS = "mediacenterartists"
ACTION_KEY_ALBUMS = "mediacenteralbums"
ACTION_KEY_MUSIC_GENRES = "mediacentermusicgenres"
ACTION_KEY_TV_SHOWS = "mediacentertvshows"
ACTION_KEY_TV_SHOW_SEASONS = "mediacentertvshowseasons"
ACTION_KEY_TV_SHOW_EPISODES = "mediacentertvshowepisodes"
ACTION_KEY_MOVIES = "mediacentermovies"
ACTION_KEY_MOVIE_GENRES = "mediacentermoviegenres"
ACTION_KEY_PLAYING = "mediacenterplaying"

class MediaCenterAPIModule(APIModule):
    def __init__(self):
        super(MediaCenterAPIModule, self).__init__()
        self.manager = MediaCenterManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_MEDIA_CENTERS: self.get_media_centers,
            ACTION_KEY_CONTROL: self.control,
            ACTION_KEY_SEND_TEXT: self.send_text,
            ACTION_KEY_MUSIC: self.get_music,
            ACTION_KEY_ARTISTS: self.get_artists,
            ACTION_KEY_ALBUMS: self.get_albums,
            ACTION_KEY_MUSIC_GENRES: self.get_music_genres,
            ACTION_KEY_TV_SHOWS: self.get_tv_shows,
            ACTION_KEY_TV_SHOW_SEASONS: self.get_tv_show_seasons,
            ACTION_KEY_TV_SHOW_EPISODES: self.get_tv_show_episodes,
            ACTION_KEY_MOVIES: self.get_movies,
            ACTION_KEY_MOVIE_GENRES: self.get_movie_genres,
            ACTION_KEY_PLAYING: self.get_playing
        }

        return mappings

    def get_media_centers(self, user, request, db):
        data = self.manager.get_media_centers(user, db)
        return Status(type=STATUS_OK, data={'mediacenters': data})

    def control(self, user, request, db):
        data = self.manager.media_remote_action(request['type'], request['id'], request['remoteaction'], db)
        return Status(type=STATUS_OK, data=data)

    def send_text(self, user, request, db):
        data = self.manager.send_text(request['type'], request['id'], request['text'], db)
        return Status(type=STATUS_OK, data=data)

    def get_music(self, user, request, db):
        data = self.manager.get_music(request['type'], request['id'],
                                      request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'music': data})

    def get_artists(self, user, request, db):
        data = self.manager.get_artists(request['type'], request['id'],
                                        request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'artists': data})

    def get_albums(self, user, request, db):
        data = self.manager.get_albums(request['type'], request['id'],
                                       request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'albums': data})

    def get_music_genres(self, user, request, db):
        data = self.manager.get_music_genres(request['type'], request['id'],
                                             request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'genres': data})

    def get_tv_shows(self, user, request, db):
        data = self.manager.get_shows(request['type'], request['id'],
                                      request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'shows': data})

    def get_tv_show_seasons(self, user, request, db):
        data = self.manager.get_show_seasons(request['type'], request['id'], request['limit'],
                                             request['offset'], request['showid'], db)
        return Status(type=STATUS_OK, data={'seasons': data})

    def get_tv_show_episodes(self, user, request, db):
        data = self.manager.get_show_episodes(request['type'], request['id'], request['limit'],
                                              request['offset'], request['showid'],
                                              request['seasonid'], db)
        return Status(type=STATUS_OK, data={'episodes': data})

    def get_movies(self, user, request, db):
        data = self.manager.get_movies(request['type'], request['id'],
                                       request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'movies': data})

    def get_movie_genres(self, user, request, db):
        data = self.manager.get_movie_genres(request['type'], request['id'],
                                             request['limit'], request['offset'], db)
        return Status(type=STATUS_OK, data={'genres': data})

    def get_playing(self, user, request, db):
        data = self.manager.get_playing(request['type'], request['id'], db)
        return Status(type=STATUS_OK, data=data)