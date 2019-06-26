import json

import pytest
import requests

from ocdsextensionregistry import Extension, ExtensionVersion


def test_init():
    args = arguments()
    obj = ExtensionVersion(args)

    assert obj.id == args['Id']
    assert obj.date == args['Date']
    assert obj.version == args['Version']
    assert obj.base_url == args['Base URL']
    assert obj.download_url == args['Download URL']


def test_update():
    obj = ExtensionVersion(arguments())
    obj.update(Extension({'Id': 'location', 'Category': 'item', 'Core': 'true'}))

    assert obj.id == 'location'
    assert obj.category == 'item'
    assert obj.core is True


def test_update_ignore_private_properties():
    obj = ExtensionVersion(arguments())
    other = ExtensionVersion(arguments())
    other._files = {'key': 'value'}
    obj.update(other)

    assert obj._files is None


def test_as_dict():
    args = arguments()
    obj = ExtensionVersion(args)

    assert obj.as_dict() == {
        'id': args['Id'],
        'date': args['Date'],
        'version': args['Version'],
        'base_url': args['Base URL'],
        'download_url': args['Download URL'],
    }


def test_remote():
    obj = ExtensionVersion(arguments(**{'Download URL': None}))
    data = obj.remote('extension.json')
    # Repeat requests should return the same result.
    data = obj.remote('extension.json')

    assert json.loads(data)


def test_remote_download_url():
    obj = ExtensionVersion(arguments())
    data = obj.remote('extension.json')
    # Repeat requests should return the same result.
    data = obj.remote('extension.json')

    assert json.loads(data)


def test_remote_nonexistent():
    obj = ExtensionVersion(arguments(**{'Download URL': None}))
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        obj.remote('nonexistent')

    assert str(excinfo.value) == "404 Client Error: Not Found for url: https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.3/nonexistent"  # noqa


def test_remote_download_url_nonexistent():
    obj = ExtensionVersion(arguments())
    with pytest.raises(KeyError) as excinfo:
        obj.remote('nonexistent')

    assert str(excinfo.value) == "'nonexistent'"


def test_files():
    obj = ExtensionVersion(arguments())
    data = obj.files

    assert 'LICENSE' in data

    # This method should not parse file contents.
    for value in data.values():
        assert isinstance(value, (bytes, str))


def test_files_without_download_url():
    obj = ExtensionVersion(arguments(**{'Download URL': None}))
    data = obj.files

    assert data == {}


def test_metadata():
    obj = ExtensionVersion(arguments())
    result = obj.metadata

    assert result['codelists'] == ['locationGazetteers.csv', 'geometryType.csv']


def test_metadata_old_format():
    # See https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1/extension.json
    download_url = 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1'
    obj = ExtensionVersion(arguments(**{'Download URL': download_url}))
    result = obj.metadata

    assert result['name']['en'] == 'Location'
    assert result['description']['en'] == 'Communicates the location of proposed or executed contract delivery.'
    assert result['documentationUrl'] == {}
    assert result['compatibility'] == ['1.1']


def test_schemas():
    download_url = 'https://github.com/open-contracting-extensions/ocds_location_extension/archive/master.zip'
    obj = ExtensionVersion(arguments(**{'Download URL': download_url}))
    result = obj.schemas

    assert len(result) == 1
    assert 'Location' in result['release-schema.json']['definitions']


def test_schemas_without_metadata():
    download_url = 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1'
    obj = ExtensionVersion(arguments(**{'Download URL': download_url}))
    result = obj.schemas

    assert len(result) == 3
    assert result['record-package-schema.json'] == {}
    assert result['release-package-schema.json'] == {}
    assert 'Location' in result['release-schema.json']['definitions']


def test_schemas_without_metadata_or_download_url():
    base_url = 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1/'
    download_url = None
    obj = ExtensionVersion(arguments(**{'Base URL': base_url, 'Download URL': download_url}))
    result = obj.schemas

    assert len(result) == 3
    assert result['record-package-schema.json'] == {}
    assert result['release-package-schema.json'] == {}
    assert 'Location' in result['release-schema.json']['definitions']


def test_codelists():
    obj = ExtensionVersion(arguments())
    result = obj.codelists

    assert len(result) == 2
    assert result['locationGazetteers.csv'].fieldnames == ['Category', 'Code', 'Title', 'Description', 'Source', 'URI Pattern']  # noqa


def test_codelists_without_metadata():
    download_url = 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1'
    obj = ExtensionVersion(arguments(**{'Download URL': download_url}))
    result = obj.codelists

    assert len(result) == 1
    assert result['locationGazeteers.csv'].fieldnames == ['Category', 'Code', 'Title', 'Description', 'Source', 'URI_Pattern']  # noqa


def test_codelists_without_metadata_or_download_url():
    base_url = 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1/'
    download_url = None
    obj = ExtensionVersion(arguments(**{'Base URL': base_url, 'Download URL': download_url}))
    result = obj.codelists

    assert result == {}


def test_codelists_with_CR_newlines():
    download_url = 'https://api.github.com/repos/open-contracting-extensions/ocds_bid_extension/zipball/v1.1'
    obj = ExtensionVersion(arguments(**{'Download URL': download_url}))
    result = obj.codelists

    assert len(result) == 2
    assert result['bidStatistics.csv'].fieldnames == ['Category', 'Code', 'Title', 'Description', 'Min', 'Max', 'Required by']  # noqa


def test_repository_full_name():
    obj = ExtensionVersion(arguments())
    result = obj.repository_full_name

    assert result == 'open-contracting-extensions/ocds_location_extension'


def test_repository_name():
    obj = ExtensionVersion(arguments())
    result = obj.repository_name

    assert result == 'ocds_location_extension'


def test_repository_user():
    obj = ExtensionVersion(arguments())
    result = obj.repository_user

    assert result == 'open-contracting-extensions'


def test_repository_user_page():
    obj = ExtensionVersion(arguments())
    result = obj.repository_user_page

    assert result == 'https://github.com/open-contracting-extensions'


def test_repository_html_page():
    obj = ExtensionVersion(arguments())
    result = obj.repository_html_page

    assert result == 'https://github.com/open-contracting-extensions/ocds_location_extension'


def test_repository_url():
    obj = ExtensionVersion(arguments())
    result = obj.repository_url

    assert result == 'git@github.com:open-contracting-extensions/ocds_location_extension.git'


def arguments(**kwargs):
    data = {
        'Id': 'location',
        'Date': '2018-02-01',
        'Version': 'v1.1.3',
        'Base URL': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.3/',
        'Download URL': 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.3',  # noqa
    }

    data.update(kwargs)
    return data
