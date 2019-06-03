""" fixtures files for Server
"""
import json
import os

from core_main_app.components.data.models import Data
from core_main_app.components.template.models import Template
from core_main_app.components.template_version_manager import api as template_version_manager_api
from core_main_app.components.template_version_manager.models import TemplateVersionManager
from core_main_app.components.workspace import api as workspace_api
from core_main_app.components.workspace.models import Workspace
from core_main_app.utils.integration_tests.fixture_interface import FixtureInterface
from django.test.utils import override_settings

from core_oaipmh_provider_app.components.oai_data.models import OaiData
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import OaiProviderMetadataFormat
from core_oaipmh_provider_app.components.oai_provider_set.models import OaiProviderSet
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_oaipmh_provider_app.settings import OAI_SCHEME, OAI_REPO_IDENTIFIER
from tests.test_settings import OAI_PROVIDER_ROOT

DUMP_OAI_PMH_TEST_PATH = os.path.join(OAI_PROVIDER_ROOT, 'utils', 'tests', 'data')


class OaiPmhFixtures(FixtureInterface):
    """
        Represent OaiPmh Integration Fixture
    """

    url = "http://www.server.com"
    harvest_rate = 5000
    harvest = True
    registry = None
    oai_identify = None
    settings = None
    templates = []
    template_version = []
    oai_sets = []
    oai_metadata_formats = []
    oai_records = []
    data = []
    oai_data = []
    name = "Registry"
    identifier = 'dummy'
    data_identifiers = []
    workspaces = []
    nb_public_data = 0

    def insert_data(self):
        self.insert_settings()
        self.insert_workspaces()
        self.insert_templates()
        self.insert_record()
        self.insert_oai_record()
        self.insert_oai_metadata_format()
        self.insert_oai_set()

    """
        Setting's methods
    """
    def insert_settings(self):
        self.settings = OaiSettings(repository_name=self.name, repository_identifier=self.identifier,
                                    enable_harvesting=True).save()

    """
        Template's methods
    """

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def insert_templates(self):
        saved_templates = []
        saved_template_version = []
        list_templates = OaiPmhMock.mock_template()
        for template in list_templates:
            # Create template version manager
            template_version_manager = TemplateVersionManager(title='default_chemical_element_type')
            template_version_manager_api.insert(template_version_manager, template)
            saved_template_version.append(template_version_manager)
            saved_templates.append(template.save())

        self.templates = saved_templates
        self.template_version = saved_template_version

    """
        Workspace's methods
    """

    def insert_workspaces(self):
        saved_data = []
        list_data = OaiPmhMock.mock_workspaces()
        for elt in list_data:
            saved_data.append(elt.save())

        self.workspaces = saved_data

    """
        Data's methods
    """
    def insert_record(self):
        saved_data = []
        self.nb_public_data = 0
        list_data = OaiPmhMock.mock_data()
        for elt in list_data:
            saved_data.append(elt.save())
            if elt.workspace is not None and workspace_api.is_workspace_public(elt.workspace):
                self.nb_public_data += 1

        self.data = saved_data

    """
        OaiData's methods
    """
    def insert_oai_record(self):
        saved_data = []
        list_data = OaiPmhMock.mock_oai_data()
        for elt in list_data:
            saved_data.append(elt.save())
            identifier = '%s:%s:id/%s' % (OAI_SCHEME, OAI_REPO_IDENTIFIER, str(elt.data.id))
            self.data_identifiers.append(identifier)

        self.oai_data = saved_data

    """
        OaiPmhProviderMetadataFormat's methods
    """
    def insert_oai_metadata_format(self):
        saved_data = []
        list_data = OaiPmhMock.mock_oai_metadata_format()
        for elt in list_data:
            saved_data.append(elt.save())

        self.oai_metadata_formats = saved_data

    """
        OaiPmhProviderSet's methods
    """

    def insert_oai_set(self):
        saved_data = []
        list_data = OaiPmhMock.mock_oai_set()
        for elt in list_data:
            saved_data.append(elt.save())

        self.oai_sets = saved_data

    """
        OaiXSLTemplate's methods
    """


class OaiPmhMock(object):
    @staticmethod
    def mock_template(version=''):
        with open(os.path.join(DUMP_OAI_PMH_TEST_PATH, 'template{0}.json'.format(version))) as f:
            data = f.read()
        data_json = json.loads(data)
        list_templates = [Template(**x) for x in data_json]
        return list_templates

    @staticmethod
    def mock_oai_first_template(version=''):
        list_templates = OaiPmhMock.mock_template(version)
        return list_templates[0]

    @staticmethod
    def mock_workspaces(version=''):
        with open(os.path.join(DUMP_OAI_PMH_TEST_PATH, 'workspaces{0}.json'.format(version))) as f:
            data = f.read()
        data_json = json.loads(data)
        list_data = [Workspace(**x) for x in data_json]
        return list_data

    @staticmethod
    def mock_data(version=''):
        with open(os.path.join(DUMP_OAI_PMH_TEST_PATH, 'data{0}.json'.format(version))) as f:
            data = f.read()
        data_json = json.loads(data)
        list_data = [Data(**x) for x in data_json]
        return list_data

    @staticmethod
    def mock_oai_data(version=''):
        with open(os.path.join(DUMP_OAI_PMH_TEST_PATH, 'oai_data{0}.json'.format(version))) as f:
            data = f.read()
        data_json = json.loads(data)
        list_data = [OaiData(**x) for x in data_json]
        return list_data

    @staticmethod
    def mock_oai_metadata_format(version=''):
        with open(os.path.join(DUMP_OAI_PMH_TEST_PATH, 'oai_metadata_format{0}.json'.format(version))) as f:
            data = f.read()
        data_json = json.loads(data)
        list_metadata_format = [OaiProviderMetadataFormat(**x) for x in data_json]
        return list_metadata_format

    @staticmethod
    def mock_oai_first_metadata_format(version=''):
        list_oai_metadata_formats = OaiPmhMock.mock_oai_metadata_format(version)
        return list_oai_metadata_formats[0]

    @staticmethod
    def mock_oai_set(version=''):
        with open(os.path.join(DUMP_OAI_PMH_TEST_PATH, 'oai_set{0}.json'.format(version))) as f:
            data = f.read()
        data_json = json.loads(data)
        list_set = [OaiProviderSet(**x) for x in data_json]
        return list_set

    @staticmethod
    def mock_oai_first_set(version=''):
        list_oai_sets = OaiPmhMock.mock_oai_set(version)
        return list_oai_sets[0]
