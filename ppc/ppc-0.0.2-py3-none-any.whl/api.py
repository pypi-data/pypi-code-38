import hashlib
import json
import logging

import requests


class APIError(Exception):
    """Raised for exceptional calls to the Redlock API

    Attributes:
        url -- the http url that was called
        method -- the http verb
        status_code -- the integer code for http status
        message -- any message from server
    """

    def __init__(self, url, method, status_code, message):
        self.url = url
        self.method = method
        self.status_code = status_code
        self.message = message


def flatten(dict_to_flatten, separator='_'):
    out = {}

    def _flatten(node, name=''):
        if type(node) is dict:
            for k in node:
                _flatten(node[k], name + k + separator)
        else:
            out[name[:-1]] = node

    _flatten(dict_to_flatten)
    return out


class ItemsList:
    """A collection of Items with added functional behaviors.

    Parameters:
        items (List): a list of Item to wrap

    """
    def __init__(self, items=None):
        if items is None:
            self.items = []
        else:
            self.items = items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def append(self, item):
        """add item to end of list"""
        self.items.append(item)

    def head(self):
        """get the first item from the list  like (car list)"""
        return self.items[0]

    def tail(self):
        """get the rest of the list like (cdr list)"""
        return self.items[1:]

    def drop(self, n):
        """drop the items from before n and return what is left"""
        return self.items[n:]

    def take(self, n):
        return self.items[:n]

    @property
    def unique_keys(self):
        """the set of flattened keys from across all of these items"""
        keys = set()
        for i in self.items:
            [keys.add(k) for k in i.keys]
        return sorted(keys)


class Alerts(ItemsList):
    """An iterable of Alert built up from the RedLock API.

    Parameters:
        endpoint (str): the api endpoint without path e.g. https://api.redlock.io/
        headers (dict): http headers with auth for RedLock
        verbosity (bool): should alerts contain all of the details? defaults False

     These represent the set of issues that the system has flagged for external response. See Alert"""
    def __init__(self, endpoint, headers, verbosity):
        # TODO what about large list of Alerts?
        # TODO refactor API Call to one function and handle token timeout?
        # TODO is the time info necessary? what is the default?
        r = requests.get(f"{endpoint}v2/alert?detailed={str(verbosity).lower()}&timeType=relative&timeAmount=1&timeUnit=year", headers=headers)
        if r.status_code != requests.codes.ok:
            raise APIError(r.request.url, 'GET', r.status_code, r.text)

        items = r.json()['items']
        self.json = json.dumps(items)
        super().__init__([Alert(a) for a in r.json()['items']])

    def __getitem__(self, item):
        for a in self.items:
            if item == a.id:
                return a
        return None


class Policies(ItemsList):
    """An iterable of Policy built up from the RedLock API.

    Parameters:
        endpoint (str): the api endpoint without path e.g. https://api.redlock.io/
        headers (dict): http headers with auth for redlock

    These represent the current set of metadata that the system has available for monitoring. See Policy"""
    def __init__(self, endpoint, headers):
        r = requests.get(f"{endpoint}policy", headers=headers)
        if r.status_code != requests.codes.ok:
            raise APIError(r.request.url, 'GET', r.status_code, r.text)

        self.json = r.text
        super().__init__([Policy(p) for p in r.json()])

    def __getitem__(self, item):
        for p in self.items:
            if item == p.policyId:
                return p
        return None



class Criteria(ItemsList):
    """An iterable built up from the RedLock API. This is heavy on API calls.

    Parameters:
        endpoint (str): the api endpoint without path e.g. https://api.redlock.io/
        headers (dict): http headers with auth for redlock
        policies (Policies): the iterable of Policy to check each for Criterion

     These represent the RQL Queries that are used by Policies. See Criterion"""
    def __init__(self, endpoint, headers, policies):
        json = []
        criteria = []

        for p in policies:
            try:
                r = requests.get(f"{endpoint}search/history/{p.rule_criteria}", headers=headers)
                if r.status_code != requests.codes.ok:
                    raise APIError(r.request.url, 'GET', r.status_code, r.text)
                json.append(r.text)
                criteria.append(Criterion(r.json()))
            except KeyError as ke:
                logging.debug(f"KeyError Reading Criteria: {ke}")
            except APIError as ae:
                logging.debug(f"APIError Reading Criteria: {ae}")

        joined = ",".join(json)
        # TODO ;) yeah really
        self.json = f'[{joined}]'
        super().__init__(criteria)

    def __getitem__(self, item):
        for a in self.items:
            if item == a.id:
                return a
        return None


class Item:
    def __init__(self, args):
        self.orig = args  #: The original nested data structure which closely mimics the API response.
        self.flat = flatten(args)  #: A flattened version where the keys are composite and the values the leaves of json

    @property
    def keys(self):
        """These are composite keys which have been flattened from the json API response.

        e.g policy.rule.criteriaId -> policy_rule_criteriaId"""
        return [k for k in self.flat]

    @property
    def values(self):
        """These are the leaves from the json API response since everything is flattened."""
        return [str(v) for v in self.flat.values()]

    def __getattr__(self, item):
        return self.flat[item]

    @property
    def hash(self):
        """This is a fingerprint of all of the data for this entity.

        Useful for comparing Items over time. Mainly implemented for ppc.sql.SQLCache."""

        h = hashlib.md5()
        for k, v in self.flat.items():
            h.update((k + str(v)).encode())
        return h.hexdigest()


class Alert(Item):
    """The notification that something is amiss.

    This represents a Policy violation which is ultimately triggered by a Criterion which is RQL."""
    def __init__(self, args):
        super().__init__(args)


class Policy(Item):
    """The metadata for what is watched by Redlock.

    Ultimately, this is implemented by a Criterion and it's RQL. When violated it will create an Alert.
    See Item."""
    def __init__(self, args):
        super().__init__(args)


class Criterion(Item):
    """The RQL and associated info.

    See Item"""
    def __init__(self, args):
        super().__init__(args)


class Client:
    """A RedLock API Client. Mainly used to interface to Policies and Alerts. It calls
    the APIs and keeps results in some properties.

    Args:
         username (str): The RedLock login name. Typically an email address
         password (str): As it says ;0
         endpoint (str): This is the url for the api. App endpoint maps from e.g app -> https://api.redlock.io/

    Example:
        Client usage is straightforward. Create the Client and then access the core properties (which will instantiate
        them by pulling from the API). ::

            >>>from ppc.api import Client
            >>>c = Client("scott@oracle.com", "tiger", "https://api2.redlock.io/")


            >>>for p in c.policies.take(5):
            ...    print(f"{p.policyId}: {p.name}")
            43c42760-5283-4bc4-ac43-a80e58c4139f: AWS S3 bucket has global view ACL permissions enabled
            472e08a2-c741-43eb-a3ca-e2f5cd275cf7: Azure Network Security Group allows FTP (TCP Port 21)
            91c941aa-d110-4b33-9934-aadd86b1a4d9: AWS Redshift database does not have audit logging enabled
            f5b4b962-e053-4e73-94d2-c21bd2520a0d: AWS ElastiCache cluster not associated with VPC
            fe81b03a-c602-4b16-8ae9-973724c1adae: GCP Kubernetes Engine Clusters web UI/Dashboard is set to Enabled
    """
    def __init__(self, username, password, endpoint):
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        # TODO handle token timeout
        self.token = self.__get_token(endpoint, username, password, self.headers)
        self.headers['x-redlock-auth'] = self.token
        self.__policies = None
        self.__alerts = None
        self.__verbose_alerts = False
        self.__criteria = None

    # TODO does this help?
    @staticmethod
    def __get_token(endpoint, username, password, headers):
        body = {
            'username': username,
            'password': password
        }

        r = requests.post(f"{endpoint}login", headers=headers, json=body)
        logging.debug(f"Response from login {r.json()}")
        if r.status_code != requests.codes.ok:
            raise APIError(r.request.url, 'POST', r.status_code, r.text)

        return r.json()['token']

    @property
    def policies(self):
        """Policies: This a lazy iterable of Policy.

        Example:
            To see the full set of keys for all Policy instances across the service call. ::

                >>>for key_name in c.policies.unique_keys:
                ...    print(key_name)
                ...
                alerts
                cloudType
                complianceMetadata
                createdBy
                createdOn
                deleted
                description
                enabled
                labels
                lastModifiedBy
                lastModifiedOn
                name
                openAlertsCount
                owner
                policyId
                policyMode
                policyType
                recommendation
                remediable
                remediation_cliScriptTemplate
                remediation_description
                remediation_impact
                ruleLastModifiedOn
                rule_apiName
                rule_cloudType
                rule_criteria
                rule_criteria_$schema
                rule_criteria_properties_name_not_enum
                rule_criteria_properties_name_type
                rule_criteria_properties_trailARN_not_enum
                rule_criteria_properties_trailARN_type
                rule_criteria_properties_vpcId_type
                rule_criteria_required
                rule_criteria_title
                rule_criteria_type
                rule_filter_apiName
                rule_filter_cloudType
                rule_filter_condition
                rule_filter_criteria
                rule_filter_name
                rule_filter_resourceIdPath
                rule_filter_resourceType
                rule_filter_type
                rule_name
                rule_operator
                rule_parameters_savedSearch
                rule_resourceIdPath
                rule_resourceType
                rule_type
                severity
                systemDefault
        """
        if self.__policies is None:
            self.__policies = Policies(self.endpoint, self.headers)
        return self.__policies

    @property
    def verbose_alerts(self):
        return self.__verbose_alerts

    @verbose_alerts.setter
    def verbose_alerts(self, value: bool):
        self.__alerts = None
        self.__verbose_alerts = value

    @property
    def alerts(self):
        """Alerts: This is a lazy iterable of Alert.

        Example:
            To see the full set of keys for all Alert instances across the service call::

                >>>for key_name in c.alerts.unique_keys:
                ...    print(key_name)
                ...
                alertTime
                anomalyDetail_accessKeyUsed
                anomalyDetail_accountName
                anomalyDetail_action
                anomalyDetail_customerId
                anomalyDetail_description
                anomalyDetail_dismissedUntil
                anomalyDetail_eventId
                anomalyDetail_features
                anomalyDetail_groupedAnomalyCount
                anomalyDetail_id
                anomalyDetail_reasonIds
                anomalyDetail_reasonValues
                anomalyDetail_resource
                anomalyDetail_severity
                anomalyDetail_status
                anomalyDetail_subject
                anomalyDetail_subjectType
                anomalyDetail_time
                anomalyDetail_title
                anomalyDetail_type
                dismissalNote
                dismissedBy
                eventOccurred
                firstSeen
                history
                id
                investigateOptions_alertId
                investigateOptions_endTs
                investigateOptions_searchId
                investigateOptions_startTs
                lastSeen
                policy_complianceMetadata
                policy_deleted
                policy_description
                policy_labels
                policy_lastModifiedBy
                policy_lastModifiedOn
                policy_name
                policy_policyId
                policy_policyType
                policy_recommendation
                policy_remediable
                policy_remediation_cliScriptTemplate
                policy_remediation_description
                policy_remediation_impact
                policy_severity
                policy_systemDefault
                reason
                resource_account
                resource_accountId
                resource_additionalInfo_accessKeyAge
                resource_additionalInfo_inactiveSinceTs
                resource_cloudType
                resource_data_AccessKeysPerUserQuota
                resource_data_AccountAccessKeysPresent
                resource_data_AccountMFAEnabled
                resource_data_AccountSigningCertificatesPresent
                ... <elided> ...
                status
         """
        if self.__alerts is None:
            self.__alerts = Alerts(self.endpoint, self.headers, self.verbose_alerts)
        return self.__alerts

    @property
    def criteria(self):
        """Criteria: This is a lazy iterable of Criterion.

        While this is lazy, it is also "heavy" in that it makes many calls to the API to pull this info. It can
        take some time.

        These are RQL queries which are referenced from a Policy. For the most part there is a one to one from Policy
        to Criterion and this is that collection.

        Example:
            To see the full list of keys across the service currently call::

                >>>for key_name in c.criteria.unique_keys:
                ...    print(key_name)
                cloudType
                description
                id
                name
                query
                saved
                searchType
                timeRange_type
                timeRange_value_amount
                timeRange_value_unit

        """
        if self.__criteria is None:
            self.__criteria = Criteria(self.endpoint, self.headers, self.policies)
        return self.__criteria
