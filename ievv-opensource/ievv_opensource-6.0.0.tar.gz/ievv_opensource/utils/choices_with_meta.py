from collections import OrderedDict


class Choice(object):
    """
    A choice in a :class:`.ChoicesWithMeta`.

    This basic choice class supports value, label and description,
    but you should subclass this (and possibly also :class:`.ChoicesWithMeta`)
    if you need more metadata.

    .. attribute:: value

        The value which is typically stored in the database, or
        sent as the actual POST data value in forms.

    .. attribute:: label

        A short user-friendly label for the choice.

    .. attribute:: description

        A user-friendly longer description of the choice.
    """
    def __init__(self, value, label=None, description='',
                 attributename=None):
        """
        Args:
            value: The value for the choice.
                The value which is typically stored in the database, or
                sent as the actual POST data value in forms.
            label: A user-friendly short label for the choice.
                This is normally marked for translation.
                Defaults to ``value`` if ``bool(label) == False``.
            description: A user-friendly longer description of the choice.
                This is normally marked for translation.
                Not required.
        """
        self.value = value
        self.label = label or value
        self.description = description
        if attributename is None:
            self.attributename = self._value_to_attributename(value)
        else:
            self.attributename = attributename

    @classmethod
    def get_classpath(cls):
        return f'{cls.__module__}.{cls.__name__}'

    @property
    def classpath(self):
        return self.__class__.get_classpath()

    def _value_to_attributename(self, value):
        valuestring = str(value)
        attributename = valuestring.upper().replace('-', '_').replace(' ', '_')
        if len(attributename) > 0 and attributename[0].isdigit():
            attributename = '_{}'.format(attributename)
        return attributename

    def get_short_label(self):
        """
        Get a short label for the choice.

        Defaults to returning :attr:`~.Choice.label`, but you
        can override this in subclasses.
        """
        return self.label

    def get_long_label(self):
        """
        Get a long label for the choice.

        Generating by joining :attr:`~.Choice.label` and :attr:`~.Choice.description`
        with ``" - "``.
        """
        if self.description:
            return '{} - {}'.format(self.label, self.description)
        else:
            return self.label

    def __str__(self):
        return self.value

    @property
    def translated_label(self):
        from django.utils.translation import ugettext
        return ugettext(self.label)

    @property
    def translated_description(self):
        from django.utils.translation import ugettext
        return ugettext(self.description)

    def as_serializable_data(self):
        return {
            'value': self.value,
            'label': self.translated_label,
            'description': self.translated_description
        }


class ChoicesWithMeta(object):
    """
    An object oriented structure for model/form field choices.

    Unlike the simple ``(value, label)`` tuple used in
    Django, this miniframework supports more metadata because
    the choices are defined through :class:`.Choice` (which you can subclass
    and extend).

    Compatible with the ``choices``-attribute used in Django
    (I.E.: django.forms.ChoiceField, django.forms.CharField, ...)
    through the :meth:`~.ChoicesWithMeta.iter_as_django_choices_short`
    and :meth:`~.ChoicesWithMeta.iter_as_django_choices_long` methods.

    Examples:

        Usage in Django model::

            class User(models.Model):
                username = models.CharField(max_length=255, unique=True)

                USERTYPE_CHOICES = choices_with_meta.ChoicesWithMeta(
                    choices_with_meta.Choice(value='normal', label='Normal'),
                    choices_with_meta.Choice(value='editor', label='Editor'),
                    choices_with_meta.Choice(value='admin', label='Admin')
                )

                usertype = models.CharField(
                    max_length=255,
                    choices=USERTYPE_CHOICES.iter_as_django_choices_short,
                    default=USERTYPE_CHOICES.NORMAL
                )

        Lets say you want to provivide a bit more information about
        each choice. Then you can use the ``description`` parameter
        for :class:`.Choice`::

            choices_with_meta.Choice(
                value='admin',
                label='Admin',
                description='An administrator user with access to everything.')

        You will most likely also want to update the ``choices``-argument for
        your choice field to use :meth:`~.ChoicesWithMeta.iter_as_django_choices_long`
        (to include description in the default label), or you may just want
        to do that in certain views. You can also extend the :class:`Choice class<.Choice>`
        and add your own logic in :meth:`.get_long_label` and :meth:`.get_short_label`.

        ChoicesWithMeta makes it easier to provide good exception messages::

            if "somechoice" not in User.USERTYPE_CHOICES:
                raise ValidationError({
                    'usertype': 'Must be one of: {}'.format(
                        User.USERTYPE_CHOICES.get_values_as_commaseparated_string()
                    )
                })

        Getting choices by value is easy::

            User.USERTYPE_CHOICES['admin'].label

        You can access values as an attribute of the ChoicesWithMeta object
        as the value uppercased with ``-`` and space replaced with ``_``::

            User.USERTYPE_CHOICES.ADMIN.label

        Getting choices by index is also easy::

            User.USERTYPE_CHOICES.get_choice_at_index(1).label

        Getting the first choice (typically the default choice) is easy::

            User.USERTYPE_CHOICES.get_first_choice()

        You can iterate over the choices or values::

            for choice in User.USERTYPE_CHOICES.iterchoices():
                pass

            for value in User.USERTYPE_CHOICES.itervalues():
                pass

        You can get the values as a list or as a comma separated string::

            User.USERTYPE_CHOICES.get_values_as_list()
            User.USERTYPE_CHOICES.get_values_as_commaseparated_string()
    """
    def __init__(self, *choices):
        self.choices = OrderedDict()
        for choice in self.get_default_choices():
            self.add(choice)
        for choice in choices:
            self.add(choice)

    def get_by_value(self, value, fallback=None):
        """
        Get the :class:`.Choice` with the provided ``value``.

        Args:
            value: The value to lookup.
            fallback: Fallback value if ``value`` is not registered as a choice value.

        Returns:
            .Choice: The Choice matching the value if it exists, otherwise return ``fallback``.
        """
        return self.choices.get(value, fallback)

    def __getitem__(self, value):
        """
        Get the :class:`.Choice` with the provided ``value``.

        Raises:
            KeyError: If no :class:`.Choice` with the provided
                ``value`` is in the ChoicesWithMeta.
        """
        return self.choices[value]

    def __contains__(self, value):
        """
        Check if ``value`` is one of the choices.

        Returns:
            bool: True a :class:`.Choice` with the provided ``value``
                is in the ChoicesWithMeta.
        """
        return value in self.choices

    def __len__(self):
        """
        Get the number of choices.
        """
        return len(self.choices)

    def get_default_choices(self):
        """
        Lets say you have a field where a set of default choices
        make sense. You then create a subclass of ChoicesWithMeta
        and override this method to return these default choices.

        Developers can still override this method for special
        cases, but the default will be that these default choices
        are included.

        This is most useful when choices are a Django setting
        that users of your app can override.

        Returns:
            iterable: An iterable of :class:`.Choice` objects.
        """
        return []

    def get_choice_at_index(self, index):
        """
        Args:
            index: The numeric index of the choice.

        Raises:
            IndexError: If the index does not correspond to a choice.

        Returns:
            .Choice: The :class:`.Choice` at the provided index.
        """
        keys = list(self.choices.keys())
        value = keys[index]
        return self.choices[value]

    def get_first_choice(self):
        """
        Uses :meth:`.get_choice_at_index` to get the first (index=0) choice.
        If there is no first choice, ``None`` is returned.
        """
        try:
            return self.get_choice_at_index(0)
        except IndexError:
            return None

    def add(self, choice):
        """
        Add a :class:`.Choice`.

        Args:
            choice: A :class:`.Choice` object.
        """
        if choice.value in self.choices:
            raise KeyError('A choice with value "{}" alredy exists.'.format(choice.value))
        self.choices[choice.value] = choice
        setattr(self, choice.attributename, choice)

    def remove(self, value):
        """
        Remove a choice by value.

        Args:
            value: The value to remove from the ChoicesWithMeta.
        """
        if value in self.choices:
            attributename = self.choices[value].attributename
            delattr(self, attributename)
            del self.choices[value]
        else:
            raise KeyError('{value} is not a valid choice value.'.format(value=value))

    def itervalues(self):
        """
        Iterate over the choices yielding only the values in the added order.
        """
        return self.choices.keys()

    def iterchoices(self, *extra_choices):
        """
        Iterate over the choices yielding :class:`.Choice` objects in the added order.

        Args:
            *extra_choices: Extra choices. Zero or more extra choices (:class:`.Choice` objects) to
                yield at the end. Can be used in cases where you allow invalid choices if they are
                already set (so you want to include the current invalid choice along with the
                correct choices).
        """
        for choice in self.choices.values():
            yield choice
        for choice in extra_choices:
            yield choice

    def iter_as_django_choices_short(self, *extra_choices):
        """
        Iterate over the choices as a Django choices list,
        where each item is a ``(value, label)``-tuple.

        Uses :meth:`.Choice.get_short_label` to create the ``label``.

        Args:
            *extra_choices: See :meth:`.iterchoices`.
        """
        for choice in self.iterchoices(*extra_choices):
            yield choice.value, choice.get_short_label()

    def iter_as_django_choices_long(self, *extra_choices):
        """
        Iterate over the choices as a Django choices list,
        where each item is a ``(value, label)``-tuple.

        Uses :meth:`.Choice.get_long_label` to create the ``label``.

        Args:
            *extra_choices: See :meth:`.iterchoices`.
        """
        for choice in self.iterchoices(*extra_choices):
            yield choice.value, choice.get_long_label()

    def get_values_as_list(self):
        """
        Get the values of all choices in the added order as a list.
        """
        return list(self.itervalues())

    def get_values_as_commaseparated_string(self):
        """
        Get the values as a comma-separated string.

        Perfect for showing available choices in error messages.

        Returns:
            String with all the values separated by comma.
        """
        return ', '.join(self.itervalues())

    def __str__(self):
        return 'ChoicesWithMeta({})'.format(self.get_values_as_commaseparated_string())
