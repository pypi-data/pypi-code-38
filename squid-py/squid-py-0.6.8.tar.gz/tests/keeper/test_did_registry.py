"""Test DIDRegistry contract."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import secrets

from squid_py.keeper.didregistry import DIDRegistry
from tests.resources.tiers import e2e_test

did_registry = DIDRegistry('DIDRegistry')


@e2e_test
def test_did_registry_contract():
    assert did_registry
    assert isinstance(did_registry, DIDRegistry)


@e2e_test
def test_did_registry_get_block_number_updated():
    test_id = secrets.token_hex(32)
    assert did_registry.get_block_number_updated(test_id) == 0
