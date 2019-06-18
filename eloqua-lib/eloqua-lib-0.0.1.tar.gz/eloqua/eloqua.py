import json
import requests
from requests import Response
import logging
from .paths import *
from .errors import *

logger = logging.getLogger("Eloqua")


class EloquaObject(object):
    """ Base object for Assets, Data and all things Eloqua"""
    id = None

    def __str__(self):
        """Default str method"""
        if hasattr(self, "name"):
            return "<%s> %s (%s)" % (self.__class__.__name__, self.name, self.id)
        else:
            return "<%s> %s" % (self.__class__.__name__, str(self.Id))


class Asset(EloquaObject):
    """ Base object for all Eloqua Assets like Custom Objects, Forms, Emails and Landing Pages

        Example of how to manipulate an asset

            # Connect to Elouqa
            elq = EloquaConnection(COMPANY, USERNAME, PASSWORD)

            # Fetch a the custom object with id 501
            dog_owner_custom_object = elq.get_asset(CustomObject, id="501")

            # Change the folder
            dog_owner_custom_object.folderId = 101

            # Update the asset
            elq.update_asset(dog_owner_custom_object)


        Subclassing Asset allows for implementing Assets that are not included in the library yet

    """

    # When inheriting from this object, define the API paths
    create_path = None
    delete_path = None
    update_path = None
    get_path = None
    get_list_path = None

    # Predefined System Fields for Eloqua Objects
    id = None
    name = None
    type = None
    createdAt = None
    updatedAt = None
    updatedBy = None
    depth = None

    raw_data = None

    # Override this functionality
    def to_update_json(self):
        rdata = self.raw_data
        for attribute in ['name', 'description']:
            if getattr(self, attribute, None):
                rdata[attribute] = getattr(self, attribute)
        return rdata

    # Override this functionality
    def to_create_json(self):
        rdata = self.raw_data
        for attribute in ['name', 'description']:
            if getattr(self, attribute, None):
                rdata[attribute] = getattr(self, attribute)
        return rdata

    def __init__(self, raw_data=None):
        if isinstance(raw_data, Response):
            raw_data = raw_data.json()
        self.raw_data = raw_data
        if raw_data:
            self.id = raw_data.get('id')
            self.name = raw_data.get('name')
            self.type = raw_data.get('type')
            self.createdAt = raw_data.get('createdAt')
            self.updatedAt = raw_data.get('updatedAt')
            self.updatedBy = raw_data.get('updatedBy')
            self.depth = raw_data.get('depth')

    @classmethod
    def from_list(cls, from_eloqua_response=None):
        """
        Returns a list of Asset based on a response from Eloqua API

        :param from_eloqua_response: The response from eloqua API list CDOs
        :return: a list of CustomObjectModel
        """

        if from_eloqua_response:
            if isinstance(from_eloqua_response, Response):
                data = from_eloqua_response.json()
            else:
                data = from_eloqua_response

            resp_list = []
            for element in data['elements']:
                resp_list.append(cls(element))
            return resp_list


class Email(Asset):
    """ Eloqua Email Asset Class """
    create_path = EMAIL_CREATE_PATH
    delete_path = EMAIL_DELETE_PATH
    update_path = EMAIL_UPDATE_PATH
    get_path = EMAIL_GET_PATH
    get_list_path = EMAIL_GET_LIST_PATH


class LandingPage(Asset):
    """ Eloqua Landing Page Asset Class """
    create_path = LANDING_PAGE_CREATE_PATH
    delete_path = LANDING_PAGE_DELETE_PATH
    update_path = LANDING_PAGE_UPDATE_PATH
    get_path = LANDING_PAGE_GET_PATH
    get_list_path = LANDING_PAGE_GET_LIST_PATH


class Form(Asset):
    """ Eloqua Form Asset Class """
    create_path = FORM_CREATE_PATH
    delete_path = FORM_DELETE_PATH
    update_path = FORM_UPDATE_PATH
    get_path = FORM_GET_PATH
    get_list_path = FORM_GET_LIST_PATH


class CustomObject(Asset):
    """ Custom Object Asset Class """

    create_path = CUSTOM_OBJECT_CREATE_PATH
    delete_path = CUSTOM_OBJECT_DELETE_PATH
    update_path = CUSTOM_OBJECT_UPDATE_PATH
    get_path = CUSTOM_OBJECT_GET_PATH
    get_list_path = CUSTOM_OBJECT_GET_LIST_PATH


class CustomObjectModel(EloquaObject):
    """
    Custom Object Model Class

    Generate a usable python class for a specific custom object in your instance using
    EloquaConnection.generate_custom_object_code()

    For example, a class can be generated for a custom object Dog_Owner_0003 by connecting to Eloqua and generating
    the code.

        elq = EloquaConnection(COMPANY, USERNAME, PASSWORD)
        print (elq.generate_custom_object_code("Dog_Owner_0003", class_name="DogOwner"))

    The above code will yield:

        class DogOwner(CustomObject):
            NAME = "Dog_Owner_0003"
            PARENT_ID = "501"
            FIELDS = ["DogName1", "Breed1", "DateOfOwnership1"]
            ID_FIELD_MAP = {
                "123" : "DogName1",
                "124" : "Breed1",
                "125" : "DateOfOwnership1"
            }
            DogName1 = None
            Breed1 = None
            DateOfOwnership1 = None


    Once you have a model defined, you can use it to fetch data using the EloquaConnection class. For example:

        first_dog_owner = elq.get(DogOwner, record_id='1')

        all_corgi_dog_owners = elq.get(DogOwner, query_params={"search" : "Breed1='Corgi'"})


    """
    create_path = CUSTOM_OBJECT_DATA_CREATE_PATH
    delete_path = CUSTOM_OBJECT_DATA_DELETE_PATH
    update_path = CUSTOM_OBJECT_DATA_UPDATE_PATH
    get_path = CUSTOM_OBJECT_DATA_GET_PATH
    get_list_path = CUSTOM_OBJECT_DATA_GET_LIST_PATH

    NAME = None
    PARENT_ID = None
    FIELDS = None
    ID_FIELD_MAP = None
    META_FIELDS = None
    RAW_DATA = None

    # Extra Default Fields
    accountId = None
    isMapped = None
    uniqueCode = None
    name = None

    def __str__(self):
        """Default str method"""
        if hasattr(self, "name"):
            return "%s (%s)" % (self.name, self.id)
        else:
            return "%s %s" % (self.CDO_NAME, str(self.PARENT_ID))

    def __init__(self, from_eloqua_response=None):
        """
        Initialize from an eloqua response
        :param from_eloqua_response: Eloqua response data
        """
        if from_eloqua_response:
            if isinstance(from_eloqua_response, Response):
                data = from_eloqua_response.json()
            else:
                data = from_eloqua_response
            self.RAW_DATA = data
            for field in data['fieldValues']:
                field_id = field['id']
                self.__setattr__(self.ID_FIELD_MAP[field_id], field.get("value", None))
            for meta_field in data.keys():
                if meta_field != "fieldValues":
                    self.__setattr__(meta_field, data[meta_field])

    @classmethod
    def from_list(cls, from_eloqua_response=None):
        """
        Returns a list of CustomObjectModel based on a response from Eloqua API
        :param from_eloqua_response: The response from eloqua API list custom objects
        :return:
        """
        if from_eloqua_response:
            if isinstance(from_eloqua_response, Response):
                data = from_eloqua_response.json()
            else:
                data = from_eloqua_response

            resp_list = []
            for element in data['elements']:
                resp_list.append(cls(from_eloqua_response=element))
            return resp_list

    def to_update_json(self):
        """ Returns an object ready for use with the Eloqua API """

        fields_data = []
        for field_id, field_name in self.ID_FIELD_MAP.items():
            if getattr(self, field_name, None):
                fields_data.append({
                    "id":    field_id,
                    "value": getattr(self, field_name)
                })
        robj = {
            "id":          self.id,
            "type":        "CustomObjectData",
            "description": getattr(self, "description", ""),
            "name":        self.name,
            "fieldValues": fields_data,
        }

        return robj

    def to_create_json(self):
        """ Returns an object ready to create with the Eloqua API """

        fields_data = []
        for field_id, field_name in self.ID_FIELD_MAP.items():
            if getattr(self, field_name, None):
                fields_data.append({
                    "id":    field_id,
                    "value": getattr(self, field_name)
                })
        robj = {
            "fieldValues": fields_data
        }
        for attribute in ["name", "description"]:
            if getattr(self, attribute, None):
                robj[attribute] = getattr(self, attribute)

        return robj


class DataResponse(object):
    """
    Response of CustomObjectData

    `data` is a list of CustomObjectData

    The other info is gathered from the eloqua api response on init
    """
    data = None
    page_size = None
    page = None
    total = None

    def __init__(self, data=None, eloqua_response=None):
        self.data = data
        if eloqua_response:
            if isinstance(eloqua_response, Response):
                elq_data = eloqua_response.json()
            else:
                elq_data = eloqua_response

            self.total = elq_data.get('total')
            self.page = elq_data.get('page')
            self.page_size = elq_data.get('pageSize')


# noinspection PyPep8Naming
class EloquaConnection(object):
    """Manages connections to Eloqua initialized with credentials."""

    def __init__(self, company, username, password, base_url=None):
        """
        Initializes the connection using a company, username and password with API access

        :param company: Company
        :param username: Username
        :param password: Password
        :param base_url: Base URL if you have it already. Without it, init method will fetch it when you initialize the
                connection.
        """
        self.username = '%s\%s' % (company, username)
        self.password = password
        self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        if not base_url:
            self.base_url = self.get_base_url(self.auth)
        else:
            self.base_url = base_url

    @staticmethod
    def get_base_url(auth, login_url=DEFAULT_LOGIN_URL):
        """
        Gets the base_url if there is none defined

        :param auth: Authentication object
        :param login_url: Login url to use. Default is provided in paths.py
        :return: Returns the base url of the instance
        """
        response = requests.get(
            login_url,
            auth=auth,
            headers={
                "accept": 'application/json'
            })

        try:
            resp_json = response.json()
            base_url = resp_json['urls']['base']
            return base_url
        except TypeError:
            raise EloquaConnectionException('Could not authenticate with eloqua. Please check credentials')

    def request(self, path, http_method, data=None):
        """
        Does a raw eloqua request given a path and payload.

        :param path: API path. Ex: "/api/REST/2.0/assets/forms"
        :param http_method: Method to use. Ex: "POST", "GET", "PUT". Case does not matter
        :param data: Data to use in the request, parameters for get request, json for post

        :return: Returns the HTTP Response object from the request

        """
        """"""
        url = self.base_url + path
        logger.debug("Request (%s) (%s) %s" % (http_method.lower(), path, "with data" if data else "without data"))
        if http_method.lower() == 'get':
            response = requests.get(url, auth=self.auth, params=data)
        elif http_method.lower() == 'post':
            response = requests.post(url, auth=self.auth, json=data)
        elif http_method.lower() == 'put':
            response = requests.put(url, auth=self.auth, json=data)
        elif http_method.lower() == 'delete':
            response = requests.delete(url, auth=self.auth, params=data)
        else:
            raise EloquaInvalidUseageException("Invalid request type %s" % http_method)

        if response.status_code == 404:
            raise EloquaRequestErrorNotFound(response)
        elif response.status_code == 400:
            if not response.content:
                response._content = """    !!!! No Content in the Error response from Eloqua !!!!
    If you are creating custom object data, this could be due to a field having the wrong data type (date, number)
    Eloqua is bad at telling us what the error is here.
    
    Helpful hints:
        -Dates need to be an integer value of a timestamp. Try using int(datetime.datetime.timestamp(some_date)) 
    
    """
            raise EloquaRequestError(response)
        elif response.status_code > 300:
            raise EloquaRequestError(response)
        return response

    def generate_custom_object_code(self, custom_object_name=None, custom_object_id=None, class_name=None):
        """
        Generates the custom object class code given the name or id of the custom object and an optional class name

        :param custom_object_name: Name of the custom object to search for
        :param custom_object_id: Id of the custom object
        :param class_name: (optional) class name. Default will be the custom object name

        :return: code as a string for the custom object
        """
        if custom_object_id:
            custom_object = self.get(CustomObject, asset_id=custom_object_id)
        else:
            custom_objects_with_name = self.get_list(CustomObject, {
                "search": "name=%s" % custom_object_name,
                "depth":  "complete"
            })
            custom_object = custom_objects_with_name.data[0]

        code = self._generate_custom_object_class_code(custom_object.raw_data, class_name=class_name)
        return code

    @classmethod
    def _generate_custom_object_class_code(cls, eloqua_response, class_name=None):
        """
        Generates the custom object class code given a custom object and a class name
        :param eloqua_response: Json response from eloqua for the custom object
        :param class_name: (optional) class name

        :return: the code for a python class for the Custom Object
        """

        field_to_id_map = {}
        id_to_field_map = {}
        meta_fields = []
        for field in eloqua_response.keys():
            if field != "fields":
                meta_fields.append(field)
        for field in eloqua_response["fields"]:
            field_to_id_map[field["internalName"]] = field["id"]
            id_to_field_map[field["id"]] = field["internalName"]

        object_name = eloqua_response['name']
        if not class_name:
            class_name = object_name

        printable_fields_list = ""
        for field_name in field_to_id_map.keys():
            printable_fields_list += "\t%s = None\n" % field_name

        rstring = """class %s(%s):
\tCDO_NAME = "%s"
\tPARENT_ID = "%s"
\tFIELDS = %s
\tID_FIELD_MAP = %s
\tMETA_FIELDS = %s 
%s
    """ % (
            class_name, CustomObjectModel.__name__,
            object_name,
            eloqua_response['id'],
            "[%s]" % ", ".join('"%s"' % x for x in field_to_id_map.keys()),
            json.dumps(id_to_field_map),
            json.dumps(meta_fields),
            printable_fields_list)

        return rstring

    def get_custom_object_data(self, customObjectModel, record_id=None, query_params=None):
        """
        Fetches CDO records from eloqua provided a description of that data object. Can fetch 1 record if record id
        is provided.
        :param customObjectModel: CustomObjectModel for the object to be fetched (REQUIRED)
        :param record_id: single record id for single requests
        :param query_params: parameters included in a multi search request for example {"search" : "name=John", "count": 1}

        :return: The custom object data object or list of objects
        """
        if not issubclass(customObjectModel, CustomObjectModel):
            raise EloquaInvalidUseageException("eloqua_custom_data_object must be a subclass of CustomObjectModel")

        if record_id:
            if query_params:
                logger.warning("calling EloquaConnection.get_custom_object_data() with a record_id and query params "
                               "only returns the record with the record Id. IT DOES NOT USE THE QUERY PARAMS")
            resp = self.request(CUSTOM_OBJECT_DATA_GET_PATH.format(
                parent_id=customObjectModel.PARENT_ID, id=record_id), "GET")
            return customObjectModel(resp)
        else:
            resp = self.request(CUSTOM_OBJECT_DATA_GET_LIST_PATH.format(
                parent_id=customObjectModel.PARENT_ID), "GET", data=query_params)
            data = customObjectModel.from_list(resp)
            data_response = DataResponse(data=data, eloqua_response=resp)
            return data_response

    # ------------ API Methods ------------

    def get(self, objectClass, data_id, params={}):
        """
        Gets the object from eloqua using the objectClass as the type of object and the data id as the instance
        Includes the params in the request

        :param objectClass: An Asset class, CustomObjectModel etc
        :param data_id: Id string "501" for example
        :param params: (optional) additional parameters for the API request

        :return: An instance of the objectClass provided
        """

        if issubclass(objectClass, Asset):
            resp = self.request(objectClass.get_path.format(id=data_id), "GET", params)
        elif issubclass(objectClass, CustomObjectModel):
            params['depth'] = 'complete'
            resp = self.request(objectClass.get_path.format(parent_id=objectClass.PARENT_ID, id=data_id), "GET", params)
        else:
            raise EloquaInvalidUseageException("%s is not a valid class to use with this method" % objectClass)

        return objectClass(resp)

    def get_list(self, objectClass, params=None):
        """
        Gets a list of Assets using the provided parameters for the API request

        :param objectClass: An Asset class, CustomObjectModel etc
        :param params: (optional) additional parameters for the API request

        :return: A DataResponse object
        """

        if issubclass(objectClass, Asset):
            resp = self.request(objectClass.get_list_path, "GET", params)
        elif issubclass(objectClass, CustomObjectModel):
            resp = self.request(objectClass.get_list_path.format(parent_id=objectClass.PARENT_ID), "GET", params)
        else:
            raise EloquaInvalidUseageException("%s is not a valid class to use with this method" % objectClass)

        data = objectClass.from_list(resp)
        return DataResponse(data=data, eloqua_response=resp)

    def update(self, eloqua_object):
        """
        Updates an eloqua object

        :param eloqua_object: An instance of an Asset class or data object

        :return: Returns the response from eloqua
        """
        if isinstance(eloqua_object, Asset):
            resp = self.request(eloqua_object.update_path.format(id=eloqua_object.id), "PUT",
                                data=eloqua_object.to_update_json())
        elif isinstance(eloqua_object, CustomObjectModel):
            resp = self.request(
                eloqua_object.update_path.format(parent_id=eloqua_object.PARENT_ID, id=eloqua_object.id), "PUT",
                data=eloqua_object.to_update_json())
        else:
            raise EloquaInvalidUseageException("%s is not a valid class to use with this method" %
                                               eloqua_object.__class__)

        return resp

    def delete(self, eloqua_object):
        """
        Deletes an eloqua object

        :param eloqua_object: An instance of an Asset class

        :return: Returns the response from eloqua
        """
        if isinstance(eloqua_object, Asset):
            resp = self.request(eloqua_object.delete_path.format(id=eloqua_object.id), "DELETE")
        elif isinstance(eloqua_object, CustomObjectModel):
            resp = self.request(eloqua_object.delete_path.format(parent_id=eloqua_object.PARENT_ID,
                                                                 id=eloqua_object.id), "DELETE")
        return resp

    def create(self, eloqua_object):
        """
        Creates an eloqua object

        :param eloqua_object: An instance of an Eloqua Object like CustomObjectModel or Asset etc

        :return: Returns the response from eloqua
        """
        if isinstance(eloqua_object, Asset):
            resp = self.request(eloqua_object.create_path, "POST", eloqua_object.to_create_json())
        elif isinstance(eloqua_object, CustomObjectModel):
            path = eloqua_object.create_path.format(parent_id=eloqua_object.PARENT_ID)
            data = eloqua_object.to_create_json()
            resp = self.request(path, "POST", data)

        return eloqua_object.__class__(resp.json())
