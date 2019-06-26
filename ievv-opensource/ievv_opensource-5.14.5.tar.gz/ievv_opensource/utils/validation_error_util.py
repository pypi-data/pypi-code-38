class ValidationErrorUtil(object):
    """
    A wrapper around :class:`django.core.exceptions.ValidationError`
    that provides useful extra functionality.

    Examples:

        Get a serializable dict::

            ValidationErrorUtil(some_validation_error).as_serializable_dict()

        Convert ValidationError to :class:`rest_framework.exceptions.ValidationError`::

            ValidationErrorUtil(some_validation_error).as_drf_validation_error()
    """
    def __init__(self, validation_error):
        self.validation_error = validation_error

    @property
    def is_dict_based(self):
        return hasattr(self.validation_error, 'error_dict')

    @property
    def is_single_message(self):
        return hasattr(self.validation_error, 'message')

    def as_dict(self):
        """
        Get the ValidationError as a dict mapping fieldname to
        a list of ValidationError object.

        Works no matter how the ValidationError was created.
        If the ValidationError was created with ``ValidationError('message')``
        or ``ValidationError(['message1', 'message2'])`` the values will
        end up in the ``__all__`` key of the dict.
        """
        if self.is_dict_based:
            return self.validation_error.error_dict
        return {
            '__all__': self.validation_error.error_list
        }

    def as_list(self):
        """
        Get the ValidationError as a list of ``ValidationError`` objects.

        Works even if the ValidationError was created with a dict as input.
        """
        if self.is_dict_based:
            validation_error_list = []
            for error_list in self.validation_error.error_dict.values():
                validation_error_list.extend(error_list)
            return validation_error_list
        else:
            return self.validation_error.error_list

    def as_serializable_list(self):
        """
        Get the ValidationError as a serializable list (a flat list with all the error messages).
        """
        return [validation_error.message
                for validation_error in self.as_list()]

    def as_serializable_dict(self):
        """
        Get the ValidationError as a serializable dict - a dict mapping
        fieldname to a list of error messages. If the ValidationError was
        not created with a dict as input, the error messages will be
        added to the ``__all__`` key.
        """
        serializable_dict = {}
        for field, validation_error_list in self.as_dict().items():
            serializable_dict[field] = []
            for validation_error in validation_error_list:
                serializable_dict[field].extend(self.__class__(validation_error).as_serializable_list())
        return serializable_dict

    def _as_drf_error_detail(self):
        from rest_framework import exceptions
        return exceptions.ErrorDetail(
            self.validation_error.message or exceptions.ValidationError.default_detail,
            code=self.validation_error.code or exceptions.ValidationError.default_code)

    def as_drf_validation_error(self):
        """
        Convert the ValidationError to a :class:`rest_framework.exceptions.ValidationError`.
        """
        from rest_framework import exceptions
        if self.is_dict_based:
            error_dict = {}
            for field, validation_error_list in self.as_dict().items():
                error_dict[field] = []
                for validation_error in validation_error_list:
                    error_dict[field].append(self.__class__(validation_error)._as_drf_error_detail())
            return exceptions.ValidationError(detail=error_dict)
        elif self.is_single_message:
            return exceptions.ValidationError(self._as_drf_error_detail())
        else:
            error_message_list = []
            for validation_error in self.as_list():
                error_message_list.append(self.__class__(validation_error)._as_drf_error_detail())
            return exceptions.ValidationError(detail=error_message_list)
