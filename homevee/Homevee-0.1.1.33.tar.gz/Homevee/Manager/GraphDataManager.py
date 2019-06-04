#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Item.Status import *
from Homevee.Manager.SensorDataManager import SensorDataManager
from Homevee.Utils.Database import Database


class GraphDataManager:
    def __init__(self):
        return

    '''Gibt den Sensorwerteverlauf für den gewünschten Zeitraum zurück'''
    def get_graph_data(self, user, room, type, id, von, bis, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return Status(type=STATUS_NO_PERMISSION).get_dict()

        if von == bis:
            datum = datetime.datetime.strptime(von, "%d.%m.%Y").strftime("%Y-%m-%d")
            return self.get_day_data(type, id, datum, db)
        else:
            return self.get_day_min_max(type, id, von, bis, db)

    '''Gibt den Tageswerteverlauf des Sensors zurück'''
    def get_day_data(self, type, id, datum, db: Database = None):
        if db is None:
            db = Database()
        results = db.select_all("""SELECT * FROM 'SENSOR_DATA' WHERE DEVICE_TYPE == :type AND DEVICE_ID == :id 
                AND DATETIME >= :start AND DATETIME < :ende AND VALUE != \"N/A\" ORDER BY DATETIME ASC""",
                    {'type':type, 'id':id, 'start':datum+" 00:00", 'ende':datum+" 23:59"})
        values = []

        for data in results:
            item = {'value':float(data['VALUE']), 'id':id, 'time':data['DATETIME'].replace(datum+" ","")}
            values.append(item)

        return {'values': values, 'einheit': SensorDataManager().get_einheit(type, id)}

    '''Gibt die Höchst- & Tiefstwerte des angegebenen Datumsbereichs zurück'''
    def get_day_min_max(self, type, id, von, bis, db: Database = None):
        if db is None:
            db = Database()
        start = datetime.datetime.strptime(von, "%d.%m.%Y").strftime("%Y-%m-%d")
        ende = datetime.datetime.strptime(bis, "%d.%m.%Y").strftime("%Y-%m-%d")

        values = []

        results = db.select_all("""SELECT MIN(VALUE) as MIN, MAX(VALUE) as MAX, strftime(\"%d.%m.%Y\", DATETIME) as FORMATTED_DATE
             FROM SENSOR_DATA WHERE DEVICE_TYPE == :type AND DEVICE_ID == :id AND DATETIME >= :start 
             AND DATETIME <= :ende AND VALUE != \"N/A\" GROUP BY FORMATTED_DATE ORDER BY DATETIME ASC""",
            {'type': type, 'id': id, 'start': start+' 00:00', 'ende': ende+' 23:59'})

        #print {'type': type, 'id': id, 'start': start, 'ende': ende}

        for data in results:
            item = {'date':data['FORMATTED_DATE'], 'min':data['MIN'], 'max':data['MAX']}

            values.append(item)

        return {'values':values, 'einheit': SensorDataManager().get_einheit(type, id)}