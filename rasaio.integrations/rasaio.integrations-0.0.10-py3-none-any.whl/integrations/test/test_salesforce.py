import os, sys, traceback, unittest
from datetime import datetime, timedelta
from rasaio.integrations import * # pylint: disable=W0614
from rasaio.integrations.salesforce import SalesforceIntegration, SFApiAttributes

class TestSalesforce(unittest.TestCase):
  rasa_api_attrs = RasaApiAttributes(
    username = os.environ.get("rasa_username"),
    password = os.environ.get("rasa_password"),
    key = os.environ.get("rasa_key"),
    base_url = "https://api-dev.rasa.io/v1",
    last_run_date =  (datetime.utcnow() - timedelta(days=1))
  )

  field_mapping = FieldMapping(
    email = "Email",
    external_id = "Id",
    first_name = "FirstName",
    last_name = "LastName",
    updated = "LastModifiedDate",
    is_subscribed = "RasaSubscribed__c"
  )

  sf_api_attrs = SFApiAttributes(
    username=os.environ.get("salesfoce_username"),
    password=os.environ.get("salesfoce_password"),
    security_token=os.environ.get("salesfoce_security_token")
  )

  def test_get_persons(self):
    try:
      sf = SalesforceIntegration(self.rasa_api_attrs, self.sf_api_attrs, self.field_mapping)
      sf.sync()
      self.assertTrue(True)
    except Exception:
      traceback.print_exc()
      self.assertTrue(False)


if __name__ == '__main__':
  unittest.main()