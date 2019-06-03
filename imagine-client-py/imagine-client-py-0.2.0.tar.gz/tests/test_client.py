import pytest

from imagine_client_py import ImagineClient, ImageBasedModel


@pytest.fixture
def imagine_client():
    return ImagineClient({
            'api_key': 'test',
            'client_id': 'test'
        })


def test_imagine_client_should_throw_error_if_missing_api_key_or_client_id():
    with pytest.raises(Exception):
        _ = ImagineClient({})


def test_imagine_client_should_get_supported_image_model(imagine_client):
    ImageBasedModel.create(imagine_client, 'phenomenal-face')


def test_imagine_client_should_throw_an_error_for_invalid_image_model(imagine_client):
    with pytest.raises(Exception):
        ImageBasedModel.create(imagine_client, 'non-supported-model')
