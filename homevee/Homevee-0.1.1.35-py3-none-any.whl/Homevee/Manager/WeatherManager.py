#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json

from Homevee.Utils.Database import Database


class WeatherManager:
    def __init__(self):
        return

    def get_weather(self, daycount, db: Database = None):
        if db is None:
            db = Database()

        try:
            if daycount > 16:
                daycount = 16

            weather_data = json.loads(db.get_server_data("WEATHER_CACHE"))

            days = weather_data['list']

            output = []

            for i in range(0, min(len(days), daycount)):
                day = days[i]

                relative_days = ["Heute", "Morgen", "Übermorgen"]
                day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

                if i > 2:
                    date = datetime.datetime.fromtimestamp(day['dt'])

                    week_day_number = date.weekday()

                    date = day_names[week_day_number]+", "+date.strftime('%d.%m.')
                else:
                    date = relative_days[i]

                city_name = weather_data['city']['name']

                icon_link = "http://openweathermap.org/img/w/"+day['weather'][0]['icon']+".png"

                weather_desc = day['weather'][0]['description']
                icon = day['weather'][0]['icon']

                pressure = None
                if "pressure" in day:
                    pressure = day['pressure']

                humidity = None
                if "humidity" in day:
                    humidity = day['humidity']

                wind_speed = None
                if "speed" in day:
                    wind_speed = float(day['speed'])*3.6

                wind_direction = None
                if "deg" in day:
                    wind_direction = day['deg']

                clouds = None
                if "clouds" in day:
                    clouds = day['clouds']

                rain = None
                if "rain" in day:
                    rain = day['rain']

                snow = None
                if "snow" in day:
                    snow = day['snow']

                day_item = {'city':city_name, 'date':date, 'temps':day['temp'], 'icon':icon_link, 'iconid':icon,
                            'desc':weather_desc, 'pressure':pressure, 'humidity':humidity, 'windspeed':wind_speed,
                            'winddirection': wind_direction, 'clouds':clouds, 'rain':rain, 'snow':snow}

                output.append(day_item)

            return output
        except:
            return None

    def set_weather_city_id(self, request, db: Database = None):
        if db is None:
            db = Database()
        return None

    def get_weather_city_list(self, db):
        try:
            return db.get_server_data("WEATHER_CITY_CACHE")
        except:
            return None