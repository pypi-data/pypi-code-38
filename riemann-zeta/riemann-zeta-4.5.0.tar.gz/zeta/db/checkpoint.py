# flake8: noqa
import os

from zeta.db import connection
from zeta.zeta_types import Header

from typing import Dict, List

network: str = os.environ.get('ZETA_NETWORK', 'bitcoin_main')

CHECKPOINTS: Dict[str, List[Header]] = {
    'bitcoin_main': [
            {
                'hash': '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f',
                'version': 1,
                'prev_block': '0000000000000000000000000000000000000000000000000000000000000000',
                'merkle_root': '3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a',
                'timestamp': 1231006505,
                'nbits': 'ffff001d',
                'nonce': '1dac2b7c',
                'difficulty': 1,
                'hex': '0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c',
                'height': 0,
                'accumulated_work': 0
            },
            {
                'hash': '00000000000000000029f5e855578d7a81f4501f38093c46cb88a47664bf3c0e',
                'version': 549453824,
                'prev_block': '0000000000000000001e6525727cc0a729b1e928dff16db10d789176b59dd3eb',
                'merkle_root': '19a0368be5061871be3929e11b0e13de2c5f34e45310ca2798ebe14783413252',
                'timestamp': 1544230162,
                'nbits': '7cd93117',
                'nonce': '5507350b',
                'difficulty': 5646403851534,
                'hex': '0000c020ebd39db57691780db16df1df28e9b129a7c07c7225651e00000000000000000019a0368be5061871be3929e11b0e13de2c5f34e45310ca2798ebe1478341325212150b5c7cd931175507350b',
                'height': 552955,
                'accumulated_work': 0
            },
            {
                'hash': '000000000000000002cce816c0ab2c5c269cb081896b7dcb34b8422d6b74ffa1',
                'version': 536870912,
                'prev_block': '000000000000000003035bc31911d3eea46c8a23b36d6d558141d1d09cc960cf',
                'merkle_root': 'fa0f9ea6c329b99b6d17576b73bc781267e566430aee747205b0acbca5238302',
                'timestamp': 1468082773,
                'nbits': 'fd260518',
                'nonce': 'b432bd82',
                'difficulty': 213398925331,
                'hex': '00000020cf60c99cd0d14181556d6db3238a6ca4eed31119c35b03030000000000000000fa0f9ea6c329b99b6d17576b73bc781267e566430aee747205b0acbca5238302552a8157fd260518b432bd82',
                'height': 420000,
                'accumulated_work': 0
            }],
    'bitcoin_test': [
        {
            'hash': '000000000000fce208da3e3b8afcc369835926caa44044e9c2f0caa48c8eba0f',
            'version': 536870912,
            'prev_block': '00000000000317883bdb2a052dc8370a43355aef82aec7ac88ec2bb300bb5896',
            'merkle_root': '32dfad3bd94b176f500f15bdf242b5a524d5faeb12b3431bbc0cd3980eb8975e',
            'timestamp': 1534969326,
            'nbits': '9c61031b',
            'nonce': '675abfd0',
            'difficulty': 19381,
            'hex': '000000209658bb00b32bec88acc7ae82ef5a35430a37c82d052adb3b881703000000000032dfad3bd94b176f500f15bdf242b5a524d5faeb12b3431bbc0cd3980eb8975eeec57d5b9c61031b675abfd0',
            'height': 1400000,
            'accumulated_work': 0
        }]
}
