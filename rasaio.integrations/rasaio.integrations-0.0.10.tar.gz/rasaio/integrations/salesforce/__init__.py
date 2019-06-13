import json, traceback
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from .. import *
from ..utilties.helper import *
from .salesforce import RasaSalesforce, SFApiAttributes

SALESFORCE_ID = "Id"
# TODO use mapped field
SALESFORCE_FIRSTNAME = "FirstName"
SALESFORCE_LASTNAME = "LastName"
SALESFORCE_EMAIL = "Email"
SALESFORCE_DATE_UPDATED = "LastModifiedDate"

class SalesforceIntegration(IntegrationBase):
  def __init__(self, rasa_api_attrs: RasaApiAttributes, sf_api_attrs: SFApiAttributes, field_mapping: FieldMapping, log_func= None):
    super(__class__, self).__init__(rasa_api_attrs, field_mapping, log_func)
    self.sf_api_attrs : SFApiAttributes = sf_api_attrs
    self.rasa_salesforce = RasaSalesforce(sf_api_attrs, self.customer_sync_on_fieldname)
    self.__populate_initial_data()

  def __populate_initial_data(self):
    self.__active_persons = self.rasa_salesforce.get_active_persons(self.updated_since)
    self.log("Customer persons found (subscribed) = {}".format(len(self.__active_persons)))
    self.__inactive_persons = self.rasa_salesforce.get_inactive_persons(self.updated_since)
    self.log("Customer persons found (unsubscribed) = {}".format(len(self.__inactive_persons)))

  def get_customer_active_persons(self):
    return self.__active_persons

  def get_customer_inactive_persons(self):
    # overridden method
    return self.__inactive_persons

  def sync_persons_from_rasa(self):
    self.__create_or_update_rasa_active_persons()
    self.__unsubscribe_rasa_inactive_persons()

  def __create_or_update_rasa_active_persons(self):
    mapped_persons = self.map_rasa_persons_to_customer_persons(self.rasa_active_persons)
    for mapped_person in mapped_persons:
      mapped_person[self.customer_sync_on_fieldname] = "true"
      sf_person = None
      if mapped_person.get(SALESFORCE_ID):
        sf_person = self.rasa_salesforce.get_person_by_id(mapped_person[SALESFORCE_ID])
      else:
        sf_person = self.rasa_salesforce.get_person_by_email(mapped_person[SALESFORCE_EMAIL])
      try:
        if not sf_person:
          if mapped_person.get(SALESFORCE_FIRSTNAME) and mapped_person.get(SALESFORCE_LASTNAME):
            self.log("Creating person record in salesforcce for '{}'".format(mapped_person[SALESFORCE_EMAIL]))
            self.rasa_salesforce.create_person(self.__sanitize_mapped_person(mapped_person))
          else:
            self.log("Skipping person create in Salesforce for '{}'. FirstName/LastName missing.".format(mapped_person[SALESFORCE_EMAIL]))
        else:
          if mapped_person[SALESFORCE_DATE_UPDATED] > parse_date_from(sf_person[SALESFORCE_DATE_UPDATED]):
            changes = self.__get_rasa_person_changes(mapped_person, sf_person)
            if changes:
              self.log("Updating person record in Salesforce for '{}'. Changes = {}".format(mapped_person[SALESFORCE_EMAIL], changes))
              self.rasa_salesforce.update_person(sf_person[SALESFORCE_ID], changes)
            else:
              self.log("No change found for person record - id = {}, email = {}".format(sf_person[SALESFORCE_ID], sf_person[SALESFORCE_EMAIL]))
          else:
            self.log("Ignoring person record update in Salesforce. Salesforce record is more recent - id = {}, email = {}".format(sf_person[SALESFORCE_ID], sf_person[SALESFORCE_EMAIL]))
      except Exception as ex:
        # log this and continue for next record
        traceback.print_exc()
        self.log("Failed to add/update person in Salesforce for {}. Error = {}".format(mapped_person[SALESFORCE_EMAIL], ex), MessageType.ERROR)

  def __get_rasa_person_changes(self, mapped_person, sf_person):
    result = {}
    mapped_person = self.__sanitize_mapped_person(mapped_person)
    for k, v in mapped_person.items():
      if is_different(k, v, sf_person.get(k)):
        result[k] = v
    return result

  def __unsubscribe_rasa_inactive_persons(self):
    mapped_persons = self.map_rasa_persons_to_customer_persons(self.rasa_inactive_persons)
    for mapped_person in mapped_persons:
      sf_person = None
      if mapped_person.get(SALESFORCE_ID):
        sf_person = self.rasa_salesforce.get_person_by_id(mapped_person[SALESFORCE_ID])
      else:
        sf_person = self.rasa_salesforce.get_person_by_email(mapped_person[SALESFORCE_EMAIL])
      if sf_person and not sf_person[self.customer_sync_on_fieldname] \
          and (not mapped_person[SALESFORCE_DATE_UPDATED] or mapped_person[SALESFORCE_DATE_UPDATED] > parse_date_from(sf_person[SALESFORCE_DATE_UPDATED])):
        self.log("Unsubscribing person record in Salesforce for '{}'".format(sf_person[SALESFORCE_EMAIL]))
        self.rasa_salesforce.update_person(sf_person[SALESFORCE_ID], {self.customer_sync_on_fieldname: False})
      else:
        self.log("Either record doesn't exist in Salesforce or already unsubscribed or more recent. Email = {}".format(mapped_person[SALESFORCE_EMAIL]))

  def __sanitize_mapped_person(self, mapped_person):
    mapped_person.pop("LastModifiedDate", None)
    return mapped_person

  def execute_pre_sync_process(self):
    pass

  def execute_post_sync_process(self):
    pass
