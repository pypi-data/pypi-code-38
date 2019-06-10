from abc import ABCMeta
import json
import pandas as pd

from boto3.dynamodb.conditions import Key


from metagenomi.base import MgObj
from metagenomi.logger import logger
from metagenomi.helpers import get_time
from metagenomi.db import batch_client


class MgTask(MgObj):
    '''
    MgTask - base class for all tasks
    '''
    __metaclass__ = ABCMeta

    def __init__(self, mgid, **data):
        MgObj.__init__(self, mgid, key=self.whoami(), **data)

        self.jobid = self.d.get('jobid', 'None')
        self.status = self.d.get('status')

        self.updated = get_time()
        self.cmd_run = self.d.get('cmd_run', 'None')
        self.args = self.d.get('args')
        # self.not_required.append += ['...', ]

        allowed_status = ['SUBMITTED', 'RUNNING', 'SUCEEDED', 'FAILED']
        self.schema = {
            **self.schema, **{
                'status': {'type': 'string', 'allowed': allowed_status},
                'cmd_run': {'type': 'string', 'required': True, 'minlength': 1},
                'jobid': {'type': 'string', 'required': True, 'minlength': 1},
                'updated': {'type': 'datestring', 'required': True},
                'args': {'type': 'dict'}
            }
        }

    def get_job_status(self):
        response = batch_client.describe_jobs(
                    jobs=[self.jobid]
                    )

        if len(response['jobs']) == 1:
            status = response['jobs'][0]['status']
            return status

    def write(self):
        '''
        Write this opject to the database - over-ridden in other derived
        classes when needed
        '''
        self._create(self.whoami(), self.to_dict(validate=True, clean=True))

    def run(self, jobdefnumber=None):
        # Given the appropriate inputs, run the container
        # Implemented in the derived classes
        pass

    def _create(self, key, value):
        response = self.db.table.query(
            KeyConditionExpression=Key('mgid').eq(self.mgid))

        # Add to them
        if len(response['Items']) < 1:
            raise ValueError(f'{self.mgid} does not exist in DB')

        else:
            if key in response['Items'][0]:
                print(f'{key} is already in the DynamoDB, overwriting')

            # TODO: check response?
            response = self.db.table.update_item(
                Key={'mgid': self.mgid},
                UpdateExpression=f"set {key} = :r",
                ExpressionAttributeValues={':r': value},
                ReturnValues="UPDATED_NEW"
            )


    def _delete_from_list(self, key, unique_id):
        # Given a unique_id,
        # 1) Finds the index of the item in the list with that id
        # 2) Deletes it

        response = self.db.table.query(
            KeyConditionExpression=Key('mgid').eq(self.mgid))

        if len(response['Items']) < 1:
            raise ValueError(f'{self.mgid} does not exist in DB')
        if key in response['Items'][0]:
            list_to_search = response['Items'][0][key]

            i = None
            for item in list_to_search:
                if 'unique_id' in item:
                    if item['unique_id'] == unique_id:
                        # This should never return an error
                        i = list_to_search.index(item)
                        break

            if i is None:
                raise ValueError(f'Unique id {unique_id} does not exist in \
                the {key} for {self.mgid}')

        result = self.db.table.update_item(
            Key={
                'mgid': self.mgid
            },
            UpdateExpression=f"REMOVE #mg[{i}]",
            ExpressionAttributeNames={
             '#mg': key
             }
        )

    def _overwrite(self, key, value, unique_id):
        # First, deletes the item from the list
        # Second, rewrites it. Will have the same unique_id
        self._delete_from_list(key, unique_id)
        self._update(key, value)

    # Internal method only called by base class
    # Used to update the task attributes that are actually lists
    # E.g. mapping
    def _update(self, key, value):

        response = self.db.table.query(
            KeyConditionExpression=Key('mgid').eq(self.mgid))

        if len(response['Items']) < 1:
            raise ValueError(f'{self.mgid} does not exist in DB')

        else:
            if key in response['Items'][0]:
                print(f'{key} is already in the DynamoDB')

                # make new unique_id. 1) Query existing ids, 2) chose one that
                # is unique
                existing_ids = []
                for item in response['Items'][0][key]:
                    if 'unique_id' in item:
                        existing_ids.append(item['unique_id'])

                i = 1
                while i in existing_ids:
                    i += 1

                # set the unique_id here.
                # TODO: is this the best place to do it? Could also
                # set it on the object itself and then call to_dict() here
                value['unique_id'] = i
                self.unique_id = i
                # TODO: do something with the result?
                result = self.db.table.update_item(
                    Key={
                        'mgid': self.mgid
                    },
                    UpdateExpression="SET #mg = list_append(#mg, :i)",
                    ExpressionAttributeValues={
                        ':i': [value],
                    },
                    ExpressionAttributeNames={
                     '#mg': key
                     },
                    ReturnValues="UPDATED_NEW"
                )
            else:
                print(f'{key} is not in the DynamoDB, adding...')
                # TODO: do something with the result?

                # if "mappings" for example is not in the dictionary, then
                # any unique_id you create will be unique because it is the
                # only one. Create it as 1
                value['unique_id'] = 1
                self.unique_id = 1
                result = self.db.table.update_item(
                    Key={
                        'mgid': self.mgid
                    },
                    UpdateExpression="SET #mg = :i",
                    ExpressionAttributeValues={
                        ':i': [value],
                    },
                    ExpressionAttributeNames={
                     '#mg': key
                     },
                    ReturnValues="UPDATED_NEW"
                )
