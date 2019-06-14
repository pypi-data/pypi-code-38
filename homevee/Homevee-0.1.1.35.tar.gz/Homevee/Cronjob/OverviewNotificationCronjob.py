#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Cronjob import FixedTimeCronjob
from Homevee.Manager.CalendarManager import CalendarManager
from Homevee.Manager.WeatherManager import WeatherManager
from Homevee.Utils.Database import Database
from Homevee.Utils.NotificationManager import NotificationManager


class OverviewNotificationCronjob(FixedTimeCronjob):
    def __init__(self):
        super(OverviewNotificationCronjob, self).__init__(task_name="OverviewNotificationCronjob")

    def task_to_do(self, *args):
        self.send_overview_notifications()

    def get_seconds_to_wait(self, execution_time=None):
        #wait until midnight + 5 minutes
        t = datetime.datetime.today()

        seconds_to_wait = (24-t.hour)*60*60 - ((t.minute * 60) - t.second) + 5*60 #Warten bis 00:05

        return seconds_to_wait

    def send_overview_notifications(self):
        db = Database()

        users = db.select_all("SELECT * FROM USERDATA", {})

        for user in users:
            day_overview = ""

            weather = WeatherManager().get_weather(1)
            weather_text = "Wetter: " + weather[0]['desc'] + ", " + str(weather[0]['temps']['min']) + "°C - " + str(weather[0]['temps']['max']) + "°C"

            today = datetime.datetime.today()
            date_today = today.strftime("%Y-%m-%d")
            calendar = CalendarManager().get_calendar_day_items(user['USERNAME'], date_today)
            calendar_items = calendar['calendar_entries']
            if len(calendar_items) == 0:
                calendar_text = "Keine Termine"
            else:
                if len(calendar_items) > 1:
                    calendar_text = str(len(calendar_items)) + " Termine: "
                    for i in range(0, len(calendar_items)):
                        if i == 0:
                            calendar_text += calendar_items[i]['name'] + " um " + calendar_items[i]['start'] + " Uhr"
                        else:
                            calendar_text += ", " + calendar_items[i]['name'] + " um " + calendar_items[i]['start'] + " Uhr"
                else:
                    calendar_text = "Ein Termin: "+calendar_items[0]['name']+" um "+calendar_items[0]['start']+" Uhr"

            day_overview = weather_text+"\n"+calendar_text

            NotificationManager().send_notification_to_users([user['USERNAME']], "Deine Tagesübersicht", day_overview)