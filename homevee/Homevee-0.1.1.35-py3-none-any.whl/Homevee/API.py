#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from Homevee.APIModule.APIKeyAPIModule import APIKeyAPIModule
from Homevee.APIModule.AutomationAPIModule import AutomationAPIModule
from Homevee.APIModule.BlindsAPIModule import BlindsAPIModule
from Homevee.APIModule.CalendarAPIModule import CalendarAPIModule
from Homevee.APIModule.ChatAPIModule import ChatAPIModule
from Homevee.APIModule.CustomVoiceCommandAPIModule import CustomVoiceCommandAPIModule
from Homevee.APIModule.DashboardAPIModule import DashboardAPIModule
from Homevee.APIModule.DeviceAPIModule import DeviceAPIModule
from Homevee.APIModule.DimmerAPIModule import DimmerAPIModule
from Homevee.APIModule.EnergyDataAPIModule import EnergyDataAPIModule
from Homevee.APIModule.EventAPIModule import EventAPIModule
from Homevee.APIModule.GPSDataAPIModule import GPSDataAPIModule
from Homevee.APIModule.GatewayAPIModule import GatewayAPIModule
from Homevee.APIModule.GraphDataAPIModule import GraphDataAPIModule
from Homevee.APIModule.HeatingSchemeAPIModule import HeatingSchemeAPIModule
from Homevee.APIModule.HomeBudgetAPIModule import HomeBudgetAPIModule
from Homevee.APIModule.ImageClassifierAPIModule.ARControlAPIModule import ARControlAPIModule
from Homevee.APIModule.ImageClassifierAPIModule.PeopleClassifierAPIModule import PeopleClassifierAPIModule
from Homevee.APIModule.LoginAPIModule import LoginAPIModule
from Homevee.APIModule.MQTTConnectorAPIModule import MQTTConnectorAPIModule
from Homevee.APIModule.MediaCenterAPIModule import MediaCenterAPIModule
from Homevee.APIModule.NutritionDataAPIModule import NutritionDataAPIModule
from Homevee.APIModule.PersonAPIModule import PersonAPIModule
from Homevee.APIModule.PlaceAPIModule import PlaceAPIModule
from Homevee.APIModule.RBGLightAPIModule import RGBLightAPIModule
from Homevee.APIModule.RFIDTagAPIModule import RFIDTagAPIModule
from Homevee.APIModule.RemoteControlAPIModule import RemoteControlAPIModule
from Homevee.APIModule.RoomAPIModule import RoomAPIModule
from Homevee.APIModule.RoomDataAPIModule import RoomDataAPIModule
from Homevee.APIModule.SceneAPIModule import SceneAPIModule
from Homevee.APIModule.SensorDataAPIModule import SensorDataAPIModule
from Homevee.APIModule.ShoppingListAPIModule import ShoppingListAPIModule
from Homevee.APIModule.SmartSpeakerAPIModule import SmartSpeakerAPIModule
from Homevee.APIModule.SystemInfoAPIModule import SystemInfoAPIModule
from Homevee.APIModule.TVPlanAPIModule import TVPlanAPIModule
from Homevee.APIModule.ThermostatAPIModule import ThermostatAPIModule
from Homevee.APIModule.UpdaterAPIModule import UpdaterAPIModule
from Homevee.APIModule.UserAPIModule import UserAPIModule
from Homevee.APIModule.VoiceAPIModule import VoiceAPIModule
from Homevee.APIModule.WakeOnLanAPIModule import WakeOnLanAPIModule
from Homevee.APIModule.WeatherAPIModule import WeatherAPIModule
from Homevee.Exception import NoPermissionException
from Homevee.Helper import translations
# from Functions import people_classifier, ar_control
# from Functions.people_classifier import *
from .Manager.UserManager import User
from .VoiceAssistant import *
from .VoiceAssistant.VoiceReplaceManager import *

FUNCTION_MAPPINGS = {}

class API:
    def __init__(self):
        return

    def process_data(self, data: dict, db: Database) -> dict:
        """
        Process the request
        :param data: the data dict
        :param db: the database connection
        :return: the response data dict
        """
        try:
            username = data['username']
            password = data['password']

            user = User.load_username_from_db(username, db)
            verified = user.verify(password)

            if 'language' in data and data['language'] is not None:
                language = data['language']
            else:
                language = translations.LANGUAGE

            if not verified:
                return Status(type=STATUS_WRONG_DATA).get_dict()

            if(data['action'] in FUNCTION_MAPPINGS):
                #print("########################################")
                #print("####ANTWORT DER NEUEN HANDLE REQUEST####")
                #print("########################################")
                print(json.dumps(data))
                response = self.handle_request(user, data, db).get_dict()
                print(response)
                #print("########################################")
                #print("########################################")
                return response
            else:
                return Status(type=STATUS_NO_SUCH_ACTION).get_dict()
        except NoPermissionException as e:
            if Logger.IS_DEBUG:
                traceback.print_exc()
            return Status(type=STATUS_NO_PERMISSION).get_dict()
        except Exception as e:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            return Status(type=STATUS_ERROR).get_dict()

    def create_function_mappings(self):
        modules = [LoginAPIModule(), RoomAPIModule(), UserAPIModule(), RoomDataAPIModule(), GraphDataAPIModule(),
                   VoiceAPIModule(), ChatAPIModule(), SystemInfoAPIModule(), HomeBudgetAPIModule(), WeatherAPIModule(),
                   RemoteControlAPIModule(), DashboardAPIModule(), CalendarAPIModule(), GPSDataAPIModule(),
                   PlaceAPIModule(), NutritionDataAPIModule(), PersonAPIModule(), RFIDTagAPIModule(), EventAPIModule(),
                   GatewayAPIModule(), TVPlanAPIModule(), EnergyDataAPIModule(), UpdaterAPIModule(), HeatingSchemeAPIModule(),
                   SensorDataAPIModule(), ShoppingListAPIModule(), CustomVoiceCommandAPIModule(), SceneAPIModule(),
                   AutomationAPIModule(), RGBLightAPIModule(), ARControlAPIModule(), PeopleClassifierAPIModule(),
                   BlindsAPIModule(), DimmerAPIModule(), WakeOnLanAPIModule(), MQTTConnectorAPIModule(),
                   SmartSpeakerAPIModule(), ThermostatAPIModule(), APIKeyAPIModule(), DeviceAPIModule(),
                   MediaCenterAPIModule()]
        for module in modules:
            module_mappings = module.get_function_mappings()
            for action_key in module_mappings:
                if action_key in FUNCTION_MAPPINGS:
                    raise RuntimeError("Action-Key already added to FUNCTION_MAPPINGS")
                FUNCTION_MAPPINGS[action_key] = module_mappings[action_key]

    def get_function_mappings(self):
        return FUNCTION_MAPPINGS

    def handle_request(self, user: User, request: dict, db: Database = None) -> Status:
        if db is None:
            db = Database()
        action = request['action']
        if action in FUNCTION_MAPPINGS:
            return FUNCTION_MAPPINGS[action](user, request, db)
        else:
            return Status(type=STATUS_NO_SUCH_ACTION)