import elasticsearch_dsl
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from future.utils import with_metaclass


class FieldMappingValidationError(Exception):
    """
    Superclass for exceptions raised when :meth:`.FieldMapping.validate_mapping` fails.
    """


class DoctypeFieldDoesNotExist(FieldMappingValidationError):
    """
    Raised when :meth:`.FieldMapping.validate_mapping` fails because
    the referenced doctype field does not exist on the DocType.
    """


class ModelFieldDoesNotExist(FieldMappingValidationError):
    """
    Raised when :meth:`.FieldMapping.validate_mapping` fails because
    the referenced Django model field does not exist.
    """


class FieldMapping(object):
    """
    Base class for all Django field to ElasticSearch field mappings.

    .. attribute:: doctypefieldname

        The name of the doctype field.

    .. attribute:: modelfieldname

        The name of the model field.
    """

    #: If this is ``True``, the response from :meth:`.to_doctype_value` is expected to be
    #: a dict, and that dict is merged into the document instead of added as a single key, value pair.
    merge_into_document = False

    #: The appropriate elasticearch-dsl field class to use when
    #: autocreating DocType fields from this FieldMapping.
    #: Used by :meth:`.automake_doctype_fields`.
    elasticsearchdsl_fieldclass = None

    def __init__(self, modelfieldname=None):
        self.modelfieldname = modelfieldname
        # Automatically set to the attribute name by ModelmapperMeta and Modelmapper.automap_field()
        self.doctypefieldname = None

    def _set_doctypefieldname(self, doctypefieldname):
        self.doctypefieldname = doctypefieldname
        if not self.modelfieldname:
            self.modelfieldname = doctypefieldname

    def automake_doctype_fields(self, model_class):
        """
        Create elasticsearch-dsl :class:`elasticsearch_dsl.field.Field` objects from
        this FieldMapping.

        For simple cases you do not have to override this, but instead you
        can just set :obj:`~.FieldMapping.elasticsearchdsl_fieldclass`.

        Used by :class:`ievv_opensource.ievv_elasticsearch2.doctype.ModelDocType`.

        Args:
            model_class: The Django model class.

        Returns:
            dict: A dict where the keys is the doctype field name and the values is
                :class:`elasticsearch_dsl.field.Field` objects.
        """
        return {
            self.doctypefieldname: self.elasticsearchdsl_fieldclass()
        }

    def get_model_value_from_modelobject(self, modelobject):
        """
        Get the value for the Django model field accociated with this mapping
        from the ``modelobject``.

        Args:
            modelobject: A Django model object.
        """
        return getattr(modelobject, self.modelfieldname)

    def to_doctype_value(self, modelobject):
        """
        Convert the value stored in the model to a value compatible with
        ElasticSearch.

        Args:
            modelobject: The model object. When overriding this method,
                you can get the value stored for the model field accociated
                with this mapping using :meth:`.get_model_value_from_modelobject`.

        Returns:
            object: The converted value.
        """
        return self.get_model_value_from_modelobject(modelobject)

    def prettyformat(self, model_class=None):
        """
        Prettyformat this FieldMapping instance.

        Args:
            model_class: If provided, more information is included in the prettyformatted output.

        Returns:
            str: Prettyformatted information about this FieldMapping.
        """
        if model_class:
            modelfield = model_class._meta.get_field(self.modelfieldname)
            modelfield_pretty = '{}({})'.format(modelfield.__class__.__name__, self.modelfieldname)
        else:
            modelfield_pretty = self.modelfieldname
        return '{}({} <-> {})'.format(self.__class__.__name__, modelfield_pretty, self.doctypefieldname)

    def get_required_doctype_fieldnames_list(self):
        """
        Get a list of doctype fieldnames this mapping maps to.

        For simple fields, this returns a list only containing :attr:`~.FieldMapping.doctypefieldname`,
        but for more complex cases where a single Django model field is mapped to multiple
        fields in the doctype, this is overridden to return multiple doctype fieldnames.
        One example of such a more complex case is the :class:`.ForeignKeyPrefixMapping`
        which maps foreignkey fields as multiple prefixed attributes on the doctype.

        Used by :meth:`.validate_mapping`. This means that you usually do not have to
        override :meth:`.validate_mapping`, but instead just have to override this method
        if your custom FieldMapping maps to multiple doctype fields.
        """
        return [self.doctypefieldname]

    def validate_mapping(self, model_class, doctype_class, doctype_fieldnames_set):
        """
        Validate the mapping, to ensure that the mapped doctype fields actually exists.

        Args:
            model_class: The django.db.Model class to validate the mapping against.
            doctype_class: The :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` class.
            doctype_fieldnames_set: Set of doctype fieldnames.

        Raises:
            DoctypeFieldDoesNotExist: If any of the fieldnames returned by
                :meth:`.get_required_doctype_fieldnames_list` is not in ``doctype_fieldnames_set``.
        """
        try:
            model_class._meta.get_field(self.modelfieldname)
        except FieldDoesNotExist:
            raise ModelFieldDoesNotExist(
                '{mappingfield} is mapped from '
                '{model_class_module}.{model_class_name}.{modelfieldname} which does not exist.'.format(
                    mappingfield=self,
                    model_class_module=model_class.__module__,
                    model_class_name=model_class.__name__,
                    modelfieldname=self.modelfieldname
                )
            )
        for doctypefieldname in self.get_required_doctype_fieldnames_list():
            if doctypefieldname not in doctype_fieldnames_set:
                raise DoctypeFieldDoesNotExist(
                    '{mappingfield} is mapped to '
                    '{doctype_class_module}.{doctype_class_name}.{doctypefieldname} which does not exist.'.format(
                        mappingfield=self,
                        doctype_class_module=doctype_class.__module__,
                        doctype_class_name=doctype_class.__name__,
                        doctypefieldname=doctypefieldname
                    )
                )

    def __str__(self):
        return self.prettyformat()


class StringMapping(FieldMapping):
    """
    FieldMapping suitable to string fields (CharField, TextField).
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.String


class IntegerMapping(FieldMapping):
    """
    FieldMapping suitable for integer fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Integer


class SmallIntegerMapping(IntegerMapping):
    """
    FieldMapping suitable for small integer fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Short


class BigIntegerMapping(IntegerMapping):
    """
    FieldMapping suitable for big integer fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Long


class ForeignKeyMapping(BigIntegerMapping):
    """
    FieldMapping suitable for ForeignKey fields where the ForeignKey is
    an automatic ``id`` field.
    """
    def get_model_value_from_modelobject(self, modelobject):
        return getattr(modelobject, '{}_id'.format(self.modelfieldname))


class BooleanMapping(FieldMapping):
    """
    FieldMapping suitable for boolean fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Boolean


class FloatMapping(FieldMapping):
    """
    FieldMapping suitable for float fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Float


class DoubleMapping(FieldMapping):
    """
    FieldMapping suitable for double fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Double


class DateMapping(FieldMapping):
    """
    FieldMapping suitable for date fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Date


class DateTimeMapping(FieldMapping):
    """
    FieldMapping suitable for datetime fields.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Date


class ForeignKeyObjectMapping(FieldMapping):
    """
    FieldMapping suitable for ForeignKey fields that you want to
    map as a nested object in the DocType.

    This is mapped to the ``object`` datatype in ElasticSearch.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Object

    def __init__(self, modelmapper, modelfieldname=None):
        super(ForeignKeyObjectMapping, self).__init__(modelfieldname=modelfieldname)
        self.modelmapper = modelmapper

    def automake_doctype_fields(self, model_class):
        foreignkey_doctype_fields = self.modelmapper.automake_doctype_fields()
        return {
            self.doctypefieldname: self.elasticsearchdsl_fieldclass(
                properties=foreignkey_doctype_fields
            )
        }

    def to_doctype_value(self, modelobject):
        modelvalue = self.get_model_value_from_modelobject(modelobject)
        return self.modelmapper.to_dict(modelvalue, with_meta=False)


class ForeignKeyPrefixMapping(FieldMapping):
    """
    FieldMapping suitable for ForeignKey fields that you want to
    map as prefixed document attributes in the DocType.
    """
    merge_into_document = True

    def __init__(self, modelmapper, prefix=None, modelfieldname=None):
        """
        Args:
            modelmapper: A :class:`.Modelmapper` object for mapping of the foreignkey fields.
            prefix: An optional prefix. Defaults to ``<doctypefieldname>__``.
            modelfieldname: The fieldname in the model.
        """
        super(ForeignKeyPrefixMapping, self).__init__(modelfieldname=modelfieldname)
        self.modelmapper = modelmapper
        self.prefix = prefix

    def __prefix_dict_keys(self, dct):
        output_dict = {}
        prefix = self.get_prefix()
        for key, value in dct.items():
            output_dict['{}{}'.format(prefix, key)] = value
        return output_dict

    def automake_doctype_fields(self, model_class):
        foreignkey_doctype_fields = self.modelmapper.automake_doctype_fields()
        return self.__prefix_dict_keys(foreignkey_doctype_fields)

    def get_prefix(self):
        if self.prefix is None:
            prefix = '{}__'.format(self.doctypefieldname)
        else:
            prefix = self.prefix
        return prefix

    def to_doctype_value(self, modelobject):
        modelvalue = self.get_model_value_from_modelobject(modelobject)
        raw_output = self.modelmapper.to_dict(modelvalue, with_meta=False)
        return self.__prefix_dict_keys(raw_output)

    def get_required_doctype_fieldnames_list(self):
        prefix = self.get_prefix()
        return ['{}{}'.format(prefix, mappingfield.doctypefieldname)
                for mappingfield in self.modelmapper]


class OneToManyNestedMapping(FieldMapping):
    """
    FieldMapping suitable for one-to-many realationships that you want to
    map as a nested array of objects (array of dicts) in the DocType.

    This is mapped to the ``nested`` datatype in ElasticSearch.
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Nested

    def __init__(self, modelmapper, modelfieldname=None):
        super(OneToManyNestedMapping, self).__init__(modelfieldname=modelfieldname)
        self.modelmapper = modelmapper

    def automake_doctype_fields(self, model_class):
        child_doctype_fields = self.modelmapper.automake_doctype_fields()
        return {
            self.doctypefieldname: self.elasticsearchdsl_fieldclass(
                properties=child_doctype_fields
            )
        }

    def to_doctype_value(self, modelobject):
        modelvalue = self.get_model_value_from_modelobject(modelobject)
        queryset = modelvalue.all()
        return [self.modelmapper.to_dict(modelobject, with_meta=False)
                for modelobject in queryset.all()]


class OneToManyIdArrayMapping(FieldMapping):
    """
    FieldMapping suitable for one-to-many realationships that you want to
    map as an array of IDs in the DocType.

    This is mapped to an array in ElasticSearch (which does not require a special datatype).
    """
    elasticsearchdsl_fieldclass = elasticsearch_dsl.Long

    def __init__(self, modelfieldname=None):
        super(OneToManyIdArrayMapping, self).__init__(modelfieldname=modelfieldname)

    def automake_doctype_fields(self, model_class):
        return {
            self.doctypefieldname: self.elasticsearchdsl_fieldclass(
                multi=True
            )
        }

    def to_doctype_value(self, modelobject):
        modelvalue = self.get_model_value_from_modelobject(modelobject)
        queryset = modelvalue.all()
        return [modelobject.pk for modelobject in queryset.all()]


class ModelmapperMeta(type):
    """
    Metaclass for :class:`.DocType`.
    """
    def __new__(cls, name, parents, attrs):
        mappingfields = {}
        for key, value in attrs.items():
            if isinstance(value, FieldMapping):
                mappingfield = value
                mappingfield._set_doctypefieldname(doctypefieldname=key)
                mappingfields[mappingfield.modelfieldname] = mappingfield

        attrs['_explicit_mappingfields'] = mappingfields
        model_to_doctype_class = super(ModelmapperMeta, cls).__new__(cls, name, parents, attrs)
        return model_to_doctype_class


class Modelmapper(with_metaclass(ModelmapperMeta)):
    """
    Makes it easy to convert a Django model to a :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType`.
    """
    def __init__(self, model_class, automap_fields=False, automap_id_field=False, doctype_class=None,
                 exclude=None, include=None):
        """
        Args:
            model_class: A :class:`django.models.db.Model` class.
            automap_fields: Set this to ``True`` to automatically map fields. You can change
                the ElasticSearch field types fields are mapped to by overriding
                :meth:`.modelfield_to_mappingfieldclass`.
            automap_id_field: Automap the automatic ``id`` field? This defaults to ``False`` because
                we set the ``id`` as the meta ``_id`` attribute by default instead. This is useful
                when you map a ForeignKey as an object (with :class:`.ForeignKeyObjectMapping` or
                :class:`.ForeignKeyPrefixMapping`), and you want to include the id-field of the
                foreignkey object. In that case, you set this to ``True`` for the ``modelmapper``
                you initialize the :class:`.ForeignKeyObjectMapping` or :class:`.ForeignKeyPrefixMapping` with.
            doctype_class: Initialize with a doctype class. This is normally not needed outside of
                tests because this is set (through :meth:`.set_doctype_class`) by the
                :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` metaclass when it detects
                the ``modelmapper``-attribute.
        """
        self.model_class = model_class
        self.doctype_class = None
        self.mappingfields = self._explicit_mappingfields.copy()
        self._automap_fields = automap_fields
        self._automap_id_field = automap_id_field

        if exclude and include:
            raise ValueError('You can not use both exclude and include at the same time.')
        self._exclude = exclude
        self._include = include

        if doctype_class:
            self.set_doctype_class(doctype_class=doctype_class)
        if self._automap_fields:
            self.automap_fields()

    def clone(self):
        copy = self.__class__(model_class=self.model_class,
                              automap_fields=self._automap_fields,
                              automap_id_field=self._automap_id_field,
                              doctype_class=self.doctype_class,
                              exclude=self._exclude,
                              include=self._include)
        return copy

    def automake_doctype_fields(self):
        """
        Create elasticsearch-dsl :class:`elasticsearch_dsl.field.Field` objects from
        this Modelmapper.

        Used by :class:`ievv_opensource.ievv_elasticsearch2.doctype.ModelDocType`.

        Returns:
            dict: A dict where the keys is the doctype field name and the values is
                :class:`elasticsearch_dsl.field.Field` objects.
        """
        doctype_fields = {}
        for mappingfield in self.mappingfields.values():
            doctype_fields.update(mappingfield.automake_doctype_fields(model_class=self.model_class))
        return doctype_fields

    def set_doctype_class(self, doctype_class):
        doctype_fieldnames_set = {fieldname for fieldname in doctype_class.get_doc_type_options().mapping}
        for mappingfield in self.mappingfields.values():
            mappingfield.validate_mapping(model_class=self.model_class,
                                          doctype_class=doctype_class,
                                          doctype_fieldnames_set=doctype_fieldnames_set)
        self.doctype_class = doctype_class

    def modelfield_to_mappingfieldclass(self, modelfield):
        """
        Gets a model field, and returns a :class:`.FieldMapping` subclass
        to use for that field. Used by :meth:`.automap_fields`.

        You can override this to add support for your own Django model fields,
        or to change how fields are mapped.

        Args:
            modelfield: A :class:`django.db.models.fields.Field` object.

        Returns:
            FieldMapping: The :class:`.FieldMapping` subclass to use for the provided modelfield.
        """
        if isinstance(modelfield, models.CharField):
            return StringMapping
        elif isinstance(modelfield, models.TextField):
            return StringMapping
        elif isinstance(modelfield, models.ForeignKey):
            return ForeignKeyMapping
        elif isinstance(modelfield, models.BigIntegerField):
            return BigIntegerMapping
        elif isinstance(modelfield, models.SmallIntegerField):
            return SmallIntegerMapping
        elif isinstance(modelfield, models.IntegerField):
            return IntegerMapping
        elif isinstance(modelfield, models.BooleanField):
            return BooleanMapping
        elif isinstance(modelfield, models.FloatField):
            # We map FloatField to DoubleMapping because FloatField is
            # mapped to a DOUBLE in SQL.
            return DoubleMapping
        elif isinstance(modelfield, models.DateTimeField):
            return DateTimeMapping
        elif isinstance(modelfield, models.DateField):
            return DateMapping
        elif self._automap_id_field and isinstance(modelfield, models.AutoField) and modelfield.name == 'id':
            return BigIntegerMapping
        else:
            return None

    def automap_field(self, modelfield):
        """
        Called by :meth:`.automap_field` for each field in the model.

        You normally want to override :meth:`.modelfield_to_mappingfieldclass` instead of this
        method.

        Args:
            modelfield: The :class:`django.db.models.fields.Field` to automap.
        """
        mappingfieldclass = self.modelfield_to_mappingfieldclass(modelfield=modelfield)
        if mappingfieldclass:
            modelfieldname = modelfield.name
            # if issubclass(mappingfieldclass, IntegerMapping) and isinstance(modelfield, models.ForeignKey):
                # modelfieldname = '{}_id'.format(modelfield.name)
            mappingfield = mappingfieldclass()
            mappingfield._set_doctypefieldname(doctypefieldname=modelfieldname)
            self.mappingfields[modelfieldname] = mappingfield

    def _get_automapped_modelfields(self):
        all_modelfields = self.model_class._meta.get_fields()
        if self._exclude:
            return filter(lambda modelfield: modelfield.name not in self._exclude, all_modelfields)
        elif self._include:
            return filter(lambda modelfield: modelfield.name in self._include, all_modelfields)
        else:
            return all_modelfields

    def automap_fields(self):
        """
        Update the mapping with automapped fields. This is called in ``__init__`` if
        ``automap_fields=True``. Ignores manually mapped fields.

        You can override this, but you will most likely rather want to override
        :meth:`.modelfield_to_mappingfieldclass` or :meth:`.automap_field`.
        """
        for modelfield in self._get_automapped_modelfields():
            if modelfield.name not in self.mappingfields:
                self.automap_field(modelfield=modelfield)

    def to_meta_dict(self, modelobject):
        """
        Get a dict of meta attributes for the provided ``modelobject``.

        This is used by :meth:`.to_dict` to create the ``meta``-key.

        Defaults to ``{"id": modelobject.pk}``, and this is usually what you need.

        Args:
            modelobject:

        Returns:
            dict: A dict with the meta attributes for the document.
        """
        return {
            'id': modelobject.pk
        }

    def to_dict(self, modelobject, with_meta=True):
        """
        Convert the provided ``modelobject`` into dict.

        Uses :meth:`.FieldMapping.to_doctype_value` to convert the values.

        Args:
            modelobject: A Django data model object.
            with_meta: If this is ``True`` (the default), we include the return
                value of :meth:`.to_meta_dict` in the ``meta``-key.

        Returns:
            dict: A dict representing data for the document.
        """
        dct = {}
        for mappingfield in self.mappingfields.values():
            doctype_value = mappingfield.to_doctype_value(modelobject)
            if mappingfield.merge_into_document:
                dct.update(doctype_value)
            else:
                dct[mappingfield.doctypefieldname] = doctype_value
        if with_meta:
            dct['meta'] = self.to_meta_dict(modelobject=modelobject)
        return dct

    def to_doctype_object(self, modelobject):
        """
        Convert a Django data model object into a DocType object.

        Uses :meth:`.to_dict` as the keyword arguments when instansiating the doctype object.
        This means that you should normally override :meth:`.to_dict` or :meth:`.to_meta_dict`
        (used by to_dict()) instead of this method.

        Args:
            modelobject: A Django data model object.

        Returns:
            DocType: A DocType object.
        """
        return self.doctype_class(**self.to_dict(modelobject=modelobject))

    def prettyformat(self, separator='\n', prefix='- '):
        """
        Prettyformat the mapping. Useful for debugging.
        """
        output = separator.join('{}{}'.format(prefix, mappingfield.prettyformat(model_class=self.model_class))
                                for mappingfield in self.mappingfields.values())
        if output:
            return output
        else:
            return 'NO MAPPINGS'

    def __str__(self):
        return self.prettyformat(separator=', ', prefix='')

    def get_mappingfield_by_modelfieldname(self, modelfieldname, fallback=None):
        """
        Get mappingfield by model field name.

        Args:
            modelfieldname: Name of a model field.
            fallback: Fallback value if the model field does not exist. Defaults to ``None``.

        Returns:
            FieldMapping: A :class:`.FieldMapping` object.
        """
        return self.mappingfields.get(modelfieldname, fallback)

    def __iter__(self):
        """
        Iterate over mappingfields in this Modelmapper.
        """
        return iter(self.mappingfields.values())
