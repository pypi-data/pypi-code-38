#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Manager.APIKeyManager import APIKeyManager
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceMovieApiModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['wie', 'ist', 'film'],
            ['wie', ['gut', 'schlecht'], 'ist', 'film'],
            ['ist', 'film', ['gut', 'schlecht']]
        ]

    def get_label(self):
        return "getmovierating"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_movie_rating(username, text, context, db)

    def get_movie_rating(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        api_key = APIKeyManager().get_api_key('TMDB', db)

        words = text.split(" ")

        query = None

        is_query = False

        film_index = -1

        for i in range(0, len(words)):
            word = words[i]
            if is_query:
                if query is None:
                    query = word.capitalize()
                else:
                    query = query + " " + word.capitalize()

            if word == "film":
                if not is_query:
                    film_index = i
                is_query = True

            if is_query and i > film_index and query != None:
                if word == "gut" or word == "schlecht":
                    break

        #url = 'https://api.themoviedb.org/3/movie/'+movie_id+'?api_key='+api_key+'&language=de/'
        #response = urllib2.urlopen(url).read()
        #print(response)

        output = "getmovierating"

        return {'msg_speech': output, 'msg_text': output}