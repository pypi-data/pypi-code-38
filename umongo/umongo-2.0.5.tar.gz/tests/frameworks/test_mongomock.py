from datetime import datetime

import pytest

from ..common import TEST_DB

try:
    from mongomock import MongoClient
except ImportError:
    dep_error = 'Missing mongomock module'
else:
    dep_error = None


if not dep_error:  # Make sure the module is valid by importing it
    from umongo.frameworks import mongomock  # noqa


def make_db():
    return MongoClient()[TEST_DB]


@pytest.fixture
def db():
    return make_db()


# MongoMockBuilder is 100% based on PyMongoBuilder so no need for really heavy tests
@pytest.mark.skipif(dep_error is not None, reason=dep_error)
def test_mongomock(classroom_model):
    Student = classroom_model.Student
    john = Student(name='John Doe', birthday=datetime(1995, 12, 12))
    john.commit()
    assert john.to_mongo() == {
        '_id': john.id,
        'name': 'John Doe',
        'birthday': datetime(1995, 12, 12)
    }
    john2 = Student.find_one(john.id)
    assert john2._data == john._data
    johns = Student.find()
    assert list(johns) == [john]
