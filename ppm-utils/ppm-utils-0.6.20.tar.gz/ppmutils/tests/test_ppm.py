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

    def test_ppm_study_meta_4(self):

        # Compare methods for determining study meta
        ppm_enum = PPM.Study
        for enum in ppm_enum:
            # Compare getters on name
            self.assertEqual(ppm_enum.enum(enum.name), enum)
            # Compare getters on value
            self.assertEqual(ppm_enum.enum(enum.value), enum)
            # Compare getters on title
            self.assertEqual(ppm_enum.enum(ppm_enum.title(enum)), enum)
            # Compare getters on identifier
            self.assertEqual(ppm_enum.enum(ppm_enum.fhir_id(enum)), enum)

        # Check edge cases
        self.assertEqual(ppm_enum.enum('ppm-asd'), PPM.Study.ASD)
        self.assertEqual(ppm_enum.enum('asd'), PPM.Study.ASD)

    def test_ppm_enrollment_meta_1(self):

        # Compare methods for determining study meta
        ppm_enum = PPM.Enrollment
        for enum in ppm_enum:
            # Compare getters on name
            self.assertEqual(ppm_enum.enum(enum.name), enum)
            # Compare getters on value
            self.assertEqual(ppm_enum.enum(enum.value), enum)
            # Compare getters on title
            self.assertEqual(ppm_enum.enum(ppm_enum.title(enum)), enum)

    def test_ppm_communication_meta_1(self):

        # Compare methods for determining study meta
        ppm_enum = PPM.Communication
        for enum in ppm_enum:
            # Compare getters on name
            self.assertEqual(ppm_enum.enum(enum.name), enum)
            # Compare getters on value
            self.assertEqual(ppm_enum.enum(enum.value), enum)
            # Compare getters on title
            self.assertEqual(ppm_enum.enum(ppm_enum.title(enum)), enum)

    def test_ppm_provider_meta_1(self):

        # Compare methods for determining study meta
        ppm_enum = PPM.Provider
        for enum in ppm_enum:
            # Compare getters on name
            self.assertEqual(ppm_enum.enum(enum.name), enum)
            # Compare getters on value
            self.assertEqual(ppm_enum.enum(enum.value), enum)
            # Compare getters on title
            self.assertEqual(ppm_enum.enum(ppm_enum.title(enum)), enum)

    def test_ppm_tracked_item_meta_1(self):

        # Compare methods for determining study meta
        ppm_enum = PPM.TrackedItem
        for enum in ppm_enum:
            # Compare getters on name
            self.assertEqual(ppm_enum.enum(enum.name), enum)
            # Compare getters on value
            self.assertEqual(ppm_enum.enum(enum.value), enum)
            # Compare getters on title
            self.assertEqual(ppm_enum.enum(ppm_enum.title(enum)), enum)
