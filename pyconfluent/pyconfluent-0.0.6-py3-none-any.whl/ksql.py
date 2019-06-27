import requests
import json


class KSQL:
    """
    Create streams and tables, manage servers, and get status information.
    """

    def __init__(self, host='http://localhost'):
        self.host = host + ":8088"
        self.headers = {"Content-Type": "application/json",
                        "Accept": "application/json"}

    def server_status(self):
        """
        Check the health of the server
        :return:
        """
        url = self.host + "/info"
        r = requests.get(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def ksql(self, _ksql, properties=None, seq_number=None):
        """
        Used to run any KSQL statement except SELECT, use query() for SELECT statements

        :param sql: a semicolon-deliminated sequence of SQL statements to run
        :param properties: config mappings (optional)
        :param seq_number: prevents this statement from running until all other
                        specified sequence numbers have completed. Used for
                         ordering separate sql queries (optional)
        :return:
        """
        if _ksql[-1] != ';':
            _ksql + ';'

        url = self.host + "/ksql"
        payload = {"ksql": _ksql}

        if properties:
            payload['streamsProperties'] = properties
        if seq_number:
            payload['commandSequenceNumber'] = seq_number

        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def query(self, _ksql, properties=None):
        """
        Run a SELECT query and stream the output.

        :param sql: the SELECT statement to run
        :param properties: config mappings (optional)
        :return:
        """
        if _ksql[-1] != ';':
            _ksql + ';'

        url = self.host + "/query"
        payload = {"ksql": _ksql}

        if properties:
            payload['streamsProperties'] = properties

        s = requests.Session()
        req = requests.post(url, data=json.dumps(payload), headers=self.headers, stream=True)
        return req.content

    def statement_status(self, command_id):
        """
        Get the current status of a query

        :param command_id: commandId returned when the query was run (required)
        :return:
        """
        url = self.host + "/status/%s" % command_id
        r = requests.get(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def terminate_cluster(self, topics=None):
        """
        Use this function to shut down the last KSQL server alive.

        :param topics: list of topics to delete (optional)
        :return:
        """
        url = self.host + "/ksql/terminate"
        if topics:
            payload = {"deleteTopicList": topics}
            r = requests.post(url, data=payload, headers=self.headers)
            return json.loads(r.content)
        r = requests.post(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp
