# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
import re

from django.conf import settings

from ievv_opensource.utils.singleton import Singleton
import gsm0338  # registers the gsm03.38 text encoder used in get_sms_text_length


class AbstractSmsBackend(object):
    """
    Base class for SMS backends.

    An instance of this class is created each time an SMS is created.

    This means that you can store temporary information related
    to building the SMS on ``self``.

    Example (simple print SMS backend)::

        class PrintBackend(sms_registry.AbstractSmsBackend):
            @classmethod
            def get_backend_id(cls):
                return 'print'

            def send(self):
                print(
                    'Phone number: {phone_number}. '
                    'Message: {message}'.format(
                        phone_number=self.cleaned_phone_number,
                        message=self.cleaned_message
                    )
                )

    To use the PrintBackend, add it to the registry via an AppConfig for your
    Django app::

        from django.apps import AppConfig

        class MyAppConfig(AppConfig):
            name = 'myapp'

            def ready(self):
                from ievv_opensource.ievv_sms import sms_registry
                from myapp import sms_backends
                sms_registry.Registry.get_instance().add(sms_backends.PrintBackend)

    Now you can use the backend to send an SMS::

        from ievv_opensource.ievv_sms import sms_registry
        sms_registry.Registry.get_instance().send(
            phone_number='12345678',
            message='This is a test',
            backend_id='print')

    You can also set the backend as the default backend
    for SMS sending by adding ``IEVV_SMS_DEFAULT_BACKEND_ID = 'print'`` to
    your django settings. With this setting you can call send()
    without the ``backend_id`` argument, and the SMS will be sent
    with the print backend.
    """
    STRIP_WHITESPACE_PATTERN = re.compile(r'\s+')

    @classmethod
    def get_max_length(cls):
        return 153 * 6

    @classmethod
    def get_sms_text_length(cls, text):
        return len(text.encode('gsm03.38', errors='replace'))

    @classmethod
    def get_part_count(cls, text):
        sms_text_length = cls.get_sms_text_length(text)
        if sms_text_length <= 160:
            return 1
        return int(math.ceil(sms_text_length / 153))

    @classmethod
    def get_backend_id(cls):
        """
        The ID this backend will get get in the :class:`.Registry` singleton.

        Defaults to the full python path for the class.
        """
        return '{}.{}'.format(cls.__module__, cls.__name__)

    @classmethod
    def validate_backend_setup(cls):
        """
        Validate backend setup (required settings, etc).

        Raises:
            .SmsBackendSetupError: When the setup validation fails.
        """

    def __init__(self, phone_number, message, send_as=None, **kwargs):
        """
        All the arguments are forwarded from :meth:`.Registry.send` /
        :meth:`.Registry.make_backend_instance`.

        Args:
            phone_number (str): The phone number to send the message to.
            message (str): The message to send.
            **kwargs: Extra kwargs. Both for future proofing, and
                to make it possible for backends to support extra
                kwargs.
        """
        self.phone_number = phone_number
        self.message = message
        self.send_as = send_as
        self.kwargs = kwargs

    def clean_phone_number(self, phone_number):
        """
        Clean/validate the phone number.

        By default this does nothing. It is here for backends
        that need to format phone numbers in a specific way.

        Args:
            phone_number (str): The phone number to clean.

        Raises:
             django.core.exceptions.ValidationError: If validation of the phone number fails.

        Returns:
            str: The cleaned phone number.
        """
        return phone_number

    def clean_message(self, message):
        """
        Clean/validate the message.

        By default this does nothing. It is here for backends
        that need to format or validate the message in a specific way.

        Args:
            message (str): The message to clean.

        Raises:
             django.core.exceptions.ValidationError: If validation of the message fails.

        Returns:
            str: The cleaned message.
        """
        return message

    def clean(self):
        """
        Clean the phone number, message, and kwargs.

        Calls :meth:`.clean_phone_number` and :meth:`.clean_message`.

        If you need to clean extra kwargs, you should override this method,
        but make sure you call ``super().clean()``.

        Raises:
             django.core.exceptions.ValidationError: If validation fails.
        """
        self.cleaned_phone_number = self.clean_phone_number(phone_number=self.phone_number)
        self.cleaned_message = self.clean_message(message=self.message)

    def send(self):
        """
        Send the message.

        Must be overridden in subclasses.

        Should send ``self.cleaned_message`` to ``self.cleaned_phone_number``.
        """
        raise NotImplementedError()

    def __str__(self):
        return '{}.{}(phone_number={!r}, message={!r}, kwargs={!r})'.format(
            self.__class__.__module__, self.__class__.__name__,
            self.phone_number, self.message, self.kwargs
        )

    def __repr__(self):
        return str(self)


class Registry(Singleton):
    """
    Registry of :class:`.AbstractSmsBackend` objects.
    """

    def __init__(self):
        super(Registry, self).__init__()
        self._backend_class_map = {}

    def add(self, backend_class):
        """
        Add the given ``backend_class`` to the registry.

        Parameters:
            backend_class: A subclass of :class:`.AbstractSmsBackend`.
        """
        backend_id = backend_class.get_backend_id()
        if backend_id in self._backend_class_map:
            raise ValueError('{!r} is already in the SMS backend registry.'.format(
                backend_id))
        self._backend_class_map[backend_id] = backend_class

    def remove_by_backend_id(self, backend_id):
        """
        Remove the backend class with the provided ``backend_id`` from the registry.
        """
        del self._backend_class_map[backend_id]

    def remove(self, backend_class):
        """
        Remove the provided backend class from the registry.
        """
        self.remove_by_backend_id(backend_class.get_backend_id())

    def __contains__(self, backend_class):
        """
        Returns ``True`` if the provided backend_class is in the registry.

        Parameters:
            backend_class: A subclass of :class:`.AbstractSmsBackend`.
        """
        return backend_class.get_backend_id() in self._backend_class_map

    def __iter__(self):
        """
        Returns an iterator over all backend classes in the registry.

        Same as :meth:`.iter_backend_classes`.
        """
        return self.iter_backend_classes()

    def iter_backend_classes(self):
        """
        Returns an iterator over all backend classes in the registry.
        """
        return iter(self._backend_class_map.values())

    def get_default_backend_id(self):
        """
        Get the default backend ID.

        Retrieved from the :setting:`IEVV_SMS_DEFAULT_BACKEND_ID` setting.

        Defaults to ``debugprint`` if the setting is not defined, or if it
        boolean False (None, empty string, ...).
        """
        return getattr(settings, 'IEVV_SMS_DEFAULT_BACKEND_ID', None) or 'debugprint'

    def get_backend_class_by_id(self, backend_id):
        """
        Get backend class by ID.

        Args:
            backend_id (str): The backend ID. If this is ``None``, we use
                the default backend (see :meth:`.get_default_backend_id`)
        """
        if backend_id is None:
            backend_id = self.get_default_backend_id()
        return self._backend_class_map[backend_id]

    def make_backend_instance(self, phone_number, message, backend_id=None, **kwargs):
        """
        Make a backend instance. Does not send the message.

        Args:
            phone_number (str): The phone number to send the message to.
            message (str): The message to send.
            backend_id (str): The ID of the backend to use for sending.
                If this is ``None``, we use the default backend
                (see :meth:`.get_default_backend_id`).
            **kwargs: Extra kwargs for the :class:`.AbstractSmsBackend`
                constructor.

        Returns:
            .AbstractSmsBackend: An instance of a subclass of :class:`.AbstractSmsBackend`.
        """
        backend_class = self.get_backend_class_by_id(backend_id=backend_id)
        backend = backend_class(phone_number=phone_number, message=message, **kwargs)
        return backend

    def send(self, phone_number, message, backend_id=None, **kwargs):
        """
        Send an SMS message.

        Shortcut for ``make_backend_instance(...).send()``.

        See :meth:`.make_backend_instance`.

        Args:
            phone_number: See :meth:`.make_backend_instance`.
            message: See :meth:`.make_backend_instance`.
            backend_id: See :meth:`.make_backend_instance`.
            **kwargs: See :meth:`.make_backend_instance`.

        Raises:
             django.core.exceptions.ValidationError: If validation of the phone number,
                message or kwargs fails.

        Returns:
            .AbstractSmsBackend: An instance of a subclass of :class:`.AbstractSmsBackend`.
        """
        backend = self.make_backend_instance(
            phone_number=phone_number, message=message,
            backend_id=backend_id, **kwargs)
        backend.clean()
        backend.send()
        return backend

    def get_backend_class(self, backend_id=None):
        if not backend_id:
            backend_id = self.get_default_backend_id()
        return self._backend_class_map[backend_id]


class MockableRegistry(Registry):
    """
    A non-singleton version of :class:`.Registry`. For tests.

    Typical usage in a test::

        from ievv_opensource.ievv_sms import sms_registry

        class MockSmsBackend(sms_registry.AbstractSmsBackend):
            def send(self):
                print('{}: {}'.format(self.clean_phone_number, self.cleaned_message))

        mockregistry = sms_registry.MockableRegistry()
        mockregistry.add(MockSmsBackend)

        with mock.patch('ievv_opensource.ievv_sms.sms_registry.Registry.get_instance',
                        lambda: mockregistry):
            pass  # ... your code here ...
    """

    def __init__(self):
        self._instance = None  # Ensure the singleton-check is not triggered
        super(MockableRegistry, self).__init__()


def send_sms(phone_number, message, backend_id=None, **kwargs):
    """
    Send SMS message.

    Just a shortcut for :meth:`.Registry.send`
    (``Registry.get_instance().send(...)``).

    Args:
        phone_number (str): The phone number to send the message to.
        message (str): The message to send.
        backend_id (str): The ID of the backend to use for sending.
            If this is ``None``, we use the default backend
            (see :meth:`.get_default_backend_id`).
        **kwargs: Extra kwargs for the :class:`.AbstractSmsBackend`
            constructor.

    Returns:
        .AbstractSmsBackend: An instance of a subclass of :class:`.AbstractSmsBackend`.
    """
    return Registry.get_instance().send(
        phone_number=phone_number,
        message=message,
        backend_id=backend_id,
        **kwargs)


def get_sms_part_count(message, backend_id=None):
    backend_class = Registry.get_instance().get_backend_class(backend_id=backend_id)
    return backend_class.get_part_count(message)


def get_sms_text_length(message, backend_id=None):
    backend_class = Registry.get_instance().get_backend_class(backend_id=backend_id)
    return backend_class.get_sms_text_length(message)


def get_sms_max_length(backend_id=None):
    backend_class = Registry.get_instance().get_backend_class(backend_id=backend_id)
    return backend_class.get_max_length()
