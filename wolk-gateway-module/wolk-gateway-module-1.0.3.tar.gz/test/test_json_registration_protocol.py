"""Tests for JsonRegistrationProtocol."""
#   Copyright 2019 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json
import sys
import unittest

sys.path.append("..")  # noqa

from wolk_gateway_module.json_registration_protocol import (
    JsonRegistrationProtocol,
)
from wolk_gateway_module.model.actuator_template import ActuatorTemplate
from wolk_gateway_module.model.alarm_template import AlarmTemplate
from wolk_gateway_module.model.configuration_template import (
    ConfigurationTemplate,
)
from wolk_gateway_module.model.data_type import DataType
from wolk_gateway_module.model.device_registration_request import (
    DeviceRegistrationRequest,
)
from wolk_gateway_module.model.device_registration_response import (
    DeviceRegistrationResponse,
)
from wolk_gateway_module.model.device_registration_response_result import (
    DeviceRegistrationResponseResult,
)
from wolk_gateway_module.model.device_template import DeviceTemplate
from wolk_gateway_module.model.message import Message
from wolk_gateway_module.model.reading_type_measurement_unit import (
    ReadingTypeMeasurementUnit,
)
from wolk_gateway_module.model.reading_type_name import ReadingTypeName
from wolk_gateway_module.model.sensor_template import SensorTemplate
from wolk_gateway_module.protocol.registration_protocol import (
    RegistrationProtocol,
)


class JsonRegistrationProtocolTests(unittest.TestCase):
    """JsonRegistrationProtocol Tests."""

    DEVICE_PATH_PREFIX = "d/"
    CHANNEL_WILDCARD = "#"
    DEVICE_REGISTRATION_REQUEST_TOPIC_ROOT = "d2p/register_subdevice_request/"
    DEVICE_REGISTRATION_RESPONSE_TOPIC_ROOT = (
        "p2d/register_subdevice_response/"
    )

    def test_get_inbound_topics_for_device(self):
        """Test that returned list is correct for given device key."""
        json_registration_protocol = JsonRegistrationProtocol()
        device_key = "some_key"

        self.assertEqual(
            json_registration_protocol.get_inbound_topics_for_device(
                device_key
            ),
            [
                self.DEVICE_REGISTRATION_RESPONSE_TOPIC_ROOT
                + self.DEVICE_PATH_PREFIX
                + device_key
            ],
        )

    def test_extract_key_from_message(self):
        """Test that device key is extracted."""
        json_registration_protocol = JsonRegistrationProtocol()
        device_key = "some_device_key"

        message = Message(
            self.DEVICE_REGISTRATION_RESPONSE_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key
        )

        self.assertEqual(
            json_registration_protocol.extract_key_from_message(message),
            device_key,
        )

    def test_is_registration_response_message(self):
        """Test that message is device registration response."""
        json_registration_protocol = JsonRegistrationProtocol()

        message = Message(self.DEVICE_REGISTRATION_RESPONSE_TOPIC_ROOT)

        self.assertTrue(
            json_registration_protocol.is_registration_response_message(
                message
            )
        )

    def test_empty_device_registration_request(self):
        """Test registration request for empty device template."""
        json_registration_protocol = JsonRegistrationProtocol()

        device_template = DeviceTemplate()
        device_name = "device_name"
        device_key = "device_key"

        device_registration_request = DeviceRegistrationRequest(
            device_name, device_key, device_template
        )

        expected_payload = json.loads(
            "{"
            + '"name": "device_name",'
            + '"deviceKey": "device_key",'
            + '"defaultBinding": true,'
            + '"sensors": [],'
            + '"actuators": [],'
            + '"alarms": [],'
            + '"configurations": [],'
            + '"typeParameters": {},'
            + '"connectivityParameters": {},'
            + '"firmwareUpdateParameters": {"supportsFirmwareUpdate": false},'
            + '"firmwareUpdateType": ""'
            + "}"
        )

        message = json_registration_protocol.make_registration_message(
            device_registration_request
        )

        self.assertEqual(expected_payload, json.loads(message.payload))

    def test_simple_device_registration_request(self):
        """Test registration request for simple device template."""
        json_registration_protocol = JsonRegistrationProtocol()

        device_name = "simple_device"
        device_key = "simple_key"
        temperature_sensor = SensorTemplate(
            "Temperature",
            "T",
            reading_type_name=ReadingTypeName.TEMPERATURE,
            unit=ReadingTypeMeasurementUnit.CELSIUS,
            minimum=0,
            maximum=100,
            description="A temperature sensor",
        )

        sensors = [temperature_sensor]

        device_template = DeviceTemplate(sensors=sensors)

        device_registration_request = DeviceRegistrationRequest(
            device_name, device_key, device_template
        )

        expected_payload = json.loads(
            "{"
            + '"name": "simple_device",'
            + '"deviceKey": "simple_key",'
            + '"defaultBinding": true,'
            + '"sensors": ['
            + '{"name": "Temperature", '
            + '"reference": "T", '
            + '"unit": {"readingTypeName": "TEMPERATURE", "symbol": "℃"}, '
            + '"description": "A temperature sensor", '
            + '"minimum": 0, '
            + '"maximum": 100}],'
            + '"actuators": [],'
            + '"alarms": [],'
            + '"configurations": [],'
            + '"typeParameters": {},'
            + '"connectivityParameters": {},'
            + '"firmwareUpdateParameters": {"supportsFirmwareUpdate": false},'
            + '"firmwareUpdateType": ""'
            + "}"
        )

        message = json_registration_protocol.make_registration_message(
            device_registration_request
        )

        self.assertEqual(expected_payload, json.loads(message.payload))

    def test_full_device_registration_request(self):
        """Test registration request for full device template."""
        json_registration_protocol = JsonRegistrationProtocol()

        device_name = "full_device"
        device_key = "full_key"
        temperature_sensor = SensorTemplate(
            "Temperature",
            "T",
            reading_type_name=ReadingTypeName.TEMPERATURE,
            unit=ReadingTypeMeasurementUnit.CELSIUS,
            minimum=0,
            maximum=100,
            description="A temperature sensor",
        )
        pressure_sensor = SensorTemplate(
            "Pressure",
            "P",
            reading_type_name=ReadingTypeName.PRESSURE,
            unit=ReadingTypeMeasurementUnit.MILLIBAR,
            description="A pressure sensor",
            minimum=300,
            maximum=1200,
        )
        humidity_sensor = SensorTemplate(
            "Humidity",
            "H",
            reading_type_name=ReadingTypeName.HUMIDITY,
            unit=ReadingTypeMeasurementUnit.PERCENT,
            description="A humidity sensor",
            minimum=0,
            maximum=100,
        )

        accelerometer_sensor = SensorTemplate(
            "Accelerometer",
            "ACL",
            reading_type_name=ReadingTypeName.ACCELEROMETER,
            unit=ReadingTypeMeasurementUnit.METRES_PER_SQUARE_SECOND,
            description="An accelerometer sensor",
            minimum=0,
            maximum=100,
        )

        sensors = [
            temperature_sensor,
            pressure_sensor,
            humidity_sensor,
            accelerometer_sensor,
        ]

        high_humidity_alarm = AlarmTemplate(
            "High Humidity", "HH", "High humidity has been detected"
        )

        alarms = [high_humidity_alarm]

        slider_actuator = ActuatorTemplate(
            "Slider", "SL", data_type=DataType.NUMERIC, minimum=0, maximum=100
        )

        switch_actuator = ActuatorTemplate(
            "Switch", "SW", data_type=DataType.BOOLEAN
        )

        actuators = [switch_actuator, slider_actuator]

        configuration_1 = ConfigurationTemplate(
            "configuration_1",
            "config_1",
            DataType.NUMERIC,
            minimum=0,
            maximum=100,
        )
        configuration_2 = ConfigurationTemplate(
            "configuration_2", "config_2", DataType.BOOLEAN
        )
        configuration_3 = ConfigurationTemplate(
            "configuration_3", "config_3", DataType.STRING
        )
        configuration_4 = ConfigurationTemplate(
            "configuration_4",
            "config_4",
            DataType.STRING,
            size=3,
            labels="a,b,c",
        )

        configurations = [
            configuration_1,
            configuration_2,
            configuration_3,
            configuration_4,
        ]

        device_template = DeviceTemplate(
            actuators, alarms, configurations, sensors, True
        )

        device_registration_request = DeviceRegistrationRequest(
            device_name, device_key, device_template
        )

        expected_payload = json.loads(
            "{"
            + '"name": "full_device",'
            + '"deviceKey": "full_key",'
            + '"defaultBinding": true,'
            + '"typeParameters": {},'
            + '"connectivityParameters": {},'
            + '"firmwareUpdateType": "DFU",'
            + '"sensors": ['
            + "  {"
            + '    "name": "Temperature",'
            + '    "reference": "T",'
            + '    "description": "A temperature sensor",'
            + '    "unit": {'
            + '      "readingTypeName": "TEMPERATURE",'
            + '      "symbol": "℃"'
            + "    },"
            + '    "minimum": 0,'
            + '    "maximum": 100'
            + "  },"
            + "  {"
            + '    "name": "Pressure",'
            + '    "reference": "P",'
            + '    "description": "A pressure sensor",'
            + '    "unit": {'
            + '      "readingTypeName": "PRESSURE",'
            + '      "symbol": "mb"'
            + "    },"
            + '    "minimum": 300,'
            + '    "maximum": 1200'
            + "  },"
            + "  {"
            + '    "name": "Humidity",'
            + '    "reference": "H",'
            + '    "description": "A humidity sensor",'
            + '    "unit": {'
            + '      "readingTypeName": "HUMIDITY",'
            + '      "symbol": "%"'
            + "    },"
            + '    "minimum": 0,'
            + '    "maximum": 100'
            + "  },"
            + "  {"
            + '    "name": "Accelerometer",'
            + '    "reference": "ACL",'
            + '    "description": "An accelerometer sensor",'
            + '    "unit": {'
            + '      "readingTypeName": "ACCELEROMETER",'
            + '      "symbol": "m/s²"'
            + "    },"
            + '    "minimum": 0,'
            + '    "maximum": 100'
            + "  }"
            + "],"
            + '"actuators": ['
            + "  {"
            + '    "name": "Switch",'
            + '    "reference": "SW",'
            + '    "unit": {'
            + '      "readingTypeName": "SWITCH(ACTUATOR)",'
            + '      "symbol": ""'
            + "    },"
            + '    "description": ""'
            + "  },"
            + "  {"
            + '    "name": "Slider",'
            + '    "reference": "SL",'
            + '    "unit": {'
            + '      "readingTypeName": "COUNT(ACTUATOR)",'
            + '      "symbol": "count"'
            + "    },"
            + '    "description": "",'
            + '    "minimum": 0,'
            + '    "maximum": 100'
            + "  }"
            + "],"
            + '"alarms": ['
            + "  {"
            + '    "name": "High Humidity",'
            + '    "reference": "HH",'
            + '    "description": "High humidity has been detected"'
            + "  }"
            + "],"
            + '"configurations": ['
            + "  {"
            + '    "name": "configuration_1",'
            + '    "reference": "config_1",'
            + '    "dataType": "NUMERIC",'
            + '    "labels": [],'
            + '    "minimum": 0,'
            + '    "maximum": 100'
            + "  },"
            + "  {"
            + '    "name": "configuration_2",'
            + '    "reference": "config_2",'
            + '    "dataType": "BOOLEAN",'
            + '    "labels": []'
            + "  },"
            + "  {"
            + '    "name": "configuration_3",'
            + '    "reference": "config_3",'
            + '    "dataType": "STRING",'
            + '    "labels": []'
            + "  },"
            + "  {"
            + '    "name": "configuration_4",'
            + '    "reference": "config_4",'
            + '    "dataType": "STRING",'
            + '    "size": 3,'
            + '    "labels": "a,b,c"'
            + "  }"
            + "],"
            + '"firmwareUpdateParameters": {'
            + '  "supportsFirmwareUpdate": true}'
            + "}"
        )

        message = json_registration_protocol.make_registration_message(
            device_registration_request
        )

        self.assertEqual(expected_payload, json.loads(message.payload))


def test_make_registration_response(self):
    """Test for valid response parsing."""
    json_registration_protocol = JsonRegistrationProtocol()
    message = Message(
        "", '{"payload":{"device_key":"some_key"}, "result":"OK"}'
    )

    expected = DeviceRegistrationResponse(
        "some_key", DeviceRegistrationResponseResult.OK
    )

    deserialized = json_registration_protocol.make_registration_response(
        message
    )

    self.assertEqual(expected, deserialized)


if __name__ == "__main__":
    unittest.main()
