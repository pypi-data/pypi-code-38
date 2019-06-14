import mock
import responses
import random
import unittest
import uuid
import re
import json
from datetime import datetime

from ppmutils.fhir import FHIR


class TestFHIR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Set the FHIR URL
        cls.fhir_url = 'https://fhir.ppm.aws.dbmi-test.hms.harvard.edu'
        cls.fhir_url_pattern = r'{}/.*'.format(cls.fhir_url)

        # Patch PPM FHIR URL
        cls.ppm_fhir_url_patcher = mock.patch('ppmutils.ppm.PPM.fhir_url')
        cls.mock_ppm_fhir_url = cls.ppm_fhir_url_patcher.start()
        cls.mock_ppm_fhir_url.return_value = cls.fhir_url

    @classmethod
    def tearDownClass(cls):

        # Disable patcher
        cls.ppm_fhir_url_patcher.stop()

    @responses.activate
    def test_patient_update_lastname(self):

        # Build a patient with a lastname
        patient = FHIRData.patient('patient@email.org', firstname='User', lastname='Patient')

        # Set an example form
        form = {'firstname': 'Newer', 'lastname': None}

        # Build the response handler
        responses.add(responses.GET,
                      re.compile(self.fhir_url + r'/Patient/.*'),
                      json=patient,
                      status=200)

        def update_callback(request):
            payload = json.loads(request.body)

            # Ensure last name was removed
            self.assertTrue(payload['name'][0].get('family', False))

            return 200, {}, json.dumps({'operation': 'Patient resource updated!'})

        responses.add_callback(
            responses.PUT,
            re.compile(self.fhir_url + r'/Patient/.*'),
            callback=update_callback,
            content_type='application/json'
        )

        # Do the update
        updated = FHIR.update_patient(patient['id'], form=form)

        # Check it
        self.assertGreaterEqual(len(responses.calls), 2)
        self.assertTrue(updated)

    @responses.activate
    def test_patient_update_add_address2(self):

        # Build a patient with a lastname
        patient = FHIRData.patient('patient@email.org', firstname='User', lastname='Patient')

        # Set an example form
        form = {'street_address1': '3100 Some Address', 'street_address2': 'Unit 401'}

        # Build the response handler
        responses.add(responses.GET,
                      re.compile(self.fhir_url + r'/Patient/.*'),
                      json=patient,
                      status=200)

        def update_callback(request):
            payload = json.loads(request.body)

            # Ensure last name was removed
            self.assertTrue(len(payload['address'][0]['line']) > 1)

            return 200, {}, json.dumps({'operation': 'Patient resource updated!'})

        responses.add_callback(
            responses.PUT,
            re.compile(self.fhir_url + r'/Patient/.*'),
            callback=update_callback,
            content_type='application/json'
        )

        # Do the update
        updated = FHIR.update_patient(patient['id'], form=form)

        # Check it
        self.assertGreaterEqual(len(responses.calls), 2)
        self.assertTrue(updated)

    @responses.activate
    def test_patient_update_remove_address2(self):

        # Build a patient with a lastname
        patient = FHIRData.patient('patient@email.org', firstname='User', lastname='Patient', street2='Unit 500')

        # Set an example form
        form = {'street_address1': '3100 Some Address', 'street_address2': None}

        # Build the response handler
        responses.add(responses.GET,
                      re.compile(self.fhir_url + r'/Patient/.*'),
                      json=patient,
                      status=200)

        def update_callback(request):
            payload = json.loads(request.body)

            # Ensure last name was removed
            self.assertTrue(len(payload['address'][0]['line']) == 1)

            return 200, {}, json.dumps({'operation': 'Patient resource updated!'})

        responses.add_callback(
            responses.PUT,
            re.compile(self.fhir_url + r'/Patient/.*'),
            callback=update_callback,
            content_type='application/json'
        )

        # Do the update
        updated = FHIR.update_patient(patient['id'], form=form)

        # Check it
        self.assertGreaterEqual(len(responses.calls), 2)
        self.assertTrue(updated)

    @responses.activate
    def test_patient_update_add_contact_email(self):

        # Build a patient with a lastname
        patient = FHIRData.patient('patient@email.org', firstname='User', lastname='Patient', street2='Unit 500')

        # Set an example form
        form = {'contact_email': 'user@email.org'}

        # Build the response handler
        responses.add(responses.GET,
                      re.compile(self.fhir_url + r'/Patient/.*'),
                      json=patient,
                      status=200)

        def update_callback(request):
            payload = json.loads(request.body)

            # Ensure last name was removed
            self.assertTrue(next((telecom for telecom in payload['telecom'] if telecom['system'] == 'email'), False))

            return 200, {}, json.dumps({'operation': 'Patient resource updated!'})

        responses.add_callback(
            responses.PUT,
            re.compile(self.fhir_url + r'/Patient/.*'),
            callback=update_callback,
            content_type='application/json'
        )

        # Do the update
        updated = FHIR.update_patient(patient['id'], form=form)

        # Check it
        self.assertGreaterEqual(len(responses.calls), 2)
        self.assertTrue(updated)

    @responses.activate
    def test_patient_update_remove_contact_email(self):

        # Build a patient with a lastname
        patient = FHIRData.patient('patient@email.org', firstname='User', lastname='Patient',
                                   street2='Unit 500', contact_email='user@email.org')

        # Set an example form
        form = {'contact_email': None}

        # Build the response handler
        responses.add(responses.GET,
                      re.compile(self.fhir_url + r'/Patient/.*'),
                      json=patient,
                      status=200)

        def update_callback(request):
            payload = json.loads(request.body)

            # Ensure last name was removed
            self.assertFalse(next((telecom for telecom in payload['telecom'] if telecom['system'] == 'email'), False))

            return 200, {}, json.dumps({'operation': 'Patient resource updated!'})

        responses.add_callback(
            responses.PUT,
            re.compile(self.fhir_url + r'/Patient/.*'),
            callback=update_callback,
            content_type='application/json'
        )

        # Do the update
        updated = FHIR.update_patient(patient['id'], form=form)

        # Check it
        self.assertGreaterEqual(len(responses.calls), 2)
        self.assertTrue(updated)

    @responses.activate
    def test_patient_update_requirements(self):

        # Build a patient with a lastname
        patient = FHIRData.patient('patient@email.org', firstname='User', lastname='Patient',
                                   street2='Unit 500', contact_email='user@email.org')

        # Set an example form
        form = {'firstname': None, 'email': None, 'city': None, 'phone': None}

        # Build the response handler
        responses.add(responses.GET,
                      re.compile(self.fhir_url + r'/Patient/.*'),
                      json=patient,
                      status=200)

        def update_callback(request):
            payload = json.loads(request.body)

            # Ensure properties still exist
            self.assertTrue(len(payload['name'][0]['given']) > 0)
            self.assertTrue(next((id['value'] for id in payload['identifier']
                                  if id['system'] == 'http://schema.org/email'), False))
            self.assertTrue(payload['address'][0].get('city', False))
            self.assertTrue(next((telecom['value'] for telecom in payload['telecom']
                                  if telecom['system'] == 'phone'), False))

            return 200, {}, json.dumps({'operation': 'Patient resource updated!'})

        responses.add_callback(
            responses.PUT,
            re.compile(self.fhir_url + r'/Patient/.*'),
            callback=update_callback,
            content_type='application/json'
        )

        # Do the update
        updated = FHIR.update_patient(patient['id'], form=form)

        # Check it
        self.assertGreaterEqual(len(responses.calls), 2)
        self.assertTrue(updated)


class FHIRData(object):

    @staticmethod
    def patient(email, firstname, lastname=None, street1="49 West New Drive", street2=None,
                city="Boston", state="MA", zip="02445", phone="+1 (353) 233-2708", contact_email="user@email.org",
                twitter=None, identifier=str(uuid.uuid4())):
        """
        Initializes and returns a test Patient resource using the passed parameters.
        Required items not passed are randomly generated, non-required items are left blank.
        :return: The Patient FHIR resource as a dict
        :rtype: dict
        """

        data = {
            "resourceType": "Patient",
            "id": f"{random.randint(1, 9999)}",
            "meta": {
                "versionId": "21",
                "lastUpdated": datetime.now().isoformat(),
            },
            "extension": [
                {
                    "url": "https://p2m2.dbmi.hms.harvard.edu/fhir/StructureDefinition/how-did-you-hear-about-us",
                    "valueString": "Qui aut vel nihil dolor tempor id eveniet consequatur quaerat nulla dignissimos quasi incididunt et"
                },
                {
                    "url": "https://p2m2.dbmi.hms.harvard.edu/fhir/StructureDefinition/uses-twitter",
                    "valueBoolean": twitter is not None
                }
            ],
            "identifier": [
                {
                    "system": "http://schema.org/email",
                    "value": email
                },
                {
                    "system": "https://peoplepoweredmedicine.org/fhir/patient",
                    "value": identifier
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "given": [
                        firstname
                    ]
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": phone
                },
                {
                    "system": "email",
                    "value": contact_email
                }
            ],
            "address": [
                {
                    "line": [
                        street1
                    ],
                    "city": city,
                    "state": state,
                    "postalCode": zip
                }
            ]
        }

        # Set last name
        if lastname:
            data['name'][0]['family'] = lastname

        # Set address
        if street2:
            data['address'][0]['line'].append(street2)

        # Add Twitter
        if twitter:
            data['telecom'].append({
                "system": "other",
                "value": twitter
            })

        return data
