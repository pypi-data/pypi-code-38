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
                'optional': Optional, True / False,
                'nullable': Optional, True / False,
                'is_compound': Optional, True / False,
                'compound_serializer': Optional, Compound Serializer class,
                'compound_schema': Optional, `schema` of this property,
            }
            Note:
                if is_compound is True, you must provide 1 of the following:
                    `compound_serializer`, or `compound_schema` for successful
                    serialize data.

    Args:
        data: dict / JSON formatted data to be serialized.
    """

    schema = []

    _na = 'name'
    _opt = 'optional'
    _nu = 'nullable'
    _cp = 'is_compound'
    _srl = 'compound_serializer'
    _sch = 'compound_schema'

    def __init__(self, data):
        self._schema = []
        self._preproc(data)
        self._proc(data)

    def _preproc(self, data):
        for prop in self.schema:
            _name = prop[self._na]
            _optional = prop[self._opt] if self._opt in prop else False
            _nullable = prop[self._nu] if self._nu in prop else False
            _compound = prop[self._cp] if self._cp in prop else False
            _serializer = prop[self._srl] if self._srl in prop else None
            _schema = prop[self._sch] if self._sch in prop else None
            if _optional:
                if _name in data:
                    if not _nullable and not data[_name]:
                        raise ValueError(self._err(1, _name))
                    if (_compound
                            and not isinstance(data[_name], list)
                            and not isinstance(data[_name], dict)):
                        raise TypeError(self._err(2, _name))
                    if _compound and not _serializer and not _schema:
                        raise TypeError(self._err(3, _name))
            else:
                if _name not in data:
                    raise ValueError(self._err(0, _name, data))
                if not _nullable and not data[_name]:
                    raise ValueError(self._err(1, _name))
                if (_compound
                        and not isinstance(data[_name], list)
                        and not isinstance(data[_name], dict)):
                    raise TypeError(self._err(2, _name))
                if (_compound
                        and not _serializer
                        and not _schema):
                    raise TypeError(self._err(3, _name))
            _d = {
                self._na: _name,
                self._opt: _optional,
                self._nu: _nullable,
                self._cp: _compound,
                self._srl: _serializer,
                self._sch: _schema,
            }
            self._schema.append(_d)

    def _proc(self, data):
        for prop in self._schema:
            _name = prop[self._na]
            if _name in data:
                if prop[self._cp]:
                    if prop[self._srl]:
                        if isinstance(data[_name], list):
                            self.__dict__[_name] = [prop[self._srl](o)
                                                    for o in data[_name]]
                        elif isinstance(data[_name], dict):
                            self.__dict__[_name] = prop[self._srl](data[_name])
                    elif prop[self._sch]:
                        _cls = SerialJ
                        _cls.schema = prop[self._sch]
                        if isinstance(data[_name], list):
                            self.__dict__[_name] = [_cls(o)
                                                    for o in data[_name]]
                        elif isinstance(data[_name], dict):
                            self.__dict__[_name] = _cls(data[_name])
                else:
                    self.__dict__[_name] = data[_name]

    @staticmethod
    def _err(e, _name, data=None):
        if e == 0:
            return f"Property '{_name}' not found in {data}."
        elif e == 1:
            return f"Property '{_name}' is not nullable."
        elif e == 2:
            return f"Compound Property '{_name}' is not of type list or dict."
        elif e == 3:
            return (f"Compound Property '{_name}' does not have a proper "
                    f"serializer or schema.")

    def as_dict(self):
        _d = {}
        for prop in self._schema:
            _name = prop[self._na]
            if prop[self._cp]:
                if isinstance(self.__dict__[_name], list):
                    _d[_name] = [cp.as_dict() for cp in self.__dict__[_name]]
                else:
                    _d[_name] = self.__dict__[_name].as_dict()
            else:
                if _name in self.__dict__:
                    _d[_name] = self.__dict__[_name]
        return _d

    def _to_str(self):
        return json.dumps(self.as_dict())

    def __str__(self) -> str:
        return self._to_str()

    def __repr__(self) -> str:
        return self._to_str()
