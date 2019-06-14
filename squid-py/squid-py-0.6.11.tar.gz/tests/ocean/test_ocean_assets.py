#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0


def test_ocean_assets_resolve(publisher_ocean_instance, metadata):
    publisher = publisher_ocean_instance.main_account
    ddo = publisher_ocean_instance.assets.create(metadata, publisher)
    ddo_resolved = publisher_ocean_instance.assets.resolve(ddo.did)
    assert ddo.did == ddo_resolved.did


def test_ocean_assets_search(publisher_ocean_instance, metadata):
    publisher = publisher_ocean_instance.main_account
    publisher_ocean_instance.assets.create(metadata, publisher)
    assert len(publisher_ocean_instance.assets.search('Monkey')) > 0


def test_ocean_assets_validate(publisher_ocean_instance, metadata):
    assert publisher_ocean_instance.assets.validate(metadata)
