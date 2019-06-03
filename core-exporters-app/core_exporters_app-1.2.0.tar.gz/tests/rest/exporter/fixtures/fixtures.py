""" Fixture files for Exporters
"""
from core_exporters_app.components.exporter.models import Exporter
from core_main_app.utils.integration_tests.fixture_interface import FixtureInterface
import core_exporters_app.commons.constants as constants


class ExporterFixtures(FixtureInterface):
    """ Exporter fixtures
    """
    data_1 = None
    data_collection = None

    def insert_data(self):
        """ Insert a set of Data.

        Returns:

        """
        # Make a connexion with a mock database
        self.generate_data_collection()

    def generate_data_collection(self):
        """ Generate a Data collection.

        Returns:

        """
        self.data_1 = Exporter(name="name_1",
                               url=constants.XSL_URL,
                               enable_by_default=False,
                               templates=[]).save()
        self.data_collection = [self.data_1]
