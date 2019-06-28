import json
import logging
import datetime
from base64 import b64decode, b64encode
from binascii import a2b_hex, b2a_hex
from struct import *

from .loxdimmer import LoxDimmer
from .loxswitch import LoxSwitch
from .loxcolorpickerv2 import LoxColorPickerV2
from .loxlightcontrollerv2 import LoxLightControllerV2
from .loxiroomcontrollerv2 import LoxIRoomControllerV2
from .loxinfoonlyanalog import LoxInfoOnlyAnalog
from .loxinfoonlydigital import LoxInfoOnlyDigital

_LOGGER = logging.getLogger(__name__)

#https://docs.python.org/3.7/library/struct.html#format-characters

class MessageBody:

    def __init__(self, payload, isBinary, header, config_data):
        message_timestamp = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        if header.msg_type == "Text":
            """Text"""
            #_LOGGER.debug('TEXT MESSAGE - {1} bytes - Text'.format(message_timestamp, len(payload)))
            self.raw = payload 
            #_LOGGER.debug("  raw: {0} {1}".format(type(self.raw), self.raw))
            self.msg = json.loads(payload)

            if "Code" in self.raw:
                self.code = self.msg["LL"]["Code"]
                #_LOGGER.debug("    code: " + self.code)

            if "code" in self.raw:
                self.code = self.msg["LL"]["code"]
                #_LOGGER.debug("    code: {0}".format(self.code))
            
            if "control" in self.raw:
                self.control = self.msg["LL"]["control"]
                #_LOGGER.debug("    control: " + self.control)

            if "value" in self.raw:
                self.value = self.msg["LL"]["value"]
                #_LOGGER.debug("    value: {0}".format(self.value))

        elif header.msg_type == "Binary":
            """Binary"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - Binary'.format(message_timestamp, len(payload)))
            self.control = "LoxAPP3.json"
            #_LOGGER.debug("  control: " + self.control)
            self.raw = payload 
            #_LOGGER.debug("  raw: {0} {1}".format(type(self.raw), self.raw))
            self.msg = json.loads(payload)

        elif header.msg_type == "Value-States":
            """Value-States"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - Value-States'.format(message_timestamp, len(payload)))
            x = 0
            while x < len(payload):
                uuid = self.getUuid(payload[x:x+16])
                #_LOGGER.debug("  uuid: {0} {1} {2}".format(type(uuid), len(uuid), uuid))

                e = payload[x+16:x+24]
                #_LOGGER.debug("  e: {0} {1} {2}".format(type(e), len(e), e))

                dval = unpack('<d', e)[0]
                #_LOGGER.debug("  dval: {0} {1}".format(type(dval), dval))

                if uuid in config_data.fieldmap:
                    try:
                        _LOGGER.debug("UUID in fieldmap List {0}".format(uuid))
                        mapentry = config_data.fieldmap[uuid]

                        device = mapentry["device"]
                        stateName = mapentry["stateName"]

                        _LOGGER.debug("SettingState {0} {1} device_type: {2} state_name: {3}".format(device.id, device.name, device.device_type, mapentry["stateName"]))

                        device.set_value(stateName, dval)

                    except Exception as ex:
                        _LOGGER.error(ex)

                category = 'unknown'
                controlName = ''
                controlType = ''
                stateName = ''
                roomName = ''
                for k,v in config_data.data["globalStates"].items():
                    if v == uuid:
                        category = 'globalState'
                for k,v in config_data.data["caller"].items():
                    if v == uuid:
                        category = 'caller'
                    if 'states' in v:
                        for tk,tv in v["states"].items():
                            if tv == uuid:
                                category = 'callerState'
                                stateName = tk
                for k,v in config_data.data["autopilot"].items():
                    if v == uuid:
                        category = 'autopilot'
                    if 'states' in v:
                        for tk,tv in v["states"].items():
                            if tv == uuid:
                                category = 'autopilotState'
                                stateName = tk
                for k,v in config_data.data["messageCenter"].items():
                    if v == uuid:
                        category = 'messageCenter'
                        stateName = k
                    if 'states' in v:
                        for tk,tv in v["states"].items():
                            if tv == uuid:
                                category = 'messageCenterState'
                                stateName = tk

                if uuid in config_data.data["controls"]:
                    control = config_data.data["controls"][uuid]
                    category = 'control'
                    controlName = control["name"]
                    controlType = control["type"]
                    if 'room' in control:
                        roomName = config_data.get_room_name(control["room"])
                else:
                    for k,v in config_data.data["controls"].items():
                        if 'states' in v:
                            for tk,tv in v["states"].items():
                                if tv == uuid:
                                    category = 'controlState'
                                    controlName = v["name"]
                                    controlType = v["type"]
                                    stateName = tk
                                    if 'room' in v:
                                        roomName = config_data.get_room_name(v["room"])

                        if 'subControls' in v:
                            for sk,sv in v["subControls"].items():
                                if 'states' in sv:
                                    for stk,stv in sv["states"].items():
                                        if stv == uuid:
                                            category = 'subControlState'
                                            controlName = sv["name"]
                                            controlType = sv["type"]
                                            stateName = stk
                                            if 'room' in v:
                                                roomName = config_data.get_room_name(v["room"])

                _LOGGER.debug("  uuid: {0} Category: '{1}' Type: '{2}' Room: '{3}' Name: '{4}' state: '{5}' dval: {6}".format(uuid, category, controlType, roomName, controlName, stateName, dval))

                x = x + 24

        elif header.msg_type == "Text-States":
            """Text-States"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - Text-States'.format(message_timestamp, len(payload)))
            x = 0
            while x < len(payload):
                uuid = self.getUuid(payload[x:x+16])
                #_LOGGER.debug("  uuid: {0} {1} {2}".format(type(uuid), len(uuid), uuid))

                uuidIcon = self.getUuid(payload[x+16:x+32])
                #_LOGGER.debug("  uuidIcon: {0} {1} {2}".format(type(uuidIcon), len(uuidIcon), uuidIcon))

                e = payload[x+32:x+36]
                #_LOGGER.debug("  e: {0} {1} {2}".format(type(e), len(e), e))

                size = unpack('<I', e)[0]
                #_LOGGER.debug("  size: {0} {1}".format(type(size), size))

                rem = size % 4
                #_LOGGER.debug("  rem: {0} {1}".format(type(rem), rem))

                text = str(payload[x+36:x+36+size], 'utf-8')
                #_LOGGER.debug("  text: {0} {1} {2}".format(type(text), len(text), text))

                if uuid in config_data.fieldmap:
                    try:
                        #_LOGGER.debug("UUID in field map")
                        mapentry = config_data.fieldmap[uuid]

                        device = mapentry["device"]
                        stateName = mapentry["stateName"]

                        device.set_value(stateName, text)

                    except Exception as ex:
                        _LOGGER.error(ex)

                category = 'unknown'
                controlName = ''
                controlType = ''
                stateName = ''
                for k,v in config_data.data["globalStates"].items():
                    if v == uuid:
                        category = 'globalState'
                for k,v in config_data.data["caller"].items():
                    if v == uuid:
                        category = 'caller'
                    if 'states' in v:
                        for tk,tv in v["states"].items():
                            if tv == uuid:
                                category = 'callerState'
                                stateName = tk
                for k,v in config_data.data["autopilot"].items():
                    if v == uuid:
                        category = 'autopilot'
                    if 'states' in v:
                        for tk,tv in v["states"].items():
                            if tv == uuid:
                                category = 'autopilotState'
                                stateName = tk
                for k,v in config_data.data["messageCenter"].items():
                    if v == uuid:
                        category = 'messageCenter'
                        stateName = k
                    if 'states' in v:
                        for tk,tv in v["states"].items():
                            if tv == uuid:
                                category = 'messageCenterState'
                                stateName = tk
                if uuid in config_data.data["controls"]:
                    control = config_data.data["controls"][uuid]
                    category = 'control'
                    controlName = control["name"]
                    controlType = control["type"]
                else:
                    for k,v in config_data.data["controls"].items():
                        if 'states' in v:
                            for tk,tv in v["states"].items():
                                if tv == uuid:
                                    category = 'controlState'
                                    controlName = v["name"]
                                    controlType = v["type"]
                                    stateName = tk
                        if 'subControls' in v:
                            for sk,sv in v["subControls"].items():
                                if 'states' in sv:
                                    for stk,stv in sv["states"].items():
                                        if stv == uuid:
                                            category = 'subControlState'
                                            controlName = sv["name"]
                                            controlType = sv["type"]
                                            stateName = stk

                _LOGGER.debug("  uuid: {0} Category: '{1}' Type: '{2}' Name: '{3}' state: '{4}' uuidIcon: {5} text: {6}".format(uuid, category, controlType, controlName, stateName, uuidIcon, text))

                x = x + 36 + size
                if rem > 0:
                    x = x + (4 - rem)

        elif header.msg_type == "Daytime-States":
            """Daytime-States"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - Daytime-States'.format(message_timestamp, len(payload)))
            x = 0
            while x < len(payload):
                #uuid - 128-Bit uuid - 16 bytes
                uuid = self.getUuid(payload[x:x+16])
                #_LOGGER.debug("  uuid: {0} {1} {2}".format(type(uuid), len(uuid), uuid))

                #dDefValue - 64-Bit Float (little endian) default value - 8 bytes     
                dDefValue = unpack('<d', payload[x+16:x+24])[0]
                #_LOGGER.debug("  dDefValue: {0} {1}".format(type(dDefValue), dDefValue))

                #nrEntries - 32-Bit Integer (little endian) - 4 bytes
                nrEntries = unpack('<i', payload[x+24:x+28])[0]
                #_LOGGER.debug("  nrEntries: {0} {1}".format(type(nrEntries), nrEntries))

                y = 0
                while y < nrEntries:
                    ys = 28 + (y*24)
                    y = y + 1

                    #nMode - 32-Bit Integer (little endian) number of mode - 4 bytes
                    nMode = unpack('<i', payload[ys+0:ys+4])[0]
                    #_LOGGER.debug("    nMode: {0} {1}".format(type(nMode), nMode))

                    #nFrom - 32-Bit Integer (little endian) from-time in minutes since midnight - 4 bytes
                    nFrom = unpack('<i', payload[ys+4:ys+8])[0]
                    #_LOGGER.debug("    nFrom: {0} {1}".format(type(nFrom), nFrom))

                    #nTo - 32-Bit Integer (little endian) to-time in minutes since midnight - 4 bytes
                    nTo = unpack('<i', payload[ys+8:ys+12])[0]
                    #_LOGGER.debug("    nTo: {0} {1}".format(type(nTo), nTo))

                    #bNeedActivate - 32-Bit Integer (little endian) need activate (trigger) - 4 bytes
                    bNeedActivate = unpack('<i', payload[ys+12:ys+16])[0]
                    #_LOGGER.debug("    bNeedActivate: {0} {1}".format(type(bNeedActivate), bNeedActivate))

                    #dValue - 64-Bit Float (little endian) value (if analog daytimer) - 8 bytes
                    dValue = unpack('<d', payload[x+16:x+24])[0]
                    #_LOGGER.debug("    dValue: {0} {1}".format(type(dValue), dValue))

                x = x + 28 + (24 * nrEntries)

        elif header.msg_type == "OutOfService":
            """OutOfService"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - OutOfService'.format(message_timestamp, len(payload)))

        elif header.msg_type == "KeepAlive":
            """KeepAlive"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - KeepAlive'.format(message_timestamp, len(payload)))

        elif header.msg_type == "Weather-States":
            """Weather-States"""
            #_LOGGER.debug('BINARY MESSAGE - {1} bytes - Weather-States'.format(message_timestamp, len(payload)))
            x = 0
            while x < len(payload):
                #uuid - 128-Bit uuid - 16 bytes
                uuid = self.getUuid(payload[x:x+16])
                #_LOGGER.debug("  uuid: {0} {1} {2}".format(type(uuid), len(uuid), uuid))

                #lastUpdate - 32-Bit Unsigned Integer (little endian) - 4 bytes
                lastUpdate = unpack('<I', payload[x+16:x+20])[0]
                #_LOGGER.debug("  lastUpdate: {0} {1}".format(type(lastUpdate), lastUpdate))

                #nrEntries - 32-Bit Integer (little endian) - 4 bytes
                nrEntries = unpack('<i', payload[x+20:x+24])[0]
                #_LOGGER.debug("  nrEntries: {0} {1}".format(type(nrEntries), nrEntries))

                y = 0
                while y < nrEntries:
                    ys = 24 + (y*24)
                    y = y + 1

                    #​timestamp - 32-Bit Integer (little endian) - 4 bytes
                    timestamp = unpack('<i', payload[ys+0:ys+4])[0]
                    #_LOGGER.debug("    timestamp: {0} {1}".format(type(timestamp), timestamp))

                    #​weatherType - 32-Bit Integer (little endian) - 4 bytes
                    weatherType = unpack('<i', payload[ys+4:ys+8])[0]
                    #_LOGGER.debug("    ​weatherType: {0} {1}".format(type(weatherType), weatherType))

                    #​windDirection - 32-Bit Integer (little endian) - 4 bytes
                    windDirection = unpack('<i', payload[ys+8:ys+12])[0]
                    #_LOGGER.debug("    ​windDirection: {0} {1}".format(type(windDirection), windDirection))

                    #​solarRadiation - 32-Bit Integer (little endian) - 4 bytes
                    solarRadiation = unpack('<i', payload[ys+12:ys+16])[0]
                    #_LOGGER.debug("    ​solarRadiation: {0} {1}".format(type(solarRadiation), solarRadiation))

                    #​relativeHumidity - 32-Bit Integer (little endian) - 4 bytes
                    relativeHumidity = unpack('<i', payload[ys+16:ys+20])[0]
                    #_LOGGER.debug("    ​relativeHumidity: {0} {1}".format(type(relativeHumidity), relativeHumidity))

                    #​temperature - 64-Bit Float (little endian) - 8 bytes
                    temperature = unpack('<d', payload[ys+20:ys+28])[0]
                    #_LOGGER.debug("    ​temperature: {0} {1}".format(type(temperature), temperature))

                    #​perceivedTemperature - 64-Bit Float (little endian) 8 - bytes
                    perceivedTemperature = unpack('<d', payload[ys+28:ys+36])[0]
                    #_LOGGER.debug("    ​perceivedTemperature: {0} {1}".format(type(perceivedTemperature), perceivedTemperature))

                    #​dewPoint - 64-Bit Float (little endian) - 8 bytes
                    dewPoint = unpack('<d', payload[ys+36:ys+44])[0]
                    #_LOGGER.debug("    ​dewPoint: {0} {1}".format(type(dewPoint), dewPoint))

                    #​precipitation - 64-Bit Float (little endian) - 8 bytes
                    precipitation = unpack('<d', payload[ys+44:ys+52])[0]
                    #_LOGGER.debug("    ​precipitation: {0} {1}".format(type(precipitation), precipitation))

                    #​windSpeed - 64-Bit Float (little endian) - 8 bytes
                    windSpeed = unpack('<d', payload[ys+52:ys+60])[0]
                    #_LOGGER.debug("    ​windSpeed: {0} {1}".format(type(windSpeed), windSpeed))

                    #barometicPressure - 64-Bit Float (little endian) - 8 bytes
                    barometicPressure = unpack('<d', payload[ys+60:ys+68])[0]
                    #_LOGGER.debug("    barometicPressure: {0} {1}".format(type(barometicPressure), barometicPressure))

                x = x + 24 + (68 * nrEntries)

    def getUuid(self, data):
        """UUID"""
        hexva = b2a_hex(data)
        #_LOGGER.debug("    hexva: {0} {1} {2}".format(type(hexva), len(hexva), hexva))

        a = hexva[0:8]
        #_LOGGER.debug("    a: {0} {1} {2}".format(type(a), len(a), a))
        a1 = "{:08x}".format(int.from_bytes(a2b_hex(a), byteorder='little'))
        #_LOGGER.debug("    a1: {0} {1} {2}".format(type(a1), len(a1), a1))

        b = hexva[8:12]
        #_LOGGER.debug("    b: {0} {1} {2}".format(type(b), len(b), b))
        b1 = "{:04x}".format(int.from_bytes(a2b_hex(b), byteorder='little'))
        #_LOGGER.debug("    b1: {0} {1} {2}".format(type(b1), len(b1), b1))

        c = hexva[12:16]
        #_LOGGER.debug("    c: {0} {1} {2}".format(type(c), len(c), c))
        c1 = "{:04x}".format(int.from_bytes(a2b_hex(c), byteorder='little'))
        #_LOGGER.debug("    c1: {0} {1} {2}".format(type(c1), len(c1), c1))

        d1 = str(hexva[16:32],'utf8')
        #_LOGGER.debug("    d1: {0} {1} {2}".format(type(d1), len(d1), d1))

        uuid = "{0}-{1}-{2}-{3}".format(a1, b1, c1, d1)
        #_LOGGER.debug("    uuid: {0} {1} {2}".format(type(uuid), len(uuid), uuid))

        return uuid