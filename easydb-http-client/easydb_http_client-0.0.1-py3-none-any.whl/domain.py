from typing import List


class SpaceDoesNotExistException(Exception):
    def __init__(self, space_name):
        super().__init__()
        self.space_name = space_name

    def __str__(self):
        return 'SpaceDoesNotExistException(space_name=%s)' % self.space_name

    def __repr__(self):
        return self.__str__()


class BucketDoesNotExistException(Exception):
    def __init__(self, space_name, bucket_name, transaction_id=None):
        super().__init__()
        self.space_name = space_name
        self.bucket_name = bucket_name
        self.transaction_id = transaction_id

    def __str__(self):
        return 'BucketDoesNotExistException(space_name=%s, bucket_name=%s, transaction_id=%s)' % \
               (self.space_name, self.bucket_name, self.transaction_id)

    def __repr__(self):
        return self.__str__()


class BucketAlreadyExistsException(Exception):
    def __init__(self, space_name, bucket_name):
        super().__init__()
        self.space_name = space_name
        self.bucket_name = bucket_name

    def __str__(self):
        return 'BucketAlreadyExistsException(space_name=%s, bucket_name=%s)' % \
               (self.space_name, self.bucket_name)

    def __repr__(self):
        return self.__str__()


class ElementDoesNotExistException(Exception):
    def __init__(self, space_name, bucket_name, element_id, transaction_id=None):
        super().__init__()
        self.space_name = space_name
        self.bucket_name = bucket_name
        self.element_id = element_id
        self.transaction_id = transaction_id

    def __str__(self):
        return 'ElementDoesNotExistException(space_name=%s, bucket_name=%s, element_id=%s, transaction_id=%s)' % \
               (self.space_name, self.bucket_name, self.element_id, self.transaction_id)

    def __repr__(self):
        return self.__str__()


class TransactionDoesNotExistException(Exception):
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'TransactionDoesNotExistException(transaction_id=%s)' % self.transaction_id

    def __repr__(self):
        return self.__str__()


class TransactionAbortedException(Exception):
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'TransactionAbortedException(transaction_id=%s)' % self.transaction_id


class UnknownOperationException(Exception):
    pass


class UnknownError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


SPACE_DOES_NOT_EXIST = 'SPACE_DOES_NOT_EXIST'
BUCKET_DOES_NOT_EXIST = 'BUCKET_DOES_NOT_EXIST'
BUCKET_ALREADY_EXISTS = 'BUCKET_ALREADY_EXISTS'
ELEMENT_DOES_NOT_EXIST = 'ELEMENT_DOES_NOT_EXIST'
TRANSACTION_DOES_NOT_EXIST = 'TRANSACTION_DOES_NOT_EXIST'
OPERATION_TYPES = ['CREATE', 'UPDATE', 'DELETE', 'READ']
TRANSACTION_ABORTED = 'TRANSACTION_ABORTED'


class Space:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Space(name=%s)' % self.name

    def __str__(self):
        return self.__repr__()


class Bucket:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Space(name=%s)' % self.name

    def __str__(self):
        return self.__repr__()

    def _as_json(self):
        return {'bucketName': self.name}

class ElementField:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return self.name == other.name and \
               self.value == other.value

    def __hash__(self):
        return hash((self.name, self.value))

    def __str__(self):
        return 'ElementField(name=%s, value=%s)' % (self.name, self.value)

    def __repr__(self):
        return self.__str__()


class MultipleElementFields:
    def __init__(self, fields: List[ElementField] = None):
        if not fields:
            self.fields = []
        else:
            self.fields = fields

    def add_field(self, name, value):
        self.fields.append(ElementField(name, value))
        return self

    def __str__(self):
        fields_str = ", ".join(['{%s = %s}' % (f.name, f.value) for f in self.fields])
        return 'ElementFields(fields=[ %s ])' % fields_str

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.fields == other.fields

    def __hash__(self):
        return hash(self.fields)

    def _as_json(self):
        return {'fields': [dict((('name', f.name), ('value', f.value))) for f in self.fields]}


class Element:
    def __init__(self, identifier: str, fields: List[ElementField] = None):
        self.identifier = identifier
        self.element_fields = MultipleElementFields(fields)

    def __eq__(self, other):
        return self.identifier == other.identifier and \
               self.element_fields == other.element_fields

    def __hash__(self):
        return hash((self.identifier, self.element_fields))

    def __repr__(self):
        fields_str = ", ".join(['{%s = %s}' % (f.name, f.value) for f in self.fields])
        return 'Element(identifier=%s, fields=[ %s ])' % (
            self.identifier, fields_str)

    def __str__(self):
        return self.__repr__()

    @property
    def fields(self):
        return self.element_fields.fields

    def add_field(self, name, value):
        self.element_fields.add_field(name, value)
        return self


class Transaction:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'Transaction(transaction_id=%s)' % self.transaction_id

    def __repr__(self):
        return self.__str__()


class FilterQuery:
    def __init__(self, space_name, bucket_name, limit=20, offset=0, query=None):
        self.space_name = space_name
        self.bucket_name = bucket_name
        self.limit = limit
        self.offset = offset
        self.query = query

    def __str__(self):
        return 'FilterQuery(space_name=%s, bucket_name=%s, limit=%d, offset=%d, query=%s)' % \
               (self.space_name, self.bucket_name, self.limit, self.offset, self.query)

    def __repr__(self):
        return self.__str__()


class PaginatedElements:
    def __init__(self, elements: List[Element] = None, next_link: str = None):
        self.elements = elements if elements else []
        self.next_link = next_link

    def __eq__(self, other):
        return self.elements == other.elements and self.next_link == other.next_link

    def __hash__(self):
        return hash((self.elements, self.next_link))

    def __str__(self):
        return 'PaginatedElements(elements=[...], next_link=%s)' % self.next_link

    def __repr__(self):
        return self.__str__()


class TransactionOperation:
    def __init__(self, type: str, bucket_name: str, element_id: str = None, fields: MultipleElementFields = None):
        self.type = type
        self.bucket_name = bucket_name
        self.element_id = element_id
        self.fields = fields or MultipleElementFields()

    def _as_json(self):
        json = {'type': self.type, 'bucketName': self.bucket_name, 'elementId': self.element_id}
        json.update(self.fields._as_json())
        return json

    def __str__(self):
        return 'TransactionOperation(type=%s, bucket_name=%s, element_id=%s, fields=[...])' % \
               (self.type, self.bucket_name, self.element_id)

    def __repr__(self):
        self.__str__()


class OperationResult:
    def __init__(self, element: Element):
        self.element = element

    def is_empty(self):
        return not self.element

    def __eq__(self, other):
        return self.element == other.element

    def __hash__(self):
        return hash(self.element)

    def __str__(self):
        return 'OperationResult(element=%s)' % self.element

    def __repr__(self):
        return self.__str__()
