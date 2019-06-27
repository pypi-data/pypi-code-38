# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import logging


try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import boto3
except ImportError:
    boto3 = None

logger = logging.getLogger("dativa.tools.pandas.dynamodb")


class DynamoDB:
    """
    Wrapper for AWS DynamoDB which transfers pandas DataFrames to and from the service. It also creates and deletes
    tables.
    """

    def __init__(self,
                 table_name, hashname, rangename=None,
                 region='us-west-2', ddb_client=None, ddb_resource=None,
                 table=None, waiter_config=None):
        """

        :param table_name: table name for DynamoDB table
        :param hashname: name for column to be used as a DynamoDB table attribute - must consist of unique entries,
        :param region:  region for DynamoDB
        unless a range is specified. All entries must be valid.
        :param rangename: name of column to be used as a DynamoDB table attribute - allows duplicate entries in hash
        col, but requires unique pairs of hash and range values. All entries must be valid.
        :param ddb_client: incase you wish to pass through a ddb client with a specific configuration
        :param ddb_resource: incase you wish to pass through a ddb resource with a specific configuration
        :param table: pass a boto3.client("dynamodb").Table() object here to use that for the operations
        :param waiter_config: if you want to wait for different amounts of time, the option is present
        """
        if not boto3:
            raise ImportError("boto3 must be installed to run DynamoDB")

        if not pd:
            raise ImportError("pandas must be installed to run DynamoDB")

        logger.info("Initiailsing DynamoDB client with following region {}".format(region))
        self._ddb_client = ddb_client if ddb_client else boto3.client("dynamodb", region_name=region)
        self._ddb_resource = ddb_resource if ddb_resource else boto3.resource("dynamodb", region_name=region)

        self._hashname = hashname
        self._rangename = rangename
        msg ="Table creation will use columns for attributes hash {}".format(
            self._hashname) + " and range {}".format(self._rangename) if self._rangename else ""
        columns = [hashname, rangename] if rangename else [hashname]
        logger.debug(msg)

        self._columns_to_check = columns
        self._table_name = table_name
        self._waiter_config = waiter_config if waiter_config else {'Delay': 2, 'MaxAttempts': 120}
        if table:
            logger.info("Table pass through detected, using table present")
            self._table_obj = table
        else:
            logger.info("Table being created with desired name {} in region {}".format(
                self._table_name, region))
            # logger.debug("Hashing column is {}".format(self._hashname)
            #              + ", range column is {}".format(self._rangename) if self._rangename else "")
            attribute_definitions = [
                {"AttributeName": col, "AttributeType": "S"} for col in columns]

            key_schema = [{"AttributeName": hashname, "KeyType": "HASH"}]
            if rangename:
                key_schema.append({"AttributeName": rangename, "KeyType": "RANGE"})
            logger.debug("Intended table has the following attributes {}".format(attribute_definitions))
            logger.debug("Intended table has the following schema {} ".format(key_schema))
            try:
                logger.info("Creating table with name {}".format(self._table_name))
                self._table_obj = self._ddb_resource.create_table(
                    AttributeDefinitions=attribute_definitions,
                    TableName=self._table_name,
                    KeySchema=key_schema,
                    BillingMode="PAY_PER_REQUEST"
                )
                waiter = self._ddb_client.get_waiter('table_exists')
                waiter.wait(TableName=self._table_name, WaiterConfig=self._waiter_config)
                logger.info("Table created {}".format(self._table_name))
            except self._ddb_client.exceptions.ResourceInUseException:
                logger.info("Table {} found in {}, hence using created object".format(self._table_name, region))
                self._table_obj = self._ddb_resource.Table(self._table_name)
        self._table_name = self._table_obj.name

    def load_df(self, max_entries=100, consistent_read=True):
        """
        Read a DataFrame from DynamoDB, guaranteed to work if all entries are stored as str (unsure of other cases)
        paginated to ensure it picks up the entire DataFrame
        :param max_entries: maximum number of entries which should be read in a single go
        :param consistent_read: read from DynamoDB with strong consistent read (True) or eventual consistency (False)
        :return: DataFrame
        """
        config = dict(Limit=max_entries, ConsistentRead=consistent_read)
        logger.info("Reading from DynamoDB table {}".format(self._table_name))
        logger.debug(
            "Reading with following parameters {}, with the following attributes {}".format(
                config, self._table_obj.attribute_definitions))
        response = self._table_obj.scan(**config)
        list_of_dict_from_ddb = response['Items']
        while 'LastEvaluatedKey' in response:
            response = self._table_obj.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                **config)
            list_of_dict_from_ddb.extend(response['Items'])
        logger.info("Passing entries to a DataFrame")
        return pd.DataFrame(list_of_dict_from_ddb)

    def save_df(self, df):
        """
        Put DataFrame to DynamoDB
        :param df: DataFrame to be saved, all types are fixed to strings
        :return: None
        """
        logger.info("Validating DataFrame to ensure valid hashes/ranges and unique values")
        # cannot write nan or blank entries as a hash or range column
        for col in self._columns_to_check:
            if any(df[col].isna()) or (df[col].astype(str) == "").sum():
                raise ValueError("Arrays which contain pd.NaN or blank strings in the HASH or RANGE columns cannot be "
                                 "stored in DynamoDB, offending column: {}".format(col))

        if self._rangename:
            for items, slice in df.groupby(self._columns_to_check[0]):
                if any(slice[self._rangename].value_counts() > 1):
                    raise ValueError("Each HASH entry must have unique values for its RANGE column")
        else:
            if any(df[self._hashname].value_counts() > 1):
                raise ValueError("HASH column must contain unique values to be stored in DynamoDB, "
                                 "offending column: {}".format(self._columns_to_check[0]))

        logger.info("Casting all entries as string to load onto DynamoDB")
        with self._table_obj.batch_writer() as bw:
            for record in df.fillna("").astype(str).to_dict(orient='records'):
                rec_to_write = {key: rec for key, rec in record.items() if rec}
                bw.put_item(Item=rec_to_write)
        logger.info("Finished writing all entries to DynamoDB")

    def delete_table(self, blocking=True):
        """
        Recursively attempt to delete the table, to allow any operations to finish.
        :param blocking: whether to wait for the delete to complete
        :return:
        """
        logger.info("Attempting table delete {}".format(self._table_obj.name))
        try:
            response = self._table_obj.delete()
            logger.debug("Table delete response: {}".format(response))
            if blocking:
                logger.info("Waiting for delete to propagate")
                waiter = self._ddb_client.get_waiter('table_not_exists')
                waiter.wait(TableName=self._table_name, WaiterConfig=self._waiter_config)
        except self._ddb_client.exceptions.ResourceNotFoundException:
            # table has been deleted
            return
        # not sure how to delete the section below - add this wrapper outside to increase coverage?
        # except self._ddb_client.exceptions.ResourceInUseException as e:
        #     if waited > maxwait:
        #         raise e
        #     waited += wait
        #     sleep(wait)
        #     self.delete_table(waited=waited, wait=wait, maxwait=maxwait, blocking=True)
