from boto3.dynamodb.conditions import Key, Attr

from metagenomi.db import hmmdb
from metagenomi.helpers import get_time, to_decimal, in_db, gunzip_bytes_obj
from metagenomi.mgvalidator import MgValidator

'''
https://rostlab.org/rost-db-data/pfam/userman.txt
'''


class Hmm:
    def __init__(self, hmmid, check=True, db=hmmdb, load_hmm=False, **data):
        self.db = db
        # print(db.table)
        self.hmmid = hmmid
        if not len(data):
            self.d = self.load(load_hmm=load_hmm)  # TODO: what if load fails?
        else:
            self.d = data

        self.check = check
        self.hmmdb = self.d.get('hmmdb')
        self.hmm_source = self.d.get('hmm_source')
        self.source_type = self.d.get('source_type')
        self.hmm_type = self.d.get('hmm_type')
        self.description = self.d.get('description')
        self.annotation = self.d.get('annotation')
        self.hmm_group = self.d.get('hmm_group')
        self.hmm = self.d.get('hmm')
        if self.hmm and not isinstance(self.hmm, (bytes, bytearray)):
            self.hmm = self.hmm.value

        self.accn = self.d.get('accn')
        self.annotation = self.d.get('annotation')
        self.num_seqs = self.d.get('num_seqs')
        if self.num_seqs: self.num_seqs = int(self.num_seqs)
        self.hmm_length = self.d.get('hmm_length')
        if self.hmm_length: self.hmm_length = int(self.hmm_length)
        # lowest whole sequence score in bits of a match in the full alignment
        self.tc_whole_seq = self.d.get('tc_whole_seq')
        if self.tc_whole_seq is not None:
            self.tc_whole_seq = to_decimal(self.tc_whole_seq)
        # lowest per-domain score in bits of a match in the full alignment
        self.tc_per_domain = self.d.get('tc_per_domain')
        if self.tc_per_domain is not None:
            self.tc_per_domain = to_decimal(self.tc_per_domain)

        self.updated = get_time()

        if 'created' in self.d:
            self.created = self.d['created']
        else:
            self.created = get_time()

        self.not_required = ['schema', 'db', 'check', 'd', 'not_required']

        allowed_source_types = ['public', 'paper', 'patent', 'proprietary']
        allowed_types = ['domain', 'Cas', 'protein']
        self.schema = {'hmmid': {'type': 'hmmid', 'required': True},
                       'hmmdb': {'type': 's3file', 'required': True},
                       'hmm_source': {'type': 'string', 'required': True},
                       'annotation': {'type': 'string'},
                       'hmm_length': {'type': 'integer', 'required': True},
                       'source_type': {'type': 'string',
                                       'required': True,
                                       'allowed': allowed_source_types},
                       'hmm_type': {'type': 'string',
                                    'required': True,
                                    'allowed': allowed_types},
                       'description': {'type': 'string', 'required': True},
                       'accn': {'type': 'string', 'required': True},
                       'num_seqs': {'type': 'integer', 'required': True},
                       # the entire HMM
                       'hmm': {'type': 'binary', 'nullable': True},
                       'hmm_group': {'type': 'string', 'nullable': True},
                       'tc_whole_seq': {'type': 'decimal', 'nullable': True},
                       'tc_per_domain': {'type': 'decimal', 'nullable': True},
                       'updated': {'type': 'datestring', 'required': True},
                       'created': {'type': 'datestring', 'required': True}}

        if self.check:
            self.validate()

    def __str__(self):
        to_print = ''
        for k, v in self.to_dict().items():
            if k != 'hmm':
                to_print += f'{k} : {v}, {type(v)}\n'
        return to_print

    def get_hmm(self, unzip=True):
        if self.hmm is None:
            self.load_hmm()
        if unzip:
            return gunzip_bytes_obj(self.hmm)
        return self.hmm

    def validate(self, d=None, raise_error=True):
        '''
        raise_error must be default to true or else things will get written
        that you don't want written
        '''
        if d is None:
            d = self.to_dict()

        v = MgValidator(self.schema)
        if v.validate(d):
            return True
        else:
            if raise_error:
                print(f'Validation error with {self.hmmid}')
                raise(ValueError(v.errors))
            else:
                print(v.errors)
                return False

    def to_dict(self):
        newdict = {}
        for k, v in vars(self).items():
            if k not in self.not_required and v is not None:
                newdict[k] = v
        return newdict

    def load(self, hmmid=None, load_hmm=False):
        '''
        Will load either self or any hmmid passed
        '''
        k = 'hmmid'
        if hmmid is None:
            v = self.hmmid
        else:
            v = hmmid

        if load_hmm:
            response = self.db.table.query(KeyConditionExpression=Key(k).eq(v))
        else:
            pexpr = "hmmid, hmmdb, hmm_source, source_type, hmm_type, accn, "
            pexpr += "description,updated, created, annotation, hmm_group, "
            pexpr += "hmm_length, num_seqs, tc_whole_seq, tc_whole_domain"
            response = self.db.table.query(
                        KeyConditionExpression=Key(k).eq(v),
                        ProjectionExpression=pexpr
                        )

        if len(response['Items']) > 1:
            e = f'Multiple database entries associated with {v}'
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            raise ValueError(e)
        return response['Items'][0]

    def load_hmm(self):
        '''
        Will load either self or any hmmid passed
        '''
        k = 'hmmid'
        v = self.hmmid

        pexpr = "hmm"
        response = self.db.table.query(
                    KeyConditionExpression=Key(k).eq(v),
                    ProjectionExpression=pexpr
                    )

        if len(response['Items']) > 1:
            e = f'Multiple database entries associated with {v}'
            raise ValueError(e)

        if len(response['Items']) < 1:
            e = f'No database entries associated with {v}'
            raise ValueError(e)

        self.hmm = response['Items'][0]['hmm'].value
        # No return

    def write(self, force=False, dryrun=False):
        '''
        Write this object to the database - over-ridden in other derived
        classes when needed
        '''
        if in_db(self.hmmid, hmmdb, key='hmmid'):
            # update
            raise ValueError(f'{self.hmmid} already exists')

        print('VALIDATING')
        print(self.validate())
        d = self.to_dict()

        # Add it back in at the appropriate spot
        d['hmmid'] = self.hmmid

        if dryrun:
            # TODO: improve printing here
            print('--- dry run ----')
            print(f'Would write to {self.db.table}')
            print(d)
            return

        else:
            response = self.db.table.put_item(
                Item=d
            )

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f'Wrote {response} to db')
            else:
                raise ValueError('Response returned an HTTPStatusCode other than 200')

    def update(self, key, value, dryrun=False):
        '''
        TODO: VALIDATION???

        '''
        self.updated = get_time()

        if dryrun:
            print('Dry run')
            print(f'Would update {key} to {value}')
            return

        else:
            response = self.db.table.update_item(
                                Key={
                                    'hmmid': self.hmmid, 'hmm_source': self.hmm_source
                                },
                                UpdateExpression=f"set {key} = :r, updated = :a",
                                ExpressionAttributeValues={
                                    ':r': value,
                                    ':a': self.updated
                                },
                                ReturnValues="UPDATED_NEW"
                            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f'{self.hmmid} update successful')
            else:
                # TODO: wrap this into the logger??
                print(response)
                raise ValueError('Something went wrong with the update request')

            return response
