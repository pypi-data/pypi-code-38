SWITCH = 1
BRIGHTNESS = 2
POWER = 3
ENERGY = 4
BATTERY = 8
COLOR = 23
COVER_POSITION = 15
SATURATION = 206

ATTR_TYPES = {
    SWITCH: "switch",
    BRIGHTNESS: "brightness",
    SATURATION: "saturation",
    BATTERY: "battery",
    ENERGY: "energy",
    POWER: "power",
    COVER_POSITION: "cover_position"
}

CANodeProfileNone = 0
CANodeProfileHomee = 1
CANodeProfileOnOffPlug = 10
CANodeProfileDimmableMeteringSwitch = 11
CANodeProfileMeteringSwitch = 12
CANodeProfileMeteringPlug = 13
CANodeProfileDimmablePlug = 14
CANodeProfileDimmableSwitch = 15
CANodeProfileOnOffSwitch = 16
CANodeProfileDoubleOnOffSwitch = 18
CANodeProfileDimmableMeteringPlug = 19
CANodeProfileOneButtonRemote = 20
CANodeProfileBinaryInput = 21
CANodeProfileDimmableColorMeteringPlug = 22
CANodeProfileDoubleBinaryInput = 23
CANodeProfileTwoButtonRemote = 24
CANodeProfileThreeButtonRemote = 25
CANodeProfileFourButtonRemote = 26
CANodeProfileAlarmSensor = 27
CANodeProfileDoubleOnOffPlug = 28
CANodeProfileOnOffSwitchWithBinaryInput = 29
CANodeProfileWatchDogWithPressureAndTemperatures = 30
CANodeProfileFibaroButton = 31
CANodeProfileEnergyMeter = 32
CANodeProfileDoubleMeteringSwitch = 33
CANodeProfileFibaroSwipe = 34
CANodeProfileBrightnessSensor = 1e3
CANodeProfileDimmableColorLight = 1001
CANodeProfileDimmableExtendedColorLight = 1002
CANodeProfileDimmableColorTemperatureLight = 1003
CANodeProfileDimmableLight = 1004
CANodeProfileDimmableLightWithBrightnessSensor = 1005
CANodeProfileDimmableLightWithBrightnessAndPresenceSensor = 1006
CANodeProfileDimmableLightWithPresenceSensor = 1007
CANodeProfileDimmableRGBWLight = 1008
CANodeProfileOpenCloseSensor = 2e3
CANodeProfileWindowHandle = 2001
CANodeProfileShutterPositionSwitch = 2002
CANodeProfileOpenCloseAndTemperatureSensor = 2003
CANodeProfileElectricMotorMeteringSwitch = 2004
CANodeProfileOpenCloseWithTemperatureAndBrightnessSensor = 2005
CANodeProfileElectricMotorMeteringSwitchWithoutSlatPosition = 2006
CANodeProfileLock = 2007
CANodeProfileWindowHandleWithButtons = 2008
CANodeProfileWindowHandleWithButtonsAndTemperatureAndHumiditySensor = 2009
CANodeProfileTemperatureAndHumiditySensor = 3001
CANodeProfileCO2Sensor = 3002
CANodeProfileRoomThermostat = 3003
CANodeProfileRoomThermostatWithHumiditySensor = 3004
CANodeProfileBinaryInputWithTemperatureSensor = 3005
CANodeProfileRadiatorThermostat = 3006
CANodeProfileTemperatureSensor = 3009
CANodeProfileHumiditySensor = 3010
CANodeProfileWaterValve = 3011
CANodeProfileWaterMeter = 3012
CANodeProfileWeatherStation = 3013
CANodeProfileNetatmoMainModule = 3014
CANodeProfileNetatmoOutdoorModule = 3015
CANodeProfileNetatmoIndoorModule = 3016
CANodeProfileNetatmoRainModule = 3017
CANodeProfileCosiThermChannel = 3018
CANodeProfileNestThermostatWithCooling = 3020
CANodeProfileNestThermostatWithHeating = 3021
CANodeProfileNestThermostatWithHeatingAndCooling = 3022
CANodeProfileNetatmoWindModule = 3023
CANodeProfileElectricalHeating = 3024
CANodeProfileValveDrive = 3025
CANodeProfileCamera = 3026
CANodeProfileCameraWithFloodlight = 3027
CANodeProfileNetatmoTags = 3028
CANodeProfileMotionDetectorWithTemperatureBrightnessAndHumiditySensor = 4010
CANodeProfileMotionDetector = 4011
CANodeProfileSmokeDetector = 4012
CANodeProfileFloodDetector = 4013
CANodeProfilePresenceDetector = 4014
CANodeProfileMotionDetectorWithTemperatureAndBrightnessSensor = 4015
CANodeProfileSmokeDetectorWithTemperatureSensor = 4016
CANodeProfileFloodDetectorWithTemperatureSensor = 4017
CANodeProfileWatchDogDevice = 4018
CANodeProfileLAG = 4019
CANodeProfileOWU = 4020
CANodeProfileEurovac = 4021
CANodeProfileOWWG3 = 4022
CANodeProfileEuropress = 4023
CANodeProfileMinimumDetector = 4024
CANodeProfileMaximumDetector = 4025
CANodeProfileSmokeDetectorAndCODetector = 4026
CANodeProfileSiren = 4027
CANodeProfileMotionDetectorWithOpenCloseTemperatureAndBrightnessSensor = 4028
CANodeProfileMotionDetectorWithBrightness = 4029
CANodeProfileDoorbell = 4030
CANodeProfileSmokeDetectorAndSiren = 4031
CANodeProfileFloodDetectorWithTemperatureAndHumiditySensor = 4032
CANodeProfileMinimumDetectorWithTemperatureSensor = 4033
CANodeProfileMaximumDetectorWithTemperatureSensor = 4034
CANodeProfilePresenceDetectorWithTemperatureAndBrightnessSensor = 4035
CANodeProfileCODetector = 4036
CANodeProfileInovaAlarmSystem = 5e3
CANodeProfileInovaDetector = 5001
CANodeProfileInovaSiren = 5002
CANodeProfileInovaCommand = 5003
CANodeProfileInovaTransmitter = 5004
CANodeProfileInovaReciever = 5005
CANodeProfileInovaKoala = 5006
CANodeProfileInovaInternalTransmitter = 5007
CANodeProfileInovaControlPanel = 5008
CANodeProfileInovaInputOutputExtension = 5009
CANodeProfileInovaMotionDetectorWithVOD = 5010
CANodeProfileInovaMotionDetector = 5011
CANodeProfileWashingMachine = 6e3
CANodeProfileTumbleDryer = 6001
CANodeProfileDishwasher = 6002

DISCOVER_LIGHTS = "homee.lights"
DISCOVER_CLIMATE = "homee.climate"
DISCOVER_BINARY_SENSOR = "homee.binary_sensor"
DISCOVER_SWITCH = "homee.switch"

PROFILE_TYPES = {
    DISCOVER_LIGHTS: [CANodeProfileDimmableColorLight, CANodeProfileDimmableColorTemperatureLight,
                      CANodeProfileDimmableExtendedColorLight, CANodeProfileDimmableLight,
                      CANodeProfileDimmableRGBWLight, CANodeProfileDimmableLightWithBrightnessAndPresenceSensor],
    DISCOVER_CLIMATE: [CANodeProfileNestThermostatWithCooling, CANodeProfileRadiatorThermostat,
                       CANodeProfileRoomThermostat, CANodeProfileNestThermostatWithHeating,
                       CANodeProfileNestThermostatWithHeatingAndCooling, CANodeProfileRoomThermostatWithHumiditySensor],
    DISCOVER_BINARY_SENSOR: [CANodeProfileOpenCloseSensor],
    DISCOVER_SWITCH: [CANodeProfileOnOffSwitch, CANodeProfileDimmableSwitch, CANodeProfileDimmableMeteringSwitch,
                      CANodeProfileDoubleOnOffSwitch, CANodeProfileMeteringSwitch, CANodeProfileOnOffPlug,
                      CANodeProfileDimmablePlug, CANodeProfileDimmableMeteringPlug, CANodeProfileMeteringPlug]


}

ATTRIBUTE_TYPES = {
    'None': 0,
    'OnOff': 1,
    'DimmingLevel': 2,
    'CurrentEnergyUse': 3,
    'AccumulatedEnergyUse': 4,
    'Temperature': 5,
    'TargetTemperature': 6,
    'RelativeHumidity': 7,
    'BatteryLevel': 8,
    'StatusLED': 9,
    'WindowPosition': 10,
    'Brightness': 11,
    'FloodAlarm': 12,
    'Siren': 13,
    'OpenClose': 14,
    'Position': 15,
    'SmokeAlarm': 16,
    'BlackoutAlarm': 17,
    'CurrentValvePosition': 18,
    'BinaryInput': 19,
    'CO2Level': 20,
    'Pressure': 21,
    'Color': 23,
    'Saturation': 24,
    'MotionAlarm': 25,
    'MotionSensitivity': 26,
    'MotionInsensitivity': 27,
    'MotionAlarmCancelationDelay': 28,
    'WakeUpInterval': 29,
    'TamperAlarm': 30,
    'LinkQuality': 33,
    'InovaAlarmSystemState': 34,
    'InovaAlarmGroupState': 35,
    'InovaAlarmIntrusionState': 36,
    'InovaAlarmErrorState': 37,
    'InovaAlarmDoorState': 38,
    'InovaAlarmExternalSensor': 39,
    'ButtonState': 40,
    'Hue': 41,
    'ColorTemperature': 42,
    'HardwareRevision': 43,
    'FirmwareRevision': 44,
    'SoftwareRevision': 45,
    'LEDState': 46,
    'LEDStateWhenOn': 47,
    'LEDStateWhenOff': 48,
    'HighTemperatureAlarm': 52,
    'HighTemperatureAlarmTreshold': 53,
    'LowTemperatureAlarm': 54,
    'LowTemperatureAlarmTreshold': 55,
    'TamperSensitivity': 56,
    'TamperAlarmCancelationDelay': 57,
    'BrightnessReportInterval': 58,
    'TemperatureReportInterval': 59,
    'MotionAlarmIndicationMode': 60,
    'LEDBrightness': 61,
    'TamperAlarmIndicationMode': 62,
    'SwitchType': 63,
    'TemperatureOffset': 64,
    'AccumulatedWaterUse': 65,
    'AccumulatedWaterUseLastMonth': 66,
    'CurrentDate': 67,
    'LeakAlarm': 68,
    'BatteryLowAlarm': 69,
    'MalfunctionAlarm': 70,
    'LinkQualityAlarm': 71,
    'Mode': 72,
    'Calibration': 75,
    'PresenceAlarm': 76,
    'MinimumAlarm': 77,
    'MaximumAlarm': 78,
    'OilAlarm': 79,
    'WaterAlarm': 80,
    'InovaAlarmInhibition': 81,
    'InovaAlarmEjection': 82,
    'InovaAlarmCommercialRef': 83,
    'InovaAlarmSerialNumber': 84,
    'RadiatorThermostatSummerMode': 85,
    'InovaAlarmOperationMode': 86,
    'AutomaticMode': 87,
    'PollingInterval': 88,
    'FeedTemperature': 89,
    'DisplayOrientation': 90,
    'ManualOperation': 91,
    'DeviceTemperature': 92,
    'Sonometer': 93,
    'AirPressure': 94,
    'InovaAlarmAntimask': 99,
    'InovaAlarmBackupSupply': 100,
    'RainFall': 101,
    'InovaAlarmGeneralHomeCommand': 103,
    'InovaAlarmAlert': 104,
    'InovaAlarmSilentAlert': 105,
    'InovaAlarmPreAlarm': 106,
    'InovaAlarmDeterrenceAlarm': 107,
    'InovaAlarmWarning': 108,
    'InovaAlarmFireAlarm': 109,
    'UpTime': 110,
    'DownTime': 111,
    'ShutterBlindMode': 112,
    'ShutterSlatPosition': 113,
    'ShutterSlatTime': 114,
    'RestartDevice': 115,
    'SoilMoisture': 116,
    'WaterPlantAlarm': 117,
    'MistPlantAlarm': 118,
    'FertilizePlantAlarm': 119,
    'CoolPlantAlarm': 120,
    'HeatPlantAlarm': 121,
    'PutPlantIntoLightAlarm': 122,
    'PutPlantIntoShadeAlarm': 123,
    'ColorMode': 124,
    'TargetTemperatureLow': 125,
    'TargetTemperatureHigh': 126,
    'HVACMode': 127,
    'Away': 128,
    'HVACState': 129,
    'HasLeaf': 130,
    'SetEnergyConsumption': 131,
    'COAlarm': 132,
    'RestoreLastKnownState': 133,
    'LastImageReceived': 134,
    'UpDown': 135,
    'RequestVOD': 136,
    'InovaDetectorHistory': 137,
    'SurgeAlarm': 138,
    'LoadAlarm': 139,
    'OverloadAlarm': 140,
    'VoltageDropAlarm': 141,
    'ShutterOrientation': 142,
    'OverCurrentAlarm': 143,
    'SirenMode': 144,
    'AlarmAutoStopTime': 145,
    'WindSpeed': 146,
    'WindDirection': 147,
    'ComfortTemperature': 148,
    'EcoTemperature': 149,
    'ReduceTemperature': 150,
    'ProtectTemperature': 151,
    'InovaSystemTime': 152,
    'InovaCorrespondentProtocol': 153,
    'InovaCorrespondentID': 154,
    'InovaCorrespondentListen': 155,
    'InovaCorrespondentNumber': 156,
    'InovaCallCycleFireProtection': 157,
    'InovaCallCycleIntrusion': 158,
    'InovaCallCycleTechnicalProtect': 159,
    'InovaCallCycleFaults': 160,
    'InovaCallCycleDeterrence': 161,
    'InovaCallCyclePrealarm': 162,
    'InovaPSTNRings': 163,
    'InovaDoubleCallRings': 164,
    'InovaPIN': 165,
    'InovaPUK': 166,
    'InovaMainMediaSelection': 167,
    'RainFallLastHour': 168,
    'RainFallToday': 169,
    'IdentificationMode': 170,
    'ButtonDoubleClick': 171,
    'SirenTriggerMode': 172,
    'UV': 173,
    'SlatSteps': 174,
    'EcoModeConfig': 175,
    'ButtonLongRelease': 176,
    'VisualGong': 177,
    'AcousticGong': 178,
    'SurveillanceOnOff': 179,
    'StorageAlarm': 181,
    'PowerSupplyAlarm': 182,
    'NetatmoHome': 183,
    'NetatmoPerson': 184,
    'NetatmoLastEventPersonId': 185,
    'NetatmoLastEventTime': 186,
    'NetatmoLastEventType': 187,
    'NetatmoLastEventIsKnownPerson': 188,
    'NetatmoLastEventIsArrival': 189,
    'PresenceTimeout': 190,
    'KnownPersonPresence': 191,
    'UnknownPersonPresence': 192,
    'Current': 193,
    'Frequency': 194,
    'Voltage': 195,
    'PresenceAlarmCancelationDelay': 196,
    'PresenceAlarmDetectionDelay': 197,
    'PresenceAlarmThreshold': 198,
    'NetatmoThermostatMode': 199,
    'NetatmoRelayBoilerConnected': 200,
    'NetatmoRelayMac': 201,
    'NetatmoThermostatModeTimeout': 202,
    'NetatmoThermostatNextChange': 203,
    'NetatmoThermostatPrograms': 204,
    'HomeeMode': 205,
    'ColorWhite': 206,
    'MovementAlarm': 207,
    'MovementSensitivity': 208,
    'VibrationAlarm': 209,
    'VibrationSensitivity': 210,
    'AverageEnergyUse': 211,
    'BinaryInputMode': 212,
    'DeviceStatus': 213,
    'DeviceRemainingTime': 214,
    'DeviceStartTime': 215,
    'DeviceProgram': 216,
    'ButtonPressed3Times': 223,
    'ButtonPressed4Times': 224,
    'ButtonPressed5Times': 225,
    'RepeaterMode': 226,
    'AutoOffTime': 227,
    'CO2Alarm': 228,
    'InputEndpointConfiguration': 229,
    'GustSpeed': 230,
    'GustDirection': 231,
    'LockState': 232,
    'AeotecSmartPlugLEDState': 233,
    'AlarmDuration': 234,
    'DewPoint': 235,
    'Gesture': 236,
    'GestureSequenceLearningMode': 237,
    'GestureSequence': 238,
    'TotalCurrentEnergyUse': 239,
    'TotalAccumulatedEnergyUse': 240,
    'SunsetTime': 241,
    'SunriseTime': 242,
    'CurrentLocalWeatherCondition': 243,
    'CurrentLocalTemperature': 244,
    'CurrentLocalHumidity': 245,
    'ForecastLocalWeatherCondition': 246,
    'ForecastLocalTempMin': 247,
    'ForecastLocalTempMax': 248,
    'Armed': 249,
    'Floodlight': 250,
    'HumanDetected': 251,
    'VehicleDetected': 252,
    'AnimalDetected': 253,
    'VacationMode': 254,
    'BlinkInterval': 255,
    'OtherMotionDetected': 256,
    'IRCodeNumber': 257,
    'HeatingMode': 258,
    'DisplayAutoOffTime': 259,
    'Backlight': 260,
    'OpenWindowDetectionSensibility': 261,
    'CurrentLocalWindSpeed': 262,
    'CurrentLocalGustSpeed': 263,
}


ATTRIBUTE_TYPES_LOOKUP = {v: k for k, v in ATTRIBUTE_TYPES.items()}

CANodeStateNone = 0,
CANodeStateAvailable = 1
CANodeStateUnavailable = 2
CANodeStateUpdateInProgress = 3
CANodeStateWaitingForAttributes = 4
CANodeStateInitializing = 5
CANodeStateUserInteractionRequired = 6
CANodeStatePasswordRequired = 7
CANodeStateHostUnavailable = 8
CANodeStateDeleteInProgress = 9
CANodeStateCosiConnected: 10
CANodeStateBlocked = 11
CANodeStateWaitingForWakeup = 12
