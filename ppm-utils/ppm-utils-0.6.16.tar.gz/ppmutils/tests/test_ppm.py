import mock
import unittest
from furl import furl
from ppmutils.ppm import PPM

# Set test data
SERVICE_URL = 'https://some.test.api.address/'


class TestPPMService(unittest.TestCase):

    @mock.patch('ppmutils.ppm.PPM.Service.service_url')
    def test_url_build_1(self, mock_service_url):

        # Set the service URL to use
        mock_service_url.return_value = SERVICE_URL

        # Set an example path
        path = '/some/example/path'

        # Build a URL
        url = furl(PPM.Service._build_url(path=path))

        # Check it
        self.assertTrue('//' not in str(url.path))
        self.assertFalse(str(url.query))
        self.assertEqual('some.test.api.address', url.netloc)

    @mock.patch('ppmutils.ppm.PPM.Service.service_url')
    def test_url_build_2(self, mock_service_url):

        # Set the service URL to use
        mock_service_url.return_value = SERVICE_URL

        # Set an example path
        path = '/some/example/path?with=query&string=included'

        # Build a URL
        url = furl(PPM.Service._build_url(path=path))

        # Check it
        self.assertTrue('//' not in str(url.path))
        self.assertEqual(len(url.query.params.items()), 2)
        self.assertEqual('some.test.api.address', url.netloc)

    @mock.patch('ppmutils.ppm.PPM.Service.service_url')
    def test_url_build_3(self, mock_service_url):

        # Set the service URL to use
        mock_service_url.return_value = SERVICE_URL

        # Set an example path
        path = '/some//example//path'

        # Build a URL
        url = furl(PPM.Service._build_url(path=path))

        # Check it
        self.assertTrue('//' not in str(url.path))
        self.assertFalse(str(url.query))
        self.assertEqual('some.test.api.address', url.netloc)

    @mock.patch('ppmutils.ppm.PPM.Service.service_url')
    def test_url_build_4(self, mock_service_url):

        # Set the service URL to use
        mock_service_url.return_value = SERVICE_URL

        # Set an example path
        path = '/some//example//path?and=query&params=included+12'

        # Build a URL
        url = furl(PPM.Service._build_url(path=path))

        # Check it
        self.assertTrue('//' not in str(url.path))
        self.assertEqual(len(url.query.params.items()), 2)
        self.assertEqual('some.test.api.address', url.netloc)

    def test_ppm_study_meta_1(self):

        # Compare methods for determining study meta
        self.assertEqual(PPM.Study.title(PPM.Study.NEER), PPM.Study.title(PPM.Study.NEER.value))
        self.assertEqual(PPM.Study.title(PPM.Study.ASD), PPM.Study.title(PPM.Study.ASD.value))

        # Use FHIR codes
        self.assertEqual(PPM.Study.title(PPM.Study.ASD), PPM.Study.title(PPM.Study.fhir_id(PPM.Study.ASD)))
        self.assertEqual(PPM.Study.title(PPM.Study.ASD), PPM.Study.title(PPM.Study.fhir_id(PPM.Study.ASD.value)))

    def test_ppm_study_meta_2(self):

        # Compare methods for determining study meta
        self.assertTrue(PPM.Study.get(PPM.Study.NEER) is PPM.Study.NEER)
        self.assertTrue(PPM.Study.get(PPM.Study.NEER.value) is PPM.Study.NEER)
        self.assertTrue(PPM.Study.get(PPM.Study.ASD) is PPM.Study.ASD)
        self.assertTrue(PPM.Study.get(PPM.Study.ASD.value) is PPM.Study.ASD)

    def test_ppm_study_meta_3(self):

        # Compare methods for determining study meta
        self.assertTrue(PPM.Study.is_ppm(PPM.Study.fhir_id(PPM.Study.NEER)))
        self.assertTrue(PPM.Study.is_ppm(PPM.Study.fhir_id(PPM.Study.ASD)))
