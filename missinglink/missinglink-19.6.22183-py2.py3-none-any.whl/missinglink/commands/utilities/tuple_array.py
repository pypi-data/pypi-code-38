class TupleArray:
    @classmethod
    def dict_to_tuple_array(cls, data, key='Key', value='Value', value_transformer=None):
        """
        Converts a dictionary into a [{`key`: key, `value`: value} , ... ] array
        where the `key` and the `value` are predefined, Also supports transformation of the values
        :param data: Source dictionary
        :type data: dict
        :param key: The value of the `key` key name in the resulting tuple array
        :type key: str
        :param value: The value of the `value` key name in the resulting tuple array
        :type value: str
        :param value_transformer: Transformer to apply to the value. Optional
        :type value_transformer: Optional[Callable[Any,Any]]
        :return: List of "tuples"
        :rtype: List[dict]
        """

        def default_transformation(x):
            return x

        if value_transformer is None:
            value_transformer = default_transformation
        return [{key: k, value: value_transformer(v)} for k, v in data.items()]

    @classmethod
    def tuple_array_do_dict(cls, data, key='Key', value='Value'):
        return {x[key]: x[value] for x in data}
