from unittest import mock

import pytest

with mock.patch('secure_scaffold.config.get_setting') as mock_settings:
    mock_settings.return_value = {}
    from secure_scaffold.contrib.db.models import Model, Field


def test_field_no_default():
    field = Field(str)
    assert field.type == str
    assert type("Im a string") == field.type
    assert field.default is None
    assert field.unique is False


def test_field_unique():
    field = Field(str, unique=True)
    assert field.type == str
    assert type("Im a string") == field.type
    assert field.default is None
    assert field.unique is True


def test_field_correct_default():
    field = Field(str, default="Im a string")
    assert field.type == str
    assert type("Im a string") == field.type
    assert field.default == "Im a string"
    assert type(field.default) == field.type
    assert field.unique is False


def test_field_incorrect_default():
    with pytest.raises(AttributeError):
        try:
            Field(str, default=10)
        except AttributeError as err:
            assert "Default value must match the specified type {}, instead it is type {}".format(str, int) in err.args
            raise err


def test_base_model_no_collection():
    with pytest.raises(AttributeError):
        try:
            Model()
        except AttributeError as err:
            assert "Attribute 'collection' must be defined" in err.args
            raise err


def test_base_model_get_no_collection():
    with pytest.raises(AttributeError):
        Model.get()


@pytest.fixture
def empty_user():
    class User(Model):
        pass
    return User


@pytest.fixture
def collection_user():
    class User(Model):
        collection = "User"
        id_attr = Field(int, primary=True)
    return User


@pytest.fixture
def user():
    class User(Model):
        collection = "User"
        name = Field(str, primary=True)
        age = Field(int)
    return User


def test_child_model_no_collection(empty_user):
    with pytest.raises(AttributeError):
        try:
            empty_user()
        except AttributeError as err:
            assert "Attribute 'collection' must be defined" in err.args
            raise err


def test_child_model_collection(collection_user):
    user = collection_user(id_attr=1)
    assert user.collection == "User"


def test_child_model_creation(user):
    user = user(name="John", age=20)
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20

    user.name = "Jane"
    user.age = 10

    assert user.name == "Jane"
    assert user.age == 10


def test_child_model_updating_wrong_type(user):
    user = user(name="John", age=20)
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20

    with pytest.raises(TypeError):
        try:
            user.name = 10
        except TypeError as err:
            assert "Value for name should be type {} but is instead type {}".format(str, int) in err.args
            raise err


def test_child_model_creation_error_missing(user):
    with pytest.raises(AttributeError):
        try:
            user(name="John")
        except AttributeError as err:
            assert "Attribute age must be defined" in err.args
            raise err


def test_child_model_creation_error_incorrect(user):
    with pytest.raises(AttributeError):
        try:
            user(name=10, age=10)
        except AttributeError as err:
            assert "Attribute name must be type {} but instead is type {}".format(str, int) in err.args
            raise err


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
def test_child_model_deletion(mock_client, user):
    mock_client.key.return_value = "key"
    user = user(name="John", age=20)
    user.delete()

    mock_client.delete.assert_called_once_with("key")


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
@mock.patch('secure_scaffold.contrib.db.models.datastore')
def test_child_model_save_create(mock_datastore, mock_client, user):
    user = user(name="John", age=20)
    user.save()
    mock_datastore.Entity.assert_called_once()
    mock_datastore.Entity().update.assert_called_once()
    mock_client.put.assert_called_once()
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
@mock.patch('secure_scaffold.contrib.db.models.datastore')
def test_child_model_save(mock_datastore, mock_client, user):
    user = user(name="John", age=20)
    user.save()
    mock_datastore.Entity.assert_called_once()
    mock_datastore.Entity().update.assert_called_once()
    mock_client.put.assert_called_once()
    assert user.id == "John"
    assert user.collection == "User"
    assert user.name == "John"
    assert user.age == 20


class Doc(dict):
    def __init__(self, id, *args, **kwargs):
        super(Doc, self).__init__(*args, **kwargs)
        self.id = id
        self['_id'] = id
        self.kwargs = kwargs
        self['_created_at'] = mock.MagicMock()


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
def test_child_model_get_one(mock_client, user):
    mock_client.get.return_value = Doc(1, name="John", age=20)
    user_obj = user.get(id=1)

    mock_client.get.assert_called()
    assert isinstance(user_obj, user)
    assert user_obj.id == 1
    assert user_obj.collection == "User"
    assert user_obj.name == "John"
    assert user_obj.age == 20


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
def test_child_model_get_multiple(mock_client, user):
    mock_client.query().fetch.return_value = [Doc(1, name="John", age=20), Doc(2, name="Jane", age=20)]
    users = user.get(age=20)

    mock_client.query.assert_called()
    mock_client.query().add_filter.assert_called()
    mock_client.query().fetch.assert_called()

    assert len(users) == 2
    assert isinstance(users[0], user)
    assert users[0].id == 1
    assert users[0].collection == "User"
    assert users[0].name == "John"
    assert users[0].age == 20
    assert isinstance(users[1], user)
    assert users[1].id == 2
    assert users[1].collection == "User"
    assert users[1].name == "Jane"
    assert users[1].age == 20


@pytest.fixture
def unique_user():
    class User(Model):
        collection = "User"
        name = Field(str, primary=True)
        age = Field(int)
    return User


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
def test_unique_field_works(mock_client, unique_user):
    mock_client.collection().where().get.return_value = []

    user = unique_user(name="John", age=10)
    assert user.name == "John"
    assert user.age == 10


@mock.patch('secure_scaffold.contrib.db.models.DB_CLIENT')
def test_unique_field_error(mock_client, unique_user):
    mock_client.query().fetch.return_value = [Doc(1, name="John", age=20)]
    mock_client.key.side_effect = [1, 2]

    with pytest.raises(AttributeError):
        try:
            john = unique_user(name="John", age=10)
            john.save()
        except AttributeError as err:
            assert "Attribute name must be unique, but there is already a" \
                   " document defined with the value John" in err.args
            raise err
