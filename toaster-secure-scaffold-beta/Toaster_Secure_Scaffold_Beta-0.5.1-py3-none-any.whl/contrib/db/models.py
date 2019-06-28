import inspect

from secure_scaffold.config import get_setting


try:
    _DATABASE_SETTINGS = get_setting('DATABASE_SETTINGS')
except AttributeError:
    raise AttributeError("DATABASE_SETTINGS setting not defined. "
                         "For the database system to work the "
                         "DATABASE_SETTINGS setting must be defined.")


ENGINE = __import__(_DATABASE_SETTINGS['engine'])(**_DATABASE_SETTINGS['settings'])


class TooManyPrimaryKeysError(Exception):
    pass


class NoPrimaryKeyError(Exception):
    pass


class Field:
    """
    Class used to define what type an attribute on a class Model will be.
    Example usage:
        class User(Model):
            name = Field(str)
            age = Field(int)
    """
    def __init__(self,
                 field_type,
                 default=None,
                 unique=False,
                 primary=False,
                 required=True):
        self.type = field_type
        if default is not None:
            if callable(default):
                default = default()
            if not isinstance(default, field_type):
                raise AttributeError("Default value must match the specified type {}, instead it is type {}"
                                     .format(field_type, type(default)))
        self.default = default
        self.primary = primary
        self.unique = primary or unique  # Must be unique if a primary key.
        self.required = required


class Model:
    """
    Base Model class
    Each class will represent a collection in Firestore
    Each instance of a class will represent a document in the collection
    Example usage:
        class User(Model):
            collection = 'User'
            name = Field(str, primary=True)
            age = Field(int)

        user = User(name="John", age=20)
    """
    def __init__(self, _id=None, _created_at=None, **kwargs):
        """
        Initialise the class
        :param id: ID of the document in Firestore
                    If not defined then a random string will be assigned by Firestore
        :param kwargs: Named arguments matching the fields defined by the class
                        All fields defined are required, unless there is a default specified
        """
        # Check the class has a collection attribute set
        try:
            self.collection
        except AttributeError:
            raise AttributeError("Attribute 'collection' must be defined")

        # Get all the Field attributes defined by the class
        # List of tuples, [ (attribute name, field class), ... ]
        fields = [item for item in inspect.getmembers(self)
                  if isinstance(item[1], Field)]
        # convert to dictionary
        self.fields = dict(fields)

        # Set id
        self._id = _id

        self._created_at = _created_at

        # For each attribute set on the model class make sure the class is instantiated with it
        # Set each attribute and save the Field class to a __meta__ attribute name
        primary_count = 0
        for attr_name, attr_class in self.fields.items():
            if attr_class.primary:
                primary_count += 1
            if primary_count > 1:
                raise TooManyPrimaryKeysError(
                    "Model %s can only support a single Primary Key" % self.__class__.__name__
                )
            if attr_name in kwargs:
                attr_value = kwargs[attr_name]

                if isinstance(attr_value, attr_class.type):
                    setattr(self, '__meta__' + attr_name, attr_class)
                    setattr(self, attr_name, attr_value)
                else:
                    raise AttributeError("Attribute {} must be type {} but instead is type {}"
                                         .format(attr_name, attr_class.type, type(attr_value)))
            else:
                if attr_class.default is not None:
                    attr_value = attr_class.default
                    setattr(self, '__meta__' + attr_name, attr_class)
                    setattr(self, attr_name, attr_value)
                elif attr_class.required:
                    raise AttributeError("Attribute {} must be defined".format(attr_name))
        if not primary_count:
            raise NoPrimaryKeyError(
                "Model %s must have a Primary Key field." % self.__class__.__name__
            )

    def __setattr__(self, key, value):
        """
        Overwrite this function so we can validate fields before they're set
        :param key: Name of the attribute trying to be set
        :param value: Value trying to set it too
        :return: Error or sets the attribute to the value
        """
        try:
            # If we have the meta class (i.e. it is a specified Field with a type)
            attr_class = getattr(self, '__meta__' + key)
            # Check the type of the value against the specified Field type
            if isinstance(value, attr_class.type):
                super().__setattr__(key, value)
            else:
                raise TypeError("Value for {} should be type {} but is instead type {}".format(
                    key,
                    attr_class.type,
                    type(value)
                ))
        except AttributeError:
            super().__setattr__(key, value)

    def _check_unique_fields(self):
        """
        Look through the model fields and check that if one is set to be unique,
        that no other saved documents match it
        :return: Error or nothing
        """
        for attr_name, attr_class in self.fields.items():
            value = getattr(self, attr_name)
            if attr_class.unique:
                for instance in self.get(**{attr_name: value}):
                    if instance._key != self._key:
                        raise AttributeError(
                            "Attribute {} must be unique, but there is already a "
                            "document defined with the value {}".format(attr_name, value)
                        )

    def to_dict(self):
        """
        :return: all Field attributes as a dict
        """
        attrs = {}
        for field in self.fields.keys():
            attr = getattr(self, field)
            if not isinstance(attr, Field):
                attrs[field] = getattr(self, field)
            else:
                attrs[field] = None
        return attrs

    def save(self):
        """
        Save document to the Firestore using ID
        if the ID is not defined then create it instead
        """
        self._check_unique_fields()
        return ENGINE.save(self)

    def _create(self):
        """
        Create document in the Datastore
        """
        # Returns a tuple (timestamp, document)
        return ENGINE._create(self)

    @property
    def pk(self):
        for attr_name, attr_class in self.fields.items():
            if attr_class.primary:
                return getattr(self, attr_name)

    @property
    def id(self):
        if self._id:
            return self._id
        self._id = self.pk
        return self._id

    @property
    def _key(self):
        key = ENGINE.key(self)
        return key

    def delete(self):
        """
        Delete self from the datastore
        :return: None
        """
        ENGINE.delete(self)

    @classmethod
    def get(cls, id=None, **kwargs):
        """
        Get a document or list of documents from the Firestore

        :param id: If specified will return specified document model class
                    If not specified will return a list of document model classes that match the kwargs given
        :param kwargs: Named fields and values to match within documents
                        e.g. User.get(name="John", age=20)
        :return: [User, ..] or User
        """
        yield ENGINE.get(cls, id, **kwargs)

    @classmethod
    def get_all(cls):
        """
        Get all documents in this collection as a list
        :return: List of docs, e.g. [User, ..] or User
        """
        yield ENGINE.get_all(cls)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.__class__.__name__}(**{self.to_dict()})'
