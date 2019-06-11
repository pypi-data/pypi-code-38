"""
    Test Keeper class.

    This tests basic contract loading and one call to the smart contract to prove
    that the contact can be loaded and used

"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.keeper import Keeper
from tests.resources.tiers import e2e_test


@e2e_test
def test_keeper_instance():
    keeper = Keeper()
    assert keeper
    assert isinstance(keeper.get_instance(), Keeper)


@e2e_test
def test_keeper_networks():
    keeper = Keeper()
    assert isinstance(keeper.get_network_id(), int)
    assert keeper.get_network_name(1) == Keeper._network_name_map.get(1)
    assert keeper.get_network_name(2) == Keeper._network_name_map.get(2)
    assert keeper.get_network_name(3) == Keeper._network_name_map.get(3)
    assert keeper.get_network_name(4) == Keeper._network_name_map.get(4)
    assert keeper.get_network_name(42) == Keeper._network_name_map.get(42)
    assert keeper.get_network_name(77) == Keeper._network_name_map.get(77)
    assert keeper.get_network_name(99) == Keeper._network_name_map.get(99)
    assert keeper.get_network_name(8995) == Keeper._network_name_map.get(8995)
    assert keeper.get_network_name(8996) == Keeper._network_name_map.get(8996)
    assert keeper.get_network_name(0) == 'development'


def test_ec_recover():
    test_values = [
        ('0xe2DD09d719Da89e5a3D0F2549c7E24566e947260',
         'c80996119e884cb38599bcd96a22ad3eea3a4734bcfb47959a5d41ecdcbdfe67',
         '0xa50427a9d5beccdea3eeabecfc1014096b35cd05965e772e8ea32477d2f217'
         'c30d0ec5dbf6b14de1d6eeff45011d17490fe5126576b20d2cbada828cb068c9f801'),
        ('0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e',
         'd77c3a84cafe4cb8bc28bf41a99c63fd530c10da33a54acf94e8d1369d09fbb2',
         '0x9076b561e554cf657af333d9680ba118d556c5b697622636bce4b02f4d5632'
         '5a0ea6a474ca85291252c8c1b8637174ee32072bef357bb0c21b0db4c25b379e781b'),
        ('0xe2DD09d719Da89e5a3D0F2549c7E24566e947260',
         '8d5c1065a9c74da59fbb9e41d1f196e40517e92d81b14c3a8143d6887f3f4438',
         '0x662f6cffd96ada4b6ce5497d444c92126bd053ab131915332edf0dbba716ba'
         '82662275670c95eb2a4d65245cac70313c25e34f594d7c0fbca5232c3d5701a57e00')
    ]

    for expected_address, document_id, signed_document_id in test_values:
        rec_address = Keeper.get_instance().ec_recover(document_id, signed_document_id)
        print(f'recovered address: {rec_address}, original address {expected_address}')
        assert expected_address.lower() == rec_address.lower()
