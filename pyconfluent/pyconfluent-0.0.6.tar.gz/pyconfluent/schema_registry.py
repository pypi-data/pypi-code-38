import requests
import json


class SchemaRegistry:
    """
    Create schemas, update configurations, check compatibility of new schemas, etc.

    Subjects refer to the name under which the schema is registered, with kafka this
    is either the topic key or value depending on which schema is being registered
    or examined.
    """

    def __init__(self, host="http://localhost:8081"):
        self.host = host
        self.headers = {"Content-Type": "application/json",
                        "Accept": "application/json"}

    def schemas(self, _id):
        """
        Get the schema identified by _id

        :param _id:
        :return:
        """
        url = self.host + "/schemas/ids/%s" % _id
        r = requests.get(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def subjects(self, subject=None, version_id=None):
        """
        Returns a list of registered subjects

        :param subject: (optional)
        :param version_id: (optional)
        :return:
        """
        if subject:
            url = self.host + "subjects/%s/versions" % subject
        elif subject and version_id:
            url = self.host + "/subjects/%s/versions/%s" % (subject, version_id)
        else:
            url = self.host + "/subjects"
        r = requests.get(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def delete_subject(self, subject, version_id=None):
        """
        Deletes a subject from the registry

        :param subject:
        :param version_id: (optional)
        :return:
        """
        if version_id:
            url = self.host + "/subjects/%s/versions/%s" % (subject, version_id)
        else:
            url = self.host + "/subjects/%s" % subject
        r = requests.delete(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def create_subject(self, subject, schema):
        """
        Register a new subject/schema.

        :param subject: specify the subject name to be registered
        :param schema: AVRO schema string
        :return:
        """
        payload = {"schema": schema}
        print(payload)
        url = self.host + "/subjects/%s/versions" % subject
        r = requests.post(url, data=payload, headers=self.headers)
        print(r.content)
        resp = json.loads(r.content)
        return resp

    def check_subject(self, subject):
        """
        Check to see if a subject exists, if it does returns the schema string,
        subject name, unique identifier and version

        :param subject:
        :return:
        """
        url = self.host + "/subjects/%s" % subject
        r = requests.post(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def check_compatibility(self, subject, version_id, new_schema):
        """
        Test new schemas against specific versions of registered schema for
        compatibility.

        :param subject:
        :param version_id:
        :new_schema: AVRO schema string
        :return:
        """
        url = self.host + "/compatibility/subjects/%s/versions/%s" % (subject, version_id)
        payload = {"schema": new_schema}
        r = requests.post(url, headers=self.headers, data=payload)
        resp = json.loads(r.content)
        return resp

    def update_config(self, compatibility, subject=None):
        """
        Update the compatibility configuration globally or for a specific subject

        :param compatibility: Must be one of BACKWARD, BACKWARD_TRANSITIVE, FORWARD,
                                FORWARD_TRANSITIVE, FULL, FULL_TRANSITIVE, NONE
        :param subject: (optional)
        :return:
        """
        if subject:
            url = self.host + "/config/%s" % subject
        else:
            url = self.host + "/config"
        payload = {"compatibility": compatibility}
        r = requests.put(url, data=payload, headers=self.headers)
        resp = json.loads(r.content)
        return resp

    def get_config(self, subject):
        """
        Get the current compatibility configuration for a subject

        :param subject:
        :return:
        """
        url = self.host + "/config/%s" % subject
        r = requests.get(url, headers=self.headers)
        resp = json.loads(r.content)
        return resp

