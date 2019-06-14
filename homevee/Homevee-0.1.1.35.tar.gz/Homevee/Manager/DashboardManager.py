#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import traceback

from Homevee.Helper import Logger
from Homevee.Item.Room import Room
from Homevee.Manager.CalendarManager import CalendarManager
from Homevee.Manager.ControlManager.ThermostatManager import ThermostatManager
from Homevee.Manager.NutritionDataManager import NutritionDataManager
from Homevee.Manager.SensorDataManager import SensorDataManager
from Homevee.Manager.WeatherManager import WeatherManager
from Homevee.Utils.Database import Database
from Homevee.Utils.DeviceTypes import *

STATIC_DASHBOARD_ITEMS = ['calendar', 'weather', 'tvprogramme', 'drivingtime', 'nutritionmanager']

class DashboardManager():
    def __init__(self):
        return

    def get_user_dashboard(self, user, db: Database = None):
        if db is None:
            db = Database()
        user_dashboard = user.dashboard_data

        if user_dashboard is None:
            data = {'static': [], 'dynamic': []}
        else:
            data = json.loads(user_dashboard)

        dashboard_data = {}
        dashboard_data['static'] = data['static']

        if dashboard_data is not None and dashboard_data != "":

            dashboard_keys = []
            for item in dashboard_data['static']:
                Logger.log(item)
                dashboard_keys.append(item['id'])


            for item in STATIC_DASHBOARD_ITEMS:
                if item not in dashboard_keys:
                    Logger.log(item+" not existing")
                    dashboard_data['static'].append({'id': item, 'checked': False})

            dashboard_data['dynamic'] = []

            devices_map = {}
            for item in data['dynamic']:
                if item is None:
                    continue

                found = False

                if (item['type'] not in devices_map):
                    devices_map[item['type']] = []

                if item['id'] not in devices_map[item['type']]:
                    devices_map[item['type']].append(item['id'])
                else:
                    found = True

                if not found:
                    dashboard_data['dynamic'].append(self.get_device_info(user, item['type'], item['id']))

            return dashboard_data
        else:
            return None

    def get_user_dashboard_items(self, user, db: Database = None):
        if db is None:
            db = Database()
        dashboard_array = []

        data = user.dashboard_data

        if data is None:
            return dashboard_array

        data = json.loads(data)

        static_items = data['static']

        static_data = {}

        for item in static_items:
            static_data[item['id']] = item['checked']

        dynamic_temp_items = data['dynamic']
        devices_map = {}
        dynamic_items = []

        Logger.log(dynamic_temp_items)

        for item in dynamic_temp_items:
            if item is None:
                continue

            found = False

            if (item['type'] not in devices_map):
                devices_map[item['type']] = []

            if item['id'] not in devices_map[item['type']]:
                devices_map[item['type']].append(item['id'])
            else:
                found = True

            if not found:
                dynamic_items.append(item)

        Logger.log(dynamic_items)

        # Wetter hinzufügen
        if 'weather' in static_data:
            if static_data['weather']:
                weather_data = WeatherManager().get_weather(1)
                dashboard_array.append({'id': 'weather', 'data': weather_data[0]})

        # TV Programm hinzufügen
        if 'tvprogramme' in static_data:
            if static_data['tvprogramme']:
                dashboard_array.append({'id': 'tvprogramme', 'data': None})

        # Kalender hinzufügen
        if 'calendar' in static_data:
            if static_data['calendar']:
                calendar_entries = CalendarManager().get_calendar_day_items(user, datetime.datetime.now().strftime("%Y-%m-%d"))

                items = calendar_entries

                data = None
                for item in items:
                    start = datetime.datetime.strptime(item.start, '%H:%M')
                    dnow = datetime.datetime.now()

                    if (dnow.time() > start.time()):
                        continue

                    if data is None:
                        data = item.name + " um " + item.start
                    else:
                        data += '\n' + item.name + " um " + item.start + " Uhr"

                if data is None:
                    data = 'Keine Termine heute'

                dashboard_array.append({'id': 'calendar', 'data': data})

        # Fahrzeit
        if 'drivingtime' in static_data:
            if static_data['drivingtime']:
                dashboard_array.append({'id': 'drivingtime', 'data': '27 min'})

        # Ernährungsmanager
        try:
            if 'nutritionmanager' in static_data:
                if static_data['nutritionmanager']:
                    data_item = NutritionDataManager().get_user_nutrition_overview(user)

                    if 'nutrition_day_data' in data_item:
                        calories_left = data_item['nutrition_day_data']['calories_left']
                        if (calories_left >= 0):
                            text = str(calories_left) + ' Kalorien übrig'
                        else:
                            text = str(calories_left) + ' Kalorien über deinem Ziel'

                        dashboard_array.append({'id': 'nutritionmanager', 'data': text})
                    else:
                        dashboard_array.append({'id': 'nutritionmanager',
                                                'data': "Ernährungsmanager noch nicht eingerichtet"})
        except:
            if Logger.IS_DEBUG:
                traceback.print_exc()
            pass

        if len(dynamic_items) > 0:
            dashboard_array.append({'id': 'favouritedevices', 'data': None})

        return dashboard_array

    def edit_user_dashboard(self, user, dashboard_data, db: Database = None):
        if db is None:
            db = Database()

        try:
            dashboard_data = json.loads(dashboard_data)

            #Check duplicates

            dynamic_temp_items = dashboard_data['dynamic']
            devices_map = {}
            dynamic_items = []

            #Logger.log(dynamic_temp_items)

            for item in dynamic_temp_items:
                found = False

                if (item['type'] not in devices_map):
                    devices_map[item['type']] = []

                if item['id'] not in devices_map[item['type']]:
                    devices_map[item['type']].append(item['id'])
                else:
                    found = True

                if not found:
                    dynamic_items.append(item)

            #Logger.log(dynamic_items)

            dashboard_data['dynamic'] = dynamic_items

            #Check duplicates end

            dashboard_data_json = json.dumps(dashboard_data)

            print(dashboard_data_json)

            db.update("UPDATE USERDATA SET DASHBOARD_DATA = :data WHERE USERNAME == :username",
                        {'data': dashboard_data_json, 'username': user.username})

            return True
        except:
            if Logger.IS_DEBUG:
                traceback.print_exc()
            return False

    def get_user_favourite_devices(self, user, db: Database = None):
        if db is None:
            db = Database()
        data = json.loads(user.dashboard_data)

        dynamic_items = data['dynamic']

        #Logger.log("data: "+str(data))

        fav_array = self.get_dynamic_items(user, dynamic_items)

        return fav_array

    def get_dynamic_items(self, user, dynamic_items, db: Database = None):
        if db is None:
            db = Database()
        rooms = Room.load_all(db)

        favourites = {}

        room_map = {}

        for room in rooms:
            if(user.has_permission(room.id)):
                favourites[int(room.id)] = []
                room_map[room.id] = room.get_dict()
            else:
                continue

        types = {}

        for item in dynamic_items:
            #print item
            if item['type'] not in types:
                types[item['type']] = []

            types[item['type']].append(item['id'])
            #Logger.log(types)

        for type in types:
            ids = types[type]
            if len(ids) > 0:
                for id in ids:
                    item = self.get_device_info(user, type, id)

                    if item is None:
                        continue

                    #Logger.log(favourites)

                    favourites[int(item['room'])].append(item)

        output = []
        for location in list(favourites.keys()):
            room_item = room_map[location]

            if len(favourites[location]) > 0:
                room_item['devices'] = favourites[location]
                output.append(room_item)

        return output

    def get_device_info(self, user, type, id, db: Database = None):
        if db is None:
            db = Database()
        Logger.log(type + " - " + id)

        device_data = None

        try:
            if type == FUNKSTECKDOSE:
                item = db.select_one("SELECT * FROM FUNKSTECKDOSEN WHERE DEVICE == :id", {'id': id})
                device_data = {'room': item['ROOM'], 'name': item['NAME'], 'icon': item['ICON'],
                               'value': item['ZUSTAND'] == "1",
                               'type': 'switch', 'devicetype': type, 'id': id}
            elif type == PHILIPS_HUE_LIGHT:
                item = db.select_one("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID == :id", {'id': id})
                device_data = {'room': item['LOCATION'], 'name': item['NAME'],
                               'icon': item['ICON'],
                               'value': {'is_on': False, 'brightness': 100, 'color': item['HUE']},
                               'type': 'rgb', 'devicetype': type, 'id': id}
            #URL-Geräte
            elif type == URL_RGB_LIGHT:
                item = db.select_one("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", {'id': id})
                device_data = {'name': item['NAME'], 'room': item['LOCATION'], 'id': item['ID'], 'type': 'rgb',
                               'icon': item['ICON'], 'value': {'is_on': False, 'brightness': 100, 'color': item['LAST_COLOR']}}
            elif type == URL_TOGGLE:
                item = db.select_one("SELECT * FROM URL_TOGGLE WHERE ID = :id",{'id': id})
                device_data = {'name': item['NAME'], 'room': item['LOCATION'], 'id': item['ID'],
                                    'icon': item['ICON'], 'value': '', 'type': 'toggle'}
            #Z-Wave
            elif type == ZWAVE_THERMOSTAT:
                item = db.select_one("SELECT * FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID == :id", {'id': id})
                data = ThermostatManager().get_thermostat_info(user, item['RAUM'], type, item['THERMOSTAT_ID'])
                device_data = {'name': item['NAME'], 'id': item['THERMOSTAT_ID'],
                        'icon': item['ICON'], 'room': item['RAUM'], 'type': 'heating',
                        'value': data['value'], 'min': data['min'], 'max': data['max'], 'step': 0.5}
            elif type == ZWAVE_DIMMER:
                item = db.select_one("SELECT * FROM ZWAVE_DIMMER WHERE ID == :id", {'id': id})
                device_data = {'name': item['NAME'], 'id': item['THERMOSTAT_ID'],
                        'icon': item['ICON'], 'room': item['LOCATION'], 'type': 'heating',
                        'value': item['VALUE']}
            elif type == ZWAVE_POWER_METER:
                item = db.select_one("SELECT * FROM ZWAVE_THERMOSTATS WHERE DEVICE_ID == :id", {'id': id})
                device_data = {'name': item['NAME'], 'id': item['DEVICE_ID'],
                        'icon': item['ICON'], 'room': item['LOCATION'], 'type': 'heating',
                        'value': item['VALUE']}
            elif type == ZWAVE_SENSOR:
                item = db.select_one("SELECT * FROM ZWAVE_SENSOREN WHERE ID == :id", {'id': id})
                device_data = {'name': item['SHORTFORM'], 'id': item['ID'],
                        'icon': item['ICON'], 'room': item['RAUM'], 'type': 'value',
                               'value': SensorDataManager().get_sensor_data(user, item['RAUM'], type, id, 1)}
            elif type == ZWAVE_SWITCH:
                item = db.select_one("SELECT * FROM ZWAVE_SWITCHES WHERE THERMOSTAT_ID == :id", {'id': id})
                device_data = {'name': item['NAME'], 'id': item['THERMOSTAT_ID'],
                        'icon': item['ICON'], 'room': item['LOCATION'], 'type': 'heating',
                        'value': item['VALUE']}
            #MAX Cube
            elif type == MAX_THERMOSTAT:
                item = db.select_one("SELECT * FROM MAX_THERMOSTATS WHERE ID == :id", {'id': id})
                data = ThermostatManager().get_thermostat_info(user, item['RAUM'], type, id)
                device_data = {'name': item['NAME'], 'id': item['ID'], 'room': item['RAUM'], 'type': 'heating',
                        'icon': item['ICON'],
                        'value': data['value'], 'min': data['min'], 'max': data['max'], 'step': 0.5}
            #Wake on Lan
            elif type == WAKE_ON_LAN:
                item = db.select_one("SELECT * FROM WAKE_ON_LAN WHERE DEVICE == :id", {'id': id})
                device_data = {'name': item['NAME'], 'id': item['DEVICE'], 'icon': item['ICON'], 'room': item['LOCATION'],
                               'value': '', 'type': 'wakeonlan'}
            elif type == XBOX_ONE_WOL:
                item = db.select_one("SELECT * FROM XBOX_ONE_WOL WHERE ID == :id", {'id': id})
                device_data = {'name': item['NAME'], 'id': item['ID'], 'icon': item['ICON'], 'room': item['LOCATION'],
                               'value': '', 'type': 'wakeonlan'}

            #MQTT Sensor
            elif type == MQTT_SENSOR:
                item = db.select_one("SELECT * FROM MQTT_SENSORS WHERE ID == :id", {'id': id})
                device_data = {'name': item['NAME'], 'id': item['ID'],
                               'icon': item['ICON'], 'room': item['ROOM'], 'type': 'value',
                               'value': SensorDataManager().get_sensor_data(user, item['ROOM'], type, id, 1)}
        except:
            Logger.log("Error loading device")

        if device_data is None or not user.has_permission(device_data['room']):
            return None

        device_data['roomname'] = Room.get_name_by_id(device_data['room'])
        device_data['devicetype'] = type

        return device_data

        '''//DIY
            case "DIY Gerät":
                $dbQuery = $db->prepare("SELECT * FROM 'DIY_DEVICES' WHERE DEVICE == :id");
                $dbQuery->execute($queryParams);
                
                
                $query = $dbQuery->fetch(PDO::FETCH_ASSOC);
                $devicedata = array("room" => $query['ROOM'], "name" => $query['NAME'], "icon" => $query['ICON'],
                "value" => "", "type" => "button");
                break;
            case "DIY Sensor":
                $dbQuery = $db->prepare("SELECT * FROM 'DIY_SENSORS' WHERE ID == :id");
                $dbQuery->execute($queryParams);
                
                
                $query = $dbQuery->fetch(PDO::FETCH_ASSOC);
                $devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
                "value" => getSensorData($query['RAUM'], $type, $id, "1", $db), "type" => "value");
            case "DIY Fensterkontakt":
                $dbQuery = $db->prepare("SELECT * FROM 'DIY_REEDSENSORS' WHERE ID == :id");
                $dbQuery->execute($queryParams);
                
                
                $query = $dbQuery->fetch(PDO::FETCH_ASSOC);
                $devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
                "value" => getReedData($query['RAUM'], $type, $id, $db), "type" => "reed");
                break;
            case "DIY Anwesenheitssensor":
                $dbQuery = $db->prepare("SELECT * FROM 'DIY_PRESENCESENSORS' WHERE ID == :id");
                $dbQuery->execute($queryParams);
                
                
                $query = $dbQuery->fetch(PDO::FETCH_ASSOC);
                $devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
                "value" => getReedData($query['RAUM'], $type, $id, $db), "type" => "presence");
                break;
            case "DIY Schalter":
                $dbQuery = $db->prepare("SELECT * FROM 'DIY_SWITCHES' WHERE ID == :id");
                $dbQuery->execute($queryParams);
                
                
                $query = $dbQuery->fetch(PDO::FETCH_ASSOC);
                $devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
                "value" => getModes($query['RAUM'], $type, $id, $db) === "1", "type" => "switch");
                break;
            case "IP Kamera":
                $dbQuery = $db->prepare("SELECT * FROM 'IP_CAMERA' WHERE ID == :id");
                $dbQuery->execute($queryParams);
                
                $query = $dbQuery->fetch(PDO::FETCH_ASSOC);
                
                $ip = $query['IP'];
                $port = $query['PORT'];
                    
                if($port != null && $port != ""){
                    $port = ":$port";
                }
                    
                $path = $query['PATH'];
                    
                $url = "http://$ip$port$path";
                
                $devicedata = array('room' => $query['LOCATION'], 'name' => $query['NAME'], 'icon' => $query['ICON'],
                'value' => "", 'url' => $url, 'username' => $query['USERNAME'], 'password' => $query['PASSWORD'],
                'type' => "ipcamera");
                break;
                
            default:
                return null;
        }
        
        if(!hasPermission($devicedata['room'], $db) || $devicedata['room'] == null){
            return null;
        }
        else{
            $devicedata['roomname'] = $roomArray[$devicedata['room']];
            $devicedata['devicetype'] = $type;
            $devicedata['id'] = $id;
            
            return $devicedata;
        }
    }
    ?>
        '''
