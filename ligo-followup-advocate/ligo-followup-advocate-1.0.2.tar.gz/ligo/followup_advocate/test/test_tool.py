import json
import os

# import astropy.utils.data
import pkg_resources
import pytest

from ..tool import main


class MockGraceDb(object):

    def __init__(self, service):
        assert service == 'https://gracedb.invalid/api/'
        self.service_url = service

    def _open(self, graceid, filename):
        if filename.endswith('.fits.gz'):
            # url = ('https://dcc.ligo.org/public/0145/T1700453/001/'
            #        'LALInference_v1.fits.gz')
            # filename = astropy.utils.data.download_file(url, cache=True)
            filename = os.path.join('data', graceid, filename)
            return open(pkg_resources.resource_filename(__name__,
                                                        filename), 'rb')
        else:
            filename = os.path.join('data', graceid, filename)
            if 'bayestar-gbm' in filename:
                filename += '.gz'
                return open(pkg_resources.resource_filename(
                    __name__, filename), 'rb')

            elif filename.endswith('.fits'):
                return open(pkg_resources.resource_filename(
                    __name__, filename), 'rb')

            else:
                f = open(pkg_resources.resource_filename(__name__, filename))

                def get_json():
                    return json.load(f)

                f.json = get_json
                return f

    def superevent(self, graceid):
        return self._open(graceid, 'superevent.json')

    def event(self, graceid):
        return self._open(graceid, 'event.json')

    def logs(self, graceid):
        return self._open(graceid, 'logs.json')

    def voevents(self, graceid):
        return self._open(graceid, 'voevents.json')

    def files(self, graceid, filename=None, raw=True):
        if filename is None:
            return self._open(graceid, 'files.json')
        else:
            return self._open(graceid, os.path.join('files', filename))


@pytest.fixture
def mock_gracedb(monkeypatch):
    return monkeypatch.setattr('ligo.gracedb.rest.GraceDb', MockGraceDb)


@pytest.fixture
def mock_webbrowser_open(mocker):
    return mocker.patch('webbrowser.open')


def test_cbc_compose(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/', 'compose', 'S1234'])


def test_burst_compose(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/', 'compose', 'S2468'])


def test_compose_mailto(mock_gracedb, mock_webbrowser_open):
    main(['--service', 'https://gracedb.invalid/api/', 'compose',
          '--mailto', 'S1234'])
    assert mock_webbrowser_open.called_once()


def test_RAVEN_with_initial_circular(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/', 'compose_RAVEN',
          'S1234'])


def test_RAVEN_without_initial_circular(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/', 'compose_RAVEN',
          'S5678'])


def test_medium_latency_cbc_detection(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/',
          'compose_grb_medium_latency', 'E1234'])


def test_medium_latency_cbc_burst_detection(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/',
          'compose_grb_medium_latency', 'E1122'])


def test_medium_latency_cbc_exclusion(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/',
          'compose_grb_medium_latency', 'E1133'])


def test_medium_latency_cbc_burst_exclusion(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/',
          'compose_grb_medium_latency', 'E2244'])


def test_retraction(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/', 'compose_retraction',
          'S1234'])
