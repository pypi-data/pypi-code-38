from abc import ABCMeta
import json
import pandas as pd

from boto3.dynamodb.conditions import Key, Attr

from metagenomi.logger import logger
from metagenomi.db import dbconn
from metagenomi.mgvalidator import MgValidator
from metagenomi.helpers import delete_keys_from_dict
from metagenomi.helpers import (is_mgid, check_s3file, check_s3path)


class MgObj:
    '''
    MgObj - base class for all models and tasks
    '''
    __metaclass__ = ABCMeta

    def __init__(self, mgid, check=False, db=dbconn, key=None, load=True, project=None, **data):
        self.db = db
        self.mgid = mgid  # required
        self.check = check

        if not len(data) and load:
            if not is_mgid(self.mgid):
                if check_s3file(self.mgid) or check_s3path(self.mgid):
                    # s3 path
                    self.d = self.load_from_s3path(key)
                else:
                    try:
                        print('Trying to loading as an alt_id')
                        # try loading as alt_id first
                        self.d = self.load_from_altid(key)

                    except ValueError:
                        print('failed to find altid')
                        if self.mgtype == 'sample':
                            raise ValueError('Samples can only be loaded with mgids or alt_ids (sra accessions)')
                        # must be either an s3 path or a sample name

                        else:
                            # last resort, string matching of s3path
                            print('Loading via string matching. Avoid if possible')
                            if project is None:
                                msg = 'Cannot load an object with just sample name '
                                msg += 'and no project. Specify project='
                                raise ValueError(msg)
                            else:
                                self.d = self.load_from_name(key, project)

            else:
                self.d = self.load(key)  # TODO: what if load fails?

        else:
            self.d = data

        self.not_required = ['dynamodb', 'table', 's3', 'd',
                             'not_required', 'schema', 'db', 'check', ]

        self.schema = {'mgid': {'type': 'mgid', 'required': True}}

        self.validate({'mgid': self.mgid})

    def __str__(self):
        '''
        Default to just dumping data as json
        '''
        # TODO: Decimal() class handling. Cannot dump Decimal() into a json
        return str(json.dumps(self.d))

    # TODO: confirm that
    def to_dict(self, validate=True, clean=True):
        newdict = {}
        for k, v in vars(self).items():
            if k not in self.not_required and v is not None:
                if isinstance(v, list):
                    if not isinstance(v[0], str):
                        if v[0].whoami() == 'Mappings':
                            k = 'Mappings'
                        if v[0].whoami() == 'CrisprConnections':
                            k = 'CrisprConnections'
                        if v[0].whoami() == 'HmmSearches':
                            k = 'HmmSearches'

                        newdict[k] = []
                        for i in v:
                            newdict[k] = newdict[k] + [i.to_dict(
                                                       validate=validate,
                                                       clean=clean)]
                    else:
                        newdict[k] = v

                elif isinstance(v, pd.DataFrame):
                    newdict[k] = v.to_dict(orient='list')

                else:
                    try:
                        newdict[v.whoami()] = v.to_dict(validate=validate,
                                                        clean=clean)
                    except AttributeError:
                        newdict[k] = v

        if validate:
            if self.validate(newdict):
                if clean:
                    return delete_keys_from_dict(newdict, ['mgid'])
                return newdict

        if clean:
            return delete_keys_from_dict(newdict, ['mgid'])

        return newdict

    def validate(self, d=None, raise_error=True):
        '''
        raise_error must be default to true or else things will get written
        that you don't want written
        '''
        if d is None:
            # print('turning into dictionary')
            # Must validate during the process of turning into a dictionary
            # because otherwise nested MgTasks will not be validated
            # TODO: not entirely sure why??
            d = self.to_dict(validate=True, clean=False)

        v = MgValidator(self.schema)
        if v.validate(d):
            return True
        else:
            logger.debug(v.errors)
            if raise_error:
                print(f'Validation error with {self.mgid}')
                raise(ValueError(v.errors))
            else:
                print(v.errors)
                return False

    def load_from_altid(self, key, altid=None):
        k = 'alt_id'
        if altid is None:
            v = self.mgid
        else:
            v = altid

        response = self.db.table.query(
            IndexName='alt_id-mgproject-index',
            KeyConditionExpression=Key(k).eq(v))

        if len(response['Items']) > 1:
            e = f'Multiple database entries associated with {v}'
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            raise ValueError(e)

        self.mgid = response['Items'][0]['mgid']
        if key is None:
            return response['Items'][0]
        return response['Items'][0][key]

    # Loads entire model from the database
    def load(self, key, mgid=None):
        '''
        Will load either self or any mgid passed
        '''
        k = 'mgid'
        if mgid is None:
            v = self.mgid
        else:
            v = mgid

        response = self.db.table.query(KeyConditionExpression=Key(k).eq(v))

        if len(response['Items']) > 1:
            e = f'Multiple database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        if key is None:
            return response['Items'][0]
        return response['Items'][0][key]

    def whoami(self):
        return(self.__class__.__name__)

    def missing(self):
        missing = []
        for k, v in self.d.items():
            if v == 'None':
                missing.append(k)
        return missing

    def load_from_name(self, key, project, name=None):
        index = 'mgproject-mgtype-index'
        k = 'mgproject'
        if name is None:
            v = self.mgid
        else:
            v = name

        filtering_exp = Attr('s3path').contains(v)
        key_condition_exp = Key(k).eq(project) & Key('mgtype').eq(self.mgtype)

        response = self.db.table.query(
            IndexName=index,
            KeyConditionExpression=key_condition_exp,
            FilterExpression=filtering_exp
            )

        if len(response['Items']) > 1:
            s3paths = {}
            for i in response['Items']:
                s3paths[i['mgid']] = i['s3path']
            e = f'Multiple database entries associated with {v} \n'
            for k, v in s3paths.items():
                e += f'{v} = {k}\n'
            logger.info(e)
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        self.mgid = response['Items'][0]['mgid']
        if key is None:
            return response['Items'][0]
        return response['Items'][0][key]

    def load_from_s3path(self, key, s3path=None):
        '''
        Will load either self or any mgid passed
        '''
        k = 's3path'
        if s3path is None:
            v = self.mgid
        else:
            v = s3path

        response = self.db.table.query(
            IndexName='s3path-index',
            KeyConditionExpression=Key(k).eq(v)
            )

        if len(response['Items']) > 1:
            e = f'Multiple database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            logger.info(e)
            raise ValueError(e)

        self.mgid = response['Items'][0]['mgid']
        if key is None:
            return response['Items'][0]

        return response['Items'][0][key]
