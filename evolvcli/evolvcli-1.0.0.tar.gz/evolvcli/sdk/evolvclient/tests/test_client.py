import unittest

from unittest.mock import patch, MagicMock

from ..config import EvolvConfig
from ..client import EvolvClient


class TestEvolvClient(unittest.TestCase):
    """
    Tests the EvolvClient class.
    """
    API_KEY = 'xx_test_xx'
    ACCOUNT = {'id': 'aasqkioi3d', 'name': 'Evolv Client', 'active': True, 'created': 1549930508.2330847}
    METAMODEL = {'id': '24544355', 'content_version': '425214545'}
    METAMODELS = [{'id': '24544355'}, {'id': '23524523'}]
    METAMODEL_CONTENT = {'_name': 'Sample'}
    EXPERIMENT = {'id': '2452452'}
    EXPERIMENTS = [{'id': '234235'}, {'id': '235245'}]
    ENVIRONMENT = {'id': '1332343'}
    ENVIRONMENTS = [{'id': '234235'}, {'id': '235245'}]
    CANDIDATE = {'id': '1332343'}
    CANDIDATES = [{'id': '234235'}, {'id': '235245'}]

    def test_create_instance(self):
        """
        Tests the creation of a EvolvClient instance.
        """
        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)

        self.assertIsInstance(client, EvolvClient)

    @patch('evolvclient.client.EvolvRequest')
    def test_get_account(self, mock_evolv_request):
        """
        Tests the client's retrieval of a specific account.
        """
        requester = MagicMock()
        requester.get.return_value = self.ACCOUNT
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        account = client.get_account(account_id=self.ACCOUNT['id'])

        self.assertEqual(account, self.ACCOUNT)

    @patch('evolvclient.client.EvolvRequest')
    def test_get_metamodel(self, mock_evolv_request):
        """
        Tests the client's retrieval of a specific metamodel.
        """
        requester = MagicMock()
        requester.get.return_value = self.METAMODEL
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        metamodel = client.get_metamodel(self.ACCOUNT['id'], self.METAMODEL.get('id'))

        self.assertEqual(metamodel, self.METAMODEL)

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        metamodel = client.get_metamodel(self.ACCOUNT['id'], self.METAMODEL.get('id'),
                                         version='abc')

        self.assertEqual(metamodel, self.METAMODEL)

    @patch('evolvclient.client.EvolvRequest')
    def test_get_metamodel_content(self, mock_evolv_request):
        """
        Tests the ability to retrieve the yaml file for a specific metamodel.
        """
        requester = MagicMock()
        requester.get.return_value = {}
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)

        client.get_metamodel(self.ACCOUNT['id'], self.METAMODEL.get('id'), content_only=True)

        requester = MagicMock()
        requester.get.return_value = self.METAMODEL_CONTENT
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)

        metamodel = client.get_metamodel(self.ACCOUNT['id'], self.METAMODEL.get('id'),
                                         version=self.METAMODEL['content_version'], content_only=True)
        self.assertEqual(metamodel, self.METAMODEL_CONTENT)

    @patch('evolvclient.client.EvolvRequest')
    def test_list_metamodels(self, mock_evolv_request):
        """
        Tests the client's retrieval of all available metamodels.
        """
        requester = MagicMock()
        requester.query.return_value = self.METAMODELS
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        metamodels = client.list_metamodels(self.ACCOUNT['id'])

        self.assertEqual(metamodels, self.METAMODELS)

    def test_set_api_key(self):
        """
        Testing the ability to reset the api key used in the client.
        """
        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        self.assertEqual(client._config.api_key, self.API_KEY)

        new_api_key = "12345"
        client.set_api_key(new_api_key)
        self.assertEqual(client._config.api_key, new_api_key)

    @patch('evolvclient.client.EvolvRequest')
    def test_get_experiment(self, mock_evolv_request):
        """
        Tests the ability to retrieve a specific experiment.
        """
        requester = MagicMock()
        requester.get.return_value = self.EXPERIMENT
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        experiment = client.get_experiment(self.ACCOUNT['id'], self.ENVIRONMENT['id'],
                                           self.EXPERIMENT['id'])

        self.assertEqual(experiment, self.EXPERIMENT)

    @patch('evolvclient.client.EvolvRequest')
    def test_get_environment(self, mock_evolv_request):
        """
        Tests the ability to retrieve a specific environment.
        """
        requester = MagicMock()
        requester.get.return_value = self.ENVIRONMENT
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        environment = client.get_environment(self.ACCOUNT['id'], self.ENVIRONMENT['id'])

        self.assertEqual(environment, self.ENVIRONMENT)

    @patch('evolvclient.client.EvolvRequest')
    def test_list_environments(self, mock_evolv_request):
        """
        Tests the ability to list all available environments.
        """
        requester = MagicMock()
        requester.query.return_value = self.ENVIRONMENTS
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        environments = client.list_environments(self.ACCOUNT['id'])

        self.assertEqual(environments, self.ENVIRONMENTS)

    @patch('evolvclient.client.EvolvRequest')
    def test_get_candidate(self, mock_evolv_request):
        """
        Tests the ability to retrieve a specific candidate.
        """
        requester = MagicMock()
        requester.get.return_value = self.CANDIDATE
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        candidate = client.get_candidate(self.ACCOUNT['id'], self.ENVIRONMENT['id'],
                                         self.EXPERIMENT['id'], self.CANDIDATE['id'])

        self.assertEqual(candidate, self.CANDIDATE)

    @patch('evolvclient.client.EvolvRequest')
    def test_list_candidates(self, mock_evolv_request):
        """
        Tests the ability to list all available candidates.
        """
        requester = MagicMock()
        requester.query.return_value = self.CANDIDATES
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        candidates = client.list_candidates(self.ACCOUNT['id'], self.ENVIRONMENT['id'],
                                            self.EXPERIMENT['id'])

        self.assertEqual(candidates, self.CANDIDATES)

    @patch('evolvclient.client.EvolvRequest')
    def test_list_experimments(self, mock_evolv_request):
        """
        Tests the ability to list all available candidates.
        """
        requester = MagicMock()
        requester.query.return_value = self.EXPERIMENTS
        mock_evolv_request.return_value = requester

        config = EvolvConfig(api_key=self.API_KEY)
        client = EvolvClient(config)
        experiments = client.list_experiments(self.ACCOUNT['id'], self.ENVIRONMENT['id'])

        self.assertEqual(experiments, self.EXPERIMENTS)


if __name__ == '__main__':
    unittest.main()
