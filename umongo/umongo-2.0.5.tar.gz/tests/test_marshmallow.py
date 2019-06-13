from datetime import datetime

import pytest

from bson import ObjectId
import marshmallow

from umongo import Document, EmbeddedDocument, fields, set_gettext, validate, missing
from umongo import marshmallow_bonus as ma_bonus_fields
from umongo.abstract import BaseField, BaseSchema
from umongo.marshmallow_bonus import (
    schema_validator_check_unknown_fields, schema_from_umongo_get_attribute, SchemaFromUmongo)

from .common import BaseTest


class TestMarshmallow(BaseTest):

    def teardown_method(self, method):
        # Reset i18n config before each test
        set_gettext(None)

    def setup(self):
        super().setup()

        class User(Document):
            name = fields.StrField()
            birthday = fields.DateTimeField()

            class Meta:
                allow_inheritance = True

        self.User = self.instance.register(User)

    def test_by_field(self):
        ma_name_field = self.User.schema.fields['name'].as_marshmallow_field()
        assert isinstance(ma_name_field, marshmallow.fields.Field)
        assert not isinstance(ma_name_field, BaseField)

    def test_by_schema(self):
        ma_schema_cls = self.User.schema.as_marshmallow_schema()
        assert issubclass(ma_schema_cls, marshmallow.Schema)
        assert not issubclass(ma_schema_cls, BaseSchema)

    def test_custom_base_schema(self):

        class MyBaseSchema(marshmallow.Schema):
            name = marshmallow.fields.Int()
            age = marshmallow.fields.Int()

        ma_schema_cls = self.User.schema.as_marshmallow_schema(base_schema_cls=MyBaseSchema)
        assert issubclass(ma_schema_cls, MyBaseSchema)

        schema = ma_schema_cls()
        ret = schema.dump({'name': "42", 'age': 42, 'dummy': False})
        assert not ret.errors
        assert ret.data == {'name': "42", 'age': 42}
        ret = schema.load({'name': "42", 'age': 42, 'dummy': False})
        assert ret.errors == {'_schema': ['Unknown field name dummy.']}
        ret = schema.load({'name': "42", 'age': 42})
        assert not ret.errors
        assert ret.data == {'name': "42", 'age': 42}

    def test_customize_params(self):
        ma_field = self.User.schema.fields['name'].as_marshmallow_field(params={'load_only': True})
        assert ma_field.load_only is True

        ma_schema_cls = self.User.schema.as_marshmallow_schema(params={'name': {'load_only': True, 'dump_only': True}})
        schema = ma_schema_cls()
        ret = schema.dump({'name': "42", 'birthday': datetime(1990, 10, 23), 'dummy': False})
        assert not ret.errors
        assert ret.data == {'birthday': '1990-10-23T00:00:00+00:00'}
        ret = schema.load({'name': "42", 'birthday': '1990-10-23T00:00:00+00:00', 'dummy': False})
        assert (ret.errors == {'_schema': ['Unknown field name name.', 'Unknown field name dummy.']} or
                ret.errors == {'_schema': ['Unknown field name dummy.', 'Unknown field name name.']})
        ret = schema.load({'birthday': '1990-10-23T00:00:00'})
        assert not ret.errors
        assert ret.data == {'birthday': datetime(1990, 10, 23)}

    def test_customize_nested_and_container_params(self):
        @self.instance.register
        class Accessory(EmbeddedDocument):
            brief = fields.StrField(attribute='id', required=True)
            value = fields.IntField()

        @self.instance.register
        class Bag(Document):
            id = fields.EmbeddedField(Accessory, attribute='_id', required=True)
            names = fields.ListField(fields.StringField())
            content = fields.ListField(fields.EmbeddedField(Accessory))

        ma_field = Bag.schema.fields['id'].as_marshmallow_field(params={
            'load_only': True,
            'params': {'value': {'dump_only': True}}})
        assert ma_field.load_only is True
        assert ma_field.nested._declared_fields['value'].dump_only
        ma_field = Bag.schema.fields['names'].as_marshmallow_field(params={
            'load_only': True,
            'params': {'dump_only': True}})
        assert ma_field.load_only is True
        assert ma_field.container.dump_only is True
        ma_field = Bag.schema.fields['content'].as_marshmallow_field(params={
            'load_only': True,
            'params': {'required': True, 'params': {'value': {'dump_only': True}}}})
        assert ma_field.load_only is True
        assert ma_field.container.required is True
        assert ma_field.container.nested._declared_fields['value'].dump_only

    def test_pass_meta_attributes(self):
        @self.instance.register
        class Accessory(EmbeddedDocument):
            brief = fields.StrField(attribute='id', required=True)
            value = fields.IntField()

        @self.instance.register
        class Bag(Document):
            id = fields.EmbeddedField(Accessory, attribute='_id', required=True)
            content = fields.ListField(fields.EmbeddedField(Accessory))

        ma_schema = Bag.schema.as_marshmallow_schema(meta={'exclude': ('id',)})
        assert ma_schema.Meta.exclude == ('id',)
        ma_schema = Bag.schema.as_marshmallow_schema(params={
            'id': {'meta': {'exclude': ('value',)}}})
        assert ma_schema._declared_fields['id'].nested.Meta.exclude == ('value',)
        ma_schema = Bag.schema.as_marshmallow_schema(params={
            'content': {'params': {'meta': {'exclude': ('value',)}}}})
        assert ma_schema._declared_fields['content'].container.nested.Meta.exclude == ('value',)

        class DumpOnlyIdSchema(marshmallow.Schema):
            class Meta:
                dump_only = ('id',)

        ma_custom_base_schema = Bag.schema.as_marshmallow_schema(
            base_schema_cls=DumpOnlyIdSchema, meta={'exclude': ('content',)})
        assert ma_custom_base_schema.Meta.exclude == ('content',)
        assert ma_custom_base_schema.Meta.dump_only == ('id',)

    def test_as_marshmallow_field_pass_params(self):
        @self.instance.register
        class MyDoc(Document):
            lf = fields.IntField(marshmallow_load_from='lflf')
            dt = fields.IntField(marshmallow_dump_to='dtdt')
            at = fields.IntField(marshmallow_attribute='atat')
            re = fields.IntField(marshmallow_required=True)
            an = fields.IntField(marshmallow_allow_none=True)
            lo = fields.IntField(marshmallow_load_only=True)
            do = fields.IntField(marshmallow_dump_only=True)
            va = fields.IntField(marshmallow_validate=validate.Range(min=0))
            em = fields.IntField(marshmallow_error_messages={'invalid': 'Wrong'})

        MyMaDoc = MyDoc.schema.as_marshmallow_schema()

        assert MyMaDoc().fields['lf'].load_from == 'lflf'
        assert MyMaDoc().fields['dt'].dump_to == 'dtdt'
        assert MyMaDoc().fields['at'].attribute == 'atat'
        assert MyMaDoc().fields['re'].required is True
        assert MyMaDoc().fields['an'].allow_none is True
        assert MyMaDoc().fields['lo'].load_only is True
        assert MyMaDoc().fields['do'].dump_only is True
        _, err = MyMaDoc().load({'va': -1})
        assert 'va' in err
        assert MyMaDoc().fields['em'].error_messages['invalid'] == 'Wrong'

    def test_as_marshmallow_field_infer_missing_default(self):
        @self.instance.register
        class MyDoc(Document):
            de = fields.IntField(default=42)
            mm = fields.IntField(marshmallow_missing=12)
            md = fields.IntField(marshmallow_default=12)
            mmd = fields.IntField(default=42, marshmallow_missing=12)
            mdd = fields.IntField(default=42, marshmallow_default=12)

        MyMaDoc = MyDoc.schema.as_marshmallow_schema()

        data, _ = MyMaDoc().load({})
        assert data == {
            'de': 42,
            'mm': 12,
            'mmd': 12,
            'mdd': 42,
        }

        data, _ = MyMaDoc().dump({})
        assert data == {
            'de': 42,
            'md': 12,
            'mmd': 42,
            'mdd': 12,
        }

    def test_as_marshmallow_schema_cache(self):
        ma_schema_cls = self.User.schema.as_marshmallow_schema()

        new_ma_schema_cls = self.User.schema.as_marshmallow_schema(
            params={'name': {'load_only': True}})
        assert new_ma_schema_cls != ma_schema_cls

        new_ma_schema_cls = self.User.schema.as_marshmallow_schema(
            meta={'exclude': ('name',)})
        assert new_ma_schema_cls != ma_schema_cls

        new_ma_schema_cls = self.User.schema.as_marshmallow_schema(
            check_unknown_fields=False)
        assert new_ma_schema_cls != ma_schema_cls

        new_ma_schema_cls = self.User.schema.as_marshmallow_schema(
            mongo_world=True)
        assert new_ma_schema_cls != ma_schema_cls

        class MyBaseSchema(marshmallow.Schema):
            pass

        new_ma_schema_cls = self.User.schema.as_marshmallow_schema(
            base_schema_cls=MyBaseSchema)
        assert new_ma_schema_cls != ma_schema_cls

        new_ma_schema_cls = self.User.schema.as_marshmallow_schema()
        assert new_ma_schema_cls == ma_schema_cls

    def test_keep_attributes(self):
        @self.instance.register
        class Vehicle(Document):
            brand = fields.StrField(description='Manufacturer name')
            category = fields.StrField(required=True)
            nb_wheels = fields.IntField(default=4)

        ma_schema_cls = Vehicle.schema.as_marshmallow_schema()
        schema = ma_schema_cls()

        ret = schema.load({})
        assert ret.errors == {'category': ['Missing data for required field.']}
        ret = schema.load({'category': 'Car'})
        assert ret.data == {'category': 'Car', 'nb_wheels': 4}

        assert schema.fields['brand'].metadata['description'] == 'Manufacturer name'

    def test_keep_validators(self):
        @self.instance.register
        class WithMailUser(self.User):
            email = fields.StrField(validate=[validate.Email(), validate.Length(max=100)])
            number_of_legs = fields.IntField(validate=[validate.OneOf([0, 1, 2])])

        ma_schema_cls = WithMailUser.schema.as_marshmallow_schema()
        schema = ma_schema_cls()

        ret = schema.load({'email': 'a' * 100 + '@user.com', 'number_of_legs': 4})
        assert ret.errors == {'email': ['Longer than maximum length 100.'],
                              'number_of_legs': ['Not a valid choice.']}

        ret = schema.load({'email': 'user@user.com', 'number_of_legs': 2})
        assert not ret.errors
        assert ret.data == {'email': 'user@user.com', 'number_of_legs': 2}

    def test_inheritance(self):
        @self.instance.register
        class AdvancedUser(self.User):
            name = fields.StrField(default='1337')
            is_left_handed = fields.BooleanField()

        ma_schema_cls = AdvancedUser.schema.as_marshmallow_schema()
        schema = ma_schema_cls()

        ret = schema.dump({'is_left_handed': True})
        assert not ret.errors
        assert ret.data == {'name': '1337', 'is_left_handed': True, 'cls': 'AdvancedUser'}

    def test_to_mongo(self):
        @self.instance.register
        class Dog(Document):
            name = fields.StrField(attribute='_id', required=True)
            age = fields.IntField()

        payload = {'name': 'Scruffy', 'age': 2}
        ma_schema_cls = Dog.schema.as_marshmallow_schema()
        ma_mongo_schema_cls = Dog.schema.as_marshmallow_schema(mongo_world=True)

        ret = ma_schema_cls().load(payload)
        assert not ret.errors
        assert ret.data == {'name': 'Scruffy', 'age': 2}
        assert ma_schema_cls().dump(ret.data).data == payload

        ret = ma_mongo_schema_cls().load(payload)
        assert not ret.errors
        assert ret.data == {'_id': 'Scruffy', 'age': 2}
        assert ma_mongo_schema_cls().dump(ret.data).data == payload

    def test_i18n(self):
        # i18n support should be kept, because it's pretty cool to have this !
        def my_gettext(message):
            return 'OMG !!! ' + message

        set_gettext(my_gettext)

        ma_schema_cls = self.User.schema.as_marshmallow_schema()
        ret = ma_schema_cls().load({'name': 'John', 'birthday': 'not_a_date', 'dummy_field': 'dummy'})
        assert ret.errors == {'birthday': ['OMG !!! Not a valid datetime.'],
                              '_schema': ['OMG !!! Unknown field name dummy_field.']}

    def test_unknow_fields_check(self):
        ma_schema_cls = self.User.schema.as_marshmallow_schema()
        ret = ma_schema_cls().load({'name': 'John', 'dummy_field': 'dummy'})
        assert ret.errors == {'_schema': ['Unknown field name dummy_field.']}

        ma_schema_cls = self.User.schema.as_marshmallow_schema(check_unknown_fields=False)
        ret = ma_schema_cls().load({'name': 'John', 'dummy_field': 'dummy'})
        assert not ret.errors
        assert ret.data == {'name': 'John'}

    def test_missing_accessor(self):

        @self.instance.register
        class WithDefault(Document):
            with_umongo_default = fields.StrictDateTimeField(default=datetime(1999, 1, 1))
            with_marshmallow_missing = fields.StrictDateTimeField(marshmallow_missing='2000-01-01T00:00:00+00:00')
            with_marshmallow_default = fields.StrictDateTimeField(marshmallow_default='2001-01-01T00:00:00+00:00')
            with_marshmallow_and_umongo = fields.StrictDateTimeField(
                default=datetime(1999, 1, 1), marshmallow_missing='2000-01-01T00:00:00+00:00',
                marshmallow_default='2001-01-01T00:00:00+00:00')
            with_force_missing = fields.StrictDateTimeField(
                default=datetime(2001, 1, 1), marshmallow_missing=missing, marshmallow_default=missing)
            with_nothing = fields.StrField()

        ma_schema = WithDefault.schema.as_marshmallow_schema()()
        ret = ma_schema.dump({})
        assert not ret.errors
        assert ret.data == {
            'with_umongo_default': '1999-01-01T00:00:00+00:00',
            'with_marshmallow_default': '2001-01-01T00:00:00+00:00',
            'with_marshmallow_and_umongo': '2001-01-01T00:00:00+00:00',
        }
        ret = ma_schema.load({})
        assert not ret.errors
        assert ret.data == {
            'with_umongo_default': datetime(1999, 1, 1),
            'with_marshmallow_missing': datetime(2000, 1, 1),
            'with_marshmallow_and_umongo': datetime(2000, 1, 1),
        }

    def test_nested_field(self):
        @self.instance.register
        class Accessory(EmbeddedDocument):
            brief = fields.StrField(attribute='id', required=True)
            value = fields.IntField()

        @self.instance.register
        class Bag(Document):
            id = fields.EmbeddedField(Accessory, attribute='_id', required=True)
            content = fields.ListField(fields.EmbeddedField(Accessory))

        data = {
            'id': {'brief': 'sportbag', 'value': 100},
            'content': [{'brief': 'cellphone', 'value': 500}, {'brief': 'lighter', 'value': 2}]
        }
        # Here data is the same in both OO world and user world (no
        # ObjectId to str conversion needed for example)

        ma_schema = Bag.schema.as_marshmallow_schema()()
        ma_mongo_schema = Bag.schema.as_marshmallow_schema(mongo_world=True)()

        bag = Bag(**data)
        ret = ma_schema.dump(bag)
        assert not ret.errors
        assert ret.data == data
        ret = ma_schema.load(data)
        assert not ret.errors
        assert ret.data == data

        ret = ma_mongo_schema.dump(bag.to_mongo())
        assert not ret.errors
        assert ret.data == data
        ret = ma_mongo_schema.load(data)
        assert not ret.errors
        assert ret.data == bag.to_mongo()

        # Check as_marshmallow_schema params (check_unknown_felds, base_schema_cls)
        # are passed to nested schemas
        data = {
            'id': {'brief': 'sportbag', 'value': 100, 'name': 'Unknown'},
            'content': [
                {'brief': 'cellphone', 'value': 500, 'name': 'Unknown'},
                {'brief': 'lighter', 'value': 2, 'name': 'Unknown'}]
        }
        ret = ma_schema.load(data)
        assert ret.errors == {
            'id': {'_schema': ['Unknown field name name.']},
            'content': {
                0: {'_schema': ['Unknown field name name.']},
                1: {'_schema': ['Unknown field name name.']},
            }}

        ma_no_check_unknown_schema = Bag.schema.as_marshmallow_schema(check_unknown_fields=False)()
        ret = ma_no_check_unknown_schema.load(data)
        assert not ret.errors

        class WithNameSchema(marshmallow.Schema):
            name = marshmallow.fields.Str()

        ma_custom_base_schema = Bag.schema.as_marshmallow_schema(base_schema_cls=WithNameSchema)()
        ret = ma_custom_base_schema.load(data)
        assert not ret.errors

    def test_marshmallow_bonus_fields(self):
        # Fields related to mongodb provided for marshmallow
        @self.instance.register
        class Doc(Document):
            id = fields.ObjectIdField(attribute='_id')
            ref = fields.ReferenceField('Doc')
            gen_ref = fields.GenericReferenceField()

        for name, field_cls in (
                ('id', ma_bonus_fields.ObjectId),
                ('ref', ma_bonus_fields.ObjectId),
                ('gen_ref', ma_bonus_fields.GenericReference)
        ):
            ma_field = Doc.schema.fields[name].as_marshmallow_field()
            assert isinstance(ma_field, field_cls)
            assert not isinstance(ma_field, BaseField)

        oo_data = {
            'id': ObjectId("57c1a71113adf27ab96b2c4f"),
            'ref': ObjectId("57c1a71113adf27ab96b2c4f"),
            "gen_ref": {'cls': 'Doc', 'id': ObjectId("57c1a71113adf27ab96b2c4f")}
        }
        serialized = {
            'id': "57c1a71113adf27ab96b2c4f",
            'ref': "57c1a71113adf27ab96b2c4f",
            "gen_ref": {'cls': 'Doc', 'id': "57c1a71113adf27ab96b2c4f"}
        }
        doc = Doc(**oo_data)
        mongo_data = doc.to_mongo()

        # schema to OO world
        ma_schema_cls = Doc.schema.as_marshmallow_schema()
        ma_schema = ma_schema_cls()
        # Dump uMongo object
        ret = ma_schema.dump(doc)
        assert not ret.errors
        assert ret.data == serialized
        # Dump OO data (not uMongo object) to ensure bonus fields round-trip
        ret = ma_schema.dump(oo_data)
        assert not ret.errors
        assert ret.data == serialized
        # Load serialized data
        ret = ma_schema.load(serialized)
        assert not ret.errors
        assert ret.data == oo_data

        # schema to mongo world
        ma_mongo_schema_cls = Doc.schema.as_marshmallow_schema(mongo_world=True)
        ma_mongo_schema = ma_mongo_schema_cls()
        ret = ma_mongo_schema.dump(mongo_data)
        assert not ret.errors
        assert ret.data == serialized
        ret = ma_mongo_schema.load(serialized)
        assert ret.errors == {}
        assert ret.data == mongo_data
        # Cannot load mongo form
        ret = ma_mongo_schema.load({"gen_ref": {'_cls': 'Doc', '_id': "57c1a71113adf27ab96b2c4f"}})
        assert ret.errors == {'gen_ref': ['Generic reference must have `id` and `cls` fields.']}

    def test_marshmallow_schema_helpers(self):

        class CheckUnknownSchema(marshmallow.Schema):
            __check_unknown_fields = marshmallow.validates_schema(
                pass_original=True)(schema_validator_check_unknown_fields)
            a = marshmallow.fields.Int()

        _, errors = CheckUnknownSchema().load({'a': 1, 'dummy': 2})
        assert errors == {'_schema': ['Unknown field name dummy.']}

        data, errors = CheckUnknownSchema().load({'a': 1})
        assert not errors
        assert data == {'a': 1}

        @self.instance.register
        class Doc(Document):
            a = fields.IntField()

            @property
            def prop(self):
                return "I'm a property !"

        class VanillaSchema(marshmallow.Schema):
            a = marshmallow.fields.Int()

        class CustomGetAttributeSchema(VanillaSchema):
            get_attribute = schema_from_umongo_get_attribute

        data, errors = VanillaSchema().dump(Doc())
        assert not errors
        assert data == {'a': None}

        data, errors = CustomGetAttributeSchema().dump(Doc())
        assert not errors
        assert data == {}

        data, errors = CustomGetAttributeSchema().dump(Doc(a=1))
        assert not errors
        assert data == {'a': 1}

        class MySchemaFromUmongo(SchemaFromUmongo):
            a = marshmallow.fields.Int()
            prop = marshmallow.fields.String(dump_only=True)

        data, errors = MySchemaFromUmongo().dump(Doc())
        assert not errors
        assert data == {'prop': "I'm a property !"}

        _, errors = MySchemaFromUmongo().load({'a': 1, 'dummy': 2})
        assert errors == {'_schema': ['Unknown field name dummy.']}

        _, errors = MySchemaFromUmongo().load({'a': 1, 'prop': '2'})
        assert errors == {'_schema': ['Unknown field name prop.']}

    def test_marshmallow_access_custom_attributes(self):

        @self.instance.register
        class Doc(EmbeddedDocument):
            a = fields.IntField()

            attribute_foo = 'foo'

            @property
            def str_prop(self):
                return "I'm a property !"

            @property
            def none_prop(self):
                return None

            @property
            def missing_prop(self):
                return marshmallow.missing

            def func_get_42(self):
                return 42

        class Schema(Doc.schema.as_marshmallow_schema()):
            str_prop = marshmallow.fields.Str(dump_only=True)
            none_prop = marshmallow.fields.Str(allow_none=True, dump_only=True)
            missing_prop = marshmallow.fields.Str(dump_only=True)
            attribute_foo = marshmallow.fields.Str(dump_only=True)
            get_42 = marshmallow.fields.Int(dump_only=True, attribute="func_get_42")

        ret = Schema().dump(Doc(a=1))
        assert not ret.errors
        assert ret.data == {
            'a': 1,
            'str_prop': "I'm a property !",
            'none_prop': None,
            'attribute_foo': 'foo',
            'get_42': 42
        }

    def test_dump_only(self):

        @self.instance.register
        class Doc(Document):
            dl = fields.IntField()
            do = fields.IntField(dump_only=True)
            lo = fields.IntField(load_only=True)
            nope = fields.IntField(dump_only=True, load_only=True)

        with pytest.raises(marshmallow.ValidationError):
            Doc(do=1)

        with pytest.raises(marshmallow.ValidationError):
            Doc(nope=1)

        assert Doc(dl=1, lo=2).dump() == {'dl': 1}

        assert Doc(nope=marshmallow.missing, do=marshmallow.missing).dump() == {}
