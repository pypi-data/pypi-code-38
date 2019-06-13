import logging
import logging.config
import pprint
import time
from collections import namedtuple, OrderedDict
from collections.abc import MutableMapping
import copy
from enum import Enum
from urllib.parse import urlparse
from requests.exceptions import HTTPError

# test
import deriva.core.ermrest_model as em
import tabulate
from deriva.core import ErmrestCatalog, get_credential
from deriva.core.ermrest_config import MultiKeyedList
from deriva.core.ermrest_config import tag as chaise_tags

chaise_tags['catalog_config'] = 'tag:isrd.isi.edu,2019:catalog-config'

CATALOG_CONFIG__TAG = 'tag:isrd.isi.edu,2019:catalog-config'

logger = logging.getLogger(__name__)
# Make sure we only have one stream handler....
if len(logger.handlers) == 0:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__class__, method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logger.info('%r  %2.2f ms', method.__name__, (te - ts) * 1000)
        return result
    return timed

class DerivaMethodFilter:
    def __init__(self, include=True, exclude=[]):
        self.include = include
        self.exclude = exclude

    def filter(self, record):
        if self.include is True:
            return record.funcName not in  self.exclude
        else:
            return record.funcName in self.include


# Add filters: ['source_spec'] to use filter.
logger_config = {
    'disable_existing_loggers': False,
    'version': 1,
    'filters': {
        'method_filter': {
            '()': DerivaMethodFilter,
            'include': True
        },
        'model_filter': {
            '()': DerivaMethodFilter,
            'include': ['model_element']
        },
        'foreign_key_filter': {
            '()': DerivaMethodFilter,
            'include': ['delete']
        },
        'table_filter': {
            '()': DerivaMethodFilter,
            'exclude': ['_foreign_key', '_referenced', '_key_in_columns']
        },
        'visiblesources_filter': {
            '()': DerivaMethodFilter,
            'include': ['insert_sources']
        },
        'sourcespec_filter': {
            '()': DerivaMethodFilter,
            'include': ['rename_column']
        }

    },
    'formatters': {
        'class': {
            'style': '{',
            'format': '{levelname} {name}.{funcName}: {message}'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'class',
            'filters': ['method_filter'],
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'deriva_model': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'deriva_model.DerivaModel': {
            #     'level': 'DEBUG',
            #     'filters': ['model_filter']
        },
        'deriva_model.DerivaCatalog': {
            #   'level': 'DEBUG',
        },
        'deriva_model.DerivaColumnMap': {
            #    'level': 'DEBUG'
        },
        'deriva_model.DerivaSchema': {
            #    'level': 'DEBUG'
        },
        'deriva_model.DerivaVisibleSources': {
            #  'level': 'DEBUG',
            # 'filters': ['visiblesources_filter']
        },
        'deriva_model.DerivaSourceSpec': {
            #       'level': 'DEBUG',
            #   'filters': ['sourcespec_filter']
        },
        'deriva_model.DerivaTable': {
            #       'level': 'DEBUG',
            #   'filters': ['table_filter']
        },
        'deriva_model.DerivaColumn': {
            #   'level': 'DEBUG'
        },
        'deriva_model.DerivaKey': {
            #     'level': 'DEBUG'
        },
        'deriva_model.DerivaForeignKey': {
            #     'level': 'DEBUG',
            #   'filters': ['foreign_key_filter']
        }
    },
}


logging.config.dictConfig(logger_config)

class DerivaLogging:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('{}.{}'.format('deriva_model', type(self).__name__))


class DerivaCatalogError(Exception):
    def __init__(self, obj, msg):
        self.msg = msg
        self.obj = obj


class DerivaModelError(DerivaCatalogError):
    def __init__(self, obj, msg):
        super().__init__(obj, msg)


class DerivaSourceError(DerivaCatalogError):
    def __init__(self, obj, msg):
        super().__init__(obj, msg)


class DerivaKeyError(DerivaCatalogError):
    def __init__(self, obj, msg):
        super().__init__(obj, msg)


class DerivaForeignKeyError(DerivaCatalogError):
    def __init__(self, obj, msg):
        super().__init__(obj, msg)


class DerivaTableError(DerivaCatalogError):
    def __init__(self, obj, msg):
        super().__init__(obj, msg)


class DerivaContext(Enum):
    compact = "compact"
    compact_brief = "compact/brief"
    compact_select = "compact/select"
    detailed = "detailed"
    entry = "entry"
    entry_edit = "entry/edit"
    entry_create = "entry/create"
    filter = "filter"
    row_name = "row_name"
    row_name_title = "row_name/title"
    row_name_compact = "row_name/compact"
    row_name_detailed = "row_name/detailed"
    star = "*"
    all = "all"


class ElementList:
    """
    This is a helper class that is used to allow lists of model elements to be retrieved or iterated over.
    """

    def __init__(self, fvalue, lst):
        """

        :param fvalue: A function that retrieves the value from a model
        :param lst: A lost of model elements
        """
        self.fvalue = fvalue
        self.lst = lst

    def __getitem__(self, item):
        return self.fvalue(item)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except DerivaCatalogError:
            return False

    def __len__(self):
        return self.lst.__len__()

    def __delitem__(self, key):
        key_name = self.fvalue(key).table.schema_name, self.fvalue(key).name
        self.lst.__delitem__(key_name)

    def __iter__(self):
        def element_iterator(lst):
            for s in lst:
                yield self.fvalue(s)

        return element_iterator(self.lst)

    def validate(self):
        return all([self.fvalue(s).validate() for s in self.lst])


class DerivaModel(DerivaLogging):
    """
    Representation of a deriva model. Is primarily used as a resource manager to group catalog operations so as to
    minimize network round trips.  For example:

    ```
    with DerivaModel(catalog)
       table = schema.create_table('MyTable',[])
       table.display = 'My Nice Table'
    ```

    """
    contexts = {i for i in DerivaContext if i is not DerivaContext("all")}

    def __init__(self, catalog):
        super().__init__()
        self.catalog = catalog

    def __enter__(self):
        if self.catalog.nesting == 0:
            self.logger.debug('entering model changes %s', self.catalog_model())
        self.catalog.nesting += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.catalog.nesting -= 1
        if self.catalog.nesting == 0:
            self.logger.debug('applying changes to model %s', self.catalog_model())
            self.catalog._apply()

    def model_element(self, obj):
        self.logger.debug('type %s', type(obj).__name__)
        m = None
        try:
            m = self.column_model(obj)
            self.logger.debug('column model')
        except DerivaModelError:
            try:
                m = self.key_model(obj)
                self.logger.debug('key model')
            except DerivaModelError:
                try:
                    m = self.foreign_key_model(obj)
                    self.logger.debug('fkey model')
                except DerivaModelError:
                    try:
                        m = self.table_model(obj)
                        self.logger.debug('table model')
                    except DerivaModelError:
                        try:
                            m = self.schema_model(obj)
                            self.logger.debug('schema model')
                        except DerivaModelError:
                            m = self.catalog_model()
                            self.logger.debug('catalog model')
        if not m:
            raise DerivaModelError(self, 'Model not found for object {}'.format(obj))
        return m;

    def schema_exists(self, schema_name):
        try:
            return self.catalog.model_instance.schemas[schema_name]
        except (DerivaModelError, KeyError):
            return False

    def table_exists(self, schema, table_name):
        try:
            return self.schema_model(schema).tables[table_name]
        except (DerivaModelError, KeyError):
            return False

    def column_exists(self, table, column_name):
        self.logger.debug('column_name %s', column_name)
        try:
            return self.table_model(table).column_definitions[column_name]
        except (DerivaModelError, KeyError):
            return False

    def key_exists(self, table, key_id):
        self.logger.debug('table %s column_name %s', table.name, key_id)
        key_name = (table.schema_name, key_id) if type(key_id) == str else key_id
        self.logger.debug('key name %s', key_name)
        try:
            return self.table_model(table).keys[key_name]
        except (DerivaModelError, KeyError, TypeError):
            m = DerivaModel(self.catalog)
            # See if we can look up the key by its unique columns
            cols = {key_id} if isinstance(key_id, str) else set(key_id)
            for k in m.table_model(table).keys:
                self.logger.debug('column lookup %s %s', cols, k.unique_columns)
                if set(k.unique_columns) == cols:
                    return k
        return False

    def foreign_key_exists(self, table, fkey_id):
        fkey_name = (table.schema_name, fkey_id) if type(fkey_id) == str else fkey_id
        self.logger.debug('table: %s fkey_id: %s fkey_name %s', table.name, fkey_id, fkey_name)
        try:
            return self.table_model(table).foreign_keys[fkey_name]
        except (DerivaModelError, KeyError, TypeError):
            m = DerivaModel(self.catalog)
            try:
                t = m.table_model(table)
            except DerivaModelError:
                # Table doesn't exist, so FK doesn't exist
                return False
            else:
                # See if we can look up the key by its unique columns
                cols = {fkey_id} if isinstance(fkey_id, str) else set(fkey_id)
                for k in t.foreign_keys:
                    if {c['column_name'] for c in k.foreign_key_columns} == cols:
                        return k
                return False

    def catalog_model(self):
        return self.catalog.model_instance

    def schema_model(self, schema):
        try:
            return self.catalog_model().schemas[schema.name]
        except (AttributeError, DerivaModelError):
            raise DerivaModelError(schema, msg="Expected DerivaSchema")
        except KeyError:
            raise DerivaModelError(schema, msg="Schema does not exist: {}".format(schema.name))

    def table_model(self, table):
        try:
            return self.schema_model(table.schema).tables[table.name]
        except DerivaModelError:
            raise DerivaModelError(table, msg="Schema model not found: {}".format(table.schema))
        except KeyError:
            raise DerivaModelError(table, msg='Table does not exist: {}'.format(table.name))

    def column_model(self, column):
        try:
            return self.table_model(column.table).column_definitions[column.name]
        except AttributeError:
            raise DerivaModelError(column, msg="Expected DerivaColumn object: {}".format(column))
        except DerivaModelError:
            raise
        except KeyError:
            raise DerivaModelError(column, msg="Column does not exist: {}".format(column.name))

    def key_model(self, key):
        try:
            return self.table_model(key.table).keys[(key.table.schema_name, key.name)]
        except (AttributeError, DerivaModelError):
            raise DerivaModelError(key, msg="Expected DerivaKey")
        except KeyError:
            raise DerivaModelError(key, msg="Key not found: {}".format(key.name))

    def foreign_key_model(self, fkey):
        try:
            return self.table_model(fkey.table).foreign_keys[(fkey.table.schema_name, fkey.name)]
        except (AttributeError, DerivaModelError):
            raise DerivaModelError(fkey, msg="Expected DerivaForeignKey")
        except KeyError:
            raise DerivaModelError(fkey, msg="Foreign key not defined: {}".format(fkey.name))


class DerivaACL(MutableMapping):
    acl_matrix = {
        'DerivaCatalog': {'owner', 'create', 'select', 'insert', 'update', 'write', 'delete', 'enumerate'},
        'DerivaSchema': {'owner', 'create', 'select', 'insert', 'update', 'write', 'delete', 'enumerate'},
        'DerivaTable': {'owner', 'create', 'select', 'insert', 'update', 'write', 'delete', 'enumerate'},
        'DerivaColumn': {'owner', 'create', 'select', 'insert', 'update', 'write', 'delete', 'enumerate'},
        'DerivaForeignKey': {'owner', 'create', 'select', 'insert', 'update', 'write', 'delete', 'enumerate'}
    }

    def __init__(self, obj):
        self._catalog = obj.catalog
        self._acls = obj.get_acls()
        self._obj_type = obj.object_type()

    def __setitem__(self, key, value):
        if key not in DerivaACL.acl_matrix[self._obj_type]:
            raise DerivaCatalogError(self, msg='Invalid ACL: {}'.format(key))

        with DerivaModel(self._catalog) as m:
            self._acls[key] = value

    def __delitem__(self, key):
        with DerivaModel(self._catalog):
            self._acls.pop(key)

    def __getitem__(self, key):
        return self._acls[key]

    def __iter__(self):
        return iter(self._acls)

    def __len__(self):
        return len(self._acls)

    def __repr__(self):
        return self._acls.__repr__()

    def __str__(self):
        return self._acls.__str__()

    @property
    def value(self):
        return self._acls

    def validate(self, obj):
        keys = {i for i in self._acls.keys()}
        if keys <= DerivaACL.acl_matrix[self._obj_type]:
            return True
        else:
            logger.info('Invalid ACL: %s %s', obj.name, self)
            return False


class DerivaACLBinding(MutableMapping):
    acl_binding_matrix = {
        'DerivaTable': {'owner', 'create', 'select', 'update', 'write', 'delete', 'enumerate'},
        'DerivaColumn': {'owner', 'create', 'select', 'update', 'write', 'delete', 'enumerate'},
        'DerivaForeignKey': {'owner', 'insert', 'update'}
    }

    def __init__(self, obj):
        self._catalog = obj.catalog
        self._acl_bindings = obj.get_acl_bindings()

    def __setitem__(self, key, value):
        with DerivaModel(self._catalog) as m:
            self._acl_bindings[key] = value

    def __delitem__(self, key):
        with DerivaModel(self._catalog):
            self._acl_bindings.pop(key)

    def __getitem__(self, key):
        return self._acl_bindings[key]

    def __iter__(self):
        return iter(self._acl_bindings)

    def __len__(self):
        return len(self._acl_bindings)

    def __repr__(self):
        return self._acl_bindings.__repr__()

    def __str__(self):
        return self._acl_bindings.__str__()

    @property
    def value(self):
        return self._acl_bindings

    def validate(self, obj):
        if isinstance(self._acl_bindings, dict):
            return True
        else:
            logger.info('Invalid acl_binding %s %s', obj.name, self)
            return False


class DerivaAnnotations(MutableMapping):
    """
    Class used to represent an annotation.  Main reason for this class is to make sure apply function is called
    when needed.
    """
    annotation_tags = {v for v in chaise_tags.values()}

    def __init__(self, obj):
        self.catalog = obj.catalog
        m = DerivaModel(self.catalog)
        self.annotations = m.model_element(obj).annotations

    def __setitem__(self, key, value):
        if key not in DerivaAnnotations.annotation_tags:
            raise DerivaCatalogError(self, msg='Unknow annotation tag: {}'.format(key))

        with DerivaModel(self.catalog) as m:
            self.annotations[key] = value

    def __delitem__(self, key):
        with DerivaModel(self.catalog):
            self.annotations.pop(key)

    def __getitem__(self, key):
        return self.annotations[key]

    def __iter__(self):
        return iter(self.annotations)

    def __len__(self):
        return len(self.annotations)

    def __repr__(self):
        return self.annotations.__repr__()

    def __str__(self):
        return self.annotations.__str__()

    def validate(self, obj):
        rval = True
        for t, a in self.annotations.items():
            if t not in chaise_tags.values():
                logger.info('Invalid annotation tag %s', t)
                rval = False
            if t == chaise_tags.display:
                rval = obj.validate_display() and rval
            if t == chaise_tags.visible_columns:
                if isinstance(obj, DerivaTable):
                    rval = obj.visible_columns.validate() and rval
                else:
                    logger.info('visible_columns annotation on non-table element %s', obj.name)
                    rval = False
            if t == chaise_tags.visible_foreign_keys:
                if isinstance(obj, DerivaTable):
                    rval = obj.visible_foreign_keys.validate() and rval
                else:
                    logger.info('visible_foreign_keys annotation on non-table element %s', obj.name)
            if t == chaise_tags.foreign_key:
                pass
            if t == chaise_tags.table_display:
                if isinstance(obj, DerivaTable):
                    rval = obj.validate_table_display() and rval
                else:
                    logger.info('table_display annotation on non-table element %s', obj.name)
                    rval = False
            if t == chaise_tags.column_display:
                pass
            if t == chaise_tags.asset:
                pass
            if t == chaise_tags.bulk_upload:
                pass
            if t == chaise_tags.export:
                pass
            if t == chaise_tags.chaise_config:
                pass
        return rval


class DerivaCore(DerivaLogging):
    def __init__(self, catalog):
        self.catalog = catalog
        super().__init__()

    @property
    def annotations(self):
        """
        Get/Set a Deriva Annotation.
        :return:
        """
        return DerivaAnnotations(self)

    @annotations.setter
    def annotations(self, value):
        with DerivaModel(self.catalog) as m:
            m.schema_model(self).annotations.clear()
            m.schema_model(self).annotations.update(value)

    @property
    def acls(self):
        """
        Get/Set a Deriva ACL.
        :return:
        """
        return DerivaACL(self)

    @acls.setter
    def acls(self, value):
        with DerivaModel(self.catalog) as m:
            m.model_element(self).acls.clear()
            m.model_element(self).acls.update(value)

    @property
    def acl_bindings(self):
        """
        Get/Set a Deriva ACL.
        :return:
        """
        if self.object_type() not in DerivaACLBinding.acl_binding_matrix:
            raise DerivaCatalogError(self, msg='ACL Bindings not defined for {}'.format(type(self).__name__))
        return DerivaACLBinding(self)

    @acl_bindings.setter
    def acl_bindings(self, value):
        if self.object_type() not in DerivaACLBinding.acl_binding_matrix:
            raise DerivaCatalogError(self, msg='ACL Bindings not defined for {}'.format(type(self).__name__))
        with DerivaModel(self.catalog) as m:
            m.model_element(self).acl_bindings.clear()
            m.model_element(self).acl_bindings.update(value)

    def get_acls(self):
        """
        Get dictionary form of ACL
        :return:
        """
        with DerivaModel(self.catalog) as m:
            return m.model_element(self).acls

    def get_acl_bindings(self):
        """
        Get dictionary from of acl_bindings
        :return:
        """
        with DerivaModel(self.catalog) as m:
            return m.model_element(self).acl_bindings

    def object_type(self):

        if isinstance(self, DerivaCatalog):
            obj_type = 'DerivaCatalog'
        elif isinstance(self, DerivaSchema):
            obj_type = 'DerivaSchema'
        elif isinstance(self, DerivaTable):
            obj_type = 'DerivaTable'
        elif isinstance(self, DerivaColumn):
            obj_type = 'DerivaColumn'
        elif isinstance(self, DerivaKey):
            obj_type = 'DerivaKey'
        elif isinstance(self, DerivaForeignKey):
            obj_type = 'DerivaForeignKey'
        else:
            obj_type = type(self).__name__

        return obj_type


class DerivaCatalog(DerivaCore):
    """
    A Dervia catalog.  Operations on the catalog will alter both the ERMrest service as well as the annotations used
    by Chaise.
    """
    model_instance = None

    def __init__(self, host, scheme='https', catalog_id=1, ermrest_catalog=None, validate=True):
        """
        Initialize a DerivaCatalog.

        :param host: Name of the server hosting the deriva catalog service
        :param scheme: Scheme to be used for connecting to the host, defaults to https
        :param catalog_id: The identifer for the catalog in the server.  Is an integer
        """

        self.nesting = 0

        super().__init__(self)

        self.ermrest_catalog = (
            ermrest_catalog if ermrest_catalog else
            ErmrestCatalog(scheme, host, catalog_id, credentials=get_credential(host))
        )

        self.model_instance = self.ermrest_catalog.getCatalogModel()
        self.schema_classes = {}
        if validate and not self.validate():
            raise DerivaCatalogError(self, 'Validation error in catalog')

    def __str__(self):
        return '\n'.join([i.name for i in self.schemas])

    def __getitem__(self, schema_name):
        return self.schemas.__getitem__(schema_name)

    def __iter__(self):
        return self.schemas.__iter__()

    def __contains__(self, item):
        return self.schemas.__contains__(item)

    @property
    def host(self):
        """
        Get catalog host.

        :return: Hostname of the current catalog
        """
        return urlparse(self.ermrest_catalog.get_server_uri()).hostname

    @property
    def catalog_id(self):
        """
        Get catalog id

        :return: catalog identifier
        """
        return self.ermrest_catalog.catalog_id

    @property
    def server_uri(self):
        """
        URI for the catalog server

        :return: server uri
        """
        return self.ermrest_catalog.get_server_uri()

    @property
    def schemas(self):
        """
        Return an interable for the schemas contained in the the catalog. The return value can be indexed by
        schema name, or iterated over.

        :return:
        """
        m = DerivaModel(self)
        return ElementList(self.schema, m.catalog_model().schemas)

    @property
    def navbar_menu(self):
        """
        Get/Set the navigation bar menu.

        :return:
        """
        return self.annotations[chaise_tags.chaise_config]['navbarMenu']

    @navbar_menu.setter
    def navbar_menu(self, value):
        if not isinstance(value, dict):
            raise ValueError('Menu must be a dictionary')
        if chaise_tags.chaise_config not in self.annotations:
            self.annotations[chaise_tags.chaise_config] = {'navbarMenu': value}
        else:
            self.annotations[chaise_tags.chaise_config]['navbarMenu'] = value

    @property
    def name(self):
        return DerivaModel(self).catalog_model().annotations.get(chaise_tags.catalog_config, {'name':'unknown'})['name']

    def _apply(self):
        """
        Push any pending annotation updates to the server. Should not be need to be called except when things get
        messed up.

        :return:
        """
        self.logger.debug('%s', self.model_instance)
        self.model_instance.apply(self.ermrest_catalog)

    def describe(self):
        print(self)

    def refresh(self):
        """
        Refresh the any cached model values from the server.
        :return:
        """
        assert (self.nesting == 0)
        logger.debug('Refreshing model')
        server_url = urlparse(self.ermrest_catalog.get_server_uri())
        catalog_id = server_url.path.split('/')[-1]
        self.ermrest_catalog = ErmrestCatalog(server_url.scheme,
                                              server_url.hostname,
                                              catalog_id,
                                              credentials=get_credential(server_url.hostname))
        self.model_instance = self.ermrest_catalog.getCatalogModel()

    def update_referenced_by(self):
        """Introspects the 'foreign_keys' and updates the 'referenced_by' properties on the 'Table' objects.
        """
        with DerivaModel(self) as m:
            for schema in self:
                for table in schema:
                    m.table_model(table).referenced_by = MultiKeyedList([])
            self.model_instance.update_referenced_by()

    def getPathBuilder(self):
        return self.ermrest_catalog.getPathBuilder()

    def _make_schema_instance(self, schema_name):
        return DerivaSchema(self, schema_name)

    def schema(self, schema_name):
        m = DerivaModel(self)
        if m.schema_exists(schema_name):
            return self.schema_classes.setdefault(schema_name, self._make_schema_instance(schema_name))
        else:
            raise DerivaCatalogError(self, 'schema {} not defined'.format(schema_name))

    def create_schema(self, schema_name, comment=None, acls={}, annotations={}):
        """
        Create a new schema in this catalog.

        :param schema_name: The name of the schema
        :param comment: A comment for the schema
        :param acls: ACLs for the schema
        :param annotations: Schema annotations.
        :return: A DerivaSchema object
        """
        self.logger.debug('name: %s', schema_name)
        self.model_instance.create_schema(self.ermrest_catalog,
                                          em.Schema.define(
                                              schema_name,
                                              comment=comment,
                                              acls=acls,
                                              annotations=annotations
                                          )
                                          )
        return self.schema(schema_name)

    def get_groups(self):
        if chaise_tags.catalog_config in self.annotations:
            return self.annotations[chaise_tags.catalog_config]['groups']
        else:
            raise DerivaCatalogError(self, msg='Attempting to configure table before catalog is configured')

    def validate(self):
        """
        Validate all of the objects in the catalog.

        :return:
        """

        rval = self.annotations.validate(self)
        rval = self.acls.validate(self) and rval
        for s in self.schemas:
            logger.info('Validating %s', s.name)
            # TODO Validate schema attributes.
            rval = s.validate() and rval

        return rval

    def validate_display(self):
        # TODO impliment
        pass

    def rename_visible_columns(self, column_map, validate=False):
        for s in self:
            for t in s:
                try:
                    t.visible_columns = t.visible_columns.rename_columns(column_map, validate=validate)
                except DerivaSourceError:
                    pass

class DerivaSchema(DerivaCore):
    def __init__(self, catalog, schema_name):
        super().__init__(catalog)
        self.schema_name = schema_name
        self.schema = self
        self.table_classes = {}

    def __str__(self):
        return '\n'.join([t.name for t in self.tables])

    def __getitem__(self, table_name):
        return self.tables.__getitem__(table_name)

    def __iter__(self):
        return self.tables.__iter__()

    def __contains__(self, table_name):
        self.tables.__contains__(table_name)

    @property
    def name(self):
        return self.schema_name

    @property
    def comment(self):
        with DerivaModel(self.catalog) as m:
            return m.schema_model(self).comment

    @comment.setter
    def comment(self, value):
        with DerivaModel(self.catalog) as m:
            m.schema_model(self).comment = value

    @property
    def tables(self):
        m = DerivaModel(self.catalog)
        return ElementList(self.table, m.schema_model(self).tables)

    @property
    def display(self):
        return self.annotations[chaise_tags.display]

    @display.setter
    def display(self, value):
        self.annotations[chaise_tags.display] = value

    def _make_table_instance(self, schema_name, table_name):
        return DerivaTable(self.catalog, schema_name, table_name)

    def _create_table(self, table_def):
        with DerivaModel(self.catalog) as m:
            schema = m.schema_model(self)
            schema.create_table(self.catalog.ermrest_catalog, table_def)
        table = self.table(table_def['table_name'])
        table.deleted = False  # Table may have been previously been deleted.
        return table

    def describe(self):
        print(self)

    def table(self, table_name):
        """
        Return a DerivaTable object for the named table.

        :param table_name:
        :return:
        """
        m = DerivaModel(self.catalog)
        if m.table_exists(self, table_name):
            return self.table_classes.setdefault(table_name,
                                                 self._make_table_instance(self.name, table_name))
        else:
            raise DerivaCatalogError(self, 'table {}:{} not defined'.format(self.name, table_name))

    def create_table(self, table_name, column_defs,
                     key_defs=[], fkey_defs=[],
                     comment=None,
                     acls={},
                     acl_bindings={},
                     annotations={},
                     default_config=True):
        """
        Create a new table from the provided arguments.

        :param table_name: The name of the new table to be created.
        :param column_defs:
        :param key_defs:
        :param fkey_defs:
        :param comment:
        :param acls:
        :param acl_bindings:
        :param annotations:
        :return:
        """
        self.logger.debug('table_name: %s', table_name)
        # Now that we know the table name, patch up the key and fkey defs to have the correct name.
        proto_table = namedtuple('ProtoTable', ['catalog', 'schema', 'schema_name', 'name', 'columns'])
        for k in key_defs:
            k.update_table(proto_table(self.catalog, self.schema, self.name, table_name, column_defs))
        for k in fkey_defs:
            k.update_table(proto_table(self.catalog, self.schema, self.name, table_name, column_defs))

        with DerivaModel(self.catalog) as m:
            self.logger.debug('create_fkeys ', [fk.name for fk in fkey_defs])

            table = self._create_table(em.Table.define(
                table_name, [col.definition() for col in column_defs],
                key_defs=[key.definition() if isinstance(key, DerivaKey) else key for key in key_defs],
                fkey_defs=[fkey.definition() if type(fkey) is DerivaForeignKey else fkey for fkey in fkey_defs],
                comment=comment,
                acls=acls, acl_bindings=acl_bindings,
                annotations=annotations))
            for fkey in fkey_defs:
                # Add foreign key to appropriate referenced_by list
                m.table_model(fkey.referenced_table).referenced_by.append((m.foreign_key_model(fkey)))
                _, _, inbound_sources = fkey.referenced_table.sources()
                fkey.referenced_table.visible_foreign_keys.insert_sources(inbound_sources)

            column_sources, outbound_sources, inbound_sources = table.sources(merge_outbound=True)
            table.visible_columns.insert_context(DerivaContext('*'), column_sources)
            table.visible_columns.insert_context(DerivaContext('entry'), column_sources)

            table.visible_foreign_keys.insert_context(DerivaContext('*'), inbound_sources)

        return table

    def create_asset(self, table_name,
                     column_defs=[],
                     key_defs=[], fkey_defs=[],
                     comment=None,
                     acls={},
                     acl_bindings={},
                     annotations={},
                     file_pattern='.*',
                     extensions=[]):
        """
        Create an asset table.  This function creates a new table that has the standard asset columns in addition
        to columns provided by the caller.

        :param table_name:
        :param column_defs:
        :param key_defs:
        :param fkey_defs:
        :param comment:
        :param acls:
        :param acl_bindings:
        :param annotations:
        :return: A DerivaTable object
        """

        self.logger.debug('table_name: %s', table_name)
        # Now that we know the table name, patch up the key and fkey defs to have the correct name.

        with DerivaModel(self.catalog):
            proto_table = namedtuple('ProtoTable', ['catalog', 'schema', 'schema_name', 'name', 'columns'])
            for k in key_defs:
                k.update_table(proto_table(self.catalog, self.schema, self.name, table_name, column_defs))
            for k in fkey_defs:
                k.update_table(proto_table(self.catalog, self.schema, self.name, table_name, column_defs))

            asset_table = self._create_table(em.Table.define_asset(
                self.schema_name,
                table_name,
                key_defs=[key.definition() if isinstance(key, DerivaKey) else key for key in key_defs],
                fkey_defs=[fkey.definition() if type(fkey) is DerivaForeignKey else fkey for fkey in fkey_defs],
                column_defs=[col.definition() for col in column_defs],
                annotations=annotations,
                acls=acls, acl_bindings=acl_bindings,
                comment=comment)
            )
            asset_table.columns['URL'].annotations[chaise_tags.column_display] = \
                {'*': {'markdown_pattern': '[**{{URL}}**]({{{URL}}})'}}
            asset_table.columns['Filename'].annotations[chaise_tags.column_display] = \
                {'*': {'markdown_pattern': '[**{{Filename}}**]({{{URL}}})'}}
            asset_table.columns['Length'].annotations[chaise_tags.generated] = True
            asset_table.columns['MD5'].annotations[chaise_tags.generated] = True
            asset_table.columns['URL'].annotations[chaise_tags.generated] = True
            asset_table._create_upload_spec(file_pattern, extensions)
            return asset_table

    def create_vocabulary(self, vocab_name, curie_template, uri_template='/id/{RID}', column_defs=[],
                          key_defs=[], fkey_defs=[],
                          comment=None,
                          acls={}, acl_bindings={},
                          annotations={}
                          ):
        """
        Create a vocabulary table that can be used to reference externally defined terms. This funcion provides the
        option to add additional columns to the table, as well as set access control and additional table annotations.

        :param vocab_name: Name of the vocabulary table to be created.
        :param curie_template: Default shortform name for the term, in the form of 'NAMESPACE:{RID}',
        :param uri_template:
        :param column_defs: Additional columns to be added to the vocabulary table.
        :param key_defs:
        :param fkey_defs:
        :param comment: Comment string.
        :param acls:
        :param acl_bindings:
        :param annotations:
        :return: A DerivaTable object
        """
        return self._create_table(
            em.Table.define_vocabulary(vocab_name, curie_template, uri_template=uri_template,
                                       column_defs=column_defs,
                                       key_defs=key_defs, fkey_defs=fkey_defs, comment=comment,
                                       acls=acls, acl_bindings=acl_bindings,
                                       annotations=annotations)
        )

    def validate(self):
        """
        Validate the annotations associated with the tables in this schema.  Look at all visable column,
        visible foreign key, display and other configurable fields associated with the catalog and check to ensure
        they use valid column and key definitions.  Some limited syntax checking is done as well.  Throws an
        exception if an invalid value is found.

        :return: True if all values are valid.
        """

        rval = self.validate_display()
        rval = self.acls.validate(self) and rval
        rval = self.annotations.validate(self) and rval
        for t in self.tables:
            logger.info('Validating table %s', t.name)
            rval = t.validate() and rval
        return rval

    def validate_display(self):
        #TODO Finish....
        return True


class DerivaColumnMap(DerivaLogging, OrderedDict):
    """
    The DerivaColumnMap class is used to define a mapping between columns.  This mapping is used to define how
    columns are renamed.  A column map is an ordered dictionary that reflects the order that the columns should
    be added to the table.  The key of the dictionary is the *current* column name.  The value may take several forms:

    * A string which is the new name of the column.  In this case, all attributes of the column are preserved.

    * A Deriva DerivaColumnDef or ermrest_model Column object, which provides all of the values for the new column.

    * A dictionary that can specify standard column attributes (name, type, nullok,
    default, comment, acls, acl_bindings). In addition the attribute **fill* can be provided, which is a value to
    be used to fill in missing values when mapping a column that has nullok=True to a column that has nullok=Falsue

    """
    def __init__(self, table, column_map, dest_table):
        self.table = table
        self.dest_table = dest_table
        super().__init__()
        self.logger.debug('table: %s dest_table: %s column_map: %s ',
                          table.name if table is None else None,
                          dest_table.name if dest_table else None, column_map)
        self.update(self._normalize_column_map(table, column_map, dest_table))

    def _normalize_column_map(self, table, column_map, dest_table):
        """
        Put a column map into a standard format which is a dictionary in the form of {source-name: DerivaColumnDef}
        where source-name can be in the form of a column or key name.
        A simplified format which is just the SrcCol:DestCo is converted.
        dest_table is used to specify the target table of the mapping if it is not included as part
        of the DerviaColumnSpec.  Entries for each column in columns are also added.

        Once the column_map is normalized, mappings for keys and foreign keys are added based on the columns that are
        being mapped.  We use ordered dictionaries to make the order of the columns consistant with the order of the
        columns, then the order of the column map.
.
        :param column_map:
        :param dest_table:
        :return:
        """

        def normalize_column(k, v):
            """
            The form of a column can be one of:
                column_name: DerivaColumnDef|em.Column
                new_column: typename|dict
                column: new_name
            These are all put into a standard form of name: DerivaColumnDef, with the table attribute set to dest_table
            if provided.

            :param k: Name of the column being mapped
            :param v: Either the name of the new colu\n or a dictionary of new column attributes.
            :return:
            """
            self.logger.debug('column: %s', k)
            if isinstance(v, (DerivaColumn, DerivaKey, DerivaForeignKey)):
                return v

            try:
                # Get the existing column definition if it exists.
                col = table[k]  # Get current definition for the column
                name = v if type(v) is str else v.get('name', k)  # Name may be provided in v, if not use k.
            except DerivaCatalogError:
                # Column is new, so create a default definition for it. If value is a string, then its the type.
                col = DerivaColumn(**{'define': True,
                                      'name': k,
                                      'table': dest_table,
                                      **({'type': v} if type(v) is str else v)})
                name = k

            # We have a column remap in the form of col: new_name or col: dictionary
            # Create a proper dictionary spec for the value adding in a table entry in the case if needed.
            args = {'define': True,
                    'name': name,
                    'table': dest_table,
                    'type': col.type,
                    'nullok': col.nullok,
                    'default': col.default,
                    'fill': col.fill,
                    'comment': col.comment,
                    'acls': col.acls,
                    'acl_bindings': col.acl_bindings}
            return DerivaColumn(**args)

        # Go through the columns in order and add map entries, converting any map entries that are just column names
        # or dictionaries to DerivaColumnDefs

        column_map = OrderedDict((k, normalize_column(k, v)) for k, v in column_map.items())

        # Collect up all of the column name maps.
        column_name_map = OrderedDict((k, v.name) for k, v in column_map.items())
        self.logger.debug('column_map: %s column_name_map %s', column_map, column_name_map)
        self.logger.debug('keys: %s \nkey_columns: %s \n mapped_keys %s \n%s \nfkeys %s \n mapped fkeys %s',
                          [key.name for key in table.keys],
                          [[c.name for c in key.columns] for key in table.keys],
                          [[column_name_map.get(c.name, c.name) for c in key.columns] for key in table.keys],
                          [fkey.name for fkey in table.foreign_keys],
                          [[c.name for c in key.columns] for key in table.foreign_keys],
                          [[column_name_map.get(c.name, c.name) for c in fkey.columns] for fkey in table.foreign_keys],
                          )

        # Get new key and fkey definitions by mapping to new column names.
        column_map.update(
            {key.name:
                 DerivaKey(define=True,
                           table=dest_table,
                           columns=[column_name_map.get(c.name, c.name) for c in key.columns],
                           comment=key.comment,
                           annotations=key.annotations
                           )
             for key in table.keys
             if table._key_in_columns(column_name_map.keys(), key.columns, rename=(table == dest_table))
             }
        )

        column_map.update(
            {
                fkey.name:
                    DerivaForeignKey(define=True,
                                     table=dest_table,
                                     columns=[column_name_map.get(c.name, c.name) for c in fkey.columns],
                                     dest_table=fkey.referenced_table,
                                     dest_columns=[c.name for c in fkey.referenced_columns],
                                     comment=fkey.comment,
                                     acls=fkey.acls,
                                     acl_bindings=fkey.acl_bindings
                                     )
                for fkey in table.foreign_keys
                if table._key_in_columns(column_name_map.keys(), fkey.columns, rename=(table == dest_table))
            }
        )
        self.logger.debug('normalized column map %s', {k:v.name for k,v in column_map.items()})
        return column_map

    def get_columns(self):
        return OrderedDict((k, v) for k, v in self.items() if isinstance(v, DerivaColumn))

    def get_keys(self):
        return OrderedDict((k, v) for k, v in self.items() if isinstance(v, DerivaKey))

    def get_foreign_keys(self):
        return OrderedDict((k, v) for k, v in self.items() if isinstance(v, DerivaForeignKey))

    def get_names(self):
        field = 'name'
        return OrderedDict((k, getattr(v, field)) for k, v in self.items() if getattr(v, field))


class DerivaVisibleSources(DerivaLogging):
    def __init__(self, table, tag):
        super().__init__()
        self.table = table
        self.tag = tag
        self.logger.debug('table: %s tag: %s', table.name, tag)

    def __str__(self):
        return pprint.pformat(self.table.annotations[self.tag])

    def __repr__(self):
        return self.table.annotations[self.tag].__repr__()

    def __getitem__(self, item):
        return self.table.annotations[self.tag][item]

    def __setitem__(self, instance, value):
        with DerivaModel(self.table.catalog):
            self.table.annotations[self.tag].update({instance: value})

    def __iter__(self):
        return self.table.annotations[self.tag].__iter__()

    def to_json(self):
        pass

    def validate(self):
        if self.tag not in self.table.annotations:
            return True
        rval = True
        for c, l in self.table.annotations[self.tag].items():
            try:
                DerivaContext(c)  # Make sure that we have a valid context value.
            except ValueError:
                rval = False
                logger.info('Invalid context name %s', c)
            if c == 'filter':
                if self.tag == chaise_tags.visible_foreign_keys:
                    rval = False
                    logger.info('Filter context not allowed in visible_foreign_key annotation.')
                    continue
                else:
                    try:
                        l = l['and']
                    except TypeError:
                        logger.info('Invalid filter specification %s', l)
                        rval = False
                        continue
            for j in l:
                try:
                    DerivaSourceSpec(self.table, j)
                except DerivaCatalogError as e:
                    logger.info('Invalid source specification %s %s', self.tag, e.msg)
                    rval = False
        return rval

    def clean(self, dryrun=False):
        new_vs = {}
        for c, l in self.table.annotations[self.tag].items():
            new_context = []
            if c == 'filter':
                l = l['and']
            for j in l:
                try:
                    new_context.append(DerivaSourceSpec(self.table, j).spec)
                except DerivaCatalogError:
                    print("Removing {} {}".format(c, j))
            new_vs.update({c: {'and': new_context} if c == 'filter' else new_context})
        if not dryrun:
            with DerivaModel(self.table.catalog):
                self.table.annotations[self.tag] = new_vs

    @staticmethod
    def _normalize_positions(positions):
        """
        A position can be in the form:
          {context: {key:list}, context: {key:list} ...}
          {key:list, ...}
          {context,context}
        where context can be all.  Convert these into a standard format:
           { context: {key:list} ...}

        :param positions: position list
        :return: normalized position.
        """

        def remove_new_columns(plist):
            return OrderedDict((k, v) for k, v in plist.items() if k != v[0])

        # If just a set of contexts, convert to normal form.
        if isinstance(positions, set) or positions == {}:
            return OrderedDict((DerivaContext(j), {})
                                for i in positions
                                for j in (DerivaModel.contexts
                                          if DerivaContext(i) is DerivaContext("all") else [i]))

        try:
            # Map all contexts to enum values...
            return OrderedDict((DerivaContext(j), remove_new_columns(v))
                                for k, v in positions.items()
                                for j in (DerivaModel.contexts
                                          if DerivaContext(k) is DerivaContext("all") else [k]))

        except ValueError:
            # Keys are not valid context name, so we must have keylist dictionary.
            return OrderedDict((k, remove_new_columns(positions)) for k in DerivaModel.contexts)

    def insert_context(self, context, sources=[], replace=False):

        # Map over sources and make sure that they are all ok before we insert...
        if context == 'filter':
            if sources == []:
                sources = {'and': []}
            else:
                sources = copy.deepcopy({'and': [DerivaSourceSpec(self.table, s).spec for s in sources['and']]})
        else:
            sources = copy.deepcopy([DerivaSourceSpec(self.table, s).spec for s in sources])
        self.logger.debug('context: %s %s sources: %s', self.tag, context, sources)
        # check for valid context.

        context = DerivaContext(context)
        if self.tag not in self.table.annotations:
            self.table.annotations[self.tag] = {context.value: sources}
        elif context.value not in self.table.annotations[self.tag] or replace:
            self.table.annotations[self.tag][context.value] = sources
        return

    def insert_sources(self, source_list, positions={}):
        """
        Insert a set of columns into a source list.  If column is included in a foreign-key, make source an outgoing
        spec.

        :param source_list: A column map which will indicate the sources to be included.
        :param positions: where it insert the so
        :return:
        """

        positions = self._normalize_positions({'all'} if positions == {} else positions)
        self.logger.debug('positions: %s', positions)
        self.logger.debug('table: %s sources: %s', self.table.name, [i.spec for i in source_list])

        with DerivaModel(self.table.catalog):
            # Identify any columns that are references to assets and collect up associated columns.
            skip_columns, assets = [], []

            for col in [i.column_name for i in source_list]:
                self.logger.debug('source col %s', col)
                if col == 'pseudo_column':
                    continue
                if chaise_tags.asset in self.table[col].annotations:
                    assets.append(col)
                    skip_columns.extend(self.table[col][chaise_tags.asset].values())

            sources = {}
            try:
                s = self.table.annotations[self.tag]
            except KeyError:
                s = self.table.annotations[self.tag] = {}
            for context, context_list in s.items():
                if DerivaContext(context) not in positions.keys():
                    continue

                if context == 'filter':
                    context_list = context_list['and']

                # Get list of column names that are in the spec, mapping back simple FK references.
                self.logger.debug('source_specs %s %s', self.table.name, [i.spec for i in source_list])
                self.logger.debug('context %s %s', context, [i for i in context_list])
                self.logger.debug('referenced_by %s', [i.name for i in self.table.referenced_by])
                source_specs = [DerivaSourceSpec(self.table, i, validate=False) for i in source_list]
                new_context = [
                    DerivaSourceSpec(self.table, i, validate=False, src_tag=self.tag).spec for i in context_list
                ]
                self.logger.debug('getting source names %s %s', source_specs, new_context)

                for source in source_specs:
                    self.logger.debug('source: %s %s', source.spec, source.spec in new_context)
                    if (context == 'entry' and source.column_name in skip_columns) or source.spec in new_context:
                        # Skip over asset columns in entry context and make sure we don't have repeat column specs.
                        continue
                    new_context.append(source.spec)

                sources[context] = {'and': new_context} if context == 'filter' else new_context
            self.logger.debug('updated sources: %s', pprint.pformat(sources))
            sources = self._reorder_sources(sources, positions)
            self.logger.debug('reordered sources: source:%s',sources)
            # All is good, so update the visible columns annotation.
            self.logger.debug('updated annotations: source:%s %s', sources, pprint.pformat(self.table.annotations.get(self.tag,{})))
            self.table.annotations[self.tag] = {**self.table.annotations.get(self.tag,{}), **sources}
            self.logger.debug('annotations updated: %s', self.table.annotations[self.tag])

    def rename_columns(self, column_map, validate=False):
        """
        Go through a list of visible specs and rename the spec, returning a new visible column spec.

        :param column_map:
        :return:
        """
        if self.tag not in self.table.annotations:
            raise DerivaSourceError(self, msg='tag {} does not exist'.format(self.tag))
        self.logger.debug('column_map %s %s', column_map, pprint.pformat(self.table.annotations[self.tag]))
        # For each context, go through the source specs and rename columns
        new_vc = {}
        for context, vc_list in self.table.annotations[self.tag].items():
            if context == 'filter':
                vc_list = vc_list['and']
            renamed_list = [
                DerivaSourceSpec(self.table, i, validate=validate).rename_column(column_map) for i in vc_list
            ]
            new_vc[context] = {'and': renamed_list} if context == 'filter' else renamed_list

        self.logger.debug('renamed %s', new_vc)
        return new_vc

    def copy_visible_source(self, from_context):
        pass

    def make_outbound(self, column, contexts=None):
        """
        Go through the contexts assoicated with the source list and look for a spec for column and convert this
        from a basic column spec to a outbound source spec.

        :param column: column to convert to outbound spec
        :param contexts:  List of contexts to apply transformation to.  If the empty list, then use all columns.
        :return:
        """

        contexts = contexts if contexts else []

        self.logger.debug('tag: %s columns: %s vc before %s', self.tag, column, self.table.annotations[self.tag])

        context_names = [i.value for i in (DerivaContext if contexts == [] else contexts)]
        for context, vc_list in self.table.annotations[self.tag].items():
            # Get list of column names that are in the spec, mapping back simple FK references.
            if context not in context_names:
                continue

            if context == 'filter':
                vc_list = vc_list['and']
            for s in vc_list:
                # Get the spec for the current element.
                try:
                    spec = DerivaSourceSpec(self.table, s, validate=False, src_tag=self.tag)
                except DerivaSourceError:
                    continue

                if spec.column_name == column:
                    spec = DerivaSourceSpec(self.table, s, validate=False, src_tag=self.tag)
                    # Create a SourceSpec for the column and then convert to outbound spec.
                    spec.make_outbound()
                    s.update(spec.spec)

        self.logger.debug('done %s', self.table.annotations[self.tag])

    def make_column(self, column, contexts=[], validate=True):
        self.logger.debug('tag: %s columns: %s vc before %s', self.tag, column, self.table.annotations[self.tag])
        context_names = [i.value for i in (DerivaContext if contexts == [] else contexts)]
        for context, vc_list in self.table.annotations[self.tag].items():
            if context == 'filter':
                vc_list = vc_list['and']

            # Get list of column names that are in the spec, mapping back simple FK references.
            if context not in context_names:
                continue
            for s in vc_list:
                try:
                    spec = DerivaSourceSpec(self.table, s, validate=False, src_tag=self.tag)
                except DerivaSourceError:
                    # Spec is not correct....
                    continue
                if spec.column_name == column:
                    # Create a SourceSpec for the column and then convert to outbound spec.
                    spec.make_column(validate)
                    s.update(spec.spec)
        self.logger.debug('done %s', self.table.annotations[self.tag])

    def _reorder_sources(self, sources, positions):
        """
        Reorder the columns in a visible columns specification.  Order is determined by the positions argument. The
        form of this is a dictionary whose elements are:
            context: {key_column: column_list, key_column:column_list}
        The columns in the specified context are then reorded so that the columns in the column list follow the column
        in order.  Key column specs are processed in order specified. The context name 'all' can be used to indicate
        that the order should be applied to all contexts currently in the visible_columns annotation.  The context name
        can also be omitted an positions can be in the form of {key_column: columnlist, ...} and the context all is
        implied.

        :param sources:
        :param positions:
        :return:
        """

        if positions == {}:
            return sources

        # Set up positions to apply to all contexts if you have {key_column: column_list} form.
        positions = self._normalize_positions(positions)
        self.logger.debug('normized positions %s', positions)
        new_sources = {}
        for context, source_list in sources.items():
            deriva_context = DerivaContext(context)
            if deriva_context not in positions.keys():
                continue

            if deriva_context == DerivaContext('filter'):
                source_list = source_list['and']

            # Get the list of column names for the spec.
            source_names = []
            for i in range(len(source_list)):
                name = DerivaSourceSpec(self.table, source_list[i], validate=False, src_tag=self.tag).column_name
                source_names.append(name + str(i) if name == 'pseudo_column' else name)

            self.logger.debug('source_names %s', source_names)
            # Now build up a map that has the indexes of the reordered columns.  Include the columns in order
            # Unless they are in the column_list, in which case, insert them immediately after the key column.
            reordered_names = source_names[:]
            for key_col, column_list in positions[deriva_context].items():
                if not (set(column_list + [key_col]) <= set(source_names)):
                    # The column we are looking for is not in this source list.
                    continue
                mapped_list = [j for i in reordered_names if i not in column_list
                               for j in [i] + (
                                   column_list
                                   if i == key_col
                                   else []
                               )
                               ]
                reordered_names = mapped_list

            source_list = [source_list[source_names.index(i)] for i in reordered_names]
            new_sources[context] = {'and': source_list} if context == 'filter' else source_list

        return {**sources, **new_sources}

    def delete_visible_source(self, columns, contexts=[]):
        """
        Delete the named columns from a visible source list.

        :param columns: A list of column names.
        :param contexts: Names of the context to delete the sources from.
        :return:
        """

        if self.tag not in self.table.annotations:
            return

        self.logger.debug('tag: %s columns: %s vc before %s', self.tag, columns,
                          self.table.annotations.get(self.tag, None))
        context_names = [i.value for i in (DerivaContext if contexts == [] else contexts)]
        self.logger.debug('context names %s', context_names)
        columns = [columns] if isinstance(columns, str) else columns
        for context, vc_list in self.table.annotations[self.tag].items():
            # Get list of column names that are in the spec, mapping back simple FK references.
            if context not in context_names:
                continue

            if context == 'filter':
                vc_list = vc_list['and']

            for col in columns:
                # Columns may have already been deleted, so do not validate.
                col_spec = DerivaSourceSpec(self.table, col, validate=False)
                self.logger.debug('checking %s %s %s', col, col_spec, vc_list)
                if col_spec.spec in vc_list:
                    self.logger.debug('deleting %s', col)
                    vc_list.remove(col_spec.spec)
        self.logger.debug('vc after %s', self.table.annotations[self.tag])

    def reorder_visible_source(self, positions):
        vc = self._reorder_sources(self.table.annotations[self.tag], positions)
        self.table.annotations[self.tag].update({**self.table.annotations[self.tag], **vc})


class DerivaVisibleColumns(DerivaVisibleSources):
    def __init__(self, table):
        super().__init__(table, chaise_tags.visible_column)


class DerivaVisibleForeignKeys(DerivaVisibleSources):
    def __init__(self, table):
        super().__init__(table, chaise_tags.visible_foreign_keys)


class DerivaSourceSpec(DerivaLogging):
    def __init__(self, table, spec, validate=True, src_tag=chaise_tags.visible_columns):
        super().__init__()
        self.logger.debug('table: %s spec: %s', table.name, spec)
        self.table = table
        self.tag = src_tag
        if isinstance(spec, DerivaSourceSpec):
            self.spec = copy.deepcopy(spec.spec)
            self.tag = spec.tag
        else:
            self.spec = self._normalize_source_spec(spec, src_tag)

        self.logger.debug('normalized: %s', self.spec)
        if validate:
            self.validate()
        try:
            self.column_name = self._referenced_columns()
        except DerivaSourceError:
            if validate:
                raise
            else:
                self.column_name = 'pseudo_column'
        self.logger.debug('initialized: table %s spec: %s', table.name, self.spec)

    def __str__(self):
        return pprint.pformat(self.spec)

    @property
    def source(self):
        return self.spec['source']

    @source.setter
    def source(self, value):
        self.spec['source'] = value

    def source_type(self):
        if type(self.source) is str:
            return 'column'
        elif isinstance(self.source, (list, tuple)) and len(self.source) == 2:
            if 'inbound' in self.source[0]:
                return 'inbound'
            elif 'outbound' in self.source[0]:
                return 'outbound'
        return None

    def _referenced_columns(self):
        """
        Return the column name that is referenced in the source spec.
        If the spec is a a path then return the value pseudo_column.  If it is a single
        This will require us to look up the column behind an outbound foreign key reference. If

        :return:
        """

        if type(self.source) is str:
            return self.source
        elif len(self.source) == 2 and 'outbound' in self.source[0]:
                t = self.source[0]['outbound'][1]
                try:
                    fk_cols = self.table.foreign_key[t].columns
                except DerivaForeignKeyError:
                        raise DerivaSourceError(self, msg='Outbound source with non-existent foreign key: {}'.format(t))
                return list(fk_cols)[0].name if len(fk_cols) == 1 else None
        else:
            return 'pseudo_column'

    def validate(self):
        """
        Check the values of a normalized spec and make sure that all of the columns and keys in the source exist.

        :return:
        """
        spec = self._normalize_source_spec(self.spec, None)
        source_entry = spec['source']
        if type(spec['source']) is str:
            if spec['source'] not in [i.name for i in self.table.columns]:
                raise DerivaSourceError(self, 'Invalid source entry {}'.format(spec))
        else:
            # We have a path of FKs so follow the path to make sure that all of the constraints line up.
            path_table = self.table
            for c in source_entry[0:-1]:
                if 'inbound' in c and len(c['inbound']) == 2:
                    self.logger.debug('validating inbound table: %s: context: %s refererenced_by: %s',
                                      path_table.name, c, [i.name for i in path_table.referenced_by])
                    path_table = path_table.referenced_by[c['inbound']].table
                elif 'outbound' in c and len(c['outbound']) == 2:
                    self.logger.debug('validating outbound %s: %s', path_table.name, c)
                    path_table = path_table.foreign_keys[c['outbound']].referenced_table
                else:
                    raise DerivaSourceError(self, 'Invalid source entry {}'.format(c))

            try:
                if source_entry[-1] not in path_table.columns:
                    raise DerivaSourceError(self, 'Invalid source entry {}'.format(source_entry[-1]))
            except TypeError:
                raise DerivaSourceError(self, 'Invalid source entry {}'.format(source_entry[-1]))
        return spec

    def _normalize_source_spec(self, spec, src_tag):
        """
        Convert a source spec into a uniform form using the new source notations.

        :param spec:
        :return:
        """
        self.logger.debug('%s %s', self.table.name, spec)
        if type(spec) is str:
            if spec in self.table.columns:
                spec = {'source': spec}
            elif spec in self.table.foreign_keys:
                spec = {'source': [{'outbound': (self.table.schema_name, spec)}, 'RID']}
            elif spec in self.table.referenced_by:
                spec = {'source': [{'inbound': (self.table.schema_name, spec)}, 'RID']}
            else:
                raise DerivaSourceError(self, 'Invalid source entry {}'.format(spec))
        # Check for old style foreign key notation and turn into inbound or outbound source.
        elif isinstance(spec, (tuple, list)) and len(spec) == 2:
            if spec[1] in self.table.keys:
                return {'source': next(iter(self.table.keys[spec[1]].columns)).name}
            elif spec[1] in self.table.foreign_keys:
                return {'source': [{'outbound': tuple(spec)}, 'RID']}
            elif spec[1] in self.table.referenced_by:
                return {'source': [{'inbound': tuple(spec)}, 'RID']}
            else:
                default_direction = 'inbound' if src_tag == chaise_tags.visible_foreign_keys else 'outbound'
                return {'source': [{default_direction: tuple(spec)}, 'RID']}
        else:
            # We have a spec that is already in source form.
            # every element of pseudo column source except the last must be either an inbound or outbound spec.
            try:
                if not (isinstance(spec['source'], str) or
                        all(map(lambda x: len(x.get('inbound', x.get('outbound',[]))) == 2, spec['source'][0:-1]))):
                    raise DerivaSourceError(self, 'Invalid source entry {}'.format(spec))
            except (TypeError, KeyError):
                raise DerivaSourceError(self, 'Invalid source entry {}'.format(spec))
        return spec

    def rename_column(self, column_map):
        self.logger.debug('spec: %s map %s ', self.spec, column_map)
        if self.column_name != 'pseudo_column':
            if self.column_name in column_map:
                # See if the column is used as a simple foreign key.
                try:

                    fkey_name = self.table.foreign_keys[self.column_name].name
                    self.logger.debug('column %s foreign key name %s %s',
                                      self.source,
                                      fkey_name,
                                      fkey_name in column_map)
                except DerivaCatalogError:
                    fkey_name = None

                # If we are renaming a column, and it is used in a foreign_key, then make the spec be a outbound
                # source using the FK.  Otherwise, just rename the column in the spec if needed.
                if fkey_name and fkey_name in column_map:
                    return {'source':
                        [
                            {'outbound': (column_map[fkey_name].referenced_table.schema_name,
                                          column_map[fkey_name].name)}, 'RID'
                        ]
                    }
                elif self.column_name in column_map:
                    return {'source': column_map[self.column_name].name}
                else:
                    self.logger.debug('mapping source , to %s ', {**self.spec, **{'source': column_map[self.source].name}})
                    return {**self.spec, **{'source': column_map[self.source].name}}
            else:
                return self.spec
        else:
            # We have a list of  inbound/outbound specs.  Go through the list and replace any names that are in the map.
            self.logger.debug('Looking for rename in source path: %s', self.source[:-1])
            source = []
            for s in self.source[:-1]:
                direction = next(iter(s))   # inbound or outbound
                key_schema, key_name = next(iter(s.values()))
                if key_schema == column_map.table.schema_name and key_name in column_map:
                    source.append({direction: (key_schema, column_map[key_name].name)})
                else:
                    source.append(s)
            source.append(self.source[-1:])

            return {**self.spec, **{'source': source}}


    def make_outbound(self, validate=True):
        if self.source_type() is 'column':
            col_name = self.table.foreign_key[self.source].name
            self.spec.update(self._normalize_source_spec([self.table.schema_name, col_name], self.tag))
            if validate:
                self.validate()
        return self

    def make_column(self, validate=True):
        """
        Convert a outbound spec on a foreign key to a column spec.
        :param validate:
        :return:
        """
        # Get the fk_name from the spec and then change spec to be the key column.
        if self.source_type() is 'outbound':
            fk_name = self.source[0]['outbound'][1]
            self.spec.update(self._normalize_source_spec(
                next(iter(self.table.foreign_keys[fk_name].columns)).name, self.tag)
            )

            if validate:
                self.validate()
        return self


class DerivaColumn(DerivaCore):
    """
    Class that represents columns in Deriva catalog.  The same class is used for columns that are being defined
    as well as columns that have already been defined.
    """
    class _DerivaColumnDef(DerivaLogging):
        def __init__(self, name, type, nullok=True, default=None, fill=None, comment=None, acls={},
                     acl_bindings={}, annotations={}):
            super().__init__()

            self.name = name
            self.type = type if isinstance(type, em.Type) else em.builtin_types[type]
            self.nullok = nullok
            self.default = default
            self.fill = fill
            self.comment = comment
            self.acls = copy.deepcopy(acls.value
                                      if isinstance(acls, DerivaACL) else acls)
            self.acl_bindings = copy.deepcopy(acl_bindings.value
                                              if isinstance(acl_bindings, DerivaACLBinding) else acl_bindings)
            self.annotations =  copy.deepcopy(annotations.annotations
                if isinstance(annotations, DerivaAnnotations) else annotations)

        def definition(self):
            return em.Column.define(
                self.name,
                self.type,
                nullok=self.nullok,
                default=self.default,
                comment=self.comment,
                acls=self.acls,
                acl_bindings=self.acl_bindings,
                annotations=self.annotations
            )

    def __init__(self, table, name, type=type,
                 nullok=True, default=None, fill=None, comment=None,
                 acls={}, acl_bindings={},
                 annotations={}, define=False
                 ):
        """
        The
        Column name already exists in table. If so the existing definition is used.
        Column name doesn't exist, if so other arguments are used to initialize the columns def.

        :param table: DerivaTable object, or None if the table is being defined along with the class.
        :param name: Name of the column.  If a em.Column is passed in as a name, then its name is used.
        """

        super().__init__(table.catalog if table else None)

        self.logger.debug('table: %s name: %s type: %s define: %s', table.name if table else "None",
                          name if isinstance(name, (str,int, dict)) else name.name, type, define)

        if isinstance(name, em.Column):  # We are providing a em.Column as the name argument.
            name = name.name

        # We do not yet have a table for this column, so set table to None and fill in later.
        self.table = None if define and not isinstance(table, DerivaTable) else table
        self.column = None

        if table:
            self.schema = self.catalog[table.schema_name]
            m = DerivaModel(self.catalog)
            self.column = m.column_exists(table, name)

        if self.column:
            if define:
                raise DerivaCatalogError(self, 'Column already exists: {}'.format(name))
            else:
                return
        else:
            if define:
                self.column = DerivaColumn._DerivaColumnDef(name, type,
                                                            nullok=nullok, default=default, fill=fill,
                                                            comment=comment,
                                                            acls=acls, acl_bindings=acl_bindings,
                                                            annotations=annotations)
            else:
                raise DerivaCatalogError(self, 'Column does not exist: {}'.format(name)
                                         )

    def __str__(self):
        return '\n'.join(
            [
                '{}: {}'.format(self.name, self.type.typename),
                '\tnullok: {} default: {}'.format(self.nullok, self.default),
                '\tcomment: {}'.format(self.comment),
                '\tacls: {}'.format(self.acls),
                '\tacl_bindings: {}'.format(self.acl_bindings)
            ]
        )

    @classmethod
    def define(cls, name, type,
               nullok=True, default=None, fill=None,
               comment=None,
               acls={}, acl_bindings={},
               annotations={}):

        return DerivaColumn(None, name, type, nullok=nullok, default=default, fill=fill, comment=comment,
                            acls=acls, acl_bindings=acl_bindings, annotations=annotations, define=True)

    @property
    def name(self):
        return self.column.name

    @property
    def type(self):
        return self.column.type

    @type.setter
    def type(self, type_value):
        if isinstance(self.column, DerivaColumn._DerivaColumnDef):
            self.column.type = em.builtin_types[type_value]
        else:
            raise DerivaCatalogError(self, 'Cannot alter defined column type')

    @property
    def nullok(self):
        return self.column.nullok

    @nullok.setter
    def nullok(self, nullok):
        if isinstance(self.column, DerivaColumn._DerivaColumnDef):
            self.column.nullok = nullok
        else:
            raise DerivaCatalogError(self, 'Cannot alter nullok in defined column')

    @property
    def default(self):
        return self.column.default

    @property
    def fill(self):
        return self.column.fill if isinstance(self.column, DerivaColumn._DerivaColumnDef) else None

    @property
    def comment(self):
        return self.column.comment

    @comment.setter
    def comment(self, comment):
        self.column.comment = comment

    @property
    def display(self):
        return self.annotations[chaise_tags.display]

    @display.setter
    def display(self, value):
        self.annotations[chaise_tags.display] = value

    @property
    def column_display(self):
        return self.annotations[chaise_tags.column_display]

    @column_display.setter
    def column_display(self, value):
        self.annotations[chaise_tags.column_display] = value

    @staticmethod
    def convert_def(table, column_def):
        return DerivaColumn(table,
                            column_def.name, column_def.type,
                            column_def.nullok, column_def.default,
                            comment=column_def.comment,
                            acls=column_def.acls,
                            acl_bindings=column_def.acl_bindings,
                            annotations=column_def.annotations
                            )
    def get_acls(self):
        with DerivaModel(self.catalog) as m:
            return (
                self.column.acls if isinstance(self.column, DerivaColumn._DerivaColumnDef)
                else m.column_model(self).acls
            )

    def get_acl_bindings(self):
        with DerivaModel(self.catalog) as m:
            return (
                self.column.acl_bindings
                if isinstance(self.column, DerivaColumn._DerivaColumnDef)
                else m.column_model(self).acl_bindings
            )

    def definition(self):
        # Column will either be a DerivaColumn or an ermrest column.
        try:
            return self.column.definition()
        except AttributeError:
            return self.column

    def update_table(self, table):
        if self.table:
            return
        self.catalog = table.catalog
        self.table = table
        self.schema = self.catalog[table.schema_name]

    def create(self):
        self.logger.debug('%s %s', self.table.name, self.column.definition())
        with DerivaModel(self.table.catalog) as m:
            self.column = m.table_model(self.table).create_column(self.catalog.ermrest_catalog,
                                                                  self.column.definition())

    def delete(self):
        """
        Delete a single column.
        :return:
        """
        self.table.delete_columns(self)

    def validate(self):
        rval =  self.annotations.validate(self)
        rval = self.acls.validate(self) and rval
        rval = self.acl_bindings.validate(self) and rval
        return rval

    def validate_display(self):
        # TODO Need to finish
        return True


class DerivaKey(DerivaCore):
    class _DerivaKeyDef(DerivaLogging):
        def __init__(self,
                     table,
                     columns,
                     name=None,
                     comment=None,
                     annotations={}):

            super().__init__()

            self.unique_columns = columns
            self.name = name
            self.comment = comment
            self.annotations = copy.deepcopy(
                annotations.annotations if isinstance(annotations, DerivaAnnotations) else annotations
            )
            self.update_name(table)

        def definition(self, key):
            return em.Key.define(
                self.unique_columns,
                constraint_names=[(key.table.schema_name, self.name)],
                comment=self.comment,
                annotations=self.annotations
            )

        def update_name(self, table):
            # Key column order may change, so we need to put into standard order before computing key name.
            if not self.name and table:
                self.name = '{}_'.format(table.name) + \
                            '_'.join([c for c in self.unique_columns] + ['key'])

    def __init__(self, table, columns, name=None, comment=None, annotations={}, define=False):
        """
        :param table: Table in which this key exists
        :param columns: Either the name of the key or the unique columns in the key.
        :param name:
        :param comment:
        :param annotations:
        :param define:
        """
        super().__init__(table.catalog if table else None)
        self.logger.debug('table %s columns %s %s', table.name if table else "none", columns, define)

        self.key = None
        self.table = table
        if table:
            self.schema = self.catalog[table.schema_name]

        if isinstance(name, em.Key):  # We are providing a em.Key as the name argument.
            self.key = name

        if isinstance(columns, em.Key):
            self.key = columns

        if self.key:
            return

        # Get just the name part of the potential (schema,name) pair
        if isinstance(name, tuple) and len(name) == 2 and name[0] == table.schema_name:
            name = name[1]

        if table:
            try:
                m = DerivaModel(self.catalog)
                self.key = m.key_exists(table, name if name else columns)
            except DerivaModelError:
                # Table hasn't been defined yet....
                pass
        # If we are defining a Key and it already exists, then we have an error, otherwise, we are done.
        if self.key:
            if define:
                raise DerivaCatalogError(self, 'Key already exists: {}'.format(columns))
            else:
                return
        else:
            if define:
                # We are creating a new key, so create a DerivaKeyDef
                self.key = DerivaKey._DerivaKeyDef(table, columns,
                                                   name=name, comment=comment, annotations=annotations)
            else:
                raise DerivaKeyError(self, "Key doesn't exist {}".format(name))

    def __str__(self):
        return '{name}:{columns}\n\tcomment: {comment}\n\tannotations: {annotations}'.format(
            name=self.name, columns=[i.name for i in self.columns],
            comment=self.comment, annotations=[a for a in self.annotations])

    @property
    def name(self):
        try:
            return self.key.name
        except AttributeError:
            return self.key.names[0][1] if len(self.key.names) == 1 else None

    @property
    def full_name(self):
        try:
            return (self.table.schema_name, self.key.name)
        except AttributeError:
            return self.key.names[0]

    @property
    def columns(self):
        columns = [c.name for c in self.table.columns if c.name in self.key.unique_columns]
        assert len(columns) == len(self.key.unique_columns)
        # add in any new columns....
        columns.extend([i for i in self.key.unique_columns if i not in columns])

        return ElementList(self._key_column, columns)

    @property
    def comment(self):
        return self.key.comment

    @comment.setter
    def comment(self, comment):
        if isinstance(self.key, DerivaKey._DerivaKeyDef):
            self.key.comment = comment
        else:
            raise DerivaCatalogError(self, 'Cannot alter defined key type')

    @property
    def display(self):
        return self.annotations[chaise_tags.key_display]

    @display.setter
    def display(self, value):
        self.annotations[chaise_tags.display] = value

    @property
    def key_display(self):
        return self.annotations[chaise_tags.key_display]

    @key_display.setter
    def key_display(self, value):
        self.annotations[chaise_tags.key_display] = value

    @staticmethod
    def define(columns, name=None, comment=None, annotations={}):
        return DerivaKey(None, columns, name, comment, annotations, define=True)

    @staticmethod
    def convert_def(table, key_def):
        if not isinstance(key_def, em.Key):
            raise DerivaCatalogError(table.catalog, 'convert_def must have em.Key as an argument')
        return DerivaKey(table,
                         key_def.unique_columns,
                         name=key_def.names[0],
                         comment=key_def.comment, annotations=key_def.annotations)

    def update_table(self, table):
        if self.table:
            return
        self.catalog = table.catalog
        self.table = table
        self.schema = self.catalog[table.schema_name]
        self.key.update_name(table)

    def _key_column(self, column_name):
        return DerivaColumn(self.table, column_name)

    def create(self):
        self.logger.debug('%s', self.definition())
        with DerivaModel(self.table.catalog) as m:
            self.key = m.table_model(self.table).create_key(self.catalog.ermrest_catalog, self.definition())

    def delete(self):
        try:
            with DerivaModel(self.table.catalog) as m:
                m.key_model(self).delete(self.catalog.ermrest_catalog, m.table_model(self.table))
        except HTTPError as e:
            raise DerivaKeyError(self, msg=str(e))
        self.table = None
        self.key = None

    def get_acls(self):
        with DerivaModel(self.catalog) as m:
            return (
                self.key.acls if isinstance(self.key, DerivaKey._DerivaKeyDef)
                else m.key_model(self).acls
            )

    def definition(self):
        # Key will either be a DerivaKey or an ermrest key.
        try:
            return self.key.definition(self)
        except AttributeError:
            return self.key

    def validate(self):
        return self.annotations.validate(self)

    def validate_display(self):
        # TODO finish
        return True


class DerivaForeignKey(DerivaCore):
    class _DerivaForeignKeyDef:
        def __init__(self,
                     table, columns,
                     referenced_table, referenced_columns,
                     name=None,
                     comment=None,
                     on_update='NO ACTION',
                     on_delete='NO ACTION',
                     acls={},
                     acl_bindings={},
                     annotations={}):

            self.name = name
            self.columns = columns
            self.referenced_table = referenced_table
            self.referenced_columns = referenced_columns
            self.comment = comment
            self.on_update = on_update
            self.on_delete = on_delete
            self.acls = copy.deepcopy(acls.value
                                      if isinstance(acls, DerivaACL) else acls)
            self.acl_bindings = copy.deepcopy(acl_bindings.value
                                              if isinstance(acl_bindings, DerivaACLBinding) else acl_bindings)
            self.annotations =  copy.deepcopy(annotations.annotations
                if isinstance(annotations, DerivaAnnotations) else annotations)

            self.update_name(table)
            fk_ops = ['CASCADE', 'DELETE', 'RESTRICT', 'NO ACTION', 'SET NULL']

            if on_update not in fk_ops or on_delete not in fk_ops:
                raise ValueError('Invalid value for on_update/on_delete {} {}'.format(on_update, on_delete))

        def definition(self, fkey):

            return em.ForeignKey.define(
                self.columns,
                self.referenced_table.schema_name, self.referenced_table.name, self.referenced_columns,
                constraint_names=[(fkey.table.schema_name, self.name)],
                comment=self.comment,
                on_update=self.on_update,
                on_delete=self.on_delete,
                acls=self.acls,
                acl_bindings=self.acl_bindings,
                annotations=self.annotations
            )

        def update_name(self, table):
            # Key column order may change, so we need to put into standard order before computing key name.
            if not self.name and table:
                self.name = '{}_'.format(table.name) + \
                            '_'.join([c for c in self.columns] + ['fkey'])

    def __init__(self, table, columns=None,
                 dest_table=None, dest_columns=None,
                 name=None,
                 comment=None,
                 on_update='NO ACTION',
                 on_delete='NO ACTION',
                 acls=None,
                 acl_bindings=None,
                 annotations={},
                 define=False):
        """"
        Create a DerivaForeignKey object from an existing ERMrest FKey, or initalize an object for a key to be created
            at some point in the future.

        :param table: Table in which this key exists
        :param: dest_table: A DerivaTable that is the target of this FK.
        :param name: Either the name of the key, an existing ERMrest FK or the unique columns in the key.
        :param define:
        """

        acls = acls if acls else {}
        acl_bindings if acl_bindings else {}
        annotations if annotations else {}

        super().__init__(table.catalog if table else None)
        self.logger.debug('%s %s %s %s', table.name if table else None, columns, dest_columns, define)

        if isinstance(name, em.ForeignKey):  # We are providing a em.ForeignKey as the name argument.
            name = name.names[0]

        if isinstance(columns, em.ForeignKey):  # We are providing a em.ForeignKey as the columns argument.
            name = columns.names[0]

        # Get just the name part of the potential (schema,name) pair
        if isinstance(name, (tuple, list)) and len(name) == 2 and name[0] == table.schema_name:
            name = name[1]

        self.fkey = None
        self.table = table

        # We may not have a table yet for this FK if we are creating it as part of creating a table.
        if table:
            self.schema = self.catalog[table.schema_name]
            m = DerivaModel(self.catalog)
            self.fkey = m.foreign_key_exists(table, name if name else columns)

        # If we are defining a FK and it already exists, then we have an error, otherwise, we are done.
        if self.fkey:
            if define:
                raise DerivaForeignKeyError(self, 'Foreign Key already exists'.format(columns))
            else:
                return

        # We are defining a new FK, so create a DerivaForeignKeyDef to hold the info until the key is created.
        self.logger.debug('creating fkey def %s', define)
        if define:
            self.fkey = DerivaForeignKey._DerivaForeignKeyDef(table, columns,
                                                              dest_table, dest_columns,
                                                              name=name, comment=comment,
                                                              on_update=on_update, on_delete=on_delete,
                                                              acls=acls, acl_bindings=acl_bindings,
                                                              annotations=annotations)
        else:
            raise DerivaForeignKeyError(self, "Foreign key doesn't exist: {}".format(name))
        self.logger.debug('fkey def %s', self.fkey)

    def __str__(self):
        return '\n'.join([
            '{}: {}'.format(self.name, self.columns),
            '\tcomment: {}'.format(self.comment),
            '\tannotations: {}'.format(self.annotations)
        ])

    @staticmethod
    def define(
            columns,
            dest_table, dest_columns,
            name=None,
            comment=None,
            on_update='NO ACTION',
            on_delete='NO ACTION',
            acls={},
            acl_bindings={},
            annotations={}
    ):
        return DerivaForeignKey(None, columns, dest_table, dest_columns,
                                name=name,
                                comment=comment,
                                on_update=on_update, on_delete=on_delete,
                                acls=acls, acl_bindings=acl_bindings,
                                annotations=annotations,
                                define=True)

    def update_table(self, table):
        if self.table:
            return
        self.catalog = table.catalog
        self.table = table
        self.schema = self.catalog[table.schema_name]
        self.fkey.update_name(table)

    @property
    def name(self):
        try:
            return self.fkey.name
        except AttributeError:
            return self.fkey.names[0][1]

    @property
    def full_name(self):
        try:
            return (self.table.schema_name, self.fkey.name)
        except AttributeError:
            return self.fkey.names[0]

    def _key_column(self, column_name):
        self.logger.debug('column_name %s', column_name)
        # May have a emrest column name, or just the name of the column
        return DerivaColumn(
            self.table,
            column_name if isinstance(column_name, str) else column_name['column_name'])

    @property
    def columns(self):
        m = DerivaModel(self.catalog)
        columns = [
            c.name for c in self.table.columns if c.name in [i['column_name'] for i in self.fkey.foreign_key_columns]
        ]
        assert len(columns) == len(self.fkey.foreign_key_columns)
        self.logger.debug('%s %s', m.foreign_key_model(self), m.foreign_key_model(self).foreign_key_columns)
        return ElementList( self._key_column, columns)

    @property
    def referenced_table(self):
        try:
            return self.fkey.referenced_table
        except AttributeError:
            src_schema = self.fkey.referenced_columns[0]['schema_name']
            src_table = self.fkey.referenced_columns[0]['table_name']
            return self.table.catalog[src_schema][src_table]

    def _referenced_column(self, column_name):
        # May have a emrest column name, or just the name of the column
        return DerivaColumn(
            self.referenced_table,
            column_name if isinstance(column_name, str) else column_name['column_name'])

    @property
    def referenced_columns(self):
        # Need to order columns so that they are consistant.
        m = DerivaModel(self.catalog)
        col_map = dict(zip([c['column_name'] for c in self.fkey.foreign_key_columns],
                           [c['column_name'] for c in self.fkey.referenced_columns]))
        columns = [
            col_map[c.name] for c in self.table.columns if c.name in [i['column_name'] for i in self.fkey.foreign_key_columns]
        ]
        return ElementList(self._referenced_column, columns)

    @property
    def comment(self):
        return self.fkey.comment

    @comment.setter
    def comment(self, comment):
        if isinstance(self.fkey, DerivaForeignKey):
            self.fkey.comment = comment
        else:
            raise DerivaCatalogError(self, 'Cannot alter defined key type')

    @property
    def on_update(self):
        return self.fkey.on_update

    @property
    def on_delete(self):
        return self.fkey.on_delete


    @staticmethod
    def convert_def(table, fkey_def):
        if not isinstance(fkey_def, em.ForeignKey):
            raise DerivaCatalogError(table.catalog, 'convert_def must have em.ForeignKey as an argument')
        c = fkey_def.referenced_columns[0]
        dest_table = table.catalog[c['schema_name']][c['table_name']]
        return DerivaForeignKey(table, fkey_def.foreign_key_columns,
                                dest_table, dest_columns=fkey_def.referenced_columns,
                                name=fkey_def.names[0][1],
                                comment=fkey_def.comment,
                                on_update=fkey_def.on_update, on_delete=fkey_def.on_delete,
                                acls=fkey_def.acls, acl_bindings=fkey_def.acl_bindings,
                                annotations=fkey_def.annotations)

    def create(self):
        with DerivaModel(self.table.catalog) as m:
            self.logger.debug('%s', self.definition())
            self.fkey = m.table_model(self.table).create_fkey(self.catalog.ermrest_catalog, self.definition())
            m.table_model(self.referenced_table).referenced_by.append(self.fkey)

    def delete(self):
        referenced_table = self.referenced_table
        column = next(iter(self.columns)) if len(self.columns) == 1 else False
        self.logger.debug('demoting visible column %s', column)

        referenced_table.visible_foreign_keys.delete_visible_source(self.name)
        del (referenced_table.referenced_by[self.name])

        if column:
            self.table.visible_columns.make_column(column.name, validate=False)

        with DerivaModel(self.table.catalog) as m:
            m.foreign_key_exists(self.table, self.name).delete(self.catalog.ermrest_catalog, m.table_model(self.table))

        self.table = None
        self.fkey = None

    def get_acls(self):
        with DerivaModel(self.catalog) as m:
            return self.fkey.acls

    def get_acl_bindings(self):
        with DerivaModel(self.catalog) as m:
            return self.fkey.acl_bindings

    def definition(self):
        # Key will either be a DerivaForeignKey or an ermrest fkey.
        try:
            return self.fkey.definition(self)
        except AttributeError:
            return self.fkey

    def validate(self):
        rval = self.annotations.validate(self)
        rval = self.acls.validate(self) and rval
        rval = self.acl_bindings.validate(self) and rval
        return rval

    def validate_display(self):
        # TODO need to finish....
        return True


class DerivaTable(DerivaCore):
    def __init__(self, catalog, schema_name, table_name):
        super().__init__(catalog)
        self.schema = catalog[schema_name]
        self.table = self
        self.schema_name = schema_name
        self._table_name = table_name
        self.deleted = False

    def __getitem__(self, column_name):
        return self.column(column_name)

    def __iter__(self):
        return self.columns.__iter__()

    def __str__(self):
        return '\n'.join([
            'Table {}'.format(self.name),
            tabulate.tabulate(
                [[i.name, i.type.typename, i.nullok, i.default] for i in self.columns],
                headers=['Name', 'Type', 'NullOK', 'Default']
            ),
            '\n',
            'Keys:',
            tabulate.tabulate([[i.name, [c.name for c in i.columns]] for i in self.keys],
                              headers=['Name', 'Columns']),
            '\n',
            'Foreign Keys:',
            tabulate.tabulate(
                [[i.name, [c.name for c in i.columns], '->',
                  i.referenced_table.name, [c.name for c in i.referenced_columns]]
                 for i in self.foreign_keys],
                headers=['Name', 'Columns', '', 'Referenced Table', 'Referenced Columns']),
            '\n\n',
            'Referenced By:',
            tabulate.tabulate(
                [
                    [i.name,
                     [c.name for c in i.referenced_columns],
                     '<-',
                     '{}:{}:'.format(i.table.schema_name,
                                     i.table.name),
                     [c.name for c in i.columns]
                     ]
                    for i in self.referenced_by],
                headers=['Name', 'Columns', '', '', 'Referenced Columns'])
        ]
        )

    @property
    def chaise_uri(self):
        p = urlparse(self.catalog.server_uri)
        return '{}://{}/chaise/recordset/#{}/{}:{}'.format(
            p.scheme, p.hostname, self.catalog.catalog_id, self.schema_name, self.name)

    @property
    def name(self):
        return self._table_name

    @property
    def comment(self):
        with DerivaModel(self.catalog) as m:
            return m.table_model(self).comment

    @comment.setter
    def comment(self, value):
        with DerivaModel(self.catalog) as m:
            m.table_model(self).comment = value

    @property
    def display(self):
        return self.annotations[chaise_tags.display]

    @display.setter
    def display(self, value):
        self.annotations[chaise_tags.display] = value

    @property
    def table_display(self):
        return self.annotations[chaise_tags.table_display]

    @table_display.setter
    def table_display(self, value):
        self.annotations[chaise_tags.table_display] = value

    @property
    def visible_columns(self):
        try:
            return DerivaVisibleSources(self, chaise_tags.visible_columns)
        except KeyError:
            raise DerivaSourceError(self, msg='Visible columns not defined')

    @visible_columns.setter
    def visible_columns(self, vcs):
        self.annotations[chaise_tags.visible_columns] = vcs

    @property
    def visible_foreign_keys(self):
        return DerivaVisibleSources(self, chaise_tags.visible_foreign_keys)

    @visible_foreign_keys.setter
    def visible_foreign_keys(self, keys):
        self.annotations[chaise_tags.visible_foreign_keys] = keys

    @property
    def columns(self):
        m = DerivaModel(self.catalog)
        return ElementList(self.column, m.table_model(self).column_definitions)

    @property
    def keys(self):
        m = DerivaModel(self.catalog)
        return ElementList(self._key, m.table_model(self).keys)

    @property
    def foreign_key(self):
        return self.foreign_keys

    @property
    def foreign_keys(self):
        m = DerivaModel(self.catalog)
        return ElementList(self._foreign_key, m.table_model(self).foreign_keys)

    @property
    def referenced_by(self):
        m = DerivaModel(self.catalog)
        return ElementList(lambda x: self._referenced(x, m.table_model(self).referenced_by),
                           m.table_model(self).referenced_by)

    def key_referenced(self, columns):
        """
        Given a set of columns that are a key, return the list of foreign keys that reference those columns.
        :param columns:
        :return:
        """
        if not self.key[columns]:
            raise DerivaCatalogError(self,msg='Argument to key_referenced is not a key')
        columns = set(columns)
        return [fk for fk in self.referenced_by if {i.name for i in fk.referenced_columns} == columns]

    def _key(self, key_name):
        return DerivaKey(self.catalog[self.schema_name][self.name], key_name)

    def _foreign_key(self, fkey_name):
        self.logger.debug('%s', fkey_name)
        return DerivaForeignKey(self.catalog[self.schema_name][self.name], name=fkey_name)

    def _referenced(self, fkey_id, referenced_by):
        """
        Return the list of DerivaForeignKeys associated with fk_id.  The Referenced_by list is different in that it is
        keys ih other tables which that the current table as the target.  We will name the FK we are interested
        in by providing eather 1) the name of that FK, 2)
        or 2) a ERMrest Foreign Key.  In order to reassociate the key with the source table, we need to look into
        the list of referenced_by keys and search for the schema so we get the table that the key is in.
        :param fk:
        :return: A list of foreign keys that reference the column, or the single foreign key whose name matches.
        """
        self.logger.debug('fkey_id: %s referenced_by: %s', fkey_id, [fk.names for fk in referenced_by])
        fkey = None
        if isinstance(fkey_id, em.ForeignKey):
            fkey = fkey_id
        else:
            # We have either a constraint name or a column name.
            try:
                # See if we already have a key name
                fkey = referenced_by[tuple(fkey_id)]
            except (KeyError, TypeError):
                for schema in self.catalog:
                    try:
                        fkey = referenced_by[(schema.name, fkey_id)]
                    except (TypeError, KeyError):
                        continue

        if not fkey:
            raise DerivaCatalogError(self, 'referenced by requires name or key type: {}'.format(fkey_id))

        # Now find the schema and table of the referring table
        src_schema = fkey.foreign_key_columns[0]['schema_name']
        src_table = fkey.foreign_key_columns[0]['table_name']
        self.logger.debug('creating fkey... %s', fkey.names[0])
        return DerivaForeignKey(self.table.catalog[src_schema][src_table], fkey)

    @property
    def key(self):
        return self.keys

    def datapath(self):
        return self.catalog.getPathBuilder().schemas[self.schema_name].tables[self.name]

    def _column_names(self):
        return [i.name for i in self.columns]

    def create_key(self, columns, name=None, comment=None, annotations={}):
        key = DerivaKey(self, columns, name, comment, annotations, define=True)
        self.logger.debug('creating key....')
        key.create()

    def column(self, column_name):
        return DerivaColumn(self.catalog[self.schema_name][self.name], column_name)

    def validate(self):
        with DerivaModel(self.catalog):
            rval = self.annotations.validate(self)
            rval = self.keys.validate() and rval
            rval = self.foreign_keys.validate() and rval
            rval = self.columns.validate() and rval
            rval = self.acls.validate(self) and rval
            rval = self.acl_bindings.validate(self) and rval
            return rval

    def validate_display(self):
        # TODO FInish....
        return True

    def validate_table_display(self):
        rval = True
        for k in self.table_display.keys():
            DerivaContext(k)
        return rval

    def _column_map(self, column_map, dest_table):
        return DerivaColumnMap(self, column_map, dest_table)

    def entities(self, *attributes, **renamed_attributes):
        return self.datapath().entities(*attributes, **renamed_attributes)

    def create_foreign_key(self,
                           columns, referenced_table, referenced_columns,
                           name=None,
                           comment=None,
                           on_update='NO ACTION',
                           on_delete='NO ACTION',
                           acls={},
                           acl_bindings={},
                           annotations={},
                           position={}):
        """

        :param columns: Column names in current table that are used for the foreign key
        :param referenced_table:  Dervia table that is being referenced by this foreign key
        :param referenced_columns:
        :param name:
        :param comment:
        :param on_update:
        :param on_delete:
        :param acls:
        :param acl_bindings:
        :param annotations:
        :param position:
        :return:
        """
        self.logger.debug('table: %s columns: %s %s referenced_columns: %s referenced_by: %s', self.name, columns,
                          referenced_table.name, referenced_columns,
                          [i.name for i in referenced_table.referenced_by])
        with DerivaModel(self.catalog) as m:
            try:
                fkey = DerivaForeignKey(self, columns,
                                        referenced_table,
                                        referenced_columns,
                                        comment=comment,
                                        acls=acls,
                                        acl_bindings=acl_bindings,
                                        name=name,
                                        on_update=on_update,
                                        on_delete=on_delete,
                                        annotations=annotations,
                                        define=True)
            except DerivaCatalogError as e:
                raise
            fkey.create()

            _, _, inbound_sources = referenced_table.sources(filter=[fkey.name])
            # Pick out the source for this key:

            self.logger.debug('inbound sources %s', [s.spec for s in inbound_sources])
            self.logger.debug('inbound sources %s', [c.name for c in referenced_table.referenced_by])
            referenced_table.visible_foreign_keys.insert_sources(inbound_sources, position)

            if len(columns) == 1:
                self.visible_columns.make_outbound(columns[0])
                self.logger.debug('new vc %s', self.visible_columns)

    def sources(self, merge_outbound=False, filter=None):
        """
        Create source lists from table columns.

        Go through the columns and keys in the current table and create a list of DerivaSourceSpecs for each of them.
        If filter is provided, only the column or key names in the list are examined.
        If merge_outbound is true and a column is used in a simple foreign key, used return an outbound source rather
        then the column source.

        :param merge_outbound: If True and the column is in a simple foreign_key s
        :param filter: List of column or key names to include in the returned source lists.
        :return: A triple of DerivaSourceSpec lists for columns, foreign_keys and incoming foreign_keys.
        """
        def full_key_name(k):
            return (k.table.schema_name, k.name)

        # Go through the list of foreign keys and create a list of key columns in simple foreign keys
        fkey_names = {
            [c.name for c in fk.columns][0]: fk
            for fk in self.foreign_keys if len(fk.columns) == 1
        }

        # TODO We should check to see if target is vocabulary and if so use ID rather then RID
        column_sources = [
            DerivaSourceSpec(self,
                             {'source': (
                                 [{'outbound': full_key_name(fkey_names[col.name])}, 'RID']
                                 if col.name in fkey_names and merge_outbound
                                 else col.name
                             )}
                             )
            for col in self.table.columns if not filter or col.name in filter
        ]

        outbound_sources = [
            DerivaSourceSpec(self,
                             {'source': [{'outbound': full_key_name(i)}, 'RID']}) for i in self.table.foreign_keys
            if not filter or i.name in filter]
        inbound_sources = [
            DerivaSourceSpec(self,
                             {'source': [{'inbound': full_key_name(i)}, 'RID']}) for i in self.table.referenced_by
            if not filter or i.name in filter
        ]

        return column_sources, outbound_sources, inbound_sources

    @staticmethod
    def _rename_markdown_pattern(pattern, column_map):
        # Look for column names {{columnname}} in the templace and update.
        # TODO handle: 'markdown_pattern': '{{{$fkeys.Beta_Cell.XRay_Tomography_Data_File_Type_FKey.rowName}}}'
        for k, v in column_map.get_names().items():
            pattern = pattern.replace('{{{}}}'.format(k), '{{{}}}'.format(v))
            pattern = pattern.replace('fkeys.{}.{}'.format(column_map.table.schema_name, k),
                                      'fkeys.{}.{}'.format(column_map.dest_table.schema_name, v))
        return pattern

    @staticmethod
    def _rename_columns_in_display(dval, column_map):
        return {
            k: DerivaTable._rename_markdown_pattern(v, column_map) if (k == 'markdown_name' or k == 'row_markdown_pattern') else v
            for k, v in dval.items()
        }

    @staticmethod
    def _rename_columns_in_context_display(dval, column_map):
        return {context: {k: DerivaTable._rename_markdown_pattern(v, column_map) for k, v in cvalue.items()}
                for context, cvalue in dval.items()
                }

    def _rename_columns_in_annotations(self, column_map, skip_annotations=[], validate=False):
        new_annotations = {}
        self.catalog.rename_visible_columns(column_map, validate=validate)
        for k, v in self.annotations.items():
            if k in skip_annotations:
                renamed = v
            elif k == chaise_tags.display:
                renamed = self._rename_columns_in_display(v, column_map)
            elif (k == chaise_tags.table_display or k == chaise_tags.column_display):
                renamed = DerivaTable._rename_columns_in_context_display(v, column_map)
            else:
                renamed = v
            new_annotations[k] = renamed
        return new_annotations

    def _rename_columns_in_acl_bindings(self, _column_map):
        with DerivaModel(self.catalog) as m:
            table = m.table_model(self)
            return table.acl_bindings

    def _rename_columns_in_column_annotations(self, annotation, column_map):
        return annotation

    def _key_in_columns(self, columns, key_columns, rename=False):
        """
        Given a set of columns and a key, return true if the key is in that column set.  If we are simply renaming
        columns, rather then moving them to a new table, not all of the columns in a composite key have to be present
        as we still have the other columns available to us.  Return false if there is no overlap.  Raise an exception
        if you are attmpting to break up a composite key.

        :param columns:  List of columns in a table that are being altered
        :param key_columns: list of columns in the key
        :param rename: true if you are renaming columns within a single table, rather then deleting or moving them.
        :return: True if the key is contained within columns.
        """

        overlap = set(columns).intersection({k.name for k in key_columns})
        # Determine if we are moving the column within the same table, or between tables.
        self.logger.debug('columns %s key_columns %s overlap %s', columns, {k.name for k in key_columns}, overlap)
        if len(overlap) == 0:
            return False
        if (not rename) and (len(overlap) < len(key_columns)):
            raise DerivaCatalogError(self, msg='Cannot rename part of compound key {}'.format(key_columns))
        return True

    def _check_composite_keys(self, columns, rename=False):
        """
        Go over all of the keys, incoming and outgoing foreign keys and check to make sure that renaming the set of
        columns  won't break up composite keys if they are renamed.

        :param columns:list of columns that you want to check.
        :param rename: true if you are renaming columns within a single table, rather then deleting or moving them.
        :return:
        """
        columns = set(columns)
        self.logger.debug('columns %s, %s', columns, rename)
        for i in self.keys:
            self.logger.debug('key %s', [k.name for k in i.columns])
            self._key_in_columns(columns, i.columns, rename)

        for fk in self.foreign_keys:
            self.logger.debug('foreign_key %s %s', fk.table.name, [i.name for i in fk.columns])
            self._key_in_columns(columns, fk.columns, rename)
            self._key_in_columns(columns, fk.columns, rename)

    def _copy_keys(self, column_map):
        """
        Copy over the keys from the current table to the destination table, renaming columns.
        :param column_map:
        :return:
        """

        for k, key_def in column_map.get_keys().items():
            self.logger.debug('from key_name %s to key_name: %s', k, key_def.name)
            key_def.create()

        for k, fkey_def in column_map.get_foreign_keys().items():
            self.logger.debug('fro fkey_name %s to %s', k, fkey_def.name)
            fkey_def.create()

    def _delete_columns_in_display(self, annotation, columns):
        raise DerivaCatalogError(self, 'Cannot delete column from display annotation')

    def _delete_columns_from_annotations(self, columns, column_specs):
        for k, v in self.annotations.items():
            if k == chaise_tags.display:
                self._delete_columns_in_display(v, columns)
            elif k == chaise_tags.visible_columns or k == chaise_tags.visible_foreign_keys:
                DerivaVisibleSources(self, k).delete_visible_source(column_specs)

    def _create_upload_spec(self, file_pattern, extensions):
        """
        Create a basic asset table and configures the bulk upload annotation to load the table along with a table of
        associated metadata. This routine assumes that the metadata table has already been defined, and there is a key
        associated metadata. This routine assumes that the metadata table has already been defined, and there is a key
        column the metadata table that can be used to associate the asset with a row in the table. The default
        configuration assumes that the assets are in a directory named with the table name for the metadata and that
        they either are in a subdirectory named by the key value, or that they are in a file whose name starts with the
        key value.

        :return:
        """
        extension_pattern = '^.*[.](?P<file_ext>{})$'.format('|'.join(extensions if extensions else ['.*']))

        key_column = 'foo'
        spec = [
                # Any metadata is in a file named /records/schema_name/tablename.[csv|json]
                {
                    'default_columns': ['RID', 'RCB', 'RMB', 'RCT', 'RMT'],
                    'ext_pattern': '^.*[.](?P<file_ext>json|csv)$',
                    'asset_type': 'table',
                    'file_pattern': '^((?!/assets/).)*/records/(?P<schema>%s?)/(?P<table>%s)[.]' %
                                    (self.schema_name, self.name),
                    'target_table': [self.schema_name, self.name],
                },
                # Assets are in format assets/schema_name/table_name/correlation_key/file.ext
                {
                    'checksum_types': ['md5'],
                    'column_map': {
                        'URL': '{URI}',
                        'Length': '{file_size}',
                        self.name: '{table_rid}',
                        'Filename': '{file_name}',
                        'MD5': '{md5}',
                    },
                    'dir_pattern': '^.*/(?P<schema>%s)/(?P<table>%s)/(?P<key_column>.*)/' %
                                   (self.schema_name, self.name),
                    'ext_pattern': extension_pattern,
                    'file_pattern': file_pattern,
                    'hatrac_templates': {'hatrac_uri': '/hatrac/{schema}/{table}/{md5}.{file_name}'},
                    'target_table': [self.schema_name, self.name],
                    # Look for rows in the metadata table with matching key column values.
                    'metadata_query_templates': [
                        '/attribute/D:={schema}:{table}/%s={key_column}/table_rid:=D:RID' % key_column],
                    # Rows in the asset table should have a FK reference to the RID for the matching metadata row
                    'record_query_template':
                        '/entity/{schema}:{table}/{table}={table_rid}/MD5={md5}/URL={URI_urlencoded}',
                    'hatrac_options': {'versioned_uris': True},
                }
            ]

        # The last thing we should do is update the upload spec to accomidate this new asset table.
        if chaise_tags.bulk_upload not in self.catalog.annotations:
            self.catalog.annotations.update({
                chaise_tags.bulk_upload: {
                    'asset_mappings': [],
                    'version_update_url': 'https://github.com/informatics-isi-edu/deriva-qt/releases',
                    'version_compatibility': [['>=0.4.3', '<1.0.0']]
                }
            })

        # Clean out any old upload specs if there are any and add the new specs.
        upload_annotations = self.catalog.annotations[chaise_tags.bulk_upload]
        upload_annotations['asset_mappings'] = \
            [i for i in upload_annotations['asset_mappings'] if
             not (
                     i.get('target_table', []) == [self.schema_name, self.name]
                     or
                     (
                             i.get('target_table', []) == [self.schema_name, self.name]
                             and
                             i.get('asset_type', '') == 'table'
                     )
             )
             ] + spec

    def delete_columns(self, columns):
        """
        Drop a set of columns from a table, cleaning up visible columns and keys.  You cannot delete columns if they
        are being used by a foreign key in another table, or if they are part of a composite key and you are only
        deleting a subset of the columns.

        :param columns: A list of column names or DerivaColumn instances for the current table
        """

        if isinstance(columns, DerivaColumn):
            columns = [columns.name]

        self.logger.debug('%s', columns)

        # Don't delete just part of a key or foreign_key.
        self._check_composite_keys(columns)

        # If columns are being referenced by another table, then do not delete them.
        for fk in self.referenced_by:
            self.logger.debug('referenced_columns %s %s %s %s',
                              columns, fk.table.name, fk.referenced_table.name,
                              [i.name for i in fk.referenced_columns])
            if self._key_in_columns(columns, fk.referenced_columns) and fk.on_delete != 'CASCADE':
                raise DerivaCatalogError(self, msg='Key referenced by foreign key {}'.format(columns))

        with DerivaModel(self.catalog) as m:
            # Capture the source specs before we start deleting columns....
            column_specs = [DerivaSourceSpec(self, c) for c in columns]

            # Remove keys...
            for k in self.keys:
                if self._key_in_columns(columns, k.columns):
                    k.delete()

            for fk in self.foreign_keys:
                if self._key_in_columns(columns, fk.columns):
                    fk.delete()

            # Now delete the actual columns
            for c in columns:
                m.column_model(self.column(c)).delete(self.catalog.ermrest_catalog, m.table_model(self.table))

            # Now clean up all the annotations.
            self._delete_columns_from_annotations(columns, column_specs)

    def copy_columns(self, column_map, dest_table=None):
        """
        Copy a set of columns, updating visible columns list and keys to mirror source columns. The columns to copy
        are specified by a column map.  Column map can be a dictionary with entries SrcCol: DerviaColumnSpec or
        SrcCol:TargetCol.

        :param column_map: a column_map that describes the list of columns.
        :param dest_table: Table name of destination table
        :param column_map: A dictionary that specifies column name mapping
        :return:
        """
        with DerivaModel(self.catalog):
            dest_table = dest_table if dest_table else self
            column_map = self._column_map(column_map, dest_table)

            columns = column_map.get_columns()
            column_names = [k for k in column_map.get_columns().keys()]

            # TODO we need to figure out what to do about ACL binding

            # Make sure that we can rename the columns
            overlap = {v.name for v in columns.values()}.intersection(set(dest_table._column_names()))
            if len(overlap) != 0:
                raise ValueError('Column {} already exists.'.format(overlap))

            self._check_composite_keys(column_names, rename=(dest_table == self))

            # Update visible column spec, putting copied column right next to the source column.
            positions = {col: [column_map[col].name] for col in column_map.get_columns()} if dest_table is self else {}
            dest_table.create_columns([i for i in columns.values()], positions)

            # Copy over the old values
            from_path = self.datapath()
            to_path = dest_table.datapath()

            # Get the values of the columns, and remap the old column names to the new names.  Skip over new columns that
            # don't exist in the source table.
            rows = from_path.entities(
                **{
                    **{val.name: getattr(from_path, col) for col, val in column_map.get_columns().items()
                       if col in self.columns},
                    **{'RID': from_path.RID}
                }
            )
            to_path.update(rows)

            # Copy over the keys.
            self._copy_keys(column_map)
        return

    def create_columns(self, columns, positions={}, visible=True):
        """
        Create a new column in the table.

        :param columns: A list of DerivaColumn.
        :param positions:  Where the column should be added into the visible columns spec.
        :param visible: Include this column in the visible columns spec.
        :return:
        """
        self.logger.debug('columns %s positions: %s', columns, positions, )
        column_names = []
        columns = columns if type(columns) is list else [columns]

        with DerivaModel(self.catalog):
            for column in columns:
                column.update_table(self)
                column.create()
                column_names.append(column.name)

            if visible:
                sources, _, _ = self.sources(filter=column_names)
                self.visible_columns.insert_sources(sources, positions)

    def rename_column(self, from_column, to_column, default=None, nullok=None):
        """
        Rename a column by copying it and then deleting the origional column.
        :param from_column:
        :param to_column:
        :param default:
        :param nullok:
        :return:
        """
        column_map = {from_column: DerivaColumn(table=self, name=to_column, type=from_column.type, nullok=nullok,
                                                   default=default)}
        self.rename_columns(column_map=column_map)
        return

    def rename_columns(self, column_map, dest_table=None, delete=True):
        """
        Rename a column by copying it and then deleting the origional column.
        :param dest_table:
        :param column_map:
        :param delete:
        :return:
        """
        with DerivaModel(self.catalog):
            dest_table = dest_table if dest_table else self
            column_map = self._column_map(column_map, dest_table)

            for fk in self.referenced_by:
                self.logger.debug('referenced_columns %s %s %s %s',
                                  column_map.get_names(), fk.table.name, fk.referenced_table.name,
                                  [i.name for i in fk.referenced_columns])
                if self._key_in_columns(column_map.get_names(), fk.referenced_columns, rename=(self == dest_table)):
                    raise DerivaCatalogError(self,
                                             msg='Key referenced by foreign key {}'.format(column_map.get_names()))

            self.copy_columns(column_map, dest_table)
            # Update column name in ACL bindings....
            self._rename_columns_in_acl_bindings(column_map)
            # Update annotations where the old spec was being used. We have already moved over
            # the visible columns, so skip the visible columns annotation.
            self.annotations.update(
                self._rename_columns_in_annotations(column_map, skip_annotations=[chaise_tags.visible_columns])
            )
            if delete:
                columns = [k for k in column_map.get_columns().keys()]
                # Go through the keys and foreign_keys and delete any constraints that include the columns.
                for i in self.keys:
                    if self._key_in_columns(columns, i.columns, rename=(self == dest_table)):
                        self.logger.debug('delete key %s', [k.name for k in i.columns])
                        i.delete()

                for fk in self.foreign_keys:
                    if self._key_in_columns(columns, fk.columns, rename=(self == dest_table)):
                        self.logger.debug('delete key %s', [k.name for k in fk.columns])
                        fk.delete()

                self.delete_columns(columns)
        return

    def delete(self):
        """
        Delete a table
        :return:
        """

        if len(self.referenced_by) != 0:
            DerivaCatalogError(self, 'Attept to delete table with incoming foreign keys')

        with DerivaModel(self.catalog) as m:
            for fk in self.foreign_keys:
                fk.referenced_table.visible_foreign_keys.delete_visible_source(fk.name)

            model = m.catalog_model()
            table = m.table_model(self)
            # Now we can delete the table.
            table.delete(self.catalog.ermrest_catalog, schema=model.schemas[self.schema_name])
            self.deleted = True
        self.catalog.update_referenced_by()

    def _relink_columns(self, dest_table, column_map):
        """
        We want to replace the current table with the dest_table. Go through the list of tables that are currently
        pointing to this table and replace the foreign_key to reference dest_table instead.  Some of the columns may
        have been renamed, so use the column_map to get the current table name.

        :param dest_table:
        :param column_map:
        :return:
        """
        self.logger.debug('%s %s %s', self.name, dest_table.name, [i.name for i in self.referenced_by])
        for fkey in list(self.referenced_by):
            fk_columns = [i.name for i in fkey.columns]
            referenced_columns = [i.name for i in fkey.referenced_columns]
            column_name_map = column_map.get_names()
            child_table = fkey.table
            self.logger.debug('relinking table: %s fkey: %s columns: %s %s', child_table.name, fkey.name, fk_columns, referenced_columns)
            if self._key_in_columns(column_name_map.keys(), fkey.referenced_columns, rename=(self == dest_table)):
                comment = fkey.comment
                acls = fkey.acls
                acl_bindings = fkey.acl_bindings
                annotations = fkey.annotations

                self.logger.debug('before delete table: %s fkey: %s referenced_by: %s', child_table.name, fkey.name, [i.name for i in self.referenced_by])
                fkey.delete()
                self.logger.debug('after delete referenced_by: %s', [i.name for i in self.referenced_by])
                child_table.create_foreign_key(
                    fk_columns,
                    dest_table,
                    [column_name_map.get(i, i) for i in referenced_columns],
                    comment=comment,
                    acls=acls,
                    acl_bindings=acl_bindings,
                    annotations=annotations
                )
        self.catalog.update_referenced_by()
        self.catalog.rename_visible_columns(column_map)

    def copy_table(self, schema_name, table_name, column_map={}, clone=False,
                   key_defs=[],
                   fkey_defs=[],
                   comment=None,
                   acls={},
                   acl_bindings={},
                   annotations={}
                   ):
        """
        Copy the current table to the specified target schema and table. All annotations and keys are modified to
        capture the new schema and table name. Columns can be renamed in the target table by providing a column mapping.
        Key and foreign key definitions can be augmented or overwritten by providing appropriate arguments. Lastly
        if the clone argument is set to true, the RIDs of the source table are reused, so that the equivalent of a
        move operation can be obtained.

        :param schema_name: Target schema name
        :param table_name:  Target table name
        :param column_map: A dictionary that is used to rename columns in the target table.
        :param clone:
        :param key_defs:
        :param fkey_defs:
        :param comment:
        :param acls:
        :param acl_bindings:
        :param annotations:
        :return: The new table
        """
        self.logger.debug('schema_name %s dest_table %s', schema_name, table_name)

        with DerivaModel(self.catalog):
            # Augment the column_map with entries for columns in the table, but not in the map.
            new_map = {i.name: column_map.get(i.name, i.name) for i in self.columns}
            new_map.update(column_map)
            # Add keys to column map. We need to create a dummy destination table for this call.
            proto_table = namedtuple('ProtoTable', ['catalog', 'schema', 'schema_name', 'name'])
            dest_table = proto_table(self.catalog, self.catalog[schema_name], schema_name, table_name)
            column_map = self._column_map(new_map, dest_table)

            # new_columns = [c['name'] for c in column_defs]

            # TODO May want to preserver pseudo columns that start with outbound fk.
            annotations = self._rename_columns_in_annotations(column_map)
            annotations.pop(chaise_tags.visible_foreign_keys, None)

            new_table = self.catalog[schema_name].create_table(
                table_name,
                # Use column_map to change the name of columns in the new table.
                column_defs=column_map.get_columns().values(),
                key_defs=[i for i in column_map.get_keys().values()] + key_defs,
                fkey_defs=[i for i in column_map.get_foreign_keys().values()] + fkey_defs,
                comment=comment if comment else self.comment,
                acls={**self.acls, **acls},
                acl_bindings={**self.acl_bindings, **acl_bindings},
                annotations=annotations
            )

            # Create new table
            new_table.table_model = table_name
            new_table.schema_model = schema_name

            # Copy over values from original to the new one, mapping column names where required. Use the column_fill
            # argument to provide values for non-null columns.
            pb = self.catalog.getPathBuilder()
            from_path = pb.schemas[self.schema_name].tables[self.name]
            to_path = pb.schemas[schema_name].tables[table_name]

            self.logger.debug('copying columns: %s',
                              {column_map.get(i.name, i).name: getattr(from_path, i.name) for i in self.columns})

            v = from_path.attributes(
                    **{column_map.get(i.name, i).name: getattr(from_path, i.name) for i in self.columns})

            rows = map(
                lambda x: {**x, **{k: v.fill for k, v in column_map.get_columns().items() if v.fill}},
                v.fetch())

            to_path.insert(list(rows), **({'nondefaults': {'RID', 'RCT', 'RCB'}} if clone else {}))
        return new_table

    def move_table(self, schema_name, table_name,
                   delete=True,
                   column_map={},
                   key_defs=[],
                   fkey_defs=[],
                   comment=None,
                   acls={},
                   acl_bindings={},
                   annotations={}
                   ):
        """
        Move a table, renaming and inserting new columns.

        :param schema_name: Schema for new table
        :param table_name: Name of new table
        :param delete: Delete the origional table.  Defaults to True
        :param column_map: A DerivaColumnMap that defines and column renaming or insertions.
        :param key_defs: New keys that should be defined in the target table
        :param fkey_defs:
        :param comment:
        :param acls:
        :param acl_bindings:
        :param annotations:
        :return: New DerivaTable object
        """
        self.logger.debug('%s %s %s', schema_name, table_name, column_map)

        with DerivaModel(self.catalog):
            # Augment the column_map with entries for columns in the table, but not in the map.
            new_map = {i.name: column_map.get(i.name, i.name) for i in self.columns}
            new_map.update(column_map)
            # Add keys to column map. We need to create a dummy destination table for this call.
            proto_table = namedtuple('ProtoTable', ['catalog', 'schema', 'schema_name', 'name'])
            dest_table = proto_table(self.catalog, self.catalog[schema_name], schema_name, table_name)
            column_map = self._column_map(new_map, dest_table)

            new_table = self.copy_table(schema_name, table_name, clone=True,
                                        column_map=column_map,
                                        key_defs=key_defs,
                                        fkey_defs=fkey_defs,
                                        comment=comment,
                                        acls=acls,
                                        acl_bindings=acl_bindings,
                                        annotations=annotations)

            self._relink_columns(new_table, column_map)
            if delete:
                self.delete()
        return new_table

    def create_asset_table(self, key_column,
                           extensions=[],
                           file_pattern='.*',
                           column_defs=[], key_defs=[], fkey_defs=[],
                           comment=None, acls={},
                           acl_bindings={},
                           annotations={},
                           set_policy=True):
        """
        Create a basic asset table and configures the bulk upload annotation to load the table along with a table of
        associated metadata. This routine assumes that the metadata table has already been defined, and there is a key
        associated metadata. This routine assumes that the metadata table has already been defined, and there is a key
        column the metadata table that can be used to associate the asset with a row in the table. The default
        configuration assumes that the assets are in a directory named with the table name for the metadata and that
        they either are in a subdirectory named by the key value, or that they are in a file whose name starts with the
        key value.

        :param key_column: The column in the metadata table to be used to correlate assets with entries. Assets will be
                           named using the key column.
        :param extensions: List file extensions to be matched. Default is to match any extension.
        :param file_pattern: Regex that identified the files to be considered for upload
        :param column_defs: a list of Column.define() results for extra or overridden column definitions
        :param key_defs: a list of Key.define() results for extra or overridden key constraint definitions
        :param fkey_defs: a list of ForeignKey.define() results for foreign key definitions
        :param comment: a comment string for the asset table
        :param acls: a dictionary of ACLs for specific access modes
        :param acl_bindings: a dictionary of dynamic ACL bindings
        :param annotations: a dictionary of annotations
        :param set_policy: If true, add ACLs for self serve policy to the asset table
        :return:
        """

        def create_asset_upload_spec():
            extension_pattern = '^.*[.](?P<file_ext>{})$'.format('|'.join(extensions if extensions else ['.*']))

            return [
                # Any metadata is in a file named /records/schema_name/tablename.[csv|json]
                {
                    'default_columns': ['RID', 'RCB', 'RMB', 'RCT', 'RMT'],
                    'ext_pattern': '^.*[.](?P<file_ext>json|csv)$',
                    'asset_type': 'table',
                    'file_pattern': '^((?!/assets/).)*/records/(?P<schema>%s?)/(?P<table>%s)[.]' %
                                    (self.schema_name, self.name),
                    'target_table': [self.schema_name, self.name],
                },
                # Assets are in format assets/schema_name/table_name/correlation_key/file.ext
                {
                    'checksum_types': ['md5'],
                    'column_map': {
                        'URL': '{URI}',
                        'Length': '{file_size}',
                        self.name: '{table_rid}',
                        'Filename': '{file_name}',
                        'MD5': '{md5}',
                    },
                    'dir_pattern': '^.*/(?P<schema>%s)/(?P<table>%s)/(?P<key_column>.*)/' %
                                   (self.schema_name, self.name),
                    'ext_pattern': extension_pattern,
                    'file_pattern': file_pattern,
                    'hatrac_templates': {'hatrac_uri': '/hatrac/{schema}/{table}/{md5}.{file_name}'},
                    'target_table': [self.schema_name, asset_table_name],
                    # Look for rows in the metadata table with matching key column values.
                    'metadata_query_templates': [
                        '/attribute/D:={schema}:{table}/%s={key_column}/table_rid:=D:RID' % key_column],
                    # Rows in the asset table should have a FK reference to the RID for the matching metadata row
                    'record_query_template':
                        '/entity/{schema}:{table}_Asset/{table}={table_rid}/MD5={md5}/URL={URI_urlencoded}',
                    'hatrac_options': {'versioned_uris': True},
                }
            ]

        asset_table_name = '{}_Asset'.format(self.name)

        if set_policy and chaise_tags.catalog_config not in self.catalog.annotations:
            raise DerivaCatalogError(self, msg='Attempting to configure table before catalog is configured')

        if key_column not in self.columns:
            raise DerivaCatalogError(self, msg='Key column not found in target table')

        column_defs = [
                          DerivaColumn.define('{}'.format(self.name),
                                              'text',
                                              nullok=False,
                                              comment="The {} entry to which this asset is attached".format(
                                                  self.name)),
                      ] + column_defs

        # Set up policy so that you can only add an asset to a record that you own.
        fkey_acls, fkey_acl_bindings = {}, {}
        if set_policy:
            groups = self.catalog.get_groups()

            fkey_acls = {
                "insert": [groups['curator']],
                "update": [groups['curator']],
            }
            fkey_acl_bindings = {
                "self_linkage_creator": {
                    "types": ["insert", "update"],
                    "projection": ["RCB"],
                    "projection_type": "acl",
                },
                "self_linkage_owner": {
                    "types": ["insert", "update"],
                    "projection": ["Owner"],
                    "projection_type": "acl",
                }
            }

        # Link asset table to metadata table with additional information about assets.
        asset_fkey_defs = [
                              DerivaForeignKey.define([self.name],
                                                      self.schema_name, self.name, ['RID'],
                                                      acls=fkey_acls, acl_bindings=fkey_acl_bindings,
                                                      )
                          ] + fkey_defs
        comment = comment if comment else 'Asset table for {}'.format(self.name)

        if chaise_tags.table_display not in annotations:
            annotations[chaise_tags.table_display] = {'row_name': {'row_markdown_pattern': '{{{Filename}}}'}}

        asset_table = self.schema.create_asset(
            asset_table_name,
            column_defs=column_defs, key_defs=key_defs, annotations=annotations,
            acls=acls, acl_bindings=acl_bindings,
            comment=comment)

        # The last thing we should do is update the upload spec to accomidate this new asset table.
        if chaise_tags.bulk_upload not in self.catalog.annotations:
            self.catalog.annotations.update({
                chaise_tags.bulk_upload: {
                    'asset_mappings': [],
                    'version_update_url': 'https://github.com/informatics-isi-edu/deriva-qt/releases',
                    'version_compatibility': [['>=0.4.3', '<1.0.0']]
                }
            })

        # Clean out any old upload specs if there are any and add the new specs.
        upload_annotations = self.catalog.annotations[chaise_tags.bulk_upload]
        upload_annotations['asset_mappings'] = \
            [i for i in upload_annotations['asset_mappings'] if
             not (
                     i.get('target_table', []) == [self.schema_name, asset_table_name]
                     or
                     (
                             i.get('target_table', []) == [self.schema_name, self.name]
                             and
                             i.get('asset_type', '') == 'table'
                     )
             )
             ] + create_asset_upload_spec()

        return asset_table

    def link_tables(self, target_table, column_name=None, target_column='RID', create_column=True):
        """
        Create a foreign key link from the specified column to the target table and column.

        :param column_name: Column or list of columns in current table which will hold the FK
        :param target_table: Target table to link to.
        :param target_column: Column to link the table on.  Defaults to *RID*
        :param create_column: Create a new column for the foreign key.  Name defaults to the target table name.
        """

        if not column_name:
            column_name = '{}'.format(target_table.name)
        if create_column:
            self.create_columns([DerivaColumn.define(column_name, target_table[target_column].type)])

        self.create_foreign_key([column_name], target_table, [target_column])

        # Now add the foreign key to the visible columns list so we can edit the linkage.
        self.visible_columns.insert_sources([DerivaSourceSpec(self, column_name)])

    def link_vocabulary(self, column_name, term_table):
        """
        Set an existing column in the table to refer to an existing vocabulary table.
        :param column_name: Name of the column whose value is to be from the vocabular
        :param term_table: The term table.
        :return: None.
        """
        if not self.is_vocabulary_table():
            raise DerivaCatalogError(self, 'Attempt to link_vocabulary on a non-vocabulary table')

        self.link_tables(column_name, term_table, target_column='ID')
        return

    def associate_vocabulary(self, term_table, table_column='RID'):
        """
        Set an existing column in the table to refer to an existing vocabulary table.

        :param column_name: Name of the column whose value is to be from the vocabular
        :param term_table: The term table.
        :return: None.
        """
        if not term_table.is_vocabulary_table():
            raise DerivaCatalogError(self, 'Attempt to link_vocabulary on a non-vocabulary table')

        self.associate_tables(term_table, table_column=table_column, target_column='ID')
        return

    def disassociate_tables(self, target_table):
        association_table_name = '{}_{}'.format(self.name, target_table.name)
        raise DerivaCatalogError('Not implented')

    def associate_tables(self, target_table, table_column='RID', target_column='RID', inline=True):
        """
        Create a pure binary association table that connects rows in the table to rows in the target table.
        Assume that RIDs are used for linking. however, this can be over riden.

        :param target_schema: Schema of the table that is to be associated with current table
        :param target_table: Name of the table that is to be associated with the current table
        :param table_column: Name of the column in the current table that is used for the foreign key, defaults to RID
        :param target_column: Name of the column in the target table that is to be used for the foreign key, defaults
                              to RID
        :return: Association table.
        """

        association_table_name = '{}_{}'.format(self.name, target_table.name)

        column_defs = [
            DerivaColumn.define('{}'.format(self.name), 'text', nullok=False),
            DerivaColumn.define('{}'.format(target_table.name), 'text', nullok=False)
        ]

        key_defs = [DerivaKey.define([self.name, target_table.name])]

        fkey_defs = [
            DerivaForeignKey.define([self.name], self, [table_column]),
            DerivaForeignKey.define([target_table.name], target_table, [target_column])
        ]
        table_def = self.schema.create_table(
            association_table_name,
            column_defs,
            key_defs=key_defs, fkey_defs=fkey_defs,
            comment='Association table for {}'.format(association_table_name))

        # Add reference to association table as an incoming reference to visible columns of table being associated.
        for fkey in table_def.foreign_keys:
            _, _, inbound_sources = fkey.referenced_table.sources(filter=[fkey.name])
            fkey.referenced_table.visible_columns.insert_sources(inbound_sources)

    def is_pure_binary(self):
        """
        Check to see if the table has the propoerties of a pure binary association.

          1. It only has two foreign keys,
          2. There is a uniqueness constraint on the two keys.
          3. NULL values are not allowed in the foreign keys.

        :return: Boolean
        """
        # table has only two foreign_key constraints.
        # Each constraint is over only one column.
        if [len(fk.columns) for fk in self.foreign_keys] != [1,1]:
            return False

        [c0, c1]  = [ next(iter(fk.columns)) for fk in self.foreign_keys]

        # There is a key constraint on the pair of fkey columns.

        try:
            self.key[c0.name, c1.name]
        except DerivaKeyError:
            return False

        # Null is not allowed on the column.
        if c0.nullok or c1.nullok:
            return False

        return True

    def associated_tables(self):
        """
        Assuming the table is an pure binary association table, return the two table endpoints

        :param table: ermrest table object for a table that is a pure binary association table.
        :return: list of 2-tuples that are the schema and table for the two tables in the M:N relationship
        """
        if not self.is_pure_binary():
            raise DerivaCatalogError(self,msg='Table not pure binary %s'.format(self.name))

        return [fk.referenced_table for fk in self.foreign_keys]

    def is_vocabulary_table(self):
        """
        Test to see if a table is a deriva vocabulary table.
        :return: True or False.
        """
        return  ({'ID', 'URI', 'Description', 'Name'} < set(self._column_names()))

    def describe(self):
        print(self)
