import time
from logging import getLogger
import inspect
from datetime import timedelta, datetime, timezone

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.timezone import now

from django_orion_model.models.connectors import ServicePath
from django_orion_model.models.fields import OrionField, OrionCharField

from pyfiware.history import HistoryConnector


logger = getLogger(__name__)


def _expire_time():
    return now() + timedelta(seconds=settings.ORION_EXPIRATION)


def _orion_get(self, item):
    _get = super().__getattribute__
    if item in _get('_orion_fields_names'):
        self.refresh_orion()
        #
    return _get(item)


def _orion_set(self, key, value):
    if key in self._orion_fields_names:
        #
        self.updated.append(key)
        self.save_to_orion()
    super().__setattr__(key, value)


class OrionEntity(models.Model):
    """ Stores a local Entity. Its includes the connection to Orion context broker and the necessary information to
    """

    # @classmethod
    # def orion_type(cls):
    #     return cls.ORION_TYPE or cls.__name__
    # ORION_TYPE = "Entity"
    ORION_SUB_TYPE = None

    # Created and awaiting to be pushed to Orion
    STATUS_CREATING = "CREATING"
    # Created and awaiting to be populated from Orion
    STATUS_CREATED = "CREATED"
    # The mention is currently writing from orion
    STATUS_PENDING_WRITING = "WRITING"
    # The mention is currently reading from orion
    STATUS_PENDING_READING = "READING"
    # The Entity does not need to write or read from Orion
    STATUS_OK = "OK"
    # The mention awaits for repeat a writing
    STATUS_AWAIT_REWRITING = "REWRITING"
    # The mention awaits for repeat a reading
    STATUS_AWAIT_REFRESH = "REFRESH"
    # The entity is not connected to Orion
    STATUS_OFFLINE = "OFFLINE"
    # The mention does not have a reflect in Orion
    STATUS_MISSING = "MISSING"

    STATUS_OPTIONS = [
        (STATUS_CREATING, "Creating"),
        (STATUS_CREATED, "Created"),
        (STATUS_PENDING_WRITING, "Pending writing"),
        (STATUS_PENDING_READING, "Pending reading"),
        (STATUS_OK, "Ok"),
        (STATUS_AWAIT_REFRESH, "Await refresh"),
        (STATUS_AWAIT_REWRITING, "Await rewrite"),
        (STATUS_OFFLINE, "Offline"),
        (STATUS_MISSING, "Missing"),
    ]

    CREATION_ACTIONS = [
        (STATUS_CREATED, "Existing"),
        (STATUS_CREATING, "New"),
        (STATUS_OFFLINE, "Offline"),
    ]

    # Structure fields
    orion_service_path = models.ForeignKey(ServicePath, models.CASCADE)

    # Orion Fields
    orion_id = models.CharField(unique=True, max_length=1011)
    orion_type = models.CharField(max_length=1011)

    # Functional Fields
    orion_data = JSONField(blank=True, default=dict)
    orion_updated = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    orion_expiration = models.DateTimeField(default=_expire_time, blank=True)
    orion_status = models.CharField(blank=True, default="created", max_length=50, choices=STATUS_OPTIONS)
    orion_error = models.TextField(blank=True)

    orion_time = None

    CLASS_ORION_TYPE = None

    @classmethod
    def orion_class_type(cls):
        return cls.CLASS_ORION_TYPE or cls.__name__

    def __init__(self, lazy=False, *args, **kwargs):
        data = kwargs.pop("data", {})
        self.orion_time = kwargs.pop("orion_time", None)
        service_path = kwargs.pop("service_path") if "service_path" in kwargs else None
        super().__init__(*args, **kwargs)
        # Check without triggering Orion sync if entity have a type, if no  load with class default
        self.orion_type = data.get("type", None) or \
            getattr(self, "orion_type", None) or \
            getattr(self, "ORION_TYPE", None)
        if self.orion_type is None:
            raise Exception("Set entity type as orion_type parameter or orion_type_default class attribute")

        self._orion_fields = set(f for f in self._meta.fields if issubclass(type(f), OrionField))
        self._orion_fields_names = set(f.attname for f in self._meta.fields if issubclass(type(f), OrionField))

        if service_path:
            self.orion_service_path = service_path
        if data and not lazy:
            self.fill_with_data(data)

        self.__getattribute__ = _orion_get
        self.__setattr__ = _orion_set

    def past(self, count=None, time_elapsed=None, date=None, until=None):
        if sum((bool(count), bool(time_elapsed), bool(date))) > 1:
            raise Exception("Set one, and only one, of the parameters: count, time_elapsed or date")
        scenario_id = self.orion_service_path.path.replace("/", ":")[1:]
        h = HistoryConnector(settings.HISTORY_HOST)

        if count:
            past = h.entity_get(scenario_id, self.orion_type, self.orion_id, limit=count, until=until)
        elif time_elapsed:
            until = time.time() if until == "now" else until
            past = h.entity_get(scenario_id, self.orion_type, self.orion_id,
                                since=time_elapsed.time() - time_elapsed, until=until)
        elif date:
            past = h.entity_get(scenario_id, self.orion_type, self.orion_id, since=date, until=until)
        else:
            past = h.entity_get(scenario_id, self.orion_type, self.orion_id, until=until)

        return [self.__class__(
            data=snap, orion_service_path=self.orion_service_path,
            orion_time=snap["time"], orion_status=self.STATUS_OFFLINE)
            for snap in past["entity"]]

    def class_name(self):
        return self.__class__.__name__

    @property
    def history_cache(self):
        return self._history_cache

    @history_cache.setter
    def history_cache(self, value):
        self._history_cache = value

    def history(self, time_slice):
        if type(time_slice) is list:
            return [[key, self.history_cache.get(key, None)] for key in time_slice]
        return self.history_cache.fromkeys(time_slice)

    @classmethod
    def from_db(cls, db, field_names, values):
        """Override model save methods """
        orion_object = super().from_db(db, field_names, values)
        orion_object.update_from_orion()
        # Some strange behaviour
        orion_object.pk = orion_object.id
        return orion_object

    def save(self, *args, **kwargs):
        """Override model save methods """
        self.save_to_orion()
        super().save(*args, **kwargs)

    # Orion Connectivity
    def refresh_orion(self):
        reload = self.orion_expiration > now()
        if self.orion_status == self.STATUS_CREATED:
            logger.warning("Lecture of %s while unset", self.orion_id)
            reload = True
        elif self.orion_status == self.STATUS_PENDING_WRITING:
            logger.warning("Lecture of %s while transition status %s", self.orion_id, self.orion_status)
        elif self.orion_status == self.STATUS_PENDING_READING:
            logger.warning("Lecture of %s while transition status %s", self.orion_id, self.orion_status)
            reload = True
        elif self.orion_status == self.STATUS_AWAIT_REFRESH:
            reload = True
        if reload:
            self.update_from_orion()
        for key in self.orion_data:
            try:
                super().__setattr__(key, self.orion_data[key])
            except KeyError:
                pass

    def save_to_orion(self):
        """ Saves the object to Orion context context_broker.

        If an error occurs object is marked as STATUS_AWAIT_REWRITING and keeps update flags.
        If everything goes correctly update flags are resets and a reading is launched.

        :return: Nothing
        """
        if self.orion_status == self.STATUS_OFFLINE:
            return

        if self.orion_status == self.STATUS_CREATING:
            attributes = self.orion_data
            for field in self._orion_fields_names:
                attributes[field] = super().__getattribute__(field)
            try:
                self.orion_updated = []
                self.orion_service_path.connector.create(
                    element_id=self.orion_id, element_type=self.orion_type, **attributes)
                self.update_from_orion()

            except Exception as ex:
                self.orion_error = "Error creating: {0}".format(ex)
                self.orion_status = self.STATUS_AWAIT_REWRITING
            return

        self.orion_status = self.STATUS_PENDING_WRITING
        try:
            if self.orion_updated:
                update_json = {}
                for field in self.orion_updated:
                    update_json[field] = self.orion_data[field]
                self.orion_service_path.connector.patch(element_id=self.orion_id, **update_json)
                self.orion_updated = []
            self.update_from_orion()
        except Exception as ex:
            self.orion_error = str(ex)
            self.orion_status = self.STATUS_AWAIT_REWRITING

    def fill_with_data(self, data):
        logger.debug("Filling object with %s", data)
        self.orion_id = data.get("id")
        self.orion_data = data
        self.orion_type = data.get("type")
        logger.debug("Orion fields  %s", self._orion_fields)
        for field in self._orion_fields:
            try:
                setattr(self, field.name, field.extract_from_json(data))
            except KeyError as ke:
                logger.debug(ke)

    def update_from_orion(self):
        """ The object data is updated from the Orion context context_broker.

        If an error occurs object is marked as STATUS_AWAIT_REFRESH and awaits keeps old data
        If everything goes correctly data is stored, expiration mark is set and object is marked as STATUS_OK.

        :return: Nothing
        """
        if self.orion_status == self.STATUS_OFFLINE:
            return

        self.orion_status = self.STATUS_PENDING_READING
        try:
            response = self.orion_service_path.connector.get(entity_id=self.orion_id)
            if response:
                self.fill_with_data(response)
                self.orion_expiration = _expire_time()
                self.orion_status = self.STATUS_OK
                self.orion_time = datetime.now(tz=timezone.utc)
            else:
                self.orion_status = self.STATUS_MISSING
        except Exception as ex:
            self.orion_error = str(ex)
            self.orion_expiration = now()
            self.orion_status = self.STATUS_AWAIT_REFRESH

    def __str__(self):
        return '{0}:{1}'.format(self.orion_type, self.orion_id)


class FamilyOrionEntity(OrionEntity):
    class Meta:
        abstract = True

    family = OrionCharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        """Override model save methods """
        try:
            if self.family == "":
                self.family = self.FAMILY
            if self.family != self.FAMILY:
                logger.warning("Element %s family mismatch", self.FAMILY, self.family)
            super().save(*args, **kwargs)
        except AttributeError as EX:
            logger.error("Class %s not have FAMILY attribute", self.__class__.__name__)
            raise EX


class Subclassed(models.Model):
    """Stores the class name  used during the creation of the object to restore it during the object recreation"""

    class Meta:
        abstract = True

    subclass = models.CharField(max_length=250, blank=True)

    def subclassed(self):
        c_path = self.subclass.split(".")
        current = c_path.index(self.__class__.__name__)
        c_path = c_path[:current]
        obj = self
        while c_path:
            subclass = c_path.pop(-1)
            try:
                obj = getattr(obj, subclass.lower())
            except AttributeError:
                logger.debug("class %s skipped: Maybe abstract", subclass)
        return obj

    def save(self, *args, **kwargs):
        """Override model save methods """
        if self.subclass == "":
            self.subclass = ".".join(c.__name__ for c in inspect.getmro(self.__class__))

        logger.debug("Saving object:\n %s \nargs:\n %s \nkwargs:\n %s", self, args, kwargs)
        super().save(*args, **kwargs)
