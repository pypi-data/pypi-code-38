from django.core.exceptions import ValidationError
from ievv_opensource.utils import choices_with_meta


class ChoiceSetupError(Exception):
    """
    Raised by :meth:`.SerializableChoicesWithMeta.validate_setup`.
    """


class AbstractChoiceConstants:
    """
    Base class used to define constants for some set of choices.

    You should define the choice values as attributes of the subclass,
    and then override :meth:`.get_choice_kwargs` to provide
    values for the :meth:`.make_choice` method.
    """
    @classmethod
    def get_default_choice_class(cls):
        raise NotImplementedError()

    @classmethod
    def get_choice_kwargs(cls):
        """
        Returns a dict mapping choice values to kwargs for the
        :class:`ievv_opensource.utils.choices_with_meta.Choice`
        corresponding to the value.
        """
        return {}

    @classmethod
    def make_choice(cls, value, choice_class=None, **kwargs):
        choice_class = choice_class or cls.get_default_choice_class()
        full_kwargs = {}
        for kwarg_key, kwarg_value in cls.get_choice_kwargs()[value].items():
            full_kwargs.setdefault(kwarg_key, kwarg_value)
        full_kwargs.update(kwargs)
        full_kwargs['value'] = value
        return choice_class(**full_kwargs)


class SerializableChoice(choices_with_meta.Choice):
    """
    Base class for choices within a :class:`.SerializableChoicesWithMeta`.
    """
    def validate_setup(self, choiceswithmeta_object, **kwargs):
        """
        Validate that this choice has sane attributes within
        the context of the provided ``choiceswithmeta_object``.

        See :meth:`.SerializableChoicesWithMeta.validate_setup` for more
        details.

        Args:
            choiceswithmeta_object (.SerializableChoicesWithMeta): The
                choices with meta object that contains this choice.
        """


class ImpliesAllExcept:
    def __init__(self, *except_choice_values):
        self.except_choice_values = except_choice_values

    def __call__(self, choiceswithmeta_object, source_choice):
        implies = set()
        for choice in choiceswithmeta_object.iterchoices():
            if choice.value not in self.except_choice_values:
                implies.add(choice.value)
        return implies


class ImpliesAll(ImpliesAllExcept):
    def __init__(self):
        super().__init__()


class SerializableMultiChoice(SerializableChoice):
    """
    Base class for choices within a :class:`.SerializableMultiChoicesWithMeta`.
    """
    def __init__(self, *args, implies=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_implies = implies or set()
        self._implies = None
        self._implied_by = None

        # Set in :class:`.ChoicesWithMeta.add`.
        self._choices_with_meta = None

    def _build_implies(self):
        if not self._choices_with_meta:
            raise ValueError('Can not use the "implies" property before the choice has '
                             'been added to a MultipleChoicesWithMeta.')
        if callable(self.raw_implies):
            raw_implies_callable = self.raw_implies
            implies = raw_implies_callable(choiceswithmeta_object=self._choices_with_meta,
                                           source_choice=self)
        else:
            implies = set(self.raw_implies)
        all_implies = set()
        for permission in implies:
            if permission == self.value:
                continue
            try:
                implied_choice = self._choices_with_meta[permission]
            except KeyError:
                raise ChoiceSetupError(
                    '{}: {!r} implies {!r}, but {!r} does '
                    'not exist.'.format(self.classpath, self.value, permission, permission))
            all_implies.add(implied_choice.value)
            all_implies.update(implied_choice.implies)
        return list(all_implies)

    @property
    def implies(self):
        if self._implies is None:
            self._implies = self._build_implies()
        return self._implies

    def _build_implied_by(self):
        if not self._choices_with_meta:
            raise ValueError('Can not use the "implied_by" property before the choice has '
                             'been added to a MultipleChoicesWithMeta.')
        implied_by = set()
        for choice in self._choices_with_meta.iterchoices():
            if self.value in choice.implies:
                implied_by.add(choice.value)
        return list(implied_by)

    @property
    def implied_by(self):
        if self._implied_by is None:
            self._implied_by = self._build_implied_by()
        return self._implied_by

    @property
    def value_and_implied_by(self):
        values = {self.value}
        values.update(self.implied_by)
        return list(values)

    def as_serializable_data(self):
        data = super().as_serializable_data()
        data['implies'] = list(sorted(self.implies))
        data['implied_by'] = list(sorted(self.implied_by))
        return data


class SerializableChoicesWithMeta(choices_with_meta.ChoicesWithMeta):
    """
    Extends :class:`ievv_opensource.utils.choices_with_meta.ChoicesWithMeta` with
    support for serializing choices.
    """
    @property
    def classpath(self):
        return '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)

    def iterchoices_for_as_serializable_data(self):
        """
        This is here so that subclasses can filter the
        choices exposed via the APIs. This is called by
        :meth:`.as_serializable_data` to loop the choices
        to serialize, and those serialized choices are
        exposed in the APIs.
        """
        return self.iterchoices()

    def as_serializable_data(self):
        """
        Get as a serializable list of choices.
        """
        result = []
        for choice in self.iterchoices_for_as_serializable_data():
            result.append(choice.as_serializable_data())
        return result

    def validate_choice(self, choice):
        if not isinstance(choice, SerializableChoice):
            raise TypeError(
                f'Can only add objects of the '
                f'{SerializableChoice.get_classpath()} type '
                f'(or a subclass) to a SerializableChoicesWithMeta.')

    def add(self, choice):
        self.validate_choice(choice=choice)
        super().add(choice)

    def get_model_attribute_name(self):
        raise NotImplementedError()

    def clean_choice(self, choice, model_object):
        raise NotImplementedError()

    def clean_model_object(self, model_object):
        from django.utils.translation import ugettext
        value = getattr(model_object, self.get_model_attribute_name())
        if value not in self:
            raise ValidationError({
                self.get_model_attribute_name(): ugettext('"%(value)s" is not one of the available choices') % {
                    'value': value
                }
            })
        choice = self[value]
        self.clean_choice(choice, model_object)

    def validate_setup(self, **kwargs):
        """
        Validate that this ChoicesWithMeta contains sane choices.

        Can both raise exceptions (typically :exc:`.ChoiceSetupError`) and
        log warnings depending on the severity of the problems discovered.

        This is typically called from the ready() method of an AppConfig.

        By default, this just loops over all the choices and
        call :meth:`.SerializableChoice.validate_setup`.
        """
        for choice in self.iterchoices():
            choice.validate_setup(choiceswithmeta_object=self, **kwargs)


class SerializableMultiChoicesWithMeta(SerializableChoicesWithMeta):
    """
    ChoicesWithMeta class with special handling of multichoice fields.

    The choices added must be :class:`.SerializableMultiChoice` objects.
    """
    def normalize_values(self, values):
        """
        Normalize the provided ``values``, removing any values that is implied by another value.
        """
        values = set(values)
        implies = set()
        for permission in values:
            implies.update(self[permission].implies)
        return values - implies

    def validate_choice(self, choice):
        if not isinstance(choice, SerializableMultiChoice):
            raise TypeError(
                f'Can only add objects of the '
                f'{SerializableMultiChoice.get_classpath()} type '
                f'(or a subclass) to a SerializableMultiChoicesWithMeta.')
        if choice._choices_with_meta is not None:
            raise ValueError('Can not add the same Choice object to multiple ChoicesWithMeta.')

    def add(self, choice):
        super().add(choice)
        choice._choices_with_meta = self

    def clean_model_object(self, model_object):
        from django.utils.translation import ugettext
        for value in getattr(model_object, self.get_model_attribute_name()):
            if value not in self:
                raise ValidationError({
                    self.get_model_attribute_name(): ugettext('"%(value)s" is not one of the available choices') % {
                        'value': value
                    }
                })
        setattr(
            model_object, self.get_model_attribute_name(),
            self.normalize_values(getattr(model_object, self.get_model_attribute_name()))
        )
        for value in getattr(model_object, self.get_model_attribute_name()):
            choice = self[value]
            self.clean_choice(choice, model_object)

        # Maintain sort order to keep the values clean in the database and APIs
        values = list(getattr(model_object, self.get_model_attribute_name()))
        values.sort()
        setattr(model_object, self.get_model_attribute_name(), values)
