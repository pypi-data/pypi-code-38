
import redis
from pyrediseasyio.abstract_reader_writer import AbstractReaderWriter
from typing import List


class ReaderWriter(AbstractReaderWriter):

    def __init__(self, host='localhost', port=6379, db=0,
                 channel: str = None, channels: List[str] = None):
        """
        :param host: If pointing to an external server, include the url here
        :param db: The db number can be used to segregate communication
        :param channel: for Pub/Sub only, the channel to listen to
        :param channels: For Pub/Sub only, the _channels to listen to
        Note, either supply channel, or _channels - not both.
        """
        self._server = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self._pubsub = self._server.pubsub(ignore_subscribe_messages=True)

        # If _channels provided, then subscribe
        if channel is None and channels is None:
            return
        self._channels = []  # type: List[str]
        self._channels = [channel] if channel is not None else channels
        self._pubsub.subscribe(self._channels)
        self.get_messages()

    def flush_keys(self):
        self._server.flushdb()

    @staticmethod
    def _get_channel_and_data_from_message(message: dict):
        c = message.get('channel')
        d = message.get('data')
        return c, d

    @property
    def channels(self) -> List[str]:
        """Names of all channels subscribed to for pub/sub"""
        return self._channels

    # Gets a message from the subscription if it exists, otherwise returns nothing.
    def get_next_message(self, get_subscription_message=False):
        """
        Checks to see if a single message is waiting and returns it, otherwise returns None
        :param get_subscription_message: If this is true, messages will also include first-time subscription
        notifications. It is generally better to leave this False as the data response won't match expectations.
        :return: tuple (channel, data) or None
        note: If multiple messages are waiting, only the first in line will be returned.
        """
        message = self._pubsub.get_message(ignore_subscribe_messages=not get_subscription_message)
        if message is None:
            return None
        return self._get_channel_and_data_from_message(message)

    def get_messages(self, get_subscription_messages=False, limit=100):
        """
        Checks for waiting messages and returns all of them, an empty list if none are waiting.
        :param get_subscription_messages: If this is true, messages will also include first-time subscription
        notifications. It is generally better to leave this False as the data response won't match expectations.
        :param limit: Applies a cap to the number of messages that will be returned.
        :return: Returns a list of tuples (channel, data) or an empty list if no messages are found.
        """
        messages = []
        msg = self.get_next_message(get_subscription_messages)
        while msg is not None:
            messages.append(msg)
            msg = self.get_next_message(get_subscription_messages)
            if len(messages) >= limit:
                break
        return messages

    def listen(self):
        """
        A blocking call to pub/sub - listens for a message and yields response if one arrives
        :return yields a tuple of (channel, data) under normal conditions. If error, yields tuple of ("Error", ex)
        """
        for message in self._pubsub.listen():
            try:
                channel, data = self._get_channel_and_data_from_message(message)
                yield channel, data
            except Exception as ex:
                yield 'Error', ex

    def publish(self, value: str, channel: str = None):
        """
        Publishes a message to all subscribers
        :param value: The value to publish, must be a string.
        :param channel: If none, will write to all _channels
        :return: Nothing
        """
        channels = [channel] if channel is not None else self._channels
        for channel in channels:
            self._server.publish(channel, value)

    def read(self, addr):
        return self._server.get(addr)

    def write(self, addr, value):
        value = str(value)
        self._server.set(addr, value)



