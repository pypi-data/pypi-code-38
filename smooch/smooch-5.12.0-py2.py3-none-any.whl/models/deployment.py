# coding: utf-8

"""
    Smooch

    The Smooch API is a unified interface for powering messaging in your customer experiences across every channel. Our API speeds access to new markets, reduces time to ship, eliminates complexity, and helps you build the best experiences for your customers. For more information, visit our [official documentation](https://docs.smooch.io).

    OpenAPI spec version: 5.12
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class Deployment(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, status=None, hosting=None, base_url=None, username=None, phone_number=None, callback_url=None, callback_secret=None, integration_id=None, app_id=None):
        """
        Deployment - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'status': 'str',
            'hosting': 'str',
            'base_url': 'str',
            'username': 'str',
            'phone_number': 'str',
            'callback_url': 'str',
            'callback_secret': 'str',
            'integration_id': 'str',
            'app_id': 'str'
        }

        self.attribute_map = {
            'id': '_id',
            'status': 'status',
            'hosting': 'hosting',
            'base_url': 'baseUrl',
            'username': 'username',
            'phone_number': 'phoneNumber',
            'callback_url': 'callbackUrl',
            'callback_secret': 'callbackSecret',
            'integration_id': 'integrationId',
            'app_id': 'appId'
        }

        self._id = None
        self._status = None
        self._hosting = None
        self._base_url = None
        self._username = None
        self._phone_number = None
        self._callback_url = None
        self._callback_secret = None
        self._integration_id = None
        self._app_id = None

        # TODO: let required properties as mandatory parameter in the constructor.
        #       - to check if required property is not None (e.g. by calling setter)
        #       - ApiClient.__deserialize_model has to be adapted as well
        if id is not None:
          self.id = id
        if status is not None:
          self.status = status
        if hosting is not None:
          self.hosting = hosting
        if base_url is not None:
          self.base_url = base_url
        if username is not None:
          self.username = username
        if phone_number is not None:
          self.phone_number = phone_number
        if callback_url is not None:
          self.callback_url = callback_url
        if callback_secret is not None:
          self.callback_secret = callback_secret
        if integration_id is not None:
          self.integration_id = integration_id
        if app_id is not None:
          self.app_id = app_id

    @property
    def id(self):
        """
        Gets the id of this Deployment.
        The deployment ID, generated automatically.

        :return: The id of this Deployment.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Deployment.
        The deployment ID, generated automatically.

        :param id: The id of this Deployment.
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")

        self._id = id

    @property
    def status(self):
        """
        Gets the status of this Deployment.
        The deployment status. See [**DeploymentStatusEnum**](Enums.md#DeploymentStatusEnum) for available values.

        :return: The status of this Deployment.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this Deployment.
        The deployment status. See [**DeploymentStatusEnum**](Enums.md#DeploymentStatusEnum) for available values.

        :param status: The status of this Deployment.
        :type: str
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")

        self._status = status

    @property
    def hosting(self):
        """
        Gets the hosting of this Deployment.
        The deployment hosting. See [**DeploymentHostingEnum**](Enums.md#DeploymentHostingEnum) for available values.

        :return: The hosting of this Deployment.
        :rtype: str
        """
        return self._hosting

    @hosting.setter
    def hosting(self, hosting):
        """
        Sets the hosting of this Deployment.
        The deployment hosting. See [**DeploymentHostingEnum**](Enums.md#DeploymentHostingEnum) for available values.

        :param hosting: The hosting of this Deployment.
        :type: str
        """
        if hosting is None:
            raise ValueError("Invalid value for `hosting`, must not be `None`")

        self._hosting = hosting

    @property
    def base_url(self):
        """
        Gets the base_url of this Deployment.
        The baseUrl of the deployment. Only present for `self` hosted deployments.

        :return: The base_url of this Deployment.
        :rtype: str
        """
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        """
        Sets the base_url of this Deployment.
        The baseUrl of the deployment. Only present for `self` hosted deployments.

        :param base_url: The base_url of this Deployment.
        :type: str
        """

        self._base_url = base_url

    @property
    def username(self):
        """
        Gets the username of this Deployment.
        The username of the deployment. Only present for `self` hosted deployments.

        :return: The username of this Deployment.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this Deployment.
        The username of the deployment. Only present for `self` hosted deployments.

        :param username: The username of this Deployment.
        :type: str
        """

        self._username = username

    @property
    def phone_number(self):
        """
        Gets the phone_number of this Deployment.
        The phoneNumber of the deployment. Only present once the deployment has been registered.

        :return: The phone_number of this Deployment.
        :rtype: str
        """
        return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number):
        """
        Sets the phone_number of this Deployment.
        The phoneNumber of the deployment. Only present once the deployment has been registered.

        :param phone_number: The phone_number of this Deployment.
        :type: str
        """

        self._phone_number = phone_number

    @property
    def callback_url(self):
        """
        Gets the callback_url of this Deployment.
        The URL to be called by Smooch when the status of the deployment changes.

        :return: The callback_url of this Deployment.
        :rtype: str
        """
        return self._callback_url

    @callback_url.setter
    def callback_url(self, callback_url):
        """
        Sets the callback_url of this Deployment.
        The URL to be called by Smooch when the status of the deployment changes.

        :param callback_url: The callback_url of this Deployment.
        :type: str
        """

        self._callback_url = callback_url

    @property
    def callback_secret(self):
        """
        Gets the callback_secret of this Deployment.
        The secret used to secure the callback.

        :return: The callback_secret of this Deployment.
        :rtype: str
        """
        return self._callback_secret

    @callback_secret.setter
    def callback_secret(self, callback_secret):
        """
        Sets the callback_secret of this Deployment.
        The secret used to secure the callback.

        :param callback_secret: The callback_secret of this Deployment.
        :type: str
        """

        self._callback_secret = callback_secret

    @property
    def integration_id(self):
        """
        Gets the integration_id of this Deployment.
        The integrationId of the integration using this deployment.

        :return: The integration_id of this Deployment.
        :rtype: str
        """
        return self._integration_id

    @integration_id.setter
    def integration_id(self, integration_id):
        """
        Sets the integration_id of this Deployment.
        The integrationId of the integration using this deployment.

        :param integration_id: The integration_id of this Deployment.
        :type: str
        """

        self._integration_id = integration_id

    @property
    def app_id(self):
        """
        Gets the app_id of this Deployment.
        The appId of the integration using this deployment.

        :return: The app_id of this Deployment.
        :rtype: str
        """
        return self._app_id

    @app_id.setter
    def app_id(self, app_id):
        """
        Sets the app_id of this Deployment.
        The appId of the integration using this deployment.

        :param app_id: The app_id of this Deployment.
        :type: str
        """

        self._app_id = app_id

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, Deployment):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
