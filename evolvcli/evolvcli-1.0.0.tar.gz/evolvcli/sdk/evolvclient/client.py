from .util import EvolvError
from .request import EvolvRequest
from .collections import METAMODELS, ACCOUNTS, EXPERIMENTS, ENVIRONMENTS, CANDIDATES


class EvolvClient:

    def __init__(self, config):
        """Constructs a new Experiment Client.

        :param EvolvConfig config: configuration for the Evolv account
        """
        self._config = config
        self._requester = EvolvRequest(config)

    def set_api_key(self, api_key):
        """Sets the api key being used for the request to the experiments api.

        :param string api_key: unique key
        """
        self._config.api_key = api_key
        self._requester = EvolvRequest(self._config)

    def set_bearer_token(self, bearer_token):
        """Sets the api key being used for the request to the experiments api.

        :param string bearer_token: jwt
        """
        self._config.bearer_token = bearer_token
        self._requester = EvolvRequest(self._config)

    def get_account(self, account_id):
        """Retrieves an account. Defaults to root account.

        :param string account_id: id of the account
        :return: the root account for the sdk key supplied
        :rtype: json
        """
        account = self._requester.get(ACCOUNTS, entity_id=account_id)
        return account

    def get_environment(self, environment_id, account_id, version=None, content_only=False):
        """Retrieves an environment

        :param string environment_id: the id of the environment
        :param string account_id: id of the account the environment exists in
        :param string version: get specific version
        :param bool content_only: get environments contents
        :return: the environment
        :rtype: json
        """
        environment = self._requester.get(ENVIRONMENTS, entity_id=environment_id, content_only=content_only,
                                          version=version, account_id=account_id)
        return environment

    def get_metamodel(self, metamodel_id, account_id, version=None, content_only=False):
        """Retrieves specific metamodel.

        :param string metamodel_id: a guid which identifies a specific metamodel
        :param string account_id: id of the account the metamodel exists in
        :param string version: version of the metamodel being requested
        :param bool content_only: get metamodels contents
        :return: a metamodel
        :rtype: json
        """
        metamodel = self._requester.get(METAMODELS, entity_id=metamodel_id, content_only=content_only,
                                        version=version, account_id=account_id)
        return metamodel

    def get_experiment(self, experiment_id, account_id, metamodel_id, version=None, content_only=False):
        """Retrieves experiment specified.

        :param string experiment_id: unique identifier of the experiment requested
        :param string account_id: id of the account the experiment exists in
        :param string metamodel_id: id of the metamodel the experiment exists in
        :param string version: version of the experiment being requested
        :param bool content_only: get experiments contents
        :return: an experiment
        :rtype: json
        """
        experiment = self._requester.get(EXPERIMENTS, entity_id=experiment_id, content_only=content_only,
                                         version=version, account_id=account_id, metamodel_id=metamodel_id)
        return experiment

    def get_candidate(self, candidate_id, account_id, metamodel_id, experiment_id):
        """Retrieves specified candidate.

        :param string candidate_id: unique identifier of the candidate requested
        :param string account_id: id of the account the candidate exists in
        :param string metamodel_id: id of the metamodel the candidate exists in
        :param string experiment_id: id of the experiment the candidate exists in
        :return: a candidate
        :rtype: json
        """
        candidate = self._requester.get(CANDIDATES, entity_id=candidate_id, account_id=account_id,
                                        metamodel_id=metamodel_id, experiment_id=experiment_id)
        return candidate

    def list_accounts(self):
        """Retrieves list of accounts the user has access to.

        :return: a list of accounts
        :rtype: json
        """
        accounts = self._requester.query(ACCOUNTS)
        return accounts

    def list_environments(self, account_id, query=None):
        """Retrieves list of environments available under the users account.

        :param string account_id: id of the account the environments exist in
        :param string query: experiment api query
        :return: a list of environments
        :rtype: json
        """
        environments = self._requester.query(ENVIRONMENTS, query, account_id=account_id)
        return environments

    def list_metamodels(self, account_id, query=None):
        """Retrieves a list of metamodels for the configured account.

        :param string account_id: id of the account the metamodels exist in
        :param string query: experiment api query
        :return: a list of metamodels
        :rtype: json
        """
        metamodels = self._requester.query(METAMODELS, query, account_id=account_id)
        return metamodels

    def list_experiments(self, account_id, metamodel_id, query=None):
        """Retrieves a list of experiments for the configured account.

        :param string account_id: id of the account the experiments exist in
        :param string metamodel_id: id of the metamodel the experiments exist in
        :param string query: experiment api query
        :return: a list of experiments
        :rtype: json
        """
        experiments = self._requester.query(EXPERIMENTS, query, account_id=account_id, metamodel_id=metamodel_id)
        return experiments

    def list_candidates(self, account_id, metamodel_id, experiment_id, query=None):
        """Retrieves list of candidates available under the users account.

        :param string account_id: id of the account the candidates exist in
        :param string metamodel_id: id of the metamodel the candidates exist in
        :param string experiment_id: id of the experiment the candidates exist in
        :param string query: experiment api query
        :return: list of candidates
        :rtype: json
        """
        return self._requester.query(CANDIDATES, query, account_id=account_id, metamodel_id=metamodel_id,
                                     experiment_id=experiment_id)

    def create_account(self, name):
        """Creates an account.

        :param string name: account name
        :return: the created account
        :rtype: json
        """
        account = self._requester.post(ACCOUNTS, json={'name': name})
        return account

    def create_environment(self, name, account_id, default=False, content=None, content_type=None, protected=False):
        """Creates an environment.

        :param string name: the environment name
        :param string account_id: id of the account the environment will exist in
        :param bool default: whether or not to make the environment the default
        :param string content: extra content defining the experiment
        :param string content_type: content type formatting being used ['application/json', 'application/yaml']
        :param bool protected: whether on not the environment is protected
        :return: the created environment
        :rtype: json
        """
        payload = {
            'name': name,
            'default': default,
            'protected': protected
        }

        if content:
            assert content_type
            payload['content'] = content
            payload['content_type'] = content_type

        environment = self._requester.post(ENVIRONMENTS, json=payload, account_id=account_id)
        return environment

    def create_metamodel(self, name, yaml, account_id):
        """Creates a metamodel.

        :param string name: metamodel name
        :param string yaml: yaml representing the metamodel
        :param string account_id: id of the account the metamodel will exist in
        :return: the created metamodel
        :rtype: json
        """
        metamodel = self._requester.post(METAMODELS, json={
            'name': name,
            'content_type': 'application/yaml',
            'content': yaml
        }, account_id=account_id)
        return metamodel

    def create_experiment(self, name, metamodel_id, metamodel_version, optimization_targets, account_id,
                          environment_id, experiment_type='CONTROL', population_size=10, budget=None,
                          precursor=None, algorithm_version=None, estimated_cr=5.0, long_tail_correction=True,
                          sample_rate=100, target_confidence='STANDARD', audience_query=None, content=None,
                          content_type=None):
        """Creates an experiment.

        :param string name: name of the experiment
        :param string metamodel_id: id of metamodel to create experiment from
        :param string metamodel_version: version of the metamodel to create the experiment from
        :param list optimization_targets: events to optimize the experiment upon
        :param string account_id: id of the account the experiment will exist in
        :param string environment_id: the id of the environment in which to create the experiment
        :param string experiment_type: type of experiment to build ['CONTROL', 'ABN', 'EVO']
        :param int population_size: size of the initial experiment
        :param int budget: number of participants to test before terminating
        :param string precursor: id of the experiment that precedes this one
        :param string algorithm_version: version of the algorithm to use for the experiment
        :param float estimated_cr: the estimated coversion rate of the experiment
        :param bool long_tail_correction: whether to use long tail correction or not
        :param int sample_rate: the percentage traffic allocation
        :param string target_confidence: the level of confidence needed before progressing
        :param string audience_query: dict defining the experiments target audience
        :param string content: extra content defining the experiment
        :param string content_type: content type formatting being used ['application/json', 'application/yaml']
        :return: the created experiment
        :rtype: json
        """
        experiment = self._requester.post(EXPERIMENTS, json={
            'name': name,
            'type': experiment_type,
            'population_size': population_size,
            'environment_id': environment_id,
            'metamodel_version': metamodel_version,
            'optimization_targets': optimization_targets,
            'precursor': precursor,
            'algorithm_version': algorithm_version,
            'estimated_cr': estimated_cr / 100,
            'budget': budget,
            'sample_rate': sample_rate / 100,
            'long_tail_correction': long_tail_correction,
            'target_confidence': target_confidence,
            'audience_query': audience_query,
            'content': content,
            'content_type': content_type
        }, account_id=account_id, metamodel_id=metamodel_id)
        return experiment

    def create_candidate(self, metamodel_id, metamodel_version, genome, account_id, environment_id, experiment_id,
                         allocation_probability=1.0):
        """Creates a candidate.

        :param string metamodel_id: id of the metamodel
        :param string metamodel_version: metamodel version to associate with the candidate
        :param string account_id: id of the account the candidate will exist in
        :param string environment_id: the id of the environment in which to create the candidate
        :param string experiment_id: id of the experiment for the candidate to exist in
        :param string genome: representation of the candidates genome
        :param float allocation_probability: probability that the candidate gets allocated
        :return: a candidate
        :rtype: json
        """
        candidate = self._requester.post(CANDIDATES, json={
            'environment_id': environment_id,
            'metamodel_version': metamodel_version,
            'genome': genome,
            'allocation_probability': allocation_probability,
            'strategy': 'crafted'
        }, account_id=account_id, metamodel_id=metamodel_id, experiment_id=experiment_id)
        return candidate

    def update_environment(self, environment_id, name, content, content_type, account_id):
        """Updates an environment

        :param string environment_id: the environment id
        :param string name: name of the environment
        :param string content: content to be updated
        :param string content_type: content type ['application/json', 'application/yaml']
        :param string account_id: id of the account the environment exists in
        :return: the updated environment
        :rtype: json
        """
        environment = self._requester.put(ENVIRONMENTS, environment_id, json={
            'id': environment_id,
            'name': name,
            'content_type': content_type,
            'content': content
        }, account_id=account_id)
        return environment

    def update_metamodel(self, metamodel_id, name, content, content_type, account_id):
        """Updates a metamodel

        :param string metamodel_id: the metamodel id
        :param string name: name of the metamodel
        :param string content: content to be updated
        :param string content_type: content type ['application/json', 'application/yaml']
        :param string account_id: id of the account the metamodel exists in
        :return: the updated metamodel
        :rtype: json
        """
        metamodel = self._requester.put(METAMODELS, metamodel_id, json={
            'id': metamodel_id,
            'name': name,
            'content_type': content_type,
            'content': content
        }, account_id=account_id)
        return metamodel

    def update_experiment(self, experiment_id, account_id, metamodel_id, abort=False, abort_reason=None):
        """Update an experiment.

        :param string experiment_id: the experiment id
        :param bool abort: whether or not to stop the experiment
        :param string abort_reason: the reason for stopping the experiment
        :param string account_id: id of the account the experiment exists in
        :param string metamodel_id: id of the metamodel the experiment exists in
        :return: the updated experiment
        :rtype: json
        """
        experiment = self._requester.patch(EXPERIMENTS, experiment_id, json={
            'aborted': abort,
            'abort_reason': abort_reason
        }, account_id=account_id, metamodel_id=metamodel_id)
        return experiment

    class ClientError(EvolvError):
        """To be used when there is a error in the client.

        """
        pass
