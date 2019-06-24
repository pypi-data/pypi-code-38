from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from threading import Thread


class BaobabBigQuery(Thread):
    def __init__(self, request, project, api_key_path):
        """Object Configuration"""
        Thread.__init__(self)
        self._data = None
        """Client Configuration"""
        scopes = ('https://www.googleapis.com/auth/bigquery',
                  'https://www.googleapis.com/auth/drive',
                  "https://www.googleapis.com/auth/spreadsheets.readonly")

        credentials = Credentials.from_service_account_file(
            api_key_path, scopes=scopes)

        self._client = bigquery.Client(
            credentials=credentials, project=project)

        self._job_config = bigquery.QueryJobConfig()
        self._job_config.use_legacy_sql = False
        self._job_config.allow_large_results = True
        """BigQuery Connection"""
        self._query_job = self._client.query(request)  # API request

        if self._query_job.errors:
            raise RuntimeError(self._query_job.errors)

    def run(self):

        self._data = self._query_job.to_dataframe()

    @property
    def data(self):
        return self._data
