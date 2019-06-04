#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Cronjob import IntervalCronjob
from Homevee.Helper.HomeveeAPI import HomeveeAPI
from Homevee.Manager.APIKeyManager import APIKeyManager
from Homevee.Utils.Database import Database


class WeatherUpdaterCronjob(IntervalCronjob):
    def __init__(self):
        super(WeatherUpdaterCronjob, self).__init__(task_name="WeatherUpdaterCronjob", interval_seconds=15*60)

    def task_to_do(self, *args):
        self.refresh_weather_cache()

    def get_seconds_to_wait(self, execution_time=None):
        t = datetime.datetime.today()

        seconds_to_wait = (15 * 60) - ((t.minute * 60) - t.second) % 15 * 60

        return seconds_to_wait

    def refresh_weather_cache(self):
        db = Database()

        api_key = APIKeyManager().get_api_key("Open Weather Map", db)
        location_id = db.get_server_data("WEATHER_LOCATION_ID")

        try:
            #url = "http://api.openweathermap.org/data/2.5/forecast/daily?id=" + location_id + "&cnt=16&units=metric&lang=de&type=accurate&APPID=" + api_key
            #response = urllib.request.urlopen(url).read()

            response = HomeveeAPI().get_weather(location_id)

            if(response.status_code == 200):
                data = response.response.encode('utf-8')
            else:
                data = "{}"

                # Wetter-Daten in Datenbank schreiben
            db.insert("INSERT OR REPLACE INTO SERVER_DATA (KEY, VALUE) values('WEATHER_CACHE', :response);",
                        {"response": data})

            return True
        except:
            return False