import logging
import requests
import json

from phishme_intelligence.output.base_integration import BaseIntegration
from phishme_intelligence.output.product.splunk.modules.intelligence import Malware

class SplunkHec(BaseIntegration):
    def __init__(self, config, product):
        super(SplunkHec, self).__init__(config=config, product=product)

        self.logger = logging.getLogger(__name__)

        self.hec_token = self.config.get('integration_splunk_hec', 'token')
        self.hec_url = self.config.get('integration_splunk_hec', 'event_url')

    def process(self, mrti, threat_id):
        self.logger.info('[Splunk HEC] processing {}'.format(threat_id))
        """

        :param mrti: The data returned from PhishMe Intelligence
        :type mrti: :class:`phishme_intelligence.core.intelligence.Malware`
        :param int threat_id: PhishMe Intelligence Threat ID
        :return: None
        """

        self.logger.info('Sending data into splunk via HEC')

        # This is a jack move. I'm doing this to keep consistent with our current splunk integration.
        # mrti is type Malware from core.intelligence. The Malware object imported here is from the Splunk
        # integration so I'm taking the json from the core's Malware object and creating Splunk's malware
        # object with it. I don't like it, not one bit but it works for now.
        self._process_malware(Malware(mrti.json))

    def _send_to_splunk(self, event_data):

        event = {}
        event['event'] = event_data
        auth_header = {"Authorization": "Splunk {}".format(self.hec_token)}
        response = requests.post(self.hec_url,
                                 headers=auth_header,
                                 data=json.dumps(event),
                                 verify=self.config.getboolean('integration_splunk_hec', 'verify_splunk_ssl'))
        self.logger.info("Got a response of: {}".format(response.content))

    def _process_malware(self, malware):
        # Build context object
        context = {
            'threatType': malware.get_threat_type(),
            'brands': malware.get_brand(),
            'id': malware.get_threat_id(),
            'reportURL': malware.get_active_threat_report_url(),
            'threatDetailURL': malware.get_threathq_url(),
            'firstPublished': malware.get_first_published(),
            'lastPublished': malware.get_last_published(),
            'label': malware.get_label()
        }

        if self.config.getint('integration_splunk_hec', 'json_raw'):
            malware_reduced = malware.get_content()

            # Removing unnecessary elements.
            malware_reduced.pop('threatType', None)
            malware_reduced.pop('hasReport', None)

            # Add context.
            malware_reduced.update({'cofense_event_type': 'json_raw'})

            # Push data to Splunk.
            self._send_to_splunk(malware_reduced)

        if self.config.getint('integration_splunk_hec', 'json_blockset'):
            for item in malware.get_block_set():
                # Add context.
                item.update(context)
                item.update({'cofense_event_type': 'blockset'})

                # Push data to Splunk.
                self._send_to_splunk(item)

        if self.config.getint('integration_splunk_hec', 'json_executableset'):
            for item in malware.get_executable_set():
                # Remove unnecessary elements.
                item.pop('dateEntered', None)

                # Add context.
                item.update(context)
                item.update({'cofense_event_type': 'executableset'})

                # Push data to Splunk.
                self._send_to_splunk(item)

        if self.config.getint('integration_splunk_hec', 'json_senderemailset'):
            for item in malware.get_sender_email_set():
                # Remove unnecessary elements.

                # Add context.
                item.update(context)
                item.update({'cofense_event_type': 'senderemailset'})

                # Push data to Splunk.
                self._send_to_splunk(item)

        if self.config.getint('integration_splunk_hec', 'json_sendersubjectset'):
            for item in malware.get_subject_set():
                # Remove unnecessary elements.

                # Add context.
                item.update(context)
                item.update({'cofense_event_type': 'sendersubjectset'})

                # Push data to Splunk.
                self._send_to_splunk(item)
