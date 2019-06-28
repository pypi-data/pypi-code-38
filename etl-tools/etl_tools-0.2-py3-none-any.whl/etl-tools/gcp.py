from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd
from math import ceil
from google.cloud import bigquery

import logging
logger = logging.getLogger('etl')

BQ_INSERT_BATCH_SIZE = 100000

class Storage:
    def __init__(self):
        pass

    def read_csv(self, filename):
        """Reads GCS, returns pandas DataFrame."""
        logger.info('Reading CSV file from GCS, filename: {}'.format(filename))
        try:
            result = pd.read_csv(filename)
            logger.info('Successfully read from GSS')
            logger.debug('No. rows: {}'.format(result.shape[0]))
            logger.debug('No. columns: {}'.format(result.shape[1]))
            return result
        except Exception as e:
            logger.error('Error while reading from GCS: {}'.format(e))  


class BigQuery:
    def __init__(self):
        pass

    def client(self):
        logger.info('Creating BQ clinet')
        bigquery_client = bigquery.Client()
        return bigquery_client

    def read_bigquery(self, bigquery_client, table, query):
        logger.debug('Reading from BQ table: {}'.format(table))
        result = bigquery_client.query(query).to_dataframe()
        logger.debug('No. records read: {}'.format(result.shape[0]))
        return result
        
    def write_bigquery(
        self, bigquery_client, project_id, dataset_id, table_name, df):
        def _write_single_batch(bigquery_client, df, table):
            # Convert DataFrame to list of dictionaries.
            rows_to_insert = df.to_dict('records')      
            # Insert rows to BQ.
            errors = bigquery_client.insert_rows(table, rows_to_insert)
            assert errors == []
            logger.info('Writing to BQ successful')

        full_table_name = (project_id + '.' + dataset_id + '.' + table_name)
        logger.info('Writing {0} records to BigQuery table `{1}`'.format(
            df.shape[0], full_table_name))
        # Prepare references.
        dataset_ref = bigquery_client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_name)
        table = bigquery_client.get_table(table_ref)
        df = df.where(pd.notnull(df), None)  # Replace "np.NaN" with "None".
        df.reset_index(drop=True, inplace=True)  # Reset index
        # Iterate over batches if needed.
        if df.shape[0] >= BQ_INSERT_BATCH_SIZE:
            logger.info(
                'Too large dataset. Will be splitted to smaller batches')
            no_records = df.shape[0]
            no_splits = ceil(no_records / BQ_INSERT_BATCH_SIZE)
            filter_from = 0
            for i in range(no_splits):
                logger.info('Processing batch number: {}'.format(i + 1))
                filter_to = filter_from + BQ_INSERT_BATCH_SIZE - 1
                logger.debug('Index from: {}'.format(filter_from))
                logger.debug('Index to: {}'.format(filter_to))
                df_tmp = df.loc[filter_from:filter_to]
                _write_single_batch(bigquery_client, df_tmp, table)
                filter_from = filter_to + 1
        else:
            _write_single_batch(bigquery_client, df, table)
