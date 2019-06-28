name = "serial_j"

import json


class SerialJ(object):
    """YOU SHOULD NOT BE INSTANTIATING THIS CLASS. TO BE EXTENDED ONLY.


    This class implement both __str__() and __repr__() method for proper
    conversion to string data type. Also, as_dict() method was provided for
    conversion to python dictionary data type.

    At instantiation time, constructor checks all required fields and raise

        1.`ValueError` when required fields are not provided fully.

        2.`TypeError` when data type confirmation failed.

    Any serializer class extending this class must override the class
    attribute `schema` that confirms the following rules:

        1. Class attribute `schema` must be a list of dict data type.

        2. Every dict in `schema` must have the following format:

            {
                'name': 'property_name',
                'optional': True / False,
                'nullable': True / False,
                'is_compound': True / False,
                'compound_serializer': None / Serializer Class Name,
            }

    Args:
        data: dict / JSON formatted data to be serialized.
    """

    schema = []

    def __init__(self, data):
        self.__check__(data)
        for prop in self.schema:
            prop_name = prop['name']
            prop_is_compound = prop['is_compound']
            prop_compound_serializer = prop['compound_serializer']
            if prop_name in data:
                if prop_is_compound:
                    if (isinstance(data[prop_name], list)):
                        self.__dict__[prop_name] = [
                            prop_compound_serializer(obj)
                            for obj in data[prop_name]]
                    elif (isinstance(data[prop_name], dict)):
                        self.__dict__[prop_name] = prop_compound_serializer(
                            data[prop_name])
                else:
                    self.__dict__[prop_name] = data[prop_name]

    def __check__(self, data):
        for prop in self.schema:
            prop_name = prop['name']
            prop_optional = prop['optional']
            prop_nullable = prop['nullable']
            prop_is_compound = prop['is_compound']
            prop_compound_serializer = prop['compound_serializer']
            if prop_optional:
                if prop_name in data:
                    if not prop_nullable and not data[prop_name]:
                        raise ValueError(
                            f"Property '{prop_name}' is not nullable.")
                    if (prop_is_compound
                            and not isinstance(data[prop_name], list)
                            and not isinstance(data[prop_name], dict)):
                        raise TypeError(f"Compound Property '{prop_name}' is "
                                        f"not of type list or dict.")
                    if prop_is_compound and prop_compound_serializer is None:
                        raise TypeError(f"Compound Property '{prop_name}' does "
                                        f"not have a proper serializer.")
            else:
                if prop_name not in data:
                    raise ValueError(f"Property '{prop_name}' not found in "
                                     f"{data}.")
                if not prop_nullable and not data[prop_name]:
                    raise ValueError(f"Property '{prop_name}' is not nullable.")
                if (prop_is_compound
                        and not isinstance(data[prop_name], list)
                        and not isinstance(data[prop_name], dict)):
                    raise TypeError(f"Compound Property '{prop_name}' is "
                                    f"not of type list or dict.")
                if prop_is_compound and prop_compound_serializer is None:
                    raise TypeError(f"Compound Property '{prop_name}' does "
                                    f"not have a proper serializer.")

    def as_dict(self):
        d = {}
        for prop in self.schema:
            prop_name = prop['name']
            prop_is_compound = prop['is_compound']
            if prop_is_compound:
                if (isinstance(self.__dict__[prop_name], list)):
                    d[prop_name] = [com.as_dict() for com in
                                    self.__dict__[prop_name]]
                else:
                    d[prop_name] = self.__dict__[prop_name].as_dict()

            else:
                d[prop_name] = self.__dict__[prop_name]
        return d

    def __to_str(self):
        return json.dumps(self.as_dict())

    def __str__(self) -> str:
        return self.__to_str()

    def __repr__(self) -> str:
        return self.__to_str()
