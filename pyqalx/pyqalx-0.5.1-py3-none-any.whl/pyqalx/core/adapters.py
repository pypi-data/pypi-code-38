import copy
import json
import logging
import platform
from logging import getLogger
from types import MethodType

import jsonschema
from jsonschema import validators

from pyqalx.config import UserConfig, BotConfig
from pyqalx.core import QalxNoGUIDError
from pyqalx.core.entities import Bot, QalxListEntity, Set, Item, Group, Queue
from pyqalx.core.entities.blueprint import Blueprint
from pyqalx.core.entities.worker import Worker
from pyqalx.core.errors import QalxError, QalxAPIResponseError, \
    QalxMultipleEntityReturned, QalxInvalidSession, \
    QalxEntityNotFound, QalxConfigError, QalxFileError, \
    QalxInvalidBlueprintError
from pyqalx.core.log import configure_logging
from pyqalx.core.registry import Registry
from pyqalx.core.signals import QalxWorkerSignal, QalxBotSignal
from pyqalx.transport import PyQalxAPI

logger = logging.getLogger(__name__)

class QalxSession:
    """The session that any interaction with the API will use.
    Typically this won't get called directly but it gets passed to
    :class:`QalxAdapter` instances to use for the duration of the :class:`QalxAdapter`
    session."""

    def __init__(self,
                 profile_name="default",
                 config_class=None,
                 skip_ini=False,
                 rest_api_class=None):
        """
        :param profile_name: profile name to get from `config_class` (default="default")
        :type profile_name: str
        :config_class: The class for the config that will be used for this session
        :param skip_ini: Should loading the config from the inifile be skipped
        :type skip_ini: bool
        :param rest_api_class: The class to use for the rest api
    """

        if config_class is None:
            config_class = UserConfig
        self.config = config_class()
        """an instance of the `config_class` (default=pyqalx.config.UserConfig())"""
        if not skip_ini:
            self.config.from_inifile(profile_name)

        configure_logging(self.config)
        if rest_api_class is None:
            rest_api_class = PyQalxAPI
        self.rest_api = rest_api_class(self.config)
        self._registry = Registry()
        self._registry._register_defaults()

    @property
    def log(self):
        return getLogger('pyqalx.integration')

    def _update_config(self, config):
        """
        Method to use if the config needs to be updated after the session has
        been created.  Used when creating a `~bot.Bot` as a `QalxSession`
        needs to be created using a `BotConfig` and then update it with the
        token the `~bot.Bot` needs to use to interact with the
        `~entities.Queue`.
        Also updates the rest_api with the updated config

        :param config:
        :return:
        """
        self.config.update(config)
        self.rest_api = self.rest_api.__class__(self.config)

    def register(self, cls):
        self._registry.register(cls)

    def unregister(self, cls):
        self._registry.unregister(cls)

    @property
    def _host_info(self):
        return {
            "node": platform.node(),
            "platform": platform.platform(),
            # TODO: add more platform and IP address infos
        }

    @property
    def item(self):
        """
        returns a :class:`QalxItem` adapter for this session

        :return: pyqalx.core.adapters.QalxItem
        """
        return QalxItem(self)

    @property
    def set(self):
        """
        returns a :class:`QalxSet` adapter for this session

        :return: pyqalx.core.adapters.QalxSet
        """
        return QalxSet(self)

    @property
    def group(self):
        """
        returns a :class:`QalxGroup` adapter for this session

        :return: pyqalx.core.adapters.QalxGroup
        """
        return QalxGroup(self)

    @property
    def queue(self):
        """
        returns a :class:`QalxQueue` adapter for this session

        :return: pyqalx.core.adapters.QalxQueue
        """
        return QalxQueue(self)

    @property
    def bot(self):
        """
        returns a :class:`QalxBot` adapter for this session

        :return: pyqalx.core.adapters.QalxBot
        """
        return QalxBot(self)

    @property
    def worker(self):
        """
        returns a :class:`QalxWorker` adapter for this session

        :return: pyqalx.core.adapters.QalxWorker
        """
        return QalxWorker(self)

    @property
    def blueprint(self):
        """
        returns a :class:`QalxBlueprint` adapter for this session

        :return: pyqalx.core.adapters.Qalxprint
        """
        return QalxBlueprint(self)


class QalxAdapter(object):
    """
    The base class for a QalxAdapter. An adapter is the interface for the
    entity to the rest api.  This allows us to have a consistent interface
    across all entity types.
    Can be instatiated in two ways:

    QalxAdapter(entity_type='item') -> Returns a :class:`QalxItem` instance

    QalxItem() -> Returns a :class:`QalxItem` instance
    """

    def __init__(self, session, *args, **kwargs):
        if not isinstance(session, QalxSession):
            raise QalxInvalidSession(f'`qalx_session` should be an instance of'
                                     f' `{QalxSession}`.  '
                                     f'Got `{type(session)}`')
        self.session = session
        super(QalxAdapter, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        """
        Certain methods can only be calld by sessions with a UserConfig or a
        BotConfig.  The API will return a 403 Permission Denied
        but this method handles showing the user a more useful error message
        """
        attr = super(QalxAdapter, self).__getattribute__(item)
        if callable(attr) and isinstance(attr, MethodType):
            # This is a method on `QalxBot`.  Check the config
            # is correct for the method we are calling
            def _msg(expected_class, actual_class):
                return f"Method `{item}` on `{self.__class__}` " \
                    f"must be called via a session with a `{expected_class}`" \
                    f"instance.  Got `{actual_class}`"

            is_user_config = isinstance(self.session.config, UserConfig)
            is_bot_config = isinstance(self.session.config, BotConfig)

            if item in getattr(self, '_user_only_methods', []) and not is_user_config:
                raise QalxConfigError(_msg(UserConfig, BotConfig))
            if item in getattr(self, '_bot_only_methods', []) and not is_bot_config:
                raise QalxConfigError(_msg(BotConfig, UserConfig))
        return attr

    @property
    def entity_class(self):
        return self.session._registry['entities'][self._entity_class.entity_type]

    def _process_api_request(self, method, *args, **kwargs):
        """calls to pyqalxapi

        :param method: http method required
        :param args: args to be passed to endpoint method
        :param kwargs: kwargs to be passed to endpoint method
        :returns: `dict` containing API resource data
        """

        if kwargs.get('meta', None) is None:
            # meta is optional but must always be sent through as a dict
            kwargs['meta'] = {}

        if not isinstance(kwargs['meta'], dict):
            raise QalxError('`meta` kwarg must be a `dict`')

        input_file = kwargs.pop('input_file', None)

        try:
            json.dumps(kwargs)
        except (TypeError, OverflowError):
            raise QalxError("One of the keyword arguments is "
                            "not JSON serializable")

        try:
            endpoint = getattr(self.session.rest_api, method.lower())
            logger.debug(str(endpoint))
        except AttributeError:
            raise QalxError(f"{method} not recognised.")

        if input_file is not None:
            file_name = kwargs.pop("file_name", None)
            success, data = endpoint(*args,
                                     input_file=input_file,
                                     file_name=file_name,
                                     json=kwargs)
        else:
            success, data = endpoint(*args, json=kwargs)

        if success:
            return data
        m = "API request error, message:\n\n-vvv-\n\n"
        m += "\n".join([f"{k}: {v}" for k, v in data.items()])
        m += "\n\n-^^^-"
        raise QalxAPIResponseError(m)

    def detail_endpoint(self, guid, *args, **kwargs):
        """
        The endpoint for interfacing with a single
        instance of `self.entity_class`
        """
        return f"{self.entity_class.entity_type}/{guid}"

    def list_endpoint(self, *args, **kwargs):
        """
        The endpoint for interfacing with multiple instances of
        `self.entity_class`
        """
        return self.entity_class.entity_type

    def get_keys_to_save(self, entity):
        """
        When saving an entity not every key should be saved
        """
        # info & guid are both read only
        # status should only be saved via `update_status` (if available)
        return {k: entity[k] for k in entity
                if k not in ('info', 'guid', 'status')}

    def add(self, **kwargs):
        """
        Adds a new instance of `self.entity_class`.  Provide valid `kwargs`
        for the object you are trying to create

        :return: An instance of `self.entity_class`
        """
        response = self._process_api_request('post',
                                             self.list_endpoint(**kwargs),
                                             **kwargs)
        # TODO: Should we return packable entiies in an unpacked state?
        return self.entity_class(response)

    def get(self, guid, *args, **kwargs):
        """
        Gets an instance of `self.entity_class` by the given guid.

        :param guid: The guid of the entity to get
        :return: An instance of `self.entity_class`
        """
        endpoint = self.detail_endpoint(guid=guid, *args, **kwargs)
        resp = self._process_api_request('get', endpoint, *args, **kwargs)
        logger.debug(f"get {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        return self.entity_class(resp)


    def find_one(self, **query_params):
        """
        Method for returning a unique entity. Will return the entity that matches the query_params

        :param query_params: keyword arguments to represent the query e.g. `meta="id=case-01239876"`
        :return: an instance of `self.entity_class`
        :raises: `QalxMultipleEntityReturned`
        :raises: `QalxEntityNotFound`
        """
        return self.find(many=False, limit=2, **query_params)

    def find(self, sort=None, skip=0, limit=25, many=True, **kwargs):
        """
        Method for listing entities. If `many=False` will attempt to return
        a single entity and will error if any more/less than 1 is found

        :param sort: The keys to sort by
        :param skip: The number of results to skip (offset) by
        :param limit: How many results should the response be limited to
        :param many: Should many entities be returned or just a single one
        :param kwargs: kwargs to query by
        :return:
        """
        # The list endpoint might need specific kwargs but we don't want
        # to use those kwargs when querying the endpoint
        list_endpoint_kwargs = kwargs.pop('list_endpoint_kwargs', {})
        list_endpoint = self.list_endpoint(**list_endpoint_kwargs)
        logger.debug(f"find {self.entity_class.entity_type} with {list_endpoint}")
        resp = self._process_api_request('get',
                                         list_endpoint,
                                         sort=sort,
                                         skip=skip,
                                         limit=limit,
                                         **kwargs)
        entities = QalxListEntity(self.entity_class, resp)

        if many is False:

            # We are expecting only a single entity.
            entities = entities['data']
            if len(entities) > 1:
                entities_str = "\n".join([str(q) for q in entities])
                raise QalxMultipleEntityReturned("Expected one but got "
                                                 "{}:\n{}".format(len(entities),
                                                                  entities_str))
            elif entities:
                return entities[0]
            else:
                raise QalxEntityNotFound(self.entity_class.entity_type +
                                         " not found.")
        return entities

    def reload(self, entity):
        """
        Reloads the current entity from the API

        :return: A refreshed instance of `self.entity`
        """
        return self.get(entity['guid'])

    def save(self, entity, blueprint_name=None, *args, **kwargs):
        """
        Saves `self.entity` to the database.

        :return: The updated instance of `self.entity`
        """
        if not entity.get("guid"):
            raise QalxNoGUIDError("No guid.")
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, *args, **kwargs)
        keys_to_save = self.get_keys_to_save(entity=entity)
        logger.debug(f"save {self.entity_class.entity_type} with guid {guid} with {endpoint}")

        resp = self._process_api_request('patch', endpoint, **keys_to_save)
        return self.entity_class(resp)

    def archive(self, entity, *args, **kwargs):
        """
        Archives `self.entity`

        :return: The archived instance of `self.entity`
        """
        guid = entity['guid']
        detail_endpoint = self.detail_endpoint(guid=guid,
                                               *args, **kwargs)
        endpoint = f"{detail_endpoint}/archive"
        logger.debug(f"archive {self.entity_class.entity_type} with guid {guid} with {endpoint}")

        resp = self._process_api_request('patch', endpoint)
        return self.entity_class(resp)


class QalxUnpackableAdapter(QalxAdapter):
    """
    A qalx adapter for unpackable entities (Set, Group)
    """

    @property
    def kids(self):
        """
        The key that the child entities live in
        """
        return self.child_entity_class.entity_type + 's'

    def _child_list_response(self, child_adapter, query, entity):
        return child_adapter.find(**query)

    def _child_list_request(self, entity, kids, child_adapter, query_key='guid'):
        """
        Builds the list request for getting any unpackable children. Handles
        chunking of the query and also pagination of the response
        :param entity: The entity that has the children
        :param kids: The details of the kids entities we want to lookup
        :param child_adapter: The child adapter to use
        :param query_key: The query key (defaults to `guid`)
        :return: A list of unpacked child_adapter.entity_class entities
        """
        unpacked_entities = []
        for _page in entity._chunks(kids, chunk_size=100):
            # Chunk to avoid hitting maximum request size
            values = ','.join(filter(None, _page))
            query = {query_key: f'in=({values})'}
            _resp = self._child_list_response(child_adapter=child_adapter,
                                              query=query,
                                              entity=entity)
            unpacked_entities += _resp['data']
            while _resp['query']['next'] is not None:
                # We got a paginated response so keep going through the pages
                # until we exhaust this chunk of data
                logger.debug(f"get {self.entity_class.entity_type} with {_resp['query']['next']}")
                _resp = self._process_api_request('get',
                                                  _resp['query']['next'])
                unpacked_entities += QalxListEntity(self.child_entity_class, _resp)['data']
        return unpacked_entities

    def _get_child_entities(self, entity):
        """
        Gets all the child entities for the given entity.  Handles chunking
        the children up into blocks to guard against sending a request that is
        too large.  Also handles the paginated result coming back from the
        `list` endpoint.  Does a `list` lookup for self.child_entity_class
        filtering on `guid` of the children to reduce the amount of queries

        :param entity: The entity to be unpacked
        :return: The child entities as a list
        """
        kids = entity[self.kids]
        if isinstance(kids, dict):
            # Handles Sets, Groups
            kids_guids = list(kids.values())
        elif isinstance(kids, list):
            # Handles Bot
            kids_guids = kids
        else:
            # This won't happen unless someone overrides this method or
            # has `self.kids` in an unhandled format
            raise QalxError(f'`self.kids` key on `entity` must be dict or '
                            f'list. Got `{type(kids)}`')

        child_adapter = getattr(self.session,
                                self.child_entity_class.entity_type)
        unpacked_entities = self._child_list_request(entity=entity,
                                                     kids=kids_guids,
                                                     child_adapter=child_adapter,)
        return unpacked_entities

    def _unpacked_entities_to_valid_children(self, entity, unpacked_entities):
        """
        Converts a list of `unpacked_entities` into valid child entities
        for the given entity.

        :param entity: The entity that has kids that should be unpacked
        :param unpacked_entities: The unpacked child entities that need to be
                                  stitched into the entity
        :return: The unpacked entities in the correct format to be assigne to
                 `entity[self.kids]`
        """
        to_return = {}
        for key, item_guid in entity[self.kids].items():
            for child_entity in unpacked_entities:
                if item_guid == child_entity['guid']:
                    child_entity_adapter = getattr(self.session,
                                                   child_entity.entity_type)
                    if hasattr(child_entity_adapter, 'child_entity_class'):
                        # The child entity has a child adapter of it's own.
                        # Attempt unpack. This can occur if we are unpacking
                        # a Group as we may need to unpack the Sets on the
                        # Group
                        to_return[key] = child_entity_adapter._attempt_unpack(child_entity)
                    else:
                        to_return[key] = child_entity
        return to_return

    def _attempt_unpack(self, entity):
        """
        For the given entity will attempt
        to unpack the child_entity data that it contains

        :entity: The entity to be unpack
        :return: The entity instance with the child_entity objects unpacked
        """

        should_unpack = self.session.config.getboolean(
            "UNPACK_" + self.entity_class.entity_type.upper())

        if should_unpack and self.kids in entity:
            # `self.kid` might not be there if we have specified a subset
            # of fields
            unpacked_entities = self._get_child_entities(entity)
            entity[self.kids] = self._unpacked_entities_to_valid_children(
                entity=entity,
                unpacked_entities=unpacked_entities)
        return entity

    def _pack_kids_for_request(self, kwargs):
        """
        Packs the kids into a format that they need to be in
        for sending to the API
        :param kwargs: The kwargs sent to the `add` method
        :return: kwargs with packed kids
        """
        kids = {key: str(kid['guid']) for key, kid in kwargs[self.kids].items()}
        kwargs[self.kids] = kids
        return kwargs

    def get_keys_to_save(self, entity):
        """
        Unpackable entities will have unpacked data stored on them that have
        to be submitted as packed data
        """
        keys_to_save = super(QalxUnpackableAdapter,
                             self).get_keys_to_save(entity=entity)
        keys_to_save[self.kids] = {k: str(i['guid']) for k, i in
                                   keys_to_save[self.kids].items()}
        return keys_to_save

    def get(self, guid, *args, **kwargs):
        """
        Unpackable entities need to be unpacked after retrieval

        :param guid: The `guid` of the entity to get
        :return: An unpacked entity
        """
        entity = super(QalxUnpackableAdapter, self).get(guid=guid,
                                                        *args, **kwargs)
        entity = self._attempt_unpack(entity)
        return entity

    def find(self, many=True, *args, **kwargs):
        entities = super(QalxUnpackableAdapter, self).find(many=many,
                                                           *args,
                                                           **kwargs)
        if many is False:
            # Only unpack a list view if we have a single entity
            entities = self._attempt_unpack(entities)
        return entities

    def save(self, entity, *args, **kwargs):
        """
        When saving an unpacked entity the kids need to be packed.  To save
        having to unpack them again just save the original kids and replace
        them with the packed values after saving
        """
        original_kids = copy.deepcopy(entity[self.kids])
        entity = super(QalxUnpackableAdapter, self).save(entity=entity)
        entity[self.kids] = original_kids
        return entity

    def add(self, **kwargs):
        kwargs = self._pack_kids_for_request(kwargs)
        return super(QalxUnpackableAdapter, self).add(**kwargs)


class QalxSignalAdapter(QalxAdapter):
    """
    Bots and Workers have signals that are used to determine when to stop
    processing data.  This class provides that shared functionality
    """

    def get_signal(self, entity, *args, **kwargs):
        """
        Gets just the `signal` field from the entity and then parses that
        into the `signal_class`
        """
        entity = self.get(guid=entity['guid'], fields='signal', *args,
                          **kwargs)
        signal = self.signal_class(entity)
        return signal

    def terminate(self, entity, *args, **kwargs):
        """
        Updates the entity with a terminate signal
        """
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, **kwargs)
        logger.debug(f"terminate {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        signal = self.signal_class._terminate_signal(*args, **kwargs)

        self._process_api_request('patch', endpoint, signal=signal)

    def _stop_or_resume(self, entity, stop, **kwargs):
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, **kwargs)
        signal = self.signal_class._stop_signal(stop)
        logger.debug(f"signal {signal} {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        self._process_api_request('patch', endpoint, signal=signal)

    def stop(self, entity, **kwargs):
        """
        Updates the entity with a stop signal
        """
        self._stop_or_resume(entity, stop=True, **kwargs)

    def resume(self, entity, **kwargs):
        """
        Updates the entity with a resume signal
        """
        self._stop_or_resume(entity, stop=False, **kwargs)


class QalxNamedEntityAdapter(QalxAdapter):
    """
    Certain QalxEntities have a `name` field that can be used to look up the
    entity.
    """
    def get_by_name(self, name):
        """a single entity by name

        :param name: name of entity
        :type name: str
        :return: instance of `self.entity_class`
        :raises: pyqalx.errors.QalxReturnedMultipleError,
                 pyqalx.errors.QalxEntityNotFound
        """
        return self.find_one(name=name)

    def get_or_create(self, name, meta=None, **kwargs):
        """
        Gets an Entity by the given name or creates it if it doesn't exist

        :param name: The `name` that to use to get or create the entity by
        :type name: str
        :param meta: metadata about the entity
        :param kwargs: Other kwargs on the entity to use when creating
        :return: instance of `self.entity_class`
        """
        try:
            return self.get_by_name(name=name)
        except QalxEntityNotFound:
            return self.add(name=name, meta=meta, **kwargs)


class QalxValidateBlueprintAdapter(QalxAdapter):
    """
    Certain entity types can be validated against a preexisting Blueprint
    when they are created.
    """
    def _validate(self, blueprint, **kwargs,):
        if kwargs['meta'] is None:
            # Need to handle meta not being provided as it being `None` at
            # this point breaks validation
            kwargs['meta'] = {}
        jsonschema.validate(instance=kwargs,
                            schema=blueprint['schema'])
        return

    def _get_blueprint(self, name):
        """
        Helper method for getting the blueprint instance
        :param name: The name of the blueprint
        :type name: str
        :return: A `~entities.blueprint.Blueprint` instance
        """
        blueprint = self.session.blueprint.get_by_name(name=name)
        return blueprint

    def add(self, blueprint_name, **kwargs):
        """
        When adding entities that inherit from this class, pyqalx will get
        the blueprint based on the `blueprint_name` and then ensure that
        the schema validates correctly against the data that you are creating
        the entity with

        :param blueprint_name: the name of the blueprint
        :type blueprint_name: str, None
        :return: A valid `self.entity_class` instance
        :raises: jsonschema.ValidationError
        """
        if blueprint_name is not None:
            blueprint = self._get_blueprint(name=blueprint_name)
            self._validate(blueprint=blueprint, **kwargs)
        return super(QalxValidateBlueprintAdapter, self).add(**kwargs)

    def save(self, entity, blueprint_name=None, *args, **kwargs):
        """
        When saving entities that inherit from this class, pyqalx will get
        the blueprint based on the `blueprint_name` and then ensure that
        the schema validates correctly against the data that you are updating
        the entity with
        :param entity: The entity instance that you are saving
        :type entity: entities.QalxEntity instance
        :param blueprint_name: the name of the blueprint
        :type blueprint_name: str, None
        :return: A valid `self.entity_class` instance
        :raises: jsonschema.ValidationError
        """
        if blueprint_name is not None:
            blueprint = self._get_blueprint(name=blueprint_name)
            self._validate(blueprint=blueprint, **entity)
        return super(QalxValidateBlueprintAdapter, self).save(entity,
                                                              **kwargs)


class QalxValidateUnpackableBlueprintAdapter(QalxValidateBlueprintAdapter):
    """
    If `Sets` have blueprints they will have to have children on
    them.
    To enable users to reuse a child blueprint in a parent the system needs to
    get the full child blueprint schema and unpack that into the blueprint that
    is stored against the parent.
    """
    def _kids_properties(self, blueprint):
        return blueprint['schema']['properties'][self.kids]['properties']  # noqa

    def _get_blueprint_child_entities(self, blueprint):
        kids_properties = self._kids_properties(blueprint)
        blueprint_names = []
        # Build the blueprint names to lookup - handling either no blueprint
        # name or too many blueprint names
        for key, value in kids_properties.items():
            child_blueprint_name = value.get('enum')
            if child_blueprint_name:
                if len(child_blueprint_name) > 1:
                    # Can only happen if a user builds a schema themselves
                    raise QalxInvalidBlueprintError(f'Multiple `enum` values '
                                                    f'found for `{key}`. '
                                                    f'Ensure only one '
                                                    f'is specified`')
                blueprint_names.append(child_blueprint_name[0])
        # Gets all the child blueprints doing as few queries as possible
        unpacked_entities = self._child_list_request(entity=blueprint,
                                                     kids=blueprint_names,
                                                     child_adapter=self.session.blueprint,
                                                     query_key='name')
        return unpacked_entities

    def _attempt_blueprint_unpack(self, blueprint_name):
        blueprint = self._get_blueprint(name=blueprint_name)
        unpacked_entities = self._get_blueprint_child_entities(blueprint)
        kids_properties = self._kids_properties(blueprint)
        # Rebuild the blueprints schema with the child schemas included
        for key, value in kids_properties.items():
            for child_entity in unpacked_entities:
                if value.get('enum') and value.get('enum')[0] == child_entity['name']:
                    kids_properties[key] = child_entity['schema']
        return blueprint

    def add(self, blueprint_name, **kwargs):
        """
        If given a blueprint name will recursively get the child blueprints
        based on the name of the blueprint in the `self.kids` key.  This then
        unpacks the blueprint and validates `**kwargs` against the full unpacked
        blueprint.

        :param blueprint_name: The name of the blueprint to validate the entity against
        :type blueprint_name: str, None
        :return: A valid `self.entity_class` instance
        :raises: jsonschema.ValidationError
        """
        if blueprint_name is not None:
            blueprint = self._attempt_blueprint_unpack(blueprint_name=blueprint_name,)
            self._validate(blueprint=blueprint, **kwargs)
        # Validation either hasn't happened or was successful so call the
        # super() add method without a blueprint name to add the entity
        return super(QalxValidateUnpackableBlueprintAdapter, self).add(blueprint_name=None,
                                                                       **kwargs)

    def save(self, entity, blueprint_name=None, *args, **kwargs):
        """
        If given a blueprint name will recursively get the child blueprints
        based on the name of the blueprint in the `self.kids` key.  This then
        unpacks the blueprint and validates `**entity` against the full unpacked
        blueprint.

        :param entity: The entity that is being saved
        :type entity: A valid `self.entity_class` instance
        :param blueprint_name: The name of the blueprint to validate the entity against
        :type blueprint_name: str
        :return: A valid `self.entity_class` instance
        :raises: jsonschema.ValidationError
        """
        if blueprint_name is not None:
            blueprint = self._attempt_blueprint_unpack(blueprint_name=blueprint_name, )
            self._validate(blueprint=blueprint, **entity)
        # Validation either hasn't happened or was succesful so call the
        # super() add method without a blueprint name to add the entity
        return super(QalxValidateBlueprintAdapter, self).save(entity=entity,
                                                              blueprint=None,
                                                              **kwargs)


class QalxItem(QalxValidateBlueprintAdapter):
    _entity_class = Item

    def add(self, data, meta=None, blueprint_name=None, **kwargs):
        """
        Adds an `Item` instance.  Ensures that `data` is present and is a dict

        :param data: The data to store against this Item
        :type data: dict
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :param blueprint_name: An optional blueprint name to use if you want
                              to validate this item against an existing
                              Blueprint
        :type blueprint_name: str
        :return: A newly created `Item` instance
        """
        if isinstance(data, dict):
            return super(QalxItem, self).add(blueprint_name=blueprint_name,
                                             data=data,
                                             meta=meta,
                                             **kwargs)
        else:
            raise QalxError(
                "Only item data in dict format can be added with this "
                "function. To add a file try add_file ")

    def add_file(self, input_file, data=None, meta=None,
                 file_name="", blueprint_name=None, **kwargs):
        """adds a file to qalx with optional data and metadata

        :param input_file: input file path or stream
        :type input_file: str or `filestream`
        :param data: optional data you want to store with this file
        :type data: dict
        :param meta: additional data about the item
        :param meta: dict
        :param file_name: input file name. Optional for file path. Required
                          for file stream
        :type file_name: str
        :param blueprint_name: An optional blueprint name to use if you want
                              to validate this item against an existing
                              Blueprint
        :type blueprint_name: str
        :return: pyqalx.core.Item
        """
        if data is None:
            data = {}

        if self.session.rest_api.is_filestream(input_file) and not file_name:
            raise QalxFileError('You must supply a file name when supplying'
                                ' a file stream')
        return self.add(input_file=input_file,
                        file_name=file_name,
                        data=data,
                        meta=meta,
                        blueprint_name=blueprint_name,
                        **kwargs)


class QalxSet(QalxValidateUnpackableBlueprintAdapter,
              QalxUnpackableAdapter,):
    _entity_class = Set
    child_entity_class = Item

    def add(self, items, meta=None, blueprint_name=None, **kwargs):
        """
        When adding a `Set` ensure that the items posted to the api are in the
        format {<key>: <guid>}

        :param items: A dictionary of Items to create on the set
        :type items: dict
        :param meta: A dictionary of metadata to store on this set
        :type meta: dict
        :param blueprint_name: An optional blueprint name to use if you want
                              to validate this set against an existing
                              Blueprint
        :type blueprint_name: str

        :return: A newly created `Set` instance
        """
        return super(QalxSet, self).add(items=items,
                                        blueprint_name=blueprint_name,
                                        meta=meta,
                                        **kwargs)


class QalxGroup(QalxUnpackableAdapter,):
    _entity_class = Group
    child_entity_class = Set

    def add(self, sets, meta=None, **kwargs):
        """
        When adding a `Group` ensure that the sets posted to the api are in
        the format {<key>: pyqalx.entities.Set}

        :param sets: A dictionary of Sets to create on the group
        :type sets: dict
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :return: A newly created `Group` instance
        """
        return super(QalxGroup, self).add(sets=sets,
                                          meta=meta,
                                          **kwargs)


class QalxQueue(QalxNamedEntityAdapter):
    _entity_class = Queue
    _bot_only_methods = ['get_messages']

    @property
    def _queue_params(self):
        """
        The configurable parameters for a `Queue`
        :return:
        """
        return {
            'VisibilityTimeout': int(self.session.config['MSG_BLACKOUTSECONDS'])
        }

    def add(self, name, meta=None, **kwargs):
        """
        Queues are created with a name.  This name is stored in the metadata
        of the `Queue` instance

        :param name: The name we want to assign the Queue
        :type name: str
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :param kwargs: Any other kwargs we are setting on the Queue
        :return: A newly created `Queue` instance
        """
        return super(QalxQueue, self).add(parameters=self._queue_params,
                                          name=name,
                                          meta=meta,
                                          **kwargs)

    def get_messages(self, queue):
        """
        Gets the messages on the `Queue` instance

        :return: A list of `QueueMessage` instances
        """
        config = self.session.config
        max_msgs = int(config["Q_MSGBATCHSIZE"])
        visibility = int(config["MSG_BLACKOUTSECONDS"])
        waittime = int(config["MSG_WAITTIMESECONDS"])

        message = queue.get_messages(max_msgs, visibility, waittime)
        return message

    def get_by_name(self, name):
        """a single queue by name

        :param name: name of queue
        :type name: str
        :return: pyqalx.core.entities.Queue
        :raises: pyqalx.errors.QalxReturnedMultipleError,
                 pyqalx.errors.QalxEntityNotFound
        """
        return self.find(many=False, name=name)

    def get_or_create(self, name, meta=None, **kwargs):
        """
        Gets a Queue by the given name or creates it if it doesn't exist

        :param name:
        :type name: str
        :param meta: metadata about the queue
        :return: pyqalx.core.entities.Queue
        """
        try:
            return self.get_by_name(name=name)
        except QalxEntityNotFound:
            return self.add(name, meta=meta)


class QalxBot(QalxUnpackableAdapter,
              QalxNamedEntityAdapter,
              QalxSignalAdapter):
    _entity_class = Bot
    child_entity_class = Worker
    signal_class = QalxBotSignal
    _user_only_methods = ['add']
    _bot_only_methods = ['replace_workers']

    def _unpacked_entities_to_valid_children(self, entity, unpacked_entities):
        """
        The unpacked entities are just a list on a Bot, therefore
        just return them

        :param entity: The Bot entity
        :param unpacked_entities: The unpacked Worker entities
        :return: The unpacked Worker entities
        """
        return unpacked_entities

    def _child_list_response(self, child_adapter, entity, **kwargs):
        """
        A bot needs to pass itself through to the child adapter in order
        to correctly build the list endpoint for Worker.  Don't
        filter the workers by anything - always return all of them for
        the given bot

        :param child_adapter: The child_adapter
        :param entity: The `QalxBot` entity
        :return: The child_adapter list response
        """
        return child_adapter.find(list_endpoint_kwargs={'bot_entity': entity})

    def _pack_kids_for_request(self, kwargs):
        """
        Bots don't get added with workers - so just bypass the packing
        of the kids
        :param kwargs: kwargs sent to `add` method
        :return: kwargs
        """
        return kwargs

    def add(self, name, config, meta=None, **kwargs):
        """
        Creates a `Bot` instance.

        :param name: The name that this bot will be given
        :type name: str
        :param config: The bots config
        :type config: dict
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :return: The newly created `Bot` instance
        """
        return super(QalxBot, self).add(host=self.session._host_info,
                                        name=name,
                                        meta=meta,
                                        config=config,
                                        **kwargs)

    def update_status(self, entity, status):
        """
        Updates the bots status

        :param entity: The entity that is being updated
        :param status: The status to update to
        :return: None
        """
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid)
        logger.debug(f"update status{self.entity_class.entity_type} with guid {guid} with {endpoint}")
        self._process_api_request('patch', endpoint, status=status)

    def replace_workers(self, bot_entity, workers):
        """
        Completely replaces any Workers on the given bot.  Will return the
        replaced workers in an unpacked state

        :param bot_entity: The ~entities.bot.Bot entity that is being changed
        :param workers: The number of workers that this bot should have
        :return: A ~entities.bot.Bot instance with the updated workers
        """
        guid = bot_entity['guid']
        detail_endpoint = self.detail_endpoint(guid=guid)
        endpoint = f'{detail_endpoint}/replace-workers'
        logger.debug(f"replace workers {self.entity_class.entity_type} with guid {guid} with {endpoint}")

        entity = self._process_api_request('patch',
                                           endpoint,
                                           workers=workers)
        entity = self.entity_class(entity)
        entity = self._attempt_unpack(entity)
        return entity


class QalxWorker(QalxSignalAdapter):
    _entity_class = Worker
    signal_class = QalxWorkerSignal

    def list_endpoint(self, *args, **kwargs):
        bot_entity = kwargs.get('bot_entity', None)
        bot_endpoint = self.session.bot.detail_endpoint(guid=bot_entity['guid'])
        return f'{bot_endpoint}/{self.entity_class.entity_type}'

    def detail_endpoint(self, guid, *args, **kwargs):
        bot_entity = kwargs.get('bot_entity', None)
        bot_endpoint = self.list_endpoint(bot_entity=bot_entity)
        return f'{bot_endpoint}/{guid}'

    def get(self, guid, *args, **kwargs):
        """
        We completely override this as we don't want to send the `bot_entity`
        kwarg through to the `get` endpoint
        """
        bot_entity = kwargs.pop('bot_entity', None)
        endpoint = self.detail_endpoint(guid=guid, bot_entity=bot_entity)
        logger.debug(f"get {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        resp = self._process_api_request('get', endpoint, *args, **kwargs)
        return self.entity_class(resp)

    def reload(self, entity, **kwargs):
        """
        Reloads the current entity from the API

        :param bot: An instance of ~entities.bot.Bot
        :param entity: An instance of ~entities.worker.Worker
        :return: A refreshed instance of `self.entity`
        """
        bot_entity = kwargs.get('bot_entity', None)
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, bot_entity=bot_entity)
        logger.debug(f"reload {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        worker_data = self._process_api_request('get', endpoint)
        return self.entity_class(worker_data)

    def update_status(self, bot_entity, entity, status):
        """
        Updates the workers status

        :param bot_entity: An instance of ~entities.bot.Bot
        :param entity: An instance of ~entities.worker.Worker
        :param status: The status to update to
        :return: None
        """
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, bot_entity=bot_entity)
        logger.debug(f"update status {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        self._process_api_request('patch', endpoint, status=status)


class QalxBlueprint(QalxNamedEntityAdapter):
    entity_class = Blueprint

    def _check_schema(self, schema):
        validators._LATEST_VERSION.check_schema(schema=schema)

    def add(self, name, schema, meta=None, **kwargs):
        """
        Adds a QalxBlueprint with a valid `jsonschema` `schema`.
        If the `schema` is invalid then a `jsonschema.SchemaError` is raised

        :param name: The name of this blueprint
        :type name: str
        :param schema: The schema that you want to set on the Blueprint.
        :type schema: dict
        :param meta: A dictionary of metadata to store
        :type meta: dict

        :return: pyqalx.core.entities.Blueprint
        :raises: jsonschema.SchemaError
        """
        self._check_schema(schema)
        entity_type = schema.get('entity_type', None)
        if entity_type is None:
            raise QalxInvalidBlueprintError('schema must specify '
                                            '`entity_type` top level key which'
                                            'has a valid `entity_type` as the'
                                            'value')
        return super(QalxBlueprint, self).add(name=name,
                                              schema=schema,
                                              entity_type=entity_type,
                                              meta=meta,
                                              **kwargs)

    def save(self, entity, **kwargs):
        """
        Saves any updates to the given Blueprint.  Validates that the `schema`
        on the entity is a valid `jsonschema` schema


        :param entity: A valid pyqalx.core.entities.Blueprint instance
        :param kwargs: Any kwargs you want to save against this `Blueprint`
        :return: pyqalx.core.entities.Blueprint
        :raises: jsonschema.SchemaError
        """
        self._check_schema(entity['schema'])
        return super(QalxBlueprint, self).save(entity=entity,
                                               **kwargs)


