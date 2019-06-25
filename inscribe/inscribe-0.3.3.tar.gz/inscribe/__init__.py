__author__ = "inscribe.ai"

import logging
import requests
from requests import HTTPError
import os
from ._version import __version__

logger = logging.getLogger("inscribe-api")


class InscribeAPIException(Exception):
    pass


class Client(object):

    """
    https://inscribe.ai API client.
    All public methods returns a response dictionaries or raise `InscribeAPIException`

    """

    #DOMAIN_URL = "http://127.0.0.1:8000"
    DOMAIN_URL = "https://app.inscribe.ai"
    DEFAULT_API_VERSION = 1

    def create_customer(self, customer_name: str) -> dict:
        """
        Creates a customer
        """
        url = "/customers"
        payload = {"customer_name": customer_name}
        return self._post(url, json=payload)

    def get_all_customers(self) -> dict:
        """
        Return all available customers
        """
        url = "/customers"
        return self._get(url)

    def get_customer(self, customer_id: int) -> dict:
        """
        Get particular customer
        """
        url = "/customers/{customer_id}".format(customer_id=customer_id)
        return self._get(url)

    def delete_customer(self, customer_id: int) -> dict:
        """
        Delete particular customer
        """
        url = "/customers/{customer_id}".format(customer_id=customer_id)
        return self._delete(url)

    def upload_document(self, customer_id: int, document: object):
        url = "/customers/{customer_id}/documents".format(customer_id=customer_id)
        filename = os.path.basename(document.name)

        return self._post(url, files=((filename, document),))

    def check_document(self, customer_id: int, document_id: int) -> dict:
        """
        Analyse document and returns a response with a single value `fraud_score`

        :param customer_id: id of customer folder provided in response of Create Customer
        :param document_id: id of document provided in response of Upload Document
        """

        url = "/customers/{customer_id}/documents/{document_id}".format(customer_id=customer_id, document_id=document_id)
        return self._get(url)

    def delete_document(self, customer_id: int, document_id: int) -> dict:
        """
        Delete particular document
        """
        url = "/customers/{customer_id}/documents/{document_id}".format(
            customer_id=customer_id, document_id=document_id)
        return self._delete(url)

    def document_diff(self, customer_id, document_one_id, document_two_id):
        """
        Find differences between two documents
        """
        url = "/customers/{customer_id}/documents/diff?document_one_id={document_1}&document_two_id={document_2}".format(
            customer_id=customer_id, document_1=document_one_id, document_2=document_two_id)
        return self._get(url)

    def get_blacklist(self) -> dict:
        """
        Get user blacklist
        """
        url = "/blacklist"
        return self._get(url)
        
    def create_blacklist_entry(self, name: str = None, phone_number: str = None, address: str = None, file = None) -> dict:
        """
        Create a single blacklist entry
        """
        url = "/blacklist"
        payload = {"name": name, "phone_number": phone_number, "address": address, "file": file}
        return self._post(url, json=payload)

    def update_blacklist_entry(self, blacklist_id: int, name: str = None, phone_number: str = None, address: str = None) -> dict:
        """
        Update existing blacklist entry
        """
        url = "/blacklist/{blacklist_id}".format(blacklist_id=blacklist_id)
        payload = {"name": name, "phone_number": phone_number, "address": address}
        return self._post(url, json=payload)

    def delete_blacklist_entry(self, blacklist_id: int) -> dict:
        """
        Delete particular blacklist entry
        """
        url = "/blacklist/{blacklist_id}".format(blacklist_id=blacklist_id)
        return self._delete(url)

    def upload_template(self, document: object):
        url = "/templates"
        filename = os.path.basename(document.name)
        return self._post(url, files=((filename, document),))

    def get_all_templates(self) -> dict:
        url = "/templates"
        return self._get(url)

    def get_template(self, template_id: int) -> dict:
        url = "/templates/{template_id}".format(template_id=template_id)
        return self._get(url)

    def delete_template(self, template_id: int) -> dict:
        url = "/templates/{template_id}".format(template_id=template_id)
        return self._delete(url)

    @property
    def headers(self):
        return {'Authorization': self.api_key}

    @property
    def version(self):
        return "v%s" % self._version

    @property
    def base_url(self):
        return "{domain}/api/{version}".format(domain=self.DOMAIN_URL, version=self.version)

    def __init__(self, api_key: str, version: int = None):

        logger.info("Instantiate API class")

        self.api_key = api_key
        self.session = requests.Session()

        self.token = None
        self._version = version or self.DEFAULT_API_VERSION

        self._prepare()

    def _prepare(self):
        """ Prepares API class """

        logger.info("Getting user information")
        try:
            self.user = self._get("/auth/user/")["user"]
        except (ValueError, KeyError) as e:
            logger.exception(e)
            raise InscribeAPIException("Can't instantiate API class. Can't get a valid user.")

        if not self.user:
            raise InscribeAPIException("Can't instantiate API class. Can't get a valid user.")

        logger.info("Prepared successfully")

    def _get_http_method(self, method_name):

        http_method_mapping = {
            "GET": self.session.get,
            "POST": self.session.post,
            "DELETE": self.session.delete,
            "PUT": self.session.put,
            "PATCH": self.session.patch,
            "HEAD": self.session.head
        }

        try:
            return http_method_mapping[method_name]
        except KeyError:
            raise InscribeAPIException("HTTP method '%s' is invalid!" % method_name)

    def _get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def _post(self, url, **kwargs):
        return self._request("POST", url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._request("DELETE", url, **kwargs)

    def _put(self, url, **kwargs):
        return self._request("PUT", url, **kwargs)

    def _patch(self, url, **kwargs):
        return self._request("PATCH", url, **kwargs)

    def _head(self, url, **kwargs):
        return self._request("HEAD", url, **kwargs)

    def _request(self, method, url, **kwargs):

        http_method = self._get_http_method(method)

        url = self.base_url + url
        logger.info("HTTP %s request. : %s " % (method, url))

        response = http_method(url, headers=self.headers, **kwargs)
        logger.info("Response: %s" % response.text)
        # print("response: "+response.text)
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.info(str(e))
            raise InscribeAPIException("%s\nError occurred during sending a request to %s" % (str(e), url))

        try:
            response_json = response.json()
        except ValueError:
            raise InscribeAPIException("Couldn't get a valid JSON from response")

        if "success" not in response_json:
            raise InscribeAPIException("API returned invalid response: %s" % response.text)

        # if not response_json["success"]:
        #     raise InscribeAPIException("Error occurred during API call: %s" % response_json.get("message"))

        return response_json

    def __del__(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
