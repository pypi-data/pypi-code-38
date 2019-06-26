import collections
import inspect
import typing

import dataclasses
import aspy
import django.urls.base
import django.urls.resolvers
import django.utils.encoding
import django.utils.regex_helper
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals, Model
from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor,
    ReverseManyToOneDescriptor,
    ManyToManyDescriptor,
    ReverseOneToOneDescriptor,
)
from django.utils.translation import ugettext_lazy as _

from django_vox import settings, base
from django_vox.backends.base import AttachmentData, Backend, load_backend

PROTOCOLS = {
    "email": _("Email"),
    "sms": _("SMS"),
    "slack-webhook": _("Slack Webhook"),
    "json-webhook": _("JSON Webhook"),
    "twitter": _("Twitter"),
    "xmpp": _("XMPP"),
    "activity": _("Activity Stream"),
}

PREFIX_NAMES = {
    "si": _("Site Contacts"),
    "c": "__content__",
    "se": _("Actor"),
    "re": _("Target"),
}
PREFIX_FORMATS = {"c": "{}", "se": _("Actor's {}"), "re": _("Target's {}")}

_CHANNEL_TYPE_IDS = None


def make_activity_object(obj):
    iri = None
    address_func = getattr(obj, "get_object_address", None)
    if address_func is not None:
        iri = obj.get_object_address()
    if iri is None:
        if hasattr(obj, "get_absolute_url"):
            part_iri = obj.get_absolute_url()
        else:
            part_iri = objects[obj.__class__].reverse(obj)
        if part_iri is not None:
            iri = base.full_iri(part_iri)
    name = str(obj)
    if iri is None:
        return aspy.Object(name=name)
    else:
        return aspy.Object(name=name, id=iri)


class ObjectNotFound(Exception):
    pass


class BackendManager:
    def __init__(self, class_list):
        self.proto_map = collections.defaultdict(list)
        self.id_map = {}
        for cls in class_list:
            if cls.ID in self.id_map:
                raise RuntimeError("Conflicting backend IDs: {}".format(cls.ID))
            self.proto_map[cls.PROTOCOL].append(cls)
            self.id_map[cls.ID] = cls

    def by_protocol(self, protocol: str) -> typing.List[Backend]:
        return self.proto_map[protocol]

    def by_id(self, id_val) -> Backend:
        return self.id_map[id_val]

    def all(self) -> typing.List[Backend]:
        return self.id_map.values()

    def protocols(self):
        return self.proto_map.keys()


ChannelFunc = typing.TypeVar(
    "ChannelFunc", typing.Callable[[Model], typing.List[Model]], None
)


@dataclasses.dataclass
class Channel:
    name: str
    target_class: type
    func: ChannelFunc

    @classmethod
    def self(cls, obj):
        return Channel("", obj.model, None)

    @classmethod
    def field(cls, field):
        # many → 1 & 1 → 1
        if isinstance(field, ForwardManyToOneDescriptor):
            field_name = field.field.name
            field_model = field.field.model
            field_label = field.field.verbose_name.title()
        # 1 ← 1
        elif isinstance(field, ReverseOneToOneDescriptor):
            field_name = field.related.related_name
            field_model = field.related.related_model
            field_label = field_name.replace("_", " ").title()
        # many → many & many ← many
        elif isinstance(field, ManyToManyDescriptor):
            if field.reverse:
                field_name = field.rel.related_name
                field_model = field.rel.related_model
                field_label = field_name.replace("_", " ").title()
            else:
                field_name = field.field.name
                field_model = field.field.model
                field_label = field.field.verbose_name.title()
        # many ← 1
        else:
            assert isinstance(field, ReverseManyToOneDescriptor)
            field_name = field.rel.related_name
            field_model = field.rel.related_model
            field_label = field_name.replace("_", " ").title()

        def func(model):
            if isinstance(field, ReverseManyToOneDescriptor):
                # many ← 1 & many → many & many ← many
                return getattr(model, field_name).all()
            else:
                # many → 1 & 1 → 1 & 1 ← 1
                return (getattr(model, field_name),)

        return Channel(field_label, field_model, func)


class BoundChannel:
    def __init__(self, ubc: Channel, obj: Model):
        self.name = ubc.name
        self.target_class = ubc.target_class
        self.func = ubc.func
        self.obj = obj

    def contactables(self) -> typing.List[Model]:
        return (self.obj,) if self.func is None else self.func(self.obj)


class UnboundChannelMap(dict):
    def bind(self, obj):
        return BoundChannelMap(
            ((key, BoundChannel(ubc, obj)) for (key, ubc) in self.items())
        )


class BoundChannelMap(dict):
    pass


class ChannelManagerItem:
    def __init__(self, cls):
        self.cls = cls
        self.__prefixes = {}
        self._channels = collections.defaultdict(dict)

    def __bool__(self):
        return bool(self._channels)

    def add(self, key, name, target_type, func):
        self._channels[key] = name, target_type, func
        self.__prefixes = {}

    def add_self(self):
        self.add("", "", self.cls, None)

    def prefix(self, prefix) -> UnboundChannelMap:
        # get channels by prefix
        if prefix not in self.__prefixes:
            ubc_map = UnboundChannelMap()
            for key, (name, cls, func) in self._channels.items():
                channel_key = prefix if key == "" else prefix + ":" + key
                if name == "":
                    name = PREFIX_NAMES[prefix]
                    if name == "__content__":
                        name = self.cls._meta.verbose_name.title()
                else:
                    name = PREFIX_FORMATS[prefix].format(name)
                ubc_map[channel_key] = Channel(name, cls, func)
            self.__prefixes[prefix] = ubc_map
        return self.__prefixes[prefix]


class Attachment:
    def __init__(
        self, attr: str = None, mime_attr: str = "", mime_string: str = "", label=""
    ):
        self.key = ""  # gets set later
        self.attr = attr
        if bool(mime_attr) == bool(mime_string):
            raise RuntimeError("Either mime_attr must be set or mime_string (not both)")
        self.mime_attr = mime_attr
        self.mime_string = mime_string
        self._label = label

    @property
    def label(self):
        return self._label if self._label else self.key

    def _get_field(self, model_instance, field_name):
        if hasattr(model_instance, field_name):
            result = getattr(model_instance, field_name)
        else:
            registration = objects[model_instance.__class__].registration
            result = getattr(registration, field_name)
        return result(model_instance) if callable(result) else result

    def get_data(self, model_instance: Model):
        data = self._get_field(model_instance, self.attr)
        # force bytes
        if not isinstance(data, bytes):
            if not isinstance(data, str):
                data = str(data)
            data = data.encode()
        if self.mime_attr:
            mime = self._get_field(model_instance, self.mime_attr)
        else:
            mime = self.mime_string
        return AttachmentData(data, mime)


class Notification:
    REQUIRED_PARAMS = {"codename", "description"}
    OPTIONAL_PARAMS = {
        "actor_type": "",
        "target_type": "",
        "activity_type": "Create",
        "required": False,
    }

    def __init__(self, description, codename="", **kwargs):
        self.params = {
            "codename": codename,
            "description": description,
            "from_code": True,
        }
        for key, default in self.OPTIONAL_PARAMS.items():
            if key in kwargs:
                self.params[key] = kwargs.pop(key)
            else:
                self.params[key] = default
        if kwargs:
            raise ValueError(
                "Unrecognized parameters {}".format(", ".join(kwargs.keys()))
            )

    def params_equal(self, notification):
        for key in self.params:
            value = getattr(notification, key)
            my_value = self.params[key]
            if key in ("actor_type", "target_type"):
                if value is None:
                    value = ""
                else:
                    value = "{}.{}".format(value.app_label, value.model)
            # if key == 'activity_type':
            #     value = value.get_type()
            if value != my_value:
                return False
        return True

    def param_value(self, key):
        value = self.params[key]
        if key in ("actor_type", "target_type"):
            if value == "":
                return None
            model = apps.get_model(value)
            return ContentType.objects.get_for_model(model)
        if key == "activity_type":
            if inspect.isclass(value) and issubclass(value, aspy.Object):
                value = value.get_type()
        return value

    def set_params(self, notification):
        for key in self.params:
            setattr(notification, key, self.param_value(key))

    @property
    def codename(self):
        return self.params["codename"]

    def get_notification(self, model):
        from .models import Notification

        ct = ContentType.objects.get_for_model(model)
        return Notification.objects.get(codename=self.codename, object_type=ct)

    def issue(self, object_, *, actor=None, target=None):
        notification = self.get_notification(object_)
        notification.issue(object_, actor=actor, target=target)


def provides_contacts(protocol_id):
    def inner(func):
        sig = inspect.signature(func)
        assert len(sig.parameters) == 3 or (
            len(sig.parameters) < 3
            and any(
                (
                    p.kind == inspect.Parameter.VAR_POSITIONAL
                    for p in sig.parameters.values()
                )
            )
        ), (
            "Function decorated by provides_contacts must take 3 arguments (self, "
            "model instance, and notification)"
        )

        func._vox_provides_contacts = protocol_id
        return func

    return inner


class RegistrationBase(type):
    """
    Metaclass for Vox extensions.
    """

    def __new__(mcs, name, bases, attributes):
        new = super().__new__(mcs, name, bases, attributes)

        proto_func = {}
        attachment_dict = {}
        notification_dict = {}
        for key, value in attributes.items():
            if isinstance(value, Attachment):
                if value.key == "":
                    value.key = key
                attachment_dict[key] = value
            elif isinstance(value, Notification):
                if value.codename == "":
                    value.params["codename"] = key
                notification_dict[key] = value
            rec_proto = getattr(value, "_vox_provides_contacts", None)
            if rec_proto is not None:
                proto_func[rec_proto] = value
        if proto_func:
            new._protocol_functions = new._protocol_functions.copy()
            new._protocol_functions.update(proto_func)
        if attachment_dict:
            new._attachments = new._attachments.copy()
            new._attachments.update(attachment_dict)
        if notification_dict:
            new._notifications = new._notifications.copy()
            new._notifications.update(notification_dict)
        return new


class Registration(metaclass=RegistrationBase):
    """
    A base class for Vox definitions

    instance attributes:

    - model: a django model that will serve as the object type for all of the
        attached notifications

    """

    _protocol_functions = {}
    _attachments = {}
    _notifications = {}

    def __init__(self, model):
        self.model = model

    def get_attachments(self) -> typing.List[Attachment]:
        return self._attachments.values()

    def get_attachment(self, key) -> Attachment:
        return self._attachments.get(key)

    def get_notifications(self) -> typing.List[Notification]:
        return self._notifications.values()

    def get_notification(self, key) -> Notification:
        return self._notifications.get(key)

    def get_channels(self) -> typing.Mapping[str, Channel]:
        return {}

    def has_channels(self):
        return bool(self.get_channels())

    def get_supported_protocols(self):
        return self._protocol_functions.keys()

    def get_contacts(self, instance, protocol, notification):
        func = self._protocol_functions.get(protocol, None)
        if func is None:
            return ()
        name = str(instance)
        for result in func(self, instance, notification):
            if not isinstance(result, base.Contact):
                result = base.Contact(name, protocol, result)
            yield result

    def get_activity_object(self, instance, *, codename=None, actor=None, target=None):
        """
        Gets the activity object for instance.

        Note that sometimes this is called with a specific codename (and maybe actor
        or target). This lets you vary the way the object is represented in different
        notifications.
        """
        if hasattr(instance, "get_activity_object"):
            return instance.get_activity_object(codename, actor, target)
        if hasattr(instance, "__activity__"):
            return instance.__activity__()
        return make_activity_object(instance)

    def has_activity_endpoint(self, instance):
        return False

    @staticmethod
    def _get_object_address(obj):
        url = objects[obj.__class__].reverse(obj)
        if url is None:
            return None
        else:
            return base.full_iri(url)


class _ModelRegistration(Registration):
    def __init__(self, model):
        super().__init__(model)
        meta = model._vox_meta
        notification_dict = self._notifications.copy()

        for notification in meta.notifications:
            notification_dict[notification.codename] = notification
        self._notifications = notification_dict


class SignalRegistration(Registration):
    """
    A Notification registration that automatically connects model signals
    """

    created = Notification(_("Notification that an instance was created."))
    updated = Notification(_("Notification that an instance was updated."))
    deleted = Notification(_("Notification that an instance was updated."))

    def __init__(self, model):
        super().__init__(model)
        signals.post_save.connect(self._model_post_save, sender=model)
        signals.post_delete.connect(self._model_post_delete, sender=model)

    def _model_post_save(self, instance, raw, created, **_kw):
        if not raw:
            if created:
                self.created.issue(instance)
            else:
                self.updated.issue(instance)

    def _model_post_delete(self, instance, **_kw):
        self.deleted.issue(instance)


class ObjectManagerItem:
    def __init__(self, cls, registration: Registration):
        self.cls = cls
        self.registration = registration
        self.pattern = None
        self.matcher = None
        self.reverse_form = None
        self.reverse_params = ()
        self.channels = ChannelManagerItem(cls)

    # url methods

    @property
    def has_url(self):
        return self.matcher is not None

    def set_regex(self, pattern: str):
        self.pattern = pattern
        if hasattr(django.urls.resolvers, "RegexPattern"):
            self.matcher = django.urls.resolvers.RegexPattern(pattern)
        else:
            self.matcher = django.urls.resolvers.RegexURLPattern(pattern, None)
        normal = django.utils.regex_helper.normalize(pattern)
        self.reverse_form, self.reverse_params = next(iter(normal), ("", ()))

    def match(self, path: str):
        if self.matcher is None:
            return False
        if hasattr(django.urls.resolvers, "RegexPattern"):
            return self.matcher.match(path)
        return self.matcher.resolve(path)

    def reverse(self, obj):
        if self.reverse_form is None:
            return None
        kwargs = dict(
            ((param, getattr(obj, param, None)) for param in self.reverse_params)
        )
        return "/" + (self.reverse_form % kwargs)

    # channel methods

    def channels_by_prefix(self, prefix) -> UnboundChannelMap:
        # get the old channels
        ubc_map = self.channels.prefix(prefix)
        # overwrite old channels with any new ones
        for key, channel in self.registration.get_channels().items():
            channel_key = prefix if key == "" else prefix + ":" + key
            if channel.name == "":
                if prefix == "c":
                    channel.name = self.cls._meta.verbose_name.title()
                else:
                    channel.name = PREFIX_NAMES[prefix]
            else:
                channel.name = PREFIX_FORMATS[prefix].format(channel.name)
            ubc_map[channel_key] = channel
        return ubc_map

    def has_channels(self):
        return bool(self.channels) or self.registration.has_channels()


class ObjectManager(dict):
    def __missing__(self, key):
        item = ObjectManagerItem(key, Registration(key))
        self[key] = item
        return item

    def __setitem__(self, key, value: ObjectManagerItem):
        super().__setitem__(key, value)

    def __getitem__(self, key) -> ObjectManagerItem:
        return super().__getitem__(key)

    def add(self, cls, registration_cls=Registration, *, regex=...):
        if regex is ...:
            raise RuntimeError(
                "Must set regex keyword argument, use None if object has no URL"
            )
        # a little hacky code for backwards compatibility
        from .models import VoxModel

        if registration_cls is Registration and issubclass(cls, VoxModel):
            registration_cls = _ModelRegistration
        # en hacky code
        item = ObjectManagerItem(cls, registration_cls(cls))
        if regex is not None:
            item.set_regex(regex)
        self[cls] = item

    def create_local_object(self, path):
        for key, value in self.items():
            match = value.match(path)
            if match:
                # RegexURLPattern vs RegexPattern
                kwargs = match.kwargs if hasattr(match, "kwargs") else match[2]
                return key.__class__(**kwargs)
        msg = _("Unable to find class for {}.").format(path)
        raise ObjectNotFound(msg)

    def get_local_object(self, path):
        matched_patterns = []
        for key, value in self.items():
            match = value.match(path)
            if match:
                matched_patterns.append(value.pattern)
                # RegexURLPattern vs RegexPattern
                kwargs = match.kwargs if hasattr(match, "kwargs") else match[2]
                try:
                    return key.objects.get(**kwargs)
                except key.DoesNotExist:
                    pass
        msg = _("Unable to find object for {}.").format(path)
        if matched_patterns:
            details = _("We tried the following patterns: {}.").format(
                ", ".join(matched_patterns)
            )
            msg = "{} {}".format(msg, details)
        raise ObjectNotFound(msg)


def get_protocol_choices():
    for protocol in backends.protocols():
        yield (protocol, PROTOCOLS.get(protocol, protocol))


def _channel_type_ids():
    for all_models in apps.all_models.values():
        for model in all_models.values():
            if model in objects:
                if objects[model].has_channels():
                    ct = ContentType.objects.get_for_model(model)
                    yield ct.id


def channel_type_limit():
    global _CHANNEL_TYPE_IDS
    if _CHANNEL_TYPE_IDS is None:
        _CHANNEL_TYPE_IDS = tuple(_channel_type_ids())
    return {"id__in": _CHANNEL_TYPE_IDS}


# note, these should come at the end to avoid backend import problems

backends = BackendManager(load_backend(name) for name in settings.BACKENDS)

objects = ObjectManager()


# Deprecated


class ChannelProxyManager(dict):
    def __missing__(self, key):
        if key not in objects:
            objects.add(key, regex=None)
        return objects[key].channels


channels = ChannelProxyManager()
