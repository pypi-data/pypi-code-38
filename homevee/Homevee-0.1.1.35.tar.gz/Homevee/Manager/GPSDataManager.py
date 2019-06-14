#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import radians, cos, sqrt, atan2, sin

from Homevee.Utils.Database import Database

MIN_RETENTION_PERIOD = 5 * 60 * 1000 #5 minuten
MAX_DISTANCE = 500 #500 Meter

class GPSDataManager:
    def __init__(self):
        return

    def update_gps(self, user, time, lat, lng, db: Database = None):
        if db is None:
            db = Database()

        self.on_location_change(user, int(time), float(lat), float(lng))

        new_id = db.insert("INSERT INTO GPS_DATA (user, TIMESTAMP, LATITUDE, LONGITUDE) VALUES (:user, :time, :lat, :lng);",
                    {'user': user.username, 'time': time, 'lat': lat, 'lng': lng})

        if new_id != False:
            return True
        else:
            return False

    def on_location_change(self, user, time, lat, lng, db: Database = None):
        if db is None:
            db = Database()
        #determine user location (at work, at school, at home, etc.)
        current_user_location = self.determine_user_location(user, time, lat, lng)
        self.set_user_location(user, current_user_location)

        return

    def determine_user_location(self, user, time, lat, lng, db: Database = None):
        if db is None:
            db = Database()
        #if user is longer than MIN_RETENTION_PERIOD in roughly the same place => update his location status
        #check distance to place => less than MAX_DISTANCE => user is there

        place = self.get_nearest_place(user, lat, lng)

        location_data = db.select_all("SELECT * FROM GPS_DATA WHERE USERNAME = :user ORDER BY TIMESTAMP DESC LIMIT 50", {'user': user.username})
        if place is not None and place['DISTANCE'] <= MAX_DISTANCE:
            for location in location_data:
                if(self.compute_distance(place['LATITUDE'], place['LONGITUDE'], location['LATITUDE'], location['LONGITUDE']) <= MAX_DISTANCE):
                    if(time - int(location['TIMESTAMP']) >= MIN_RETENTION_PERIOD):
                        return place
                else:
                    break

        return None

    def get_nearest_place(self, user, lat, lng, db: Database = None):
        if db is None:
            db = Database()

        place = db.select_one("SELECT *, ((LATITUDE - :lat)*(LATITUDE - :lat)) + ((LONGITUDE - :lng)*(LONGITUDE - :lng)) as DISTANCE FROM PLACES ORDER BY DISTANCE ASC LIMIT 1",
                    {'lat': lat, 'lng': lng})

        return place

    def compute_distance(self, lat1, lng1, lat2, lng2):
        R = 6373000.0

        lat1 = radians(float(lat1))
        lng1 = radians(float(lng1))
        lat2 = radians(float(lat2))
        lng2 = radians(float(lng2))

        dlon = lng2 - lng1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        return distance

    def set_user_location(self, user, place, db: Database = None):
        if db is None:
            db = Database()

        place_id = -1

        if(place is not None):
            place_id = place['ID']

        db.update("UPDATE USERDATA SET CURRENT_LOCATION = :loc WHERE USERNAME = :user",
                    {'loc': place_id, 'user': user.username})

    def get_gps_locations(self, user, db: Database = None):
        if db is None:
            db = Database()

        locations = []

        results = db.select_all("SELECT * FROM GPS_DATA WHERE USERNAME = :user", {'user': user.username})

        for item in results:
            if not self.is_near(locations, item['LATITUDE'], item['LONGITUDE']):
                locations.append({'time': item['TIMESTAMP'], 'latitude': item['LATITUDE'], 'longitude': item['LONGITUDE']})

        return locations

    def is_near(self, locations, lat, lng):
        MIN_DISTANCE_TO_OTHERS = 1000

        for location in locations:
            if (self.compute_distance(location['latitude'], location['longitude'], lat, lng) < MIN_DISTANCE_TO_OTHERS):
                return True
        return False