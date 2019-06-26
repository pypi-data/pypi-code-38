import pytest

from ocdsextensionregistry import ExtensionRegistry
from ocdsextensionregistry.exceptions import DoesNotExist, MissingExtensionMetadata

extensions_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/master/extensions.csv'
extension_versions_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/master/extension_versions.csv'  # noqa

extensions_data = """Id,Category,Core
charges,ppp,
enquiries,tender,true
location,item,true
lots,tender,true
"""

extension_versions_data = """Id,Date,Version,Base URL,Download URL
charges,,master,https://raw.githubusercontent.com/open-contracting-extensions/ocds_charges_extension/master/,https://github.com/open-contracting-extensions/ocds_charges_extension/archive/master.zip
charges,2017-05-09,v1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_charges_extension/v1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_charges_extension/zipball/v1.1
enquiries,,master,https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/master/,https://github.com/open-contracting-extensions/ocds_enquiry_extension/archive/master.zip
enquiries,2017-05-09,v1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/v1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_enquiry_extension/zipball/v1.1
enquiries,2017-08-07,v1.1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/v1.1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_enquiry_extension/zipball/v1.1.1
enquiries,2018-02-01,v1.1.3,https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/v1.1.3/,https://api.github.com/repos/open-contracting-extensions/ocds_enquiry_extension/zipball/v1.1.3
location,,master,https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/master/,https://github.com/open-contracting-extensions/ocds_location_extension/archive/master.zip
location,2017-05-09,v1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1
location,2017-08-07,v1.1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.1
location,2018-02-01,v1.1.3,https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.3/,https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.3
lots,,master,https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/master/,https://github.com/open-contracting-extensions/ocds_lots_extension/archive/master.zip
lots,2017-05-09,v1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1
lots,2017-08-07,v1.1.1,https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1.1/,https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1.1
lots,2018-01-30,v1.1.3,https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1.3/,https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1.3
"""


def test_init_with_url():
    obj = ExtensionRegistry(extension_versions_url, extensions_url)

    assert len(obj.versions) > 50
    # Skip testing data, as the data changes over time.


def test_init_with_data():
    obj = ExtensionRegistry(extension_versions_data, extensions_data)

    assert len(obj.versions) == 14
    assert obj.versions[0].as_dict() == {
        'id': 'charges',
        'date': '',
        'version': 'master',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_charges_extension/master/',
        'download_url': 'https://github.com/open-contracting-extensions/ocds_charges_extension/archive/master.zip',
        'category': 'ppp',
        'core': False,
    }
    # Assume intermediate data is correctly parsed.
    assert obj.versions[-1].as_dict() == {
        'id': 'lots',
        'date': '2018-01-30',
        'version': 'v1.1.3',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1.3/',
        'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1.3',
        'category': 'tender',
        'core': True,
    }


def test_init_with_versions_only():
    obj = ExtensionRegistry(extension_versions_data)

    assert len(obj.versions) == 14
    assert obj.versions[0].as_dict() == {
        'id': 'charges',
        'date': '',
        'version': 'master',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_charges_extension/master/',
        'download_url': 'https://github.com/open-contracting-extensions/ocds_charges_extension/archive/master.zip',
    }
    # Assume intermediate data is correctly parsed.
    assert obj.versions[-1].as_dict() == {
        'id': 'lots',
        'date': '2018-01-30',
        'version': 'v1.1.3',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1.3/',
        'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1.3',
    }


def test_filter():
    obj = ExtensionRegistry(extension_versions_data, extensions_data)
    result = obj.filter(core=True, version='v1.1.3', category='tender')

    assert len(result) == 2
    assert result[0].as_dict() == {
        'id': 'enquiries',
        'date': '2018-02-01',
        'version': 'v1.1.3',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/v1.1.3/',
        'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_enquiry_extension/zipball/v1.1.3',  # noqa
        'category': 'tender',
        'core': True,
    }
    assert result[1].as_dict() == {
        'id': 'lots',
        'date': '2018-01-30',
        'version': 'v1.1.3',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1.3/',
        'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1.3',
        'category': 'tender',
        'core': True,
    }


def test_filter_without_extensions():
    obj = ExtensionRegistry(extension_versions_data)
    with pytest.raises(MissingExtensionMetadata) as excinfo:
        obj.filter(category='tender')

    assert str(excinfo.value) == 'ExtensionRegistry must be initialized with extensions data.'


def test_get():
    obj = ExtensionRegistry(extension_versions_data)
    result = obj.get(id='lots', version='v1.1.3')

    assert result.as_dict() == {
        'id': 'lots',
        'date': '2018-01-30',
        'version': 'v1.1.3',
        'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_lots_extension/v1.1.3/',
        'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_lots_extension/zipball/v1.1.3',
    }


def test_get_no_match():
    obj = ExtensionRegistry(extension_versions_data)
    with pytest.raises(DoesNotExist) as excinfo:
        obj.get(id='nonexistent')

    assert str(excinfo.value) == "Extension version matching {'id': 'nonexistent'} does not exist."


def test_get_without_extensions():
    obj = ExtensionRegistry(extension_versions_data)
    with pytest.raises(MissingExtensionMetadata) as excinfo:
        obj.get(category='tender')

    assert str(excinfo.value) == 'ExtensionRegistry must be initialized with extensions data.'


def test_iter():
    obj = ExtensionRegistry(extension_versions_data)
    for i, version in enumerate(obj, 1):
        pass

    assert i == 14
