#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.parse
import urllib.request


def media_remote_action(data, action):
    if action == "toggleplay":
        player = get_active_player(data)

        if player is None:
            return "notplaying"

        command = {
            'jsonrpc': '2.0', 'method': 'Player.PlayPause', 'params': {'playerid': int(player['playerid'])}, 'id': int(1)
        }

        result = send_kodi_command(command, data)

        result = json.loads(result)

        #print result

        if result['result']['speed'] is 0:
            return "play"
        elif result['result']['speed'] is 1:
            return "pause"
        else:
            return "error"
    elif action == "up":
        method = "Input.Up"
    elif action == "down":
        method = "Input.Down"
    elif action == "left":
        method = "Input.Left"
    elif action == "right":
        method = "Input.Right"
    elif action == "select":
        method = "Input.select"
    elif action == "home":
        method = "Input.Home"
    elif action == "menu":
        method = "Input.ContextMenu"
    elif action == "volumedown":
        method = ""
    elif action == "volumeup":
        method = ""
    elif action == "togglemute":
        method = "Application.SetMute"
    else:
        return "nosuchaction"

    command = {
        'jsonrpc': '2.0', 'method': method, 'id': int(1)
    }

    return send_kodi_command(command, data)


def get_movies(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovies', 'params':{
            'properties':['thumbnail', 'genre', 'year'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libMovies'
    }

    return send_kodi_command(command, data)

def get_tv_shows(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params':{
            'properties':['thumbnail', 'genre', 'year'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libTvShows'
    }

    return send_kodi_command(command, data)

def get_music(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'AudioLibrary.GetSongs', 'params':{
            'properties':['artist', 'album', 'track'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libSongs'
    }

    return send_kodi_command(command, data)

def get_artists(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'AudioLibrary.GetArtists', 'params':{
            'properties':['thumgnail'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libArtists'
    }

    return send_kodi_command(command, data)

def get_music_genres(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'AudioLibrary.GetGenres', 'params':{
            'properties':['thubmnail', 'title'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libGenres'
    }

    return send_kodi_command(command, data)

def get_albums(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'AudioLibrary.GetAlbums', 'params':{
            'properties':['artist', 'title', 'thumbnail'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libAlbums'
    }

    return send_kodi_command(command, data)

def get_movie_genres(data, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'VideoLibrary.GetGenres', 'params':{'type':'movie',
            'properties':['thumbnail', 'title'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label'}},'id': 'libGenres'
    }

    return send_kodi_command(command, data)

def get_tv_show_seasons(data, show_id, limit, offset):
    command = {
        'jsonrpc': '2.0', 'method': 'VideoLibrary.GetSeasons', 'params':{
            'properties':['thumbnail'], 'limits':{'start': int(offset), 'end': int(offset)+int(limit)},
            'sort':{'order': 'ascending', 'method': 'label', 'ignorearticel': True}},'id': 'libSeasons', 'tvshowid': show_id
    }

    return send_kodi_command(command, data)

def send_text(data, text):
    command = {
        'jsonrpc': '2.0', 'method': 'Input.SendText', 'params': {'text': text, 'done': True}, 'id': 1
    }

    return send_kodi_command(command, data)

def get_active_player(data):
    command = {
        'jsonrpc': '2.0', 'method': 'Player.GetActivePlayers', 'id': 1
    }

    result = send_kodi_command(command, data)

    result = json.loads(result)

    #print result

    for player in result['result']:
        #print player
        return player

    return None

#def remote_action(data, action):

def send_kodi_command(command, data):

    command = json.dumps(command)

    #print command

    #command = '{"jsonrpc": "2.0","method": "VideoLibrary.GetMovies","params": {},"id": "libMovies"}'
    #print command

    ip = data['IP']

    port = data['PORT']

    if port is not "" and port is not None:
        port = ":" + port
    else:
        port = ""

    link = "http://"+ip+port+"/jsonrpc?request="+urllib.parse.quote(command)

    #print link

    result = urllib.request.urlopen(link).read()

    return result