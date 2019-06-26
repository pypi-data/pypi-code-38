#!/usr/bin/python
"""a class that acts a little like a dictionary that uses dynamo as a backing"""
# std imports
import base64
import sys
import time

# site imports
import boto3
import botocore.exceptions
import cbor2

# user imports


def serialize(obj):
    return base64.b64encode(cbor2.dumps(obj))


def deserialize(obj):
    return cbor2.loads(base64.b64decode(obj))


class DynamoDictionary(object):
    """a class that acts a little like a dictionary that uses dynamo as a backing"""
    empty_sentinel = object()

    def __init__(self, table_name, read_units=1, write_units=1):
        self.table_name = table_name
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.conn = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.conn.Table(self.table_name)
        try:
            self.table.get_item(Key={'key': "test"})
        except botocore.exceptions.ClientError:
            self.create_table(read_units=read_units, write_units=write_units)
            self.table.wait_until_exists()

    def create_table(self, read_units=1, write_units=1):
        """create a table in case it doesn't exist"""
        self.client.create_table(
            TableName=self.table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'key',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': read_units,
                'WriteCapacityUnits': write_units
            }
        )

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        got = self.table.get_item(Key={'key': serialize(key)})
        if 'Item' not in got:
            raise KeyError(key)
        return deserialize(got['Item']['value'])

    def __setitem__(self, key, value):
        """x.__setitem__(i, y) <==> x[i]=y"""
        skey = serialize(key)
        sval = serialize(value)
        for i in xrange(5):
            try:
                self.table.put_item(Item={'key': skey, 'value': sval})
                break
            except botocore.exceptions.ClientError as oops:
                if oops.response['Error'][
                        'Code'] != 'ProvisionedThroughputExceededException':
                    raise
                else:
                    print >> sys.stderr, "Over rate limit, backing off!"
                    time.sleep(0.1 * 2**i)
        else:
            raise Exception("Tried 5 times could not write item!")

    def get(self, key, default=None):
        """D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def pop(self, key, default=empty_sentinel):
        """D.pop(k[,d]) -> v, remove specified key and return the corresponding value.\nIf key is not found, d is returned if given, otherwise KeyError is raised"""
        deleted = self.table.delete_item(
            Key={'key': serialize(key)},
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' not in deleted:
            if default is not self.empty_sentinel:
                return default
            else:
                raise KeyError(key)
        return deserialize(
            deleted['Attributes']['value']
        )

    def iteritems(self):
        """D.iteritems() -> an iterator over the (key, value) items of D"""
        start_key = ""
        while True:
            kwargs = {
                "Limit": 1000,
                "Select": 'ALL_ATTRIBUTES',
            }
            if start_key:
                kwargs['ExclusiveStartKey'] = start_key
            response = self.table.scan(
                **kwargs
            )
            for item in response['Items']:
                yield deserialize(item['key']), deserialize(item['value'])
            start_key = response.get("LastEvaluatedKey")
            if start_key is None:
                break

    def items(self):
        """D.items() -> list of D's (key, value) pairs, as 2-tuples"""
        return [item for item in self.iteritems()]

    def keys(self):
        """D.keys() -> list of D's keys"""
        return [key for key, _ in self.iteritems()]

    def values(self):
        """D.values() -> list of D's values"""
        return [value for _, value in self.iteritems()]

    def itervalues(self):
        """D.itervalues() -> an iterator over the values of D"""
        for _, value in self.iteritems():
            yield value

    def iterkeys(self):
        """D.iterkeys() -> an iterator over the keys of D"""
        for key, _ in self.iteritems():
            yield key

    def __iter__(self):
        """x.__iter__() <==> iter(x)"""
        for key, _ in self.iteritems():
            yield key

    def __contains__(self, key):
        """D.__contains__(k) -> True if D has a key k, else False"""
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __len__(self):
        """x.__len__() <==> len(x)"""
        count = 0
        for _ in self.__iter__():
            count += 1
        return count

    def clear(self):
        """D.clear() -> None.  Remove all items from D."""
        # do a batch get an then batch write deleting in chunks of 25
        chunk = []
        for key in self.iterkeys():
            chunk.append(key)
            if 25 <= len(chunk):
                self.multi_delete(chunk)
                chunk[:] = []
        self.multi_delete(chunk)

    def multi_delete(self, keys):
        if not keys:
            return
        # todo add retries and handle unprocessed items
        res = self.client.batch_write_item(
            RequestItems={
                self.table_name: [
                    {
                        "DeleteRequest": {
                            "Key": {
                                "key": {
                                    "S": serialize(key)
                                }
                            }
                        }
                    } for key in keys
                ]
            }
        )


def main():
    d = DynamoDictionary("footable")
    d['foo'] = 'bar'
    print len(d)
    print d.items()
    print d.iteritems()
    print d.itervalues()
    for val in d.itervalues():
        print val
    print d['foo']
    print d.pop('foo')
    print len(d)


if "__main__" == __name__:
    main()
