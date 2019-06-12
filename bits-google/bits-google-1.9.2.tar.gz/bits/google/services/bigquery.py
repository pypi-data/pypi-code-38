"""Google BigQuery API."""

from bits.google.services.base import Base
from google.cloud import bigquery
from googleapiclient.discovery import build


class BigQuery(Base):
    """Directory class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.bigquery = bigquery
        self.bq = build('bigquery', 'v2', credentials=credentials)

    def create_table(self, project, dataset, body):
        """Create a BigQuery table."""
        params = {
            'projectId': project,
            'datasetId': dataset,
            'body': body,
        }
        return self.bq.tables().insert(**params).execute()

    def delete_table(self, project, dataset, table):
        """Create a BigQuery table."""
        params = {
            'projectId': project,
            'datasetId': dataset,
            'tableid': table,
        }
        return self.bq.tables().delete(**params).execute()

    def get_dataset(self, project, dataset):
        """Return a BigQuery dataset."""
        params = {
            'projectId': project,
            'datasetId': dataset,
        }
        return self.bq.datasets().get(**params).execute()

    def get_datasets(self, project):
        """Return list of BigQuery datasets."""
        datasets = self.bq.datasets()
        request = datasets.list(projectId=project)
        return self.get_list_items(datasets, request, 'datasets')

    def get_projects(self):
        """Return list of BigQuery projects."""
        projects = self.bq.projects()
        request = projects.list(maxResults=10)
        return self.get_list_items(projects, request, 'projects')

    def get_tabledata(
            self,
            project,
            dataset,
            table,
            maxResults=None,
            startIndex=None
    ):
        """Return list of BigQuery tabledata."""
        params = {
            'projectId': project,
            'datasetId': dataset,
            'tableId': table,
            'maxresults': maxResults,
            'startIndex': startIndex,
        }
        return self.bq.tabledata().list(**params).execute().get('rows', [])

    def get_table(self, project, dataset, table):
        """Return a BigQuery table."""
        params = {
            'projectId': project,
            'datasetId': dataset,
            'tableId': table,
        }
        return self.bq.tables().get(**params).execute()

    def get_tables(self, project, dataset):
        """Return list of BigQuery tables."""
        params = {
            'projectId': project,
            'datasetId': dataset,
        }
        tables = self.bq.tables()
        request = tables.list(**params)
        return self.get_list_items(tables, request, 'tables')

    def query_job(self, project, query):
        """Return results of a BigQuery query job."""
        params = {
            'projectId': project,
            'body': {
                'query': query,
                'useLegacySql': False,
            },

        }
        return self.bq.jobs().query(**params).execute().get('rows', [])

    def insert_job(self, project, body, media_body, media_mime_type):
        """Insert BigQuery job."""
        params = {
            'projectId': project,
            'body': body,
            'media_body': media_body,
            'media_mime_type': media_mime_type,
        }
        return self.bq.jobs().insert(**params).execute()

    def insert_tabledata(self, project, dataset, table, data):
        """Insert BigQuery tabledata."""
        params = {
            'projectId': project,
            'datasetId': dataset,
            'tableId': table,
            'body': data,
        }
        return self.bq.tabledata().insertAll(**params).execute()
