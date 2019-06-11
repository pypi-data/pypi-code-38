"""
    Test did_lib
"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json

from examples import ExampleConfig
from squid_py.ddo.ddo import DDO
from squid_py.ddo.public_key_base import (
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_PEM
)
from squid_py.did import DID
from squid_py.keeper.keeper import Keeper
from tests.resources.helper_functions import get_publisher_account, get_resource_path
from tests.resources.tiers import unit_test

public_key_store_types = [
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
]

TEST_SERVICE_TYPE = 'ocean-meta-storage'
TEST_SERVICE_URL = 'http://localhost:8005'

TEST_METADATA = """
{
   "base": {
     "name": "UK Weather information 2011",
     "type": "dataset",
     "description": "Weather information of UK including temperature and humidity",
     "size": "3.1gb",
     "dateCreated": "2012-10-10T17:00:000Z",
     "author": "Met Office",
     "license": "CC-BY",
     "copyrightHolder": "Met Office",
     "encoding": "UTF-8",
     "compression": "zip",
     "contentType": "text/csv",
     "workExample": "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
     "files": [
       {
         "url": "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf",
         "checksum": "efb2c764274b745f5fc37f97c6b0e761",
         "contentLength": "4535431",
         "resourceId": "access-log2018-02-13-15-17-29-18386C502CAEA932"
       }
     ],
     "links": [
       { "name": "Sample of Asset Data", "type": "sample", "url": "https://foo.com/sample.csv" },
       { "name": "Data Format Definition", "type": "format", "AssetID": 
       "4d517500da0acb0d65a716f61330969334630363ce4a6a9d39691026ac7908ea" }
     ],
     "inLanguage": "en",
     "tags": ["weather", "uk", "2011", "temperature", "humidity"],
     "price": 10
   },
   "curation": {
     "rating": 0.93,
     "numVotes": 123,
     "schema": "Binary Voting"
   },
   "additionalInformation": {
     "updateFrequency": "yearly",
     "structuredMarkup": [
       {
         "uri": "http://skos.um.es/unescothes/C01194/jsonld",
         "mediaType": "application/ld+json"
       },
       {
         "uri": "http://skos.um.es/unescothes/C01194/turtle",
         "mediaType": "text/turtle"
       }
     ]
   }
}
"""

TEST_SERVICES = [
    {"type": "OpenIdConnectVersion1.0Service",
     "serviceEndpoint": "https://openid.example.com/"
     },
    {
        "type": "CredentialRepositoryService",
        "serviceEndpoint": "https://repository.example.com/service/8377464"
    },
    {
        "type": "XdiService",
        "serviceEndpoint": "https://xdi.example.com/8377464"
    },
    {
        "type": "HubService",
        "serviceEndpoint": "https://hub.example.com/.identity/did:op:0123456789abcdef/"
    },
    {
        "type": "MessagingService",
        "serviceEndpoint": "https://example.com/messages/8377464"
    },
    {
        "type": "SocialWebInboxService",
        "serviceEndpoint": "https://social.example.com/83hfh37dj",
        "values": {
            "description": "My public social inbox",
            "spamCost": {
                "amount": "0.50",
                "currency": "USD"
            }
        }
    },
    {
        "type": "BopsService",
        "serviceEndpoint": "https://bops.example.com/enterprise/"
    },
    {
        "type": "Consume",
        "serviceEndpoint": "http://mybrizo.org/api/v1/brizo/services/consume?pubKey=${"
                           "pubKey}&agreementId={agreementId}&url={url}"
    },
    {
        "type": "Compute",
        "serviceDefinitionId": "1",
        "serviceEndpoint": "http://mybrizo.org/api/v1/brizo/services/compute?pubKey=${"
                           "pubKey}&agreementId={agreementId}&algo={algo}&container={container}"
    },
    {
        "type": "Access",
        "purchaseEndpoint": "service",
        "serviceEndpoint": "consume",
        "serviceDefinitionId": "0",
        "templateId": "0x00000",
    }
]


def generate_sample_ddo():
    did = DID.did()
    assert did
    ddo = DDO(did)
    assert ddo
    config = ExampleConfig.get_config()
    pub_acc = get_publisher_account(config)

    # add a proof signed with the private key
    ddo.add_proof('checksum', pub_acc, Keeper.get_instance())

    metadata = json.loads(TEST_METADATA)
    ddo.add_service("Metadata", "http://myaquarius.org/api/v1/provider/assets/metadata/{did}",
                    values={'metadata': metadata})
    for test_service in TEST_SERVICES:
        if 'values' in test_service:
            values = test_service['values']
        else:
            values = test_service.copy()
            values.pop('type')
            values.pop('serviceEndpoint')

        ddo.add_service(test_service['type'], test_service['serviceEndpoint'], values=values)

    return ddo


@unit_test
def test_creating_ddo():
    did = DID.did()
    assert did
    ddo = DDO(did)
    assert ddo
    config = ExampleConfig.get_config()
    pub_acc = get_publisher_account(config)

    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)

    assert len(ddo.services) == 1

    ddo_text_no_proof = ddo.as_text()
    assert ddo_text_no_proof

    ddo_text_proof = ''
    ddo.add_proof('checksum', pub_acc, Keeper.get_instance())
    ddo_text_proof = ddo.as_text()

    ddo = DDO(json_text=ddo_text_proof)
    assert ddo.is_proof_defined()

    ddo = DDO(json_text=ddo_text_no_proof)
    assert not ddo.is_proof_defined()


@unit_test
def test_creating_did_using_ddo():
    # create an empty ddo
    ddo = DDO()
    assert ddo
    config = ExampleConfig.get_config()
    pub_acc = get_publisher_account(config)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)
    # add a proof to the first public_key/authentication
    ddo.add_proof('checksum', pub_acc, Keeper.get_instance())
    ddo_text_proof = ddo.as_text()
    assert ddo_text_proof


@unit_test
def test_load_ddo_json():
    # TODO: Fix
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), f'{sample_ddo_path} does not exist!'
    with open(sample_ddo_path) as f:
        sample_ddo_json_dict = json.load(f)

    sample_ddo_json_string = json.dumps(sample_ddo_json_dict)

    this_ddo = DDO(json_text=sample_ddo_json_string)
    service = this_ddo.get_service('Metadata')
    assert service
    assert service.type == 'Metadata'
    assert service.values['metadata']


@unit_test
def test_ddo_dict():
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), f'{sample_ddo_path} does not exist!'

    ddo1 = DDO(json_filename=sample_ddo_path)
    assert len(ddo1.public_keys) == 1
    assert ddo1.did == 'did:op:0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e429'


@unit_test
def test_generate_test_ddo_files(registered_ddo):
    for index in range(1, 3):
        ddo = registered_ddo

        json_output_filename = get_resource_path('ddo',
                                                 f'ddo_sample_generated_{index}.json')
        with open(json_output_filename, 'w') as fp:
            fp.write(ddo.as_text(is_pretty=True))


@unit_test
def test_find_service():
    ddo = generate_sample_ddo()
    service = ddo.find_service_by_id(0)
    assert service and service.type == 'Access', 'Failed to find service by integer id.'
    service = ddo.find_service_by_id('0')
    assert service and service.type == 'Access', 'Failed to find service by str(int) id.'

    service = ddo.find_service_by_id(1)
    assert service and service.type == 'Compute', 'Failed to find service by integer id.'
    service = ddo.find_service_by_id('1')
    assert service and service.type == 'Compute', 'Failed to find service by str(int) id.'

    service = ddo.find_service_by_id('Access')
    assert service and service.type == 'Access', 'Failed to find service by id using service type.'
    assert service.service_definition_id == '0', 'serviceDefinitionId not as expected.'

    service = ddo.find_service_by_id('Compute')
    assert service and service.type == 'Compute', 'Failed to find service by id using service type.'
    assert service.service_definition_id == '1', 'serviceDefinitionId not as expected.'
