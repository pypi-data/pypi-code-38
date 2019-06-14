import logging
import time
from abc import abstractmethod, ABC
from json import JSONDecodeError
from typing import Type, Optional, Callable

import sseclient
from requests import ConnectionError
from requests.exceptions import ChunkedEncodingError

from coin_sdk.number_portability.domain import MessageType, ConfirmationStatus
from coin_sdk.number_portability.securityservice import SecurityService
from coin_sdk.number_portability.utils import json2obj, handle_http_error, get_stream
from coin_sdk.number_portability.config import Config

logger = logging.getLogger(__name__)


class OffsetPersister(ABC):
    @abstractmethod
    def persist_offset(self, offset):
        pass

    @abstractmethod
    def get_persisted_offset(self):
        pass


class Receiver(ABC):
    class RetriesLeft:
        def __init__(self, number_of_retries):
            self._default = number_of_retries
            self._number_of_retries = number_of_retries

        def reset(self):
            self._number_of_retries = self._default

        def decrement(self):
            self._number_of_retries -= 1

        def get(self):
            return self._number_of_retries

        def __call__(self):
            return self._number_of_retries > 0

    def __init__(self, config: Config):
        self._security_service = SecurityService(config)
        self._config = config
        self._offset_persister: Optional[OffsetPersister] = None
        self._recover_offset: Callable[[int], int] = lambda x: x
        self._event_map = {
            MessageType.PORTING_REQUEST_V1.get_event_type(): self.on_porting_request,
            MessageType.PORTING_REQUEST_ANSWER_V1.get_event_type(): self.on_porting_request_answer,
            MessageType.PORTING_REQUEST_ANSWER_DELAYED_V1.get_event_type(): self.on_porting_request_answer_delayed,
            MessageType.PORTING_PERFORMED_V1.get_event_type(): self.on_porting_performed,
            MessageType.DEACTIVATION_V1.get_event_type(): self.on_deactivation,
            MessageType.CANCEL_V1.get_event_type(): self.on_cancel,
            MessageType.ERROR_FOUND_V1.get_event_type(): self.on_error_found
        }

    def start_stream(
            self,
            offset: int = None,
            confirmation_status: ConfirmationStatus = None,
            offset_persister: Type[OffsetPersister] = None,
            recover_offset: Callable[[int], int] = lambda x: x,
            message_types: [MessageType] = None
    ):
        self._running = True
        self._setup(confirmation_status, offset_persister, recover_offset)
        retries_left = self.RetriesLeft(self._config.number_of_retries)
        while retries_left():
            try:
                self._connect(offset, confirmation_status, message_types, retries_left)
                return
            except (ConnectionError, ChunkedEncodingError) as e:
                # ChunckedEncodingError occurs when backend stops while waiting for new events
                logger.error(type(e).__name__)
                logger.error(e)
                logger.error(f'Trying to reconnect in {self._config.backoff_period} seconds. Retries left: {retries_left.get()}')
                retries_left.decrement()
                if self._offset_persister:
                    offset = self._offset_persister.get_persisted_offset()
                    offset = self._recover_offset(offset)
                time.sleep(self._config.backoff_period)

    def _setup(
            self,
            confirmation_status: ConfirmationStatus,
            offset_persister: Type[OffsetPersister],
            recover_offset: Callable[[int], int]
    ):
        if confirmation_status == ConfirmationStatus.ALL and not offset_persister:
            raise ValueError('offset_persister should be given when confirmation_status equals ALL')
        if offset_persister and not issubclass(offset_persister, OffsetPersister):
            raise ValueError(f'offset_persister should be a subclass of {OffsetPersister.__module__}.OffsetPersister')
        self._offset_persister = offset_persister and offset_persister()
        self._recover_offset = recover_offset

    def _connect(self, offset: int, confirmation_status: ConfirmationStatus, message_types: [MessageType], retries_left: RetriesLeft):
        logger.debug('Opening stream')
        response = get_stream(self._config.sse_url, offset, confirmation_status, message_types, self._security_service)
        logger.debug(f'url: {response.request.url}')
        handle_http_error(response)
        client = sseclient.SSEClient(response)
        retries_left.reset()
        self._consume_stream(client)

    def _consume_stream(self, client: sseclient.SSEClient):
        for event in client.events():
            if self._running == False:
                return
            logger.debug('Received event')
            logger.debug(f'{event}')
            if event.data:
                self._process_event(event)
            else:
                self.on_keep_alive(event.id)

    def stop(self):
        self._running = False

    def _process_event(self, event):
        try:
            event_type = event.event.lower()
            logger.debug(f'Event: {event.event}')
            message = json2obj(event.data).message
            logger.debug(f'Message: {message}')
            message_id = event.id
            logger.debug(f'Message id: {message_id}')
            event_handler = self._event_map.get(event_type, None)
            if event_handler:
                event_handler(message_id, message)
                self._persist_offset(message_id)
            else:
                logger.error(f"Number Portability Message with the following content isn't supported: {event}")
        except (JSONDecodeError, AttributeError):
            logger.error(f"Conversion of Number Portability Message failed for the following event: {event}")

    def _persist_offset(self, message_id):
        if self._offset_persister:
            self._offset_persister.persist_offset(message_id)

    @abstractmethod
    def on_keep_alive(self, message_id):
        pass

    @abstractmethod
    def on_porting_request(self, message_id, message):
        pass

    @abstractmethod
    def on_porting_request_answer(self, message_id, message):
        pass

    @abstractmethod
    def on_porting_request_answer_delayed(self, message_id, message):
        pass

    @abstractmethod
    def on_porting_performed(self, message_id, message):
        pass

    @abstractmethod
    def on_deactivation(self, message_id, message):
        pass

    @abstractmethod
    def on_cancel(self, message_id, message):
        pass

    @abstractmethod
    def on_error_found(self, message_id, message):
        pass
