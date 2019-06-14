#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import traceback

from Homevee.Helper import Logger
from Homevee.Helper.HomeveeAPI import HomeveeAPI
from Homevee.Utils.Database import Database


class TVPlanManager:
    def __init__(self):
        return

    def get_tv_plan(self, user, type, db: Database = None):
        if db is None:
            db = Database()
        try:
            tv_channels = self.get_tv_channels(user)

            if type == "2015":
                type = "heute2015"
            elif type == "2200":
                type = "heute2200"
            elif type == "jetzt":
                type = "jetzt"
            elif type == "tipps":
                type = "tipps"
            else:
                raise AttributeError("TV-Typ '" + type + "' nicht vorhanden")

            tv_shows = []

            response = HomeveeAPI().get_tv_data(type)

            if(response.status_code == 200):
                tv_data = json.loads(response.response)['tvprogramm']
                for item in tv_data:
                    if type == "tipps" or ((tv_channels is None) or (item['channel'] in tv_channels)):
                        tv_shows.append(item)
                return tv_shows
            else:
                return None
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            return None

    def get_tv_channels(self, user, db: Database = None):
        if db is None:
            db = Database()

        results = db.select_all("SELECT * FROM TV_CHANNELS WHERE USERNAME == :username", {'username': user.username})

        channels = []

        for channel in results:
            channels.append(channel['CHANNEL'])

        return channels

    def get_all_tv_channels(self, user, db: Database = None):
        if db is None:
            db = Database()
        selected_channels = self.get_tv_channels(user)

        response = HomeveeAPI().get_tv_data("channels")

        if(response.status_code == 200):
            all_channels = json.loads(response.response)
            print(all_channels)

            channels = []
            for channel in all_channels['channels']:
                if (channels is None) or (channel not in channels):
                    channels.append({'name': channel, 'selected': (channel in selected_channels)})

            return channels
        else:
            return None

    def set_tv_channels(self, user, json_data, db: Database = None):
        if db is None:
            db = Database()
        result = db.delete("DELETE FROM TV_CHANNELS WHERE USERNAME == :username", {'username': user.username})

        #Abfrage erfolgreich?
        if result:
            channels = json.loads(json_data)

            for channel in channels:
                db.insert("INSERT INTO TV_CHANNELS (USERNAME, CHANNEL) VALUES (?,?)",
                    [user.username, channel])
        else:
            raise Exception