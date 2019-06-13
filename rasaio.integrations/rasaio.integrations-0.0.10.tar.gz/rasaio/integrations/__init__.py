import abc, json, pytz
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from enum import Enum
from requests import delete, get, post, put

from .constants import * # pylint: disable=W0614
from .utilties.helper import *

class SyncDirection:
  TO_RASA = "to_rasa"
  FROM_RASA = "from_rasa"
  BOTH = "both"

class SyncType:
  INCREMENTAL = "incremental" # changes since last run date
  FULL = "full" # all changes irrespective of last run

class MessageType:
  INFO = "info"
  WARNING = "warning"
  ERROR = "error"

@dataclass_json
@dataclass
class RasaApiAttributes:
  username: str
  password: str
  key: str
  last_run_date: datetime # utc
  identity_community_guid: int
  import_type: str = CSV_IMPORT
  sync_on_fieldname: str = IS_SUBSCRIBED # choose from is_active or is_subscribed
  base_url: str = "https://api.rasa.io/v1"
  sync_direction: SyncDirection = SyncDirection.BOTH
  sync_type: SyncType = SyncType.INCREMENTAL

  limit: int = 5000
  keep_existing_members: bool = False
  is_person_attribute_supported: bool = False

@dataclass_json
@dataclass
class FieldMapping:
  email: str
  external_id: str = None # unique identifier field in customer database which doesn't change e.g. id
  first_name: str = None
  last_name: str = None
  is_active: str = None
  is_subscribed: str = None
  updated: str= None
  # exta fields can be supported by calling setattr on FieldMapping object

class IntegrationBase(abc.ABC):
  def __init__(self, rasa_api_attrs: RasaApiAttributes, field_mapping: FieldMapping, log_func):
    """
      rasa_api_attrs: rasa api attributes
      field_mapping: field mappings
      log_func: partial function with takes 2 parameter (message, message_type)
    """
    self.rasa_api_attrs = rasa_api_attrs
    self.log_func = log_func

    self.updated_since : datetime = None if self.rasa_api_attrs.sync_type == SyncType.FULL else self.rasa_api_attrs.last_run_date
    self.field_mapping_json = field_mapping.__dict__
    self.rasa_sync_on_fieldname = self.rasa_api_attrs.sync_on_fieldname
    self.customer_sync_on_fieldname = self.field_mapping_json[self.rasa_sync_on_fieldname]

    self.rasa_api_token = self.__get_rasa_api_token()
    self.rasa_active_persons = []
    self.rasa_inactive_persons = []
    self.__rasa_persons_by_email = {}
    self.__rasa_persons_by_external_id = {}
    self.rasa_all_persons = self.__get_rasa_persons()
    self.rasa_active_person_by_id = {}

  def log(self, message, message_type=MessageType.INFO):
    if self.log_func:
      self.log_func(message, message_type)
    else:
      print("{} | {} | {}".format(datetime.utcnow(), str(message_type), message))

  def get_rasa_api_tokens_endpoint(self):
    return "{}/tokens".format(self.rasa_api_attrs.base_url)

  def get_rasa_api_persons_endpoint(self):
    return "{}/persons".format(self.rasa_api_attrs.base_url)

  def get_rasa_api_person_endpoint(self, id):
    return  "{}/{}".format(self.get_rasa_api_persons_endpoint(), id)

  def get_auth_header(self):
    return (self.rasa_api_attrs.username, self.rasa_api_attrs.password)

  def __get_rasa_api_token(self):
    if self.rasa_api_attrs.key:
      body = {KEY: self.rasa_api_attrs.key}
    else:
      body = {
        COMMUNITY_ID : self.rasa_api_attrs.identity_community_guid,
        TYPE : self.rasa_api_attrs.import_type
      }
    response = post(self.get_rasa_api_tokens_endpoint(),
      auth=self.get_auth_header(),
      data=json.dumps(body))
    if (response.status_code != 201):
      raise Exception('Error generating token: {}'.format(response.status_code))
    rasa_token = response.json()['results'][0][RASA_TOKEN]
    self.log("Token created. rasa-token = {}".format(rasa_token))
    return rasa_token

  def __delete_rasa_api_token(self):
    response = delete("{}/{}".format(self.get_rasa_api_tokens_endpoint(), self.rasa_api_token), auth=self.get_auth_header())
    if (response.status_code != 204):
      self.log('Error deleting token: {}'.format(response.status_code))
    else:
      self.log("Token deleted. rasa-token = {}, ".format(self.rasa_api_token))

  def sync(self):
    """
      this method syncs the data based on configuration provided to the class
    """
    try:
      self.log("sync_direction = {}".format(self.rasa_api_attrs.sync_direction))
      self.execute_pre_sync_process()

      if self.rasa_api_attrs.sync_direction == SyncDirection.TO_RASA:
        self.sync_persons_to_rasa()
        if self.get_customer_active_persons() and not self.rasa_api_attrs.keep_existing_members:
          self.__unsubscribe_rasa_persons_for_oneway_sync()
      elif self.rasa_api_attrs.sync_direction == SyncDirection.FROM_RASA:
        self.sync_persons_from_rasa()
      elif self.rasa_api_attrs.sync_direction == SyncDirection.BOTH:
        self.log("****************************************************** SYNC TO RASA ******************************************************")
        self.sync_persons_to_rasa()
        self.log("****************************************************** SYNC FROM RASA ******************************************************")
        self.sync_persons_from_rasa()

      self.execute_post_sync_process()
    finally:
      self.__delete_rasa_api_token()

  def sync_persons_to_rasa(self):
    self.__create_or_update_persons_in_rasa()
    self.__unsubscribe_customers_inactive_persons_in_rasa()

  def __get_rasa_person_with_attributes(self, id):
    headers = {RASA_TOKEN: self.rasa_api_token}
    endpoint = self.get_rasa_api_person_endpoint(id)
    response = get("{}".format(endpoint), headers=headers)
    rasa_person = None
    if response.status_code == 200:
      results = response.json()[RESULTS]
      rasa_person = results[0].get(DATA)
    elif response.status_code == 404:
      pass # not found
    else:
      # something went wrong
      self.log("Failed to get person record with attributes. id = {}. Error = {}".format(id, self.get_rasa_response_error(response)), True)
    return rasa_person

  def __get_rasa_person_by_mapped_person(self, mapped_person):
    """
      1. search rasa person by external_id (if provided).
      2. if not found, search by email
    """
    external_id = mapped_person.get(EXTERNAL_ID)
    rasa_person = None
    if external_id:
      rasa_person = self.__rasa_persons_by_external_id.get(external_id)
    if not rasa_person and mapped_person.get(EMAIL):
      # couldn't find a person by external_id. let it search by email.
      rasa_person = self.__rasa_persons_by_email.get(mapped_person[EMAIL].lower())
    if rasa_person and self.rasa_api_attrs.is_person_attribute_supported:
      # need to get rasa_person with attribute
      rasa_person = self.__get_rasa_person_with_attributes(rasa_person.id)
    if rasa_person:
      rasa_person[UPDATED] = parse_date_from(rasa_person[UPDATED])
    return rasa_person

  def __get_rasa_persons(self):
    all_persons = []
    headers = {RASA_TOKEN: self.rasa_api_token}
    endpoint = self.get_rasa_api_persons_endpoint()
    params = {"skip" : 0, "limit": self.rasa_api_attrs.limit}
    if self.updated_since:
      params["updated_since"] = self.updated_since.strftime(RASA_DATETIME_FORMAT)
    response = get(endpoint, headers=headers, params=params)
    for result in response.json()[RESULTS]:
      all_persons.append(result.get(DATA))
    record_count = self.get_rasa_response_metadata(response).get("record_count") or 0
    while record_count > 0:
      self.log("Rasa persons found so far = {}".format(len(all_persons)))
      params["skip"] = params["skip"] + record_count
      response = get(endpoint, headers=headers, params=params)
      for result in response.json()[RESULTS]:
        all_persons.append(result.get(DATA))
      record_count = self.get_rasa_response_metadata(response).get("record_count") or 0

    for rasa_person in all_persons:
      self.__rasa_persons_by_email[rasa_person[EMAIL].lower()] = rasa_person
      if rasa_person.get(EXTERNAL_ID):
        self.__rasa_persons_by_external_id[rasa_person[EXTERNAL_ID]] = rasa_person

      if rasa_person[self.rasa_sync_on_fieldname]:
        self.rasa_active_persons.append(rasa_person)
      else:
        self.rasa_inactive_persons.append(rasa_person)

    self.log("Rasa persons found ({} = True) = {}".format(self.rasa_sync_on_fieldname, len(self.rasa_active_persons)))
    self.log("Rasa persons found ({} = False) = {}".format(self.rasa_sync_on_fieldname, len(self.rasa_inactive_persons)))
    return all_persons

  def __create_or_update_persons_in_rasa(self):
    mapped_persons = self.map_customer_persons_to_rasa_persons(self.get_customer_active_persons())
    for mapped_person in mapped_persons:
      rasa_person = self.__get_rasa_person_by_mapped_person(mapped_person)
      if not rasa_person:
        self.log("Creating person record in rasa for '{}'".format(mapped_person[EMAIL]))
        if mapped_person.get(self.rasa_sync_on_fieldname) is None:
          mapped_person[self.rasa_sync_on_fieldname] = True
        headers = {RASA_TOKEN: self.rasa_api_token}
        response = post(self.get_rasa_api_persons_endpoint(), headers=headers,
          data=json.dumps(self.__sanitize_mapped_rasa_person(mapped_person)))
        if response.status_code not in(200, 201):
          self.log("Failed to create persons record = {}. Error = {}".format(mapped_person,self.get_rasa_response_error(response)))
        else:
          self.rasa_active_person_by_id[self.__get_rasa_id_from_create_response(response)] = mapped_person
      else:
        self.rasa_active_person_by_id[rasa_person[ID]] = mapped_person
        # if customer hasn't sent updated info then assume it is new. Or if customer updated > rasa updated
        if mapped_person.get(UPDATED) is None or mapped_person[UPDATED] > rasa_person[UPDATED]:
          changes = self.__get_customer_person_changes(mapped_person, rasa_person)
          if changes:
            self.log("Updating person record in rasa for '{}'. Changes = {}".format(mapped_person[EMAIL], changes))
            headers = {RASA_TOKEN: self.rasa_api_token}
            endpoint = self.get_rasa_api_persons_endpoint() + "/" + rasa_person[ID]
            response = put(endpoint, headers=headers, data=json.dumps(changes))
            if response.status_code != 200:
              self.log("Failed to update persons record = {}. Error = {}".format(rasa_person[ID], self.get_rasa_response_error(response)))
          else:
            self.log("No change found for person record - id = {}, email = {}".format(rasa_person[ID], rasa_person[EMAIL]))
        else:
          self.log("Ignoring person record update in rasa. Rasa record is more recent - id = {}, email = {}".format(rasa_person[ID], rasa_person[EMAIL]))

  def __get_customer_person_changes(self, mapped_person, rasa_person):
    result = {}
    mapped_person = self.__sanitize_mapped_rasa_person(mapped_person)
    for k, v in mapped_person.items():
      if is_different(k, v, rasa_person.get(k)):
        result[k] = v
    return result

  def __sanitize_mapped_rasa_person(self, mapped_person):
    mapped_person.pop("updated", None)
    return mapped_person

  def __unsubscribe_customers_inactive_persons_in_rasa(self):
    mapped_persons = self.map_customer_persons_to_rasa_persons(self.get_customer_inactive_persons())
    if mapped_persons:
      for mapped_person in mapped_persons:
        rasa_person = self.__get_rasa_person_by_mapped_person(mapped_person)
        if rasa_person and rasa_person[self.rasa_sync_on_fieldname]:
          if mapped_person.get(UPDATED) is None or mapped_person[UPDATED] > rasa_person[UPDATED]:
            self.__unsubscribe_rasa_person(rasa_person)

  def __unsubscribe_rasa_person(self, rasa_person):
    self.log("Unsubscribing person record in rasa with id = '{}', email = '{}'".format(rasa_person[ID], rasa_person[EMAIL]))
    headers = {RASA_TOKEN: self.rasa_api_token}
    endpoint = self.get_rasa_api_person_endpoint(rasa_person[ID])
    response = put(endpoint, headers=headers, data=json.dumps({self.rasa_sync_on_fieldname:0}))
    if response.status_code != 200:
      self.log("Failed to unsubscribe rasa person record. id = {}. Error = {}".format(rasa_person[ID], self.get_rasa_response_error(response)))

  def __unsubscribe_rasa_persons_for_oneway_sync(self):
    for rasa_person in self.rasa_active_persons:
      if not self.rasa_active_person_by_id.get(rasa_person[ID]):
        self.__unsubscribe_rasa_person(rasa_person)

  def map_customer_persons_to_rasa_persons(self, customer_persons):
    mapped_persons = []
    for customer_person in customer_persons:
      mapped_person = {k : customer_person[v] for k, v in self.field_mapping_json.items() if v and customer_person.get(v) is not None}
      if mapped_person.get(UPDATED):
        mapped_person[UPDATED] = parse_date_from(mapped_person[UPDATED])
      mapped_persons.append(mapped_person)
    return mapped_persons

  def map_rasa_persons_to_customer_persons(self, rasa_persons):
    mapped_persons = []
    for rasa_person in rasa_persons:
      if self.rasa_api_attrs.is_person_attribute_supported:
        rasa_person = self.__get_rasa_person_with_attributes(rasa_person[ID])
        if not rasa_person:
          continue

      mapped_person = {v : rasa_person[k] for k, v in self.field_mapping_json.items() if v and rasa_person.get(k) is not None}
      if self.field_mapping_json.get(UPDATED) and mapped_person.get(self.field_mapping_json[UPDATED]):
        mapped_person[self.field_mapping_json[UPDATED]] = parse_date_from(mapped_person[self.field_mapping_json[UPDATED]])
      mapped_persons.append(mapped_person)

    return mapped_persons

  def __get_rasa_id_from_create_response(self, response):
    results = response.json()[RESULTS]
    return results[0].get(ID)

  def get_rasa_response_metadata(self, response):
    try:
      return response.json()["metadata"]
    except:
      return {}

  def get_rasa_response_error(self, response):
    try:
      return response.json()['metadata']["errors"]
    except:
      return "Error response not found"

  @abc.abstractmethod
  def get_customer_active_persons(self):
    pass # should retuns array

  @abc.abstractmethod
  def get_customer_inactive_persons(self):
    pass # should retuns array

  @abc.abstractmethod
  def sync_persons_from_rasa(self):
    pass

  @abc.abstractmethod
  def execute_pre_sync_process(self):
    pass

  @abc.abstractmethod
  def execute_post_sync_process(self):
    pass