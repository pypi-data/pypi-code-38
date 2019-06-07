from google.cloud import bigquery
from google.oauth2 import service_account
import os

def check_date(date, filename, project_id, platform): 
    count = 0;
    full_path = os.path.abspath(filename)
    credentials = service_account.Credentials.from_service_account_file(full_path)
    bigquery_client = bigquery.Client(credentials= credentials,project=project_id)

    query_job = bigquery_client.query(""" SELECT * FROM `{}.app_annie.product_sales` WHERE platform = "{}" and date = "{} 00:00:00 UTC" """.format(project_id, platform, date))

    results = query_job.result()  # Waits for job to complete.

    for i in results:
        count+=1
    return count

# a=check_date("2019-04-20", "credential.json", 'ga360-173318')
# print(a)