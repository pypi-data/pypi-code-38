""" Fixtures files for type version manager
"""
from core_composer_app.components.type.models import Type
from core_composer_app.components.type_version_manager.models import TypeVersionManager
from core_main_app.utils.integration_tests.fixture_interface import FixtureInterface


class TypeVersionManagerFixtures(FixtureInterface):
    """ Type Version Manager fixtures
    """
    type_1_1 = None
    type_1_2 = None
    type_1_3 = None
    type_2_1 = None
    type_vm_1 = None
    type_vm_2 = None
    type_vm_collection = None

    def insert_data(self):
        """ Insert a set of Types and Type Version Managers.

        Returns:

        """
        # Make a connexion with a mock database
        self.type_1_1 = Type(filename="type1_1.xsd",
                             content="content1_1",
                             hash="hash1_1",
                             is_complex=True).save()
        self.type_1_2 = Type(filename="type1_2.xsd",
                             content="content1_2",
                             hash="hash1_2",
                             is_complex=True).save()
        self.type_1_3 = Type(filename="type1_3.xsd",
                             content="content1_3",
                             hash="hash1_3",
                             is_complex=True).save()
        self.type_2_1 = Type(filename="type2_1.xsd",
                             content="content2_1",
                             hash="hash2_1",
                             is_complex=True).save()

        self.type_vm_1 = TypeVersionManager(title="type 1",
                                            user=None,
                                            versions=[str(self.type_1_1.id),
                                                      str(self.type_1_2.id),
                                                      str(self.type_1_3.id)],
                                            current=str(self.type_1_3.id),
                                            is_disabled=False,
                                            disabled_versions=[str(self.type_1_2.id)]).save()

        self.type_vm_2 = TypeVersionManager(title="type 2",
                                            user="1",
                                            versions=[str(self.type_2_1.id)],
                                            current=str(self.type_2_1.id),
                                            is_disabled=False,
                                            disabled_versions=[]).save()

        self.type_vm_collection = [self.type_vm_1, self.type_vm_2]
