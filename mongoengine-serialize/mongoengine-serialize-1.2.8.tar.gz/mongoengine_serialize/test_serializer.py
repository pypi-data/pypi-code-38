from bson.objectid import ObjectId
from . import Serialize

collection = dict({
    "_id": ObjectId("553486125ed592a10c4e8e6b"),  # random object id
    "name": str("Jeffrey Marvin"),
    "friends": [
        dict({
            "_id": ObjectId("553486125ed592a10c4e8e6c"),  # random object id of friend
            "name": str("Jeffreys Friend")
        })
    ]
})

expected_collection = dict({
    "id": str(collection['_id']),
    "name": collection['name'],
    "friends": [
        dict({
            "id": str("553486125ed592a10c4e8e6c"),  # random object id of friend
            "name": str("Jeffreys Friend")
        })
    ]
})

serialized_data = Serialize(collection).jsonify()


def test_equal_to_expected():
    assert serialized_data == expected_collection


def test_should_not_has__id_key():
    assert not hasattr(serialized_data, '_id')


def test_id_should_be_string():
    assert type(serialized_data['id']) is str


def test_should_exclude_name():
    assert not hasattr(Serialize(collection).exclude("friends").jsonify(), 'friends')
