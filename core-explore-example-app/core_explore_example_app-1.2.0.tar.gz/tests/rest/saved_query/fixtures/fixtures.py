""" Fixture files for SavedQuery
"""
from core_explore_example_app.components.saved_query.models import SavedQuery
from core_main_app.utils.integration_tests.fixture_interface import FixtureInterface
from core_main_app.components.template.models import Template


class SavedQueryFixtures(FixtureInterface):
    """ Saved Query fixtures
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
        template = Template(filename="filename",
                            content="<xml />",
                            hash="hash").save()
        query_data_1 = "{\"$or\": [{\"list_content\": {\"$elemMatch\": {\"path\": \"/.*chemical-element-type/\", \"" \
                       "value\": \"Ac\"}}}, {\"list_content\": {\"$elemMatch\": " \
                       "{\"path\": \"/.*chemical-element-type.#text/\", \"value\": \"Ac\"}}}]}"
        self.data_1 = SavedQuery(user_id="1",
                                 template=template.id,
                                 query=query_data_1,
                                 displayed_query="Element is Ac").save()
        self.data_collection = [self.data_1]
