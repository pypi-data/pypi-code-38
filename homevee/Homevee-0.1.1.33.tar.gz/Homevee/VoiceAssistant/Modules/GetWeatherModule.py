#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import random

from Homevee.Helper import Logger
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant import Helper
from Homevee.VoiceAssistant.Modules import VoiceModule

CONTEXT_GET_WEATHER = "CONTEXT_GET_WEATHER"

class VoiceGetWeatherModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['wie',['ist','wird'],'wetter'],
            ['regnet','es'],
            ['gibt','regen'],
            ['wird','regnen']
        ]

    def get_context_key(self) -> int:
        return CONTEXT_GET_WEATHER

    def get_label(self):
        return "getweather"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_weather(username, text, context, db)

    def get_weather(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        weather = db.get_server_data('WEATHER_CACHE')
        weather = json.loads(weather)
        city_name = weather['city']['name']
        weather_list = weather['list']

        now = datetime.datetime.now()

        cur_weekday = now.weekday()

        search_weekday_word, search_weekday = self.get_weekday(text, cur_weekday)

        if (context is not None and search_weekday is None):
            return False

        if search_weekday is None:
            #No day given => output tdays weather
            search_weekday_word = "Heute"
            search_weekday = cur_weekday

        search_daytime = self.get_day_time(text)

        #current day after search day?
        if search_weekday < cur_weekday:
            #add one week to search day, since its next week
            search_weekday += 7

        day_difference = search_weekday - cur_weekday

        #add the difference
        search_date = now + datetime.timedelta(days=day_difference)

        output = None

        for day in weather_list:
            cur_date = datetime.datetime.fromtimestamp(day['dt'])
            if (cur_date.date() == search_date.date()):
                single_time = False
                single_time_string = None
                if search_daytime is not None:
                    single_time = True
                    temp = int(day['temp'][search_daytime])

                    data = [
                        ['bei ' ,['ungefähr', 'in etwa', 'etwa', 'ca.', ''], ' ', temp, ' Grad'],
                        ['und die Temperatur liegt bei ' ,['ungefähr', 'in etwa', 'etwa', 'ca.', ''], ' ', temp, ' Grad'],
                        ['und die Temperatur liegt ', ['ungefähr', 'in etwa', 'etwa', 'ca.', ''], ' bei ', ' ', temp, ' Grad'],
                        ['und es wird ' ,['ungefähr', 'in etwa', 'etwa', 'ca.', ''], ' ', temp, ' Grad haben'],
                        ['und es hat ' ,['ungefähr', 'in etwa', 'etwa', 'ca.', ''], ' ', temp, ' Grad']
                    ]
                    temp_string = Helper.generate_string(data)

                    time_strings = {
                        'morn': ['früh', 'in der Früh'],
                        'day': ['tagsüber'],
                        'eve': ['Abend', 'am Abend'],
                        'night': ['in der Nacht', 'nachts']
                    }
                    single_time_string = random.choice(time_strings[search_daytime])
                else:
                    temp = {'min': int(day['temp']['min']), 'max': int(day['temp']['max'])}

                    if(temp['min'] == temp['max']):
                        data = [
                            ['und die Temperatur ', ['beträgt', 'liegt bei'], ' '+str(temp['max'])+' Grad'],
                            ['bei '+str(temp['min'])+' Grad'],
                            ['bei einer Temperatur von '+str(temp['max'])+' Grad']
                        ]
                    else:
                        data = [
                            ['und die Temperaturen ', ['betragen', 'liegen'], ' zwischen '+str(temp['min'])+' und '+str(temp['max'])+' Grad'],
                            ['bei '+str(temp['min'])+' bis '+str(temp['max'])+' Grad'],
                            ['bei Temperaturen zwischen '+str(temp['min'])+' und '+str(temp['max'])+' Grad']
                        ]
                    temp_string = Helper.generate_string(data)

                weather_ids = []

                for weather in day['weather']:
                    weather_ids.append(weather['id'])

                weather_descs = self.get_weather_description(weather_ids)

                weather_descs_string = None
                for i in range(0, len(weather_descs)):
                    if weather_descs_string is None:
                        weather_descs_string = weather_descs[i]
                    elif i == len(weather_descs)-1:
                        weather_descs_string = ' und '+weather_descs[i]
                    else:
                        weather_descs_string = ', '+weather_descs[i]

                if day_difference <= 2:
                    day_desc_words = ['Heute', 'Morgen', 'Übermorgen']
                    day_string = day_desc_words[day_difference]

                    if single_time_string is not None:
                        day_string += ' '+single_time_string

                else:
                    if single_time_string is None:
                        day_string = Helper.generate_string([
                            ['Am '+search_weekday_word],
                            [search_weekday_word+'s']
                        ])
                    else:
                        day_string = search_weekday_word+' '+single_time_string

                output_data = [
                    [day_string + ' ', ['gibt', 'hat'] ,' es ' + weather_descs_string + ' ' + temp_string + '.']
                ]
                output = Helper.generate_string(output_data)

                Logger.log("set context")
                Helper.set_context(username, self.get_context_key(), {}, db)

        return {'msg_speech': output, 'msg_text': output}

    def get_weekday(self, text, cur_weekday):
        words = text.split(' ')

        #normal weekday
        days = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag']
        for i in range(0, len(days)):
            day = days[i]
            if day in words:
                return day.capitalize(), i

        day_words = ['heute', 'morgen', 'übermorgen']
        for i in range(0, len(day_words)):
            day = day_words[i]
            if day in words:
                output_day = cur_weekday + i

                if output_day >= 7:
                    #subtract one week
                    output_day -= 7

                return day.capitalize(), output_day

        return None, None

    def get_day_time(self, text):
        day_times = [
            {'time': 'morn', 'keywords': ['morgens', 'früh']},
            {'time': 'day', 'keywords': ['tagsüber']},
            {'time': 'eve', 'keywords': ['abends', 'abend']},
            {'time': 'night', 'keywords': ['nachts', 'nacht']}
        ]

        words = text.split(' ')

        for day_time in day_times:
            for keyword in day_time['keywords']:
                if keyword in words:
                    return day_time['time']

        return None

    def get_weather_description(self, codes):
        description_map = {
            #Gewitter
            200: 'Gewitter mit leichtem Regen',
            201: 'Gewitter mit Regen',
            202: 'Gewitter mit starkem Regen',
            210: 'leichte Gewitter',
            211: 'Gewitter',
            212: 'starke Gewitter',
            221: 'Gewitter mit leichtem Regen',
            230: 'Gewitter mit leichtem Regen',
            231: 'Gewitter mit leichtem Regen',
            232: 'Gewitter mit leichtem Regen',

            #Nieselregen
            300: 'Nieselregen',
            301: 'Nieselregen',
            302: 'Nieselregen',
            310: 'Nieselregen',
            311: 'Nieselregen',
            312: 'Nieselregen',
            313: 'Nieselregen',
            314: 'Nieselregen',
            321: 'Nieselregen',

            #Regen
            500: 'leichten Regen',
            501: 'mittelstarken Regen',
            502: 'starken Regen',
            503: 'sehr starken Regen',
            504: 'extremen Regen',
            511: 'gefrierenden Regen',
            520: 'leichte Schauer',
            521: 'Schauer',
            522: 'starke Schauer',
            531: 'starke Schauer',

            #Schnee
            600: 'leichten Schneefall',
            601: 'Schneefall',
            602: 'starken Schneefall',
            611: 'Schneeregen',
            612: 'Schneeregen-Schauer',
            615: 'leichten Regen und Schnee',
            616: 'Regen und Schnee',
            620: 'leichte Schneeschauer',
            621: 'Schneeschauer',
            622: 'starke Schneeschauer',

            #Atmosphäre
            701: 'Nebel',
            711: 'Rauch',
            721: 'Dunst',
            731: 'Staubwirbel',
            741: 'Nebel',
            751: 'Sand',
            761: 'Staub',
            762: 'Vulkanasche',
            771: 'Böen',
            781: 'Tornado',

            #Klar
            800: 'klaren Himmel',

            #Wolken
            801: 'wenige Wolken',
            802: 'aufgelockerte Wolken',
            803: 'aufgelockerte Wolken',
            804: 'bedeckte Bewölkung'
        }

        output = []

        for code in codes:
            if code in description_map:
                output.append(description_map[code])

        return output