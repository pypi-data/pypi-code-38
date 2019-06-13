import json, pytz
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from simple_salesforce import Salesforce

SF_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
SF_CONTACTS_SUPPORTED_FIELDS = " Id, AccountId, FirstName, LastName, Email, Title, Name, Description, Phone, PhotoUrl, LastModifiedDate "


@dataclass_json
@dataclass
class SFApiAttributes:
  username: str
  password: str
  security_token: str
  sync_filter_field: str = None # a boolean field to filter a set of record to participate in sync

class RasaSalesforce:
  def __init__(self, sf_api_attrs:SFApiAttributes, customer_sync_on_fieldname):
    self.__instance = Salesforce(username=sf_api_attrs.username, password=sf_api_attrs.password, security_token=sf_api_attrs.security_token)
    self.customer_sync_on_fieldname = customer_sync_on_fieldname
    self.sync_filter_field = sf_api_attrs.sync_filter_field

  def get_person_by_id(self, id):
    try:
      query = "SELECT {}, {} FROM Contact WHERE id='{}' ORDER BY CreatedDate ASC LIMIT 1".format(
        SF_CONTACTS_SUPPORTED_FIELDS,
        self.customer_sync_on_fieldname,
        id
      )
      return self.__get_one_record(query)
    except Exception:
      return None


  def get_person_by_email(self, email):
    query = "SELECT {}, {} FROM Contact WHERE Email='{}' ORDER BY CreatedDate ASC LIMIT 1".format(
        SF_CONTACTS_SUPPORTED_FIELDS,
        self.customer_sync_on_fieldname,
        email
      )
    return self.__get_one_record(query)

  def __get_persons(self, active, last_modified=None):
    last_modified = self.convert_date_to_salesforce_format(last_modified)
    query = "SELECT {}, {} FROM Contact WHERE Email!='' AND {}={} AND LastModifiedDate > {} ".format(
        SF_CONTACTS_SUPPORTED_FIELDS,
        self.customer_sync_on_fieldname,
        self.customer_sync_on_fieldname,
        active,
        last_modified
      )
    if self.sync_filter_field:
      query += " AND {}=true ".format(self.sync_filter_field)

    query += " ORDER BY CreatedDate ASC"
    r =  self.__get_all_records(query)
    return r

  def get_active_persons(self, last_modified=None):
    return self.__get_persons("true", last_modified)

  def get_inactive_persons(self, last_modified=None):
    return self.__get_persons("false", last_modified)

  def create_person(self, data):
    return self.__instance.Contact.create(data)

  def update_person(self, record_id, data):
    return self.__instance.Contact.update(record_id, data)

  def delete_person(self, record_id):
    return self.__instance.Contact.delete(record_id)

  def convert_date_to_salesforce_format(self, input_date):
    if not input_date:
      input_date = datetime.strptime("1900-01-01T00:00:00.000+0000", SF_DATETIME_FORMAT)
    if input_date.tzinfo is not None and input_date.tzinfo.utcoffset(input_date) is not None:
      return input_date.isoformat() # this is timezone aware
    else:
      return input_date.replace(tzinfo=pytz.UTC).isoformat() # naive datetime

  def __get_one_record(self, query, include_deleted=False):
    response = self.__instance.query(query, include_deleted=include_deleted)
    if response.get("done"):
      records = response.get("records")
      if records:
        record = records[0]
        return {k : record[k] for k in record if k != 'attributes'}
      else:
        return None
    else:
      raise Exception("Something went wrong while fetching one record from salesforce. Query = {}".format(query))

  def __get_all_records(self, query, include_deleted=False):
    batch_size = 50
    page_number = 0
    all_records = []
    while True:
      response = self.__instance.query("{} limit {} offset {}".format(query, batch_size, page_number * batch_size),
        include_deleted=include_deleted)
      if response.get("done"):
        records = response.get("records")
        for record in records:
          all_records.append({k : record[k] for k in record if k != 'attributes'})
        page_number += 1
        if len(records) < batch_size:
          return all_records
      else:
        raise Exception("Something went wrong while fetching records from salesforce. Query = {}".format(query))
    return all_records
