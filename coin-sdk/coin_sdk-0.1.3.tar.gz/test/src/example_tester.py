import random
import unittest
import logging
import sys
import os
from collections import namedtuple

from requests import HTTPError

from coin_sdk.number_portability.config import Config, set_logging
from coin_sdk.number_portability.domain import ConfirmationStatus
from coin_sdk.number_portability.messages.cancel import CancelBuilder
from coin_sdk.number_portability.messages.deactivation import DeactivationBuilder
from coin_sdk.number_portability.messages.portingperformed import PortingPerformedBuilder
from coin_sdk.number_portability.messages.portingrequest import PortingRequestBuilder
from coin_sdk.number_portability.messages.portingrequestanswer import PortingRequestAnswerBuilder
from coin_sdk.number_portability.messages.portingrequestanswerdelayed import PortingRequestAnswerDelayedBuilder
from coin_sdk.number_portability.receiver import Receiver, OffsetPersister
from coin_sdk.number_portability.sender import Sender

config = Config(
    os.getenv('CRDB_REST_BACKEND', 'http://0.0.0.0:8000'),
    'loadtest-loada',
    private_key_file='./test/setup/private-key.pem',
    hmac_secret='./test/setup/sharedkey.encrypted'
)

sender = Sender(config)
#set_logging(level=logging.DEBUG, stream=sys.stderr)

class ExamplesTest(unittest.TestCase):
    def test_porting_request(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        porting_request = (
            PortingRequestBuilder()
            .set_dossierid(dossier_id)
            .set_recipientnetworkoperator('LOADB')
            .set_header(sender_network_operator='LOADA', receiver_network_operator='LOADB')
            .add_porting_request_seq()
                .set_number_series('0612345678', '0612345678')
                .finish()
            .add_porting_request_seq()
                .set_number_series('0612345678', '0612345678')
                .add_enum_profiles('PROF1', 'PROF2')
                .finish()
            .set_customerinfo("test", "test bv", "1", "a", "1234AB", "1")
            .build()
        )
        sender.send_message(porting_request)

    def test_cancel(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        cancel = CancelBuilder() \
            .set_dossierid(dossier_id) \
            .set_header(sender_network_operator='LOADA', receiver_network_operator='LOADB') \
            .build()
        sender.send_message(cancel)

    def test_deactivation(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        deactivation = (
            DeactivationBuilder()
            .set_header(sender_network_operator='LOADA', receiver_network_operator='LOADB')
            .set_dossierid(dossier_id)
            .set_currentnetworkoperator('LOADB')
            .set_originalnetworkoperator('LOADA')
            .add_deactivation_seq()
                .set_number_series('0612345678', '0612345678')
                .finish()
            .build()
        )
        sender.send_message(deactivation)

    def test_porting_performed(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        porting_performed = (
            PortingPerformedBuilder()
            .set_header('LOADA', 'LOADB')
            .set_dossierid(dossier_id)
            .set_donornetworkoperator('LOADB')
            .set_recipientnetworkoperator('LOADA')
            .add_porting_performed_seq()
                .set_number_series('0612345678', '0612345678')
                .finish()
            .add_porting_performed_seq()
                .set_number_series('0612345678', '0612345678')
                .add_enum_profiles('PROF1', 'PROF2')
                .finish()
            .build()
        )
        sender.send_message(porting_performed)

    def test_porting_request_answer(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        porting_performed_answer = (
            PortingRequestAnswerBuilder()
            .set_header('LOADA', 'LOADB')
            .set_dossierid(dossier_id)
            .set_blocking('N')
            .add_porting_request_answer_seq()
                .set_donornetworkoperator('LOADA')
                .set_donorserviceprovider('LOADA')
                .set_firstpossibledate('20190101120000')
                .set_number_series('0612345678', '0612345678')
                .set_note('This is a note')
                .set_blockingcode('99')
                .finish()
            .add_porting_request_answer_seq()
                .set_donornetworkoperator('LOADA')
                .set_donorserviceprovider('LOADA')
                .set_firstpossibledate('20190101120000')
                .set_number_series('0612345678', '0612345678')
                .set_note('This is a note')
                .set_blockingcode('99')
                .finish()
            .build()
        )
        sender.send_message(porting_performed_answer)

    def test_porting_request_answer_delayed(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        porting_request_answer_delayed = (
            PortingRequestAnswerDelayedBuilder()
            .set_header('LOADA', 'LOADB')
            .set_dossierid(dossier_id)
            .set_donornetworkoperator('LOADB')
            .build()
        )
        sender.send_message(porting_request_answer_delayed)

    def test_send_error(self):
        dossier_id = self._generate_random_dossier_id('LOADA')
        porting_request_answer_delayed = (
            PortingRequestAnswerDelayedBuilder()
                .set_header('LOADA', 'LOADA')
                .set_dossierid(dossier_id)
                .set_donornetworkoperator('LOADB')
                .build()
        )
        try:
            sender.send_message(porting_request_answer_delayed)
        except HTTPError as e:
            print(e)

    def test_receive_message(self):
        TestReceiver(config).start_stream(confirmation_status=ConfirmationStatus.ALL, offset_persister=TestOffsetPersister)

    @staticmethod
    def _generate_random_dossier_id(operator: str):
        random_int = random.randint(10000, 99999)
        return f'{operator}-{random_int}'


class TestReceiver(Receiver):
    def on_keep_alive(self):
        pass

    def on_porting_request(self, message_id, message):
        print('porting request')
        self.handle_message(message_id, message)

    def on_porting_request_answer(self, message_id, message):
        print('porting request answer')
        self.handle_message(message_id, message)

    def on_porting_request_answer_delayed(self, message_id, message):
        print('porting request answer delayed')
        self.handle_message(message_id, message)

    def on_porting_performed(self, message_id, message):
        print('porting performed')
        self.handle_message(message_id, message)

    def on_deactivation(self, message_id, message):
        print('deactivation')
        self.handle_message(message_id, message)

    def on_cancel(self, message_id, message):
        print('cancel')
        self.handle_message(message_id, message)

    def on_error_found(self, message_id, message):
        print('error!')
        self.handle_message(message_id, message)
        self.stop()

    def handle_message(self, message_id, message):
        print(message)
        sender.confirm(message_id)


class TestOffsetPersister(OffsetPersister):
    def __init__(self):
        self._offset = -1

    def get_persisted_offset(self):
        return self._offset

    def persist_offset(self, offset):
        self._offset = offset


if __name__ == '__main__':
    unittest.main()
