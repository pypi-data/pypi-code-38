"""Service for exchanging data with WolkGateway."""
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

from typing import Callable, List
from time import time, sleep

from paho.mqtt import client as mqtt

from wolk_gateway_module.logger_factory import logger_factory
from wolk_gateway_module.connectivity.connectivity_service import (
    ConnectivityService,
)
from wolk_gateway_module.model.message import Message


class MQTTConnectivityService(ConnectivityService):
    """Responsible for exchanging data with WolkGateway through MQTT."""

    def __repr__(self) -> str:
        """Make string representation of MQTTConnectivityService.

        :returns: representation
        :rtype: str
        """
        return (
            f"MQTTConnectivityService(host='{self.host}', "
            f"port='{self.port}', "
            f"client_id='{self.client_id}', "
            f"topics='{self.topics}', "
            f"qos='{self.qos}', "
            f"lastwill_message='{self.lastwill_message}', "
            f"inbound_message_listener='{self.inbound_message_listener}', "
            f"connected='{self._connected}')"
        )

    def __init__(
        self,
        host: str,
        port: int,
        client_id: str,
        qos: int,
        lastwill_message: Message,
        topics: list,
    ) -> None:
        """Prepare MQTT connectivity service for connecting to WolkGateway.

        :param host: Address of WolkGateway
        :type host: str
        :param port: TCP/IP port of WolkGateway used for MQTT connection
        :type port: int
        :param client_id: Unique module identifier
        :type client_id: str
        :param qos: MQTT Quality of Service level (0, 1, 2)
        :type qos: int
        :param lastwill_message: Last will message
        :type lastwill_message: Message
        :param topics: List of topics to subscribe to
        :type topics: list
        """
        self.log = logger_factory.get_logger(str(self.__class__.__name__))

        self.host = host
        self.port = port
        self.client_id = client_id
        self.topics = topics
        self.qos = qos
        self.lastwill_message = lastwill_message
        self.inbound_message_listener = None
        self._connected = False
        self.connected_rc = None

        self.log.debug(self.__repr__())

    def set_inbound_message_listener(
        self, on_inbound_message: Callable[[Message], None]
    ) -> None:
        """Set the callback function ot handle inbound messages.

        :param on_inbound_message: Callable that handles inbound messages
        :type on_inbound_message: Callable[Message]
        """
        self.log.debug(f"Set inbound message listener to {on_inbound_message}")
        self.inbound_message_listener = on_inbound_message

    def set_lastwill_message(self, message: Message) -> None:
        """Send offline state for module devices on disconnect."""
        self.log.debug(f"Set lastwill message: {message}")
        if self._connected:
            self.log.debug("Reconnecting to set lastwill")
            self.disconnect()
            self.lastwill_message = message
            self.connect()
        else:
            self.lastwill_message = message

    def add_subscription_topics(self, topics: List[str]) -> None:
        """Add subscription topics.

        :param topics: List of topics
        :type topics: List[str]
        """
        self.log.debug(f"Adding {topics} to {self.topics}")
        self.topics.extend(topics)

    def remove_topics_for_device(self, device_key: str) -> None:
        """Remove topics for device from subscription topics.

        :param device_key: Device identifier
        :type device_key: str
        """
        self.log.debug(f"Removing topics for device {device_key}")
        if len(self.topics) == 0:
            return

        for topic in self.topics:
            if device_key in topic:
                self.topics.remove(topic)

    def connected(self) -> bool:
        """Return if currently connected.

        :returns: connected
        :rtype: bool
        """
        return self._connected

    def connect(self) -> bool:
        """Establish connection with WolkGateway.

        :returns: result
        :rtype: bool

        :raises RuntimeError: Reason for connection being refused
        """
        if self._connected:
            self.log.debug("Already connected")
            return True

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_mqtt_connect
        self.client.on_disconnect = self._on_mqtt_disconnect
        self.client.on_message = self._on_mqtt_message
        self.client.username_pw_set(self.client_id)
        self.client.will_set(
            self.lastwill_message.topic, self.lastwill_message.payload
        )
        self.client.connect(self.host, self.port)
        self.client.loop_start()

        self.log.info(f"Connecting to {self.host}:{self.port} ...")

        timeout = round(time()) + 5

        while True:

            if round(time()) > timeout:
                raise RuntimeError("Connection timed out!")

            if self.connected_rc is None:
                sleep(0.1)
                continue

            if self.connected_rc == 0:
                self._connected = True
                break

            elif self.connected_rc == 1:
                raise RuntimeError(
                    "Connection refused - incorrect protocol version"
                )

            elif self.connected_rc == 2:
                raise RuntimeError(
                    "Connection refused - invalid client identifier"
                )

            elif self.connected_rc == 3:
                raise RuntimeError("Connection refused - server unavailable")

            elif self.connected_rc == 4:
                raise RuntimeError(
                    "Connection refused - bad username or password"
                )

            elif self.connected_rc == 5:
                raise RuntimeError("Connection refused - not authorised")

        self.log.debug(f"Subscribing to topics: {self.topics}")
        for topic in self.topics:
            self.client.subscribe(topic, 2)

        return self._connected

    def reconnect(self) -> bool:
        """Terminate existing and create new connection with WolkGateway.

        :returns: result
        :rtype: bool

        :raises RuntimeError: Reason for connection being refused
        """
        self.log.debug("Attempting reconnect")
        self._connected = False
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except AttributeError:
            pass
        try:
            return self.connect()
        except RuntimeError as exception:
            raise exception

    def disconnect(self) -> None:
        """Terminate connection with WolkGateway."""
        self.log.debug(f"Disconnecting from {self.host} : {self.port}")
        try:
            self.client.publish(
                self.lastwill_message.topic, self.lastwill_message.payload
            )
            self.client.loop_stop()
            self.client.disconnect()
        except AttributeError:
            pass
        self._connected = False

    def publish(self, message: Message) -> bool:
        """Publish serialized data to WolkGateway.

        :param message: Message to be published
        :type message: Message
        :returns: result
        :rtype: bool
        """
        if not self._connected:
            self.log.warning(f"Not connected, unable to publish {message}")
            return False

        info = self.client.publish(message.topic, message.payload, self.qos)

        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            self.log.debug(f"Published {message}")
            return True
        else:
            return info.is_published()

    def _on_mqtt_message(
        self, client: mqtt.Client, userdata: str, message: mqtt.MQTTMessage
    ):
        """Parse inbound messages and pass them to message listener.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: Private user data set in Client()
        :type userdata: str
        :param message: Class with members: topic, payload, qos, retain.
        :type message: paho.mqtt.MQTTMessage
        """
        self.inbound_message_listener(Message(message.topic, message.payload))

    def _on_mqtt_connect(
        self, client: mqtt.Client, userdata: str, flags: int, rc: int
    ):
        """
        Handle when the client receives a CONNACK response from the server.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: private user data set in Client()
        :type userdata: str
        :param flags: Response flags sent by the broker
        :type flags: int
        :param rc: Connection result
        :type rc: int
        """
        self.log.debug(f"CONNACK: {rc}")
        if rc == 0:  # Connection successful
            self._connected = True
            self.connected_rc = 0
            # Subscribing in on_mqtt_connect() means if we lose the connection
            # and reconnect then subscriptions will be renewed.
            if self.topics:
                for topic in self.topics:
                    self.client.subscribe(topic, 2)
        elif rc == 1:  # Connection refused - incorrect protocol version
            self.connected_rc = 1
        elif rc == 2:  # Connection refused - invalid client identifier
            self.connected_rc = 2
        elif rc == 3:  # Connection refused - server unavailable
            self.connected_rc = 3
        elif rc == 4:  # Connection refused - bad username or password
            self.connected_rc = 4
        elif rc == 5:  # Connection refused - not authorised
            self.connected_rc = 5

    def _on_mqtt_disconnect(
        self, client: mqtt.Client, userdata: str, rc: int
    ) -> None:
        """
        Handle when the client disconnects from the broker.

        :param client: Client that received the message
        :type client: paho.mqtt.Client
        :param userdata: private user data set in Client()
        :type userdata: str
        :param rc: Disconnection result
        :type rc: int
        :raises RuntimeError: Unexpected disconnection
        """
        self.log.debug(f"Disconnect return code: {rc}")
        if rc != 0:
            raise RuntimeError("Unexpected disconnection.")
        self._connected = False
        self.connected_rc = None
