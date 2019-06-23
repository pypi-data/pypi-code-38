class ModelConvert(object):
    """Model transform class，Convert the object to the corresponding dictionary"""
    @classmethod
    def key_values_list(cls, models, related_models=[], ignore_fields=[]):
        """
        Convert the list of objects into a dictionary list
        :param models: List of objects to convert
        :param related_models: The model object in the list to display the object of the associated query
        :param ignore_fields: Fields in the list that the model object does not need to display
        :return: Return list
        """
        return cls.__convert_list(models, related_models, ignore_fields)

    def key_values(self, related_models=[], ignore_fields=[]):
        """
        Convert an object into a dictionary
        :param related_models: The object to display the associated query
        :param ignore_fields: Fields that do not need to be displayed
        :return: Return dictionary
        """
        if not hasattr(self, '__table__'):
            return self.__dict__

        columns = self.__table__.columns
        attrs_dict = self.__convert_field(columns, ignore_fields)

        for model in related_models:
            value = getattr(self, model)
            if isinstance(value, ModelConvert):
                attrs_dict[model] = value.key_values()
            elif isinstance(value, list):
                attrs_dict[model] = self.key_values_list(value)

        return attrs_dict

    def __convert_field(self, fields, ignore_fields=[]):
        """Transform the corresponding fields of the database"""
        field_dict = dict()
        for column in fields:
            field = column.name
            if field in ignore_fields:
                continue
            value = getattr(self, field, None)
            field_dict[field] = self.set_field_value(field, value)

        return field_dict

    @classmethod
    def __convert_list(cls, models, related_models=[], ignore_fields=[]):
        """Convert a list"""
        list_dicts = list()
        for model in models:
            if isinstance(model, ModelConvert):
                list_dicts.append(model.key_values(related_models, ignore_fields))
            else:
                list_dicts.append(model)

        return list_dicts

    def set_field_value(self, field, value):
        """
        Set the value of the corresponding field, override the method, 
        and modify the value of a particular field, such as the value of the date field
        :param field: Field name
        :param value: value
        :return: Return the modified value
        """
        return value
