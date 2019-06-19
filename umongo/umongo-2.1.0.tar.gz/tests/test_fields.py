from decimal import Decimal
import datetime as dt
from uuid import UUID

import pytest

from dateutil.tz.tz import tzutc, tzoffset
from bson import ObjectId, DBRef, Decimal128
from marshmallow import ValidationError, missing

from umongo.data_proxy import data_proxy_factory
from umongo import Document, EmbeddedDocument, Schema, EmbeddedSchema, fields, Reference
from umongo.data_objects import List, Dict

from .common import BaseTest


class TestRequired(BaseTest):
    # `commit` calls `required_validate`

    def test_required(self):

        @self.instance.register
        class Person(Document):
            name = fields.StrField(required=True)
            birthday = fields.DateTimeField()

        person = Person(birthday=dt.datetime(1968, 6, 9))

        # required should be called during commit
        with pytest.raises(ValidationError) as exc:
            person.required_validate()
        assert exc.value.messages == {'name': ['Missing data for required field.']}

        person.name = 'Marty'
        person.required_validate()

    def test_required_nested(self):
        @self.instance.register
        class MyEmbedded(EmbeddedDocument):
            required_field = fields.IntField(required=True)
            optional_field = fields.IntField()

        @self.instance.register
        class MyDoc(Document):
            embedded = fields.EmbeddedField(MyEmbedded)
            embedded_required = fields.EmbeddedField(MyEmbedded, required=True)
            embedded_list = fields.ListField(fields.EmbeddedField(MyEmbedded))

        MyDoc(embedded={}, embedded_list=[{}])  # Required fields are check on commit
        # Don't check required fields in not required missing embedded
        MyDoc(embedded_required={'required_field': 42}).required_validate()
        # Now trigger required fails
        with pytest.raises(ValidationError) as exc:
            MyDoc().required_validate()
        assert exc.value.messages == {'embedded_required': ['Missing data for required field.']}
        with pytest.raises(ValidationError) as exc:
            MyDoc(embedded_required={'optional_field': 1}).required_validate()
        assert exc.value.messages == {'embedded_required': {'required_field': ['Missing data for required field.']}}
        with pytest.raises(ValidationError) as exc:
            MyDoc(embedded={'optional_field': 1},
                  embedded_required={'required_field': 42}).required_validate()
        assert exc.value.messages == {'embedded': {'required_field': ['Missing data for required field.']}}
        with pytest.raises(ValidationError) as exc:
            MyDoc(embedded={'required_field': 1}, embedded_list=[{'optional_field': 1}], embedded_required={'required_field': 42}).required_validate()
        assert exc.value.messages == {'embedded_list': {0: {'required_field': ['Missing data for required field.']}}}

        # Check valid constructions
        doc = MyDoc(embedded={'required_field': 1}, embedded_list=[], embedded_required={'required_field': 42})
        doc.required_validate()
        doc = MyDoc(embedded={'required_field': 1}, embedded_list=[{'required_field': 1}], embedded_required={'required_field': 42})
        doc.required_validate()


class TestFields(BaseTest):

    def test_basefields(self):

        class MySchema(EmbeddedSchema):
            string = fields.StringField()
            uuid = fields.UUIDField()
            number = fields.NumberField()
            integer = fields.IntegerField()
            decimal = fields.DecimalField()
            boolean = fields.BooleanField()
            formattedstring = fields.FormattedStringField('Hello {to_format}')
            float = fields.FloatField()
            # localdatetime = fields.LocalDateTimeField()
            url = fields.UrlField()
            email = fields.EmailField()
            constant = fields.ConstantField("const")

        s = MySchema(strict=True)
        data, err = s.load({
            'string': 'value',
            'uuid': '8c58b5fc-b902-40c8-9d55-e9beb0906f80',
            'number': 1.0,
            'integer': 2,
            'decimal': 3.0,
            'boolean': True,
            'float': 4.0,
            'url': "http://www.example.com/subject",
            'email': "jdoe@example.com",
            'constant': 'forget me'
        })
        assert not err
        assert data == {
            'string': 'value',
            'uuid': UUID('8c58b5fc-b902-40c8-9d55-e9beb0906f80'),
            'number': 1.0,
            'integer': 2,
            'decimal': 3.0,
            'boolean': True,
            'float': 4.0,
            'url': "http://www.example.com/subject",
            'email': "jdoe@example.com",
            'constant': 'const'
        }
        dumped, err = s.dump({
            'string': 'value',
            'uuid': UUID('8c58b5fc-b902-40c8-9d55-e9beb0906f80'),
            'number': 1.0,
            'integer': 2,
            'decimal': 3.0,
            'boolean': True,
            'formattedstring': 'forget me',
            'to_format': 'World',
            'float': 4.0,
            'url': "http://www.example.com/subject",
            'email': "jdoe@example.com",
            'constant': 'forget me'
        })
        assert not err
        assert dumped == {
            'string': 'value',
            'uuid': '8c58b5fc-b902-40c8-9d55-e9beb0906f80',
            'number': 1.0,
            'integer': 2,
            'decimal': 3.0,
            'boolean': True,
            'formattedstring': 'Hello World',
            'float': 4.0,
            'url': "http://www.example.com/subject",
            'email': "jdoe@example.com",
            'constant': 'const'
        }
        with pytest.raises(ValidationError):
            s.load({'to_format': 'not allowed'})

    def test_datetime(self):

        class MySchema(EmbeddedSchema):
            a = fields.DateTimeField()
            b = fields.LocalDateTimeField()

        s = MySchema(strict=True)
        data, _ = s.load({'a': dt.datetime(2016, 8, 6)})
        assert data['a'] == dt.datetime(2016, 8, 6)
        data, _ = s.load({'a': "2016-08-06T00:00:00Z"})
        assert data['a'] == dt.datetime(2016, 8, 6, tzinfo=tzutc())
        data, _ = s.load({'a': "2016-08-06T00:00:00"})
        assert data['a'] == dt.datetime(2016, 8, 6)
        with pytest.raises(ValidationError):
            s.load({'a': "dummy"})

        # Test DateTimeField and LocalDateTimeField round to milliseconds
        s = MySchema()
        data, _ = s.load({
            'a': dt.datetime(2016, 8, 6, 12, 30, 30, 123456),
            'b': dt.datetime(2016, 8, 6, 12, 30, 30, 123456),
        })
        assert data['a'].microsecond == 123000
        assert data['b'].microsecond == 123000
        s = MySchema()
        data, _ = s.load({
            'a': dt.datetime(2016, 8, 6, 12, 59, 59, 999876),
            'b': dt.datetime(2016, 8, 6, 12, 59, 59, 999876),
        })
        assert data['a'].hour == 13
        assert data['b'].hour == 13
        assert data['a'].minute == 0
        assert data['b'].minute == 0
        assert data['a'].second == 0
        assert data['b'].second == 0
        assert data['a'].microsecond == 0
        assert data['b'].microsecond == 0

    def test_strictdatetime(self):

        class MySchema(EmbeddedSchema):
            a = fields.StrictDateTimeField()
            b = fields.StrictDateTimeField(load_as_tz_aware=False)
            c = fields.StrictDateTimeField(load_as_tz_aware=True)

        # Test _deserialize
        s = MySchema(strict=True)

        for date in (
            dt.datetime(2016, 8, 6),
            dt.datetime(2016, 8, 6, tzinfo=tzutc()),
            "2016-08-06T00:00:00Z",
            "2016-08-06T00:00:00",
        ):
            data, _ = s.load({'a': date, 'b': date, 'c': date})
            assert data['a'] == dt.datetime(2016, 8, 6)
            assert data['b'] == dt.datetime(2016, 8, 6)
            assert data['c'] == dt.datetime(2016, 8, 6, tzinfo=tzutc())

        for date in (
            "2016-08-06T00:00:00+02:00",
            dt.datetime(2016, 8, 6, tzinfo=tzoffset(None, 7200)),
        ):
            data, _ = s.load({'a': date, 'b': date, 'c': date})
            assert data['a'] == dt.datetime(2016, 8, 5, 22, 0)
            assert data['b'] == dt.datetime(2016, 8, 5, 22, 0)
            assert data['c'] == dt.datetime(2016, 8, 6, tzinfo=tzoffset(None, 7200))

        with pytest.raises(ValidationError):
            s.load({'a': "dummy"})

        # Test _deserialize_from_mongo
        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()

        for date in (
            dt.datetime(2016, 8, 6),
            dt.datetime(2016, 8, 6, tzinfo=tzutc()),
        ):
            d.from_mongo({'a': date, 'b': date, 'c': date})
            assert d.get('a') == dt.datetime(2016, 8, 6)
            assert d.get('b') == dt.datetime(2016, 8, 6)
            assert d.get('c') == dt.datetime(2016, 8, 6, tzinfo=tzutc())

        for date in (
            dt.datetime(2016, 8, 6, tzinfo=tzoffset(None, 7200)),
        ):
            d.from_mongo({'a': date, 'b': date, 'c': date})
            assert d.get('a') == dt.datetime(2016, 8, 5, 22, 0)
            assert d.get('b') == dt.datetime(2016, 8, 5, 22, 0)
            assert d.get('c') == dt.datetime(2016, 8, 6, tzinfo=tzoffset(None, 7200))

        # Test StrictDateTimeField rounds to milliseconds
        s = MySchema()
        data, _ = s.load({'a': dt.datetime(2016, 8, 6, 12, 30, 30, 123456)})
        assert data['a'].microsecond == 123000
        data, _ = s.load({'a': dt.datetime(2016, 8, 6, 12, 59, 59, 999876)})
        assert data['a'].hour == 13
        assert data['a'].minute == 0
        assert data['a'].second == 0
        assert data['a'].microsecond == 0

    def test_date(self):

        class MySchema(EmbeddedSchema):
            a = fields.DateField()

        s = MySchema(strict=True)
        data, _ = s.load({'a': dt.date(2016, 8, 6)})
        assert data['a'] == dt.date(2016, 8, 6)
        data, _ = s.load({'a': "2016-08-06"})
        assert data['a'] == dt.date(2016, 8, 6)
        with pytest.raises(ValidationError):
            s.load({'a': "dummy"})

        # Test _serialize_to_mongo / _deserialize_from_mongo
        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()

        d.from_mongo({'a': dt.datetime(2019, 8, 6)})
        assert d.get('a') == dt.date(2019, 8, 6)
        assert d.to_mongo() == {'a': dt.datetime(2019, 8, 6)}

    def test_dict(self):

        class MySchema(Schema):
            dict = fields.DictField(attribute='in_mongo_dict', allow_none=True)

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.from_mongo({'in_mongo_dict': {'a': 1, 'b': {'c': True}}})
        with pytest.raises(KeyError):
            d.get('in_mongo_dict')
        assert d.dump() == {'dict': {'a': 1, 'b': {'c': True}}}
        assert d.get('dict') == {'a': 1, 'b': {'c': True}}
        assert d.to_mongo() == {'in_mongo_dict': {'a': 1, 'b': {'c': True}}}

        # Must manually set_dirty to take the changes into account
        dict_ = d.get('dict')
        dict_['a'] = 1
        assert d.to_mongo(update=True) is None
        dict_.set_modified()
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_dict': {'a': 1, 'b': {'c': True}}}}
        dict_.clear_modified()
        assert d.to_mongo(update=True) is None

        d2 = MyDataProxy({'dict': {'a': 1, 'b': {'c': True}}})
        assert d2.to_mongo() == {'in_mongo_dict': {'a': 1, 'b': {'c': True}}}

        d2.set('dict', {})
        assert d2.to_mongo() == {'in_mongo_dict': {}}
        assert d2.to_mongo(update=True) == {'$set': {'in_mongo_dict': {}}}
        d2.delete('dict')
        assert d2.to_mongo() == {}
        assert d2.to_mongo(update=True) == {'$unset': {'in_mongo_dict': ''}}

        d3 = MyDataProxy()
        d3.from_mongo({})
        assert d3.get('dict') is missing
        assert d3.to_mongo() == {}
        assert d3.to_mongo(update=True) is None

        d3.from_mongo({'in_mongo_dict': {}})
        assert d3._data.get('in_mongo_dict') == {}
        d3.get('dict')['field'] = 'value'
        assert d3.to_mongo(update=True) is None
        d3.get('dict').set_modified()
        assert d3.to_mongo(update=True) == {'$set': {'in_mongo_dict': {'field': 'value'}}}
        assert d3.to_mongo() == {'in_mongo_dict': {'field': 'value'}}

        d4 = MyDataProxy({'dict': None})
        assert d4.to_mongo() == {'in_mongo_dict': None}
        d4.from_mongo({'in_mongo_dict': None})
        assert d4.get('dict') is None

    def test_dict_default(self):

        class MySchema(Schema):
            # Passing a mutable as default is a bad idea in real life
            d_dict = fields.DictField(default={'1': 1, '2': 2})
            c_dict = fields.DictField(default=lambda: {'1': 1, '2': 2})

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        assert d.to_mongo() == {
            'd_dict': {'1': 1, '2': 2},
            'c_dict': {'1': 1, '2': 2},
        }
        assert isinstance(d.get('d_dict'), Dict)
        assert isinstance(d.get('c_dict'), Dict)
        d.get('d_dict')['3'] = 3
        d.get('c_dict')['3'] = 3

        d.delete('d_dict')
        d.delete('c_dict')
        assert d.to_mongo() == {
            'd_dict': {'1': 1, '2': 2},
            'c_dict': {'1': 1, '2': 2},
        }
        assert isinstance(d.get('d_dict'), Dict)
        assert isinstance(d.get('c_dict'), Dict)

    def test_list(self):

        class MySchema(Schema):
            list = fields.ListField(fields.IntField(), attribute='in_mongo_list', allow_none=True)

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        assert d.to_mongo() == {}

        d.load({'list': [1, 2, 3]})
        assert d.dump() == {'list': [1, 2, 3]}
        assert d.to_mongo() == {'in_mongo_list': [1, 2, 3]}
        assert d.get('list') == [1, 2, 3]
        d.get('list').append(4)
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [1, 2, 3, 4]}}

        d.clear_modified()
        d.set('list', [5, 6, 7])
        assert d.dump() == {'list': [5, 6, 7]}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [5, 6, 7]}}

        d.clear_modified()
        d.get('list').pop()
        assert d.dump() == {'list': [5, 6]}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [5, 6]}}

        d.clear_modified()
        d.get('list').clear()
        assert d.dump() == {'list': []}
        assert d.to_mongo() == {'in_mongo_list': []}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': []}}
        d.delete('list')
        assert d.to_mongo() == {}
        assert d.to_mongo(update=True) == {'$unset': {'in_mongo_list': ''}}

        d.set('list', [1, 2, 3])
        d.clear_modified()
        d.get('list').remove(1)
        assert d.dump() == {'list': [2, 3]}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [2, 3]}}

        d.clear_modified()
        d.get('list').reverse()
        assert d.dump() == {'list': [3, 2]}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [3, 2]}}

        d.clear_modified()
        d.get('list').sort()
        assert d.dump() == {'list': [2, 3]}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [2, 3]}}

        d.clear_modified()
        d.get('list').extend([4, 5])
        assert d.dump() == {'list': [2, 3, 4, 5]}
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_list': [2, 3, 4, 5]}}

        d.from_mongo({'in_mongo_list': [2, 3, 4, 5]})
        assert repr(
            d._data.get('in_mongo_list')
        ) == '<object umongo.data_objects.List([2, 3, 4, 5])>'

        d2 = MyDataProxy()
        d2.from_mongo({})
        assert d2.get('list') is missing
        assert d2.to_mongo() == {}

        d2.from_mongo({'in_mongo_list': []})
        d2.get('list').append(1)
        assert d2.to_mongo() == {'in_mongo_list': [1]}
        assert d2.to_mongo(update=True) == {'$set': {'in_mongo_list': [1]}}

        # Test repr readability
        repr_d = repr(d.get('list'))
        assert repr_d == "<object umongo.data_objects.List([2, 3, 4, 5])>"

        d3 = MyDataProxy({'list': None})
        assert d3.to_mongo() == {'in_mongo_list': None}
        d3.from_mongo({'in_mongo_list': None})
        assert d3.get('list') is None

        d3.from_mongo({'in_mongo_list': []})
        assert repr(
            d3._data.get('in_mongo_list')
        ) == '<object umongo.data_objects.List([])>'

    def test_list_default(self):

        class MySchema(Schema):
            d_list = fields.ListField(fields.IntField(), default=(1, 2, 3))
            c_list = fields.ListField(fields.IntField(), default=lambda: (1, 2, 3))

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        assert d.to_mongo() == {
            'd_list': [1, 2, 3],
            'c_list': [1, 2, 3],
        }
        assert isinstance(d.get('d_list'), List)
        assert isinstance(d.get('c_list'), List)
        d.get('d_list').append(4)
        d.get('c_list').append(4)
        assert d.to_mongo(update=True) == {
            '$set': {'c_list': [1, 2, 3, 4], 'd_list': [1, 2, 3, 4]}}

        d.delete('d_list')
        d.delete('c_list')
        assert d.to_mongo() == {
            'd_list': [1, 2, 3],
            'c_list': [1, 2, 3],
        }
        assert isinstance(d.get('d_list'), List)
        assert isinstance(d.get('c_list'), List)
        assert d.to_mongo(update=True) == {
            '$set': {'c_list': [1, 2, 3], 'd_list': [1, 2, 3]}}

    def test_complex_list(self):

        @self.instance.register
        class MyEmbeddedDocument(EmbeddedDocument):
            field = fields.IntField()

        @self.instance.register
        class ToRefDoc(Document):
            pass

        @self.instance.register
        class MyDoc(Document):
            embeds = fields.ListField(
                fields.EmbeddedField(MyEmbeddedDocument))
            refs = fields.ListField(fields.ReferenceField(ToRefDoc))

        MySchema = MyDoc.Schema

        obj_id1 = ObjectId()
        obj_id2 = ObjectId()
        to_ref_doc1 = ToRefDoc.build_from_mongo(data={'_id': obj_id1})
        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.load({
            'embeds': [MyEmbeddedDocument(field=1),
                       {'field': 2}],
            'refs': [to_ref_doc1, Reference(ToRefDoc, obj_id2)]
        })
        assert d.to_mongo() == {
            'embeds': [{'field': 1}, {'field': 2}],
            'refs': [obj_id1, obj_id2]
        }
        assert isinstance(d.get('embeds'), List)
        assert isinstance(d.get('refs'), List)
        for e in d.get('refs'):
            assert isinstance(e, Reference)
        for e in d.get('embeds'):
            assert isinstance(e, MyEmbeddedDocument)
        # Test list modification as well
        refs_list = d.get('refs')
        refs_list.append(to_ref_doc1)
        refs_list.extend([to_ref_doc1, Reference(ToRefDoc, obj_id2)])
        for e in refs_list:
            assert isinstance(e, Reference)
        embeds_list = d.get('embeds')
        embeds_list.append(MyEmbeddedDocument(field=3))
        embeds_list.extend([{'field': 4}, {'field': 5}])
        for e in embeds_list:
            assert isinstance(e, MyEmbeddedDocument)
        # Modifying an EmbeddedDocument inside a list should count a list modification
        d.clear_modified()
        d.get('refs')[0] = obj_id2
        assert d.to_mongo(update=True) == {'$set': {'refs': [
            obj_id2, obj_id2, obj_id1, obj_id1, obj_id2]}}
        d.clear_modified()
        d.get('embeds')[1].field = 42
        assert d.to_mongo(update=True) == {'$set': {'embeds': [
            {'field': 1}, {'field': 42}, {'field': 3}, {'field': 4}, {'field': 5}]}}

    def test_objectid(self):

        class MySchema(Schema):
            objid = fields.ObjectIdField(attribute='in_mongo_objid')

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.load({'objid': ObjectId("5672d47b1d41c88dcd37ef05")})
        assert d.dump() == {'objid': "5672d47b1d41c88dcd37ef05"}
        assert d.to_mongo() == {'in_mongo_objid': ObjectId("5672d47b1d41c88dcd37ef05")}
        d.load({'objid': "5672d47b1d41c88dcd37ef05"})
        assert d.dump() == {'objid': "5672d47b1d41c88dcd37ef05"}
        assert d.to_mongo() == {'in_mongo_objid': ObjectId("5672d47b1d41c88dcd37ef05")}
        assert d.get('objid') == ObjectId("5672d47b1d41c88dcd37ef05")

        d.set('objid', ObjectId("5672d5e71d41c88f914b77c4"))
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_objid': ObjectId("5672d5e71d41c88f914b77c4")}}

        d.set('objid', ObjectId("5672d5e71d41c88f914b77c4"))
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_objid': ObjectId("5672d5e71d41c88f914b77c4")}}

        d.set('objid', "5672d5e71d41c88f914b77c4")
        assert d.get('objid') == ObjectId("5672d5e71d41c88f914b77c4")

        with pytest.raises(ValidationError):
            d.set('objid', 'notanid')

    def test_reference(self):

        @self.instance.register
        class MyReferencedDoc(Document):

            class Meta:
                collection_name = 'my_collection'

        @self.instance.register
        class OtherDoc(Document):
            pass

        to_refer_doc = MyReferencedDoc.build_from_mongo(
            {'_id': ObjectId("5672d47b1d41c88dcd37ef05")})
        ref = Reference(MyReferencedDoc, to_refer_doc.pk)
        dbref = DBRef('my_collection', to_refer_doc.pk)
        other_doc = OtherDoc.build_from_mongo(
            {'_id': ObjectId("5672d47b1d41c88dcd37ef07")})

        # Test reference equality
        assert ref == to_refer_doc
        assert ref == dbref
        assert dbref == to_refer_doc
        assert dbref == ref
        assert to_refer_doc == ref
        assert to_refer_doc == dbref

        @self.instance.register
        class MyDoc(Document):
            ref = fields.ReferenceField(MyReferencedDoc, attribute='in_mongo_ref', allow_none=True)

        MySchema = MyDoc.Schema

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.load({'ref': ObjectId("5672d47b1d41c88dcd37ef05")})
        d.load({'ref': "5672d47b1d41c88dcd37ef05"})
        assert d.dump() == {'ref': "5672d47b1d41c88dcd37ef05"}
        assert d.get('ref').document_cls == MyReferencedDoc
        d.set('ref', to_refer_doc)
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_ref': to_refer_doc.pk}}
        assert d.get('ref') == ref
        d.set('ref', ref)
        assert d.get('ref') == ref
        d.set('ref', dbref)
        assert d.get('ref') == ref

        with pytest.raises(ValidationError):
            d.set('ref', other_doc)
        not_created_doc = MyReferencedDoc()
        with pytest.raises(ValidationError):
            d.set('ref', not_created_doc)
        bad_ref = Reference(OtherDoc, other_doc.pk)
        with pytest.raises(ValidationError):
            d.set('ref', bad_ref)

        d2 = MyDataProxy({'ref': None})
        assert d2.to_mongo() == {'in_mongo_ref': None}
        d2.from_mongo({'in_mongo_ref': None})
        assert d2.get('ref') is None

    def test_reference_lazy(self):

        @self.instance.register
        class MyReferencedDocLazy(Document):
            pass

        to_refer_doc = MyReferencedDocLazy.build_from_mongo(
            {'_id': ObjectId("5672d47b1d41c88dcd37ef05")})

        @self.instance.register
        class MyDoc(Document):
            ref = fields.ReferenceField("MyReferencedDocLazy", attribute='in_mongo_ref')

        MySchema = MyDoc.Schema

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.load({'ref': ObjectId("5672d47b1d41c88dcd37ef05")})
        d.load({'ref': "5672d47b1d41c88dcd37ef05"})
        assert d.dump() == {'ref': "5672d47b1d41c88dcd37ef05"}
        assert d.get('ref').document_cls == MyReferencedDocLazy
        d.set('ref', to_refer_doc)
        assert d.to_mongo(update=True) == {'$set': {'in_mongo_ref': to_refer_doc.pk}}
        assert d.get('ref').document_cls == MyReferencedDocLazy

    def test_generic_reference(self):

        @self.instance.register
        class ToRef1(Document):
            pass

        @self.instance.register
        class ToRef2(Document):
            pass

        doc1 = ToRef1.build_from_mongo({'_id': ObjectId()})
        ref1 = Reference(ToRef1, doc1.pk)

        @self.instance.register
        class MyDoc(Document):
            gref = fields.GenericReferenceField(attribute='in_mongo_gref', allow_none=True)

        MySchema = MyDoc.Schema

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.load({'gref': {'id': ObjectId("5672d47b1d41c88dcd37ef05"), 'cls': ToRef2.__name__}})
        assert d.dump() == {'gref': {'id': "5672d47b1d41c88dcd37ef05", 'cls': 'ToRef2'}}
        assert d.get('gref').document_cls == ToRef2
        d.set('gref', doc1)
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_gref': {'_id': doc1.pk, '_cls': 'ToRef1'}}}
        assert d.get('gref') == ref1
        d.set('gref', ref1)
        assert d.get('gref') == ref1
        assert d.dump() == {'gref': {'id': str(doc1.pk), 'cls': 'ToRef1'}}

        not_created_doc = ToRef1()
        with pytest.raises(ValidationError):
            d.set('gref', not_created_doc)

        # Test invalid references
        for v in [
            {'id': ObjectId()},  # missing _cls
            {'cls': ToRef1.__name__},  # missing _id
            {'id': ObjectId(), 'cls': 'dummy!'},  # invalid _cls
            {'_id': ObjectId(), '_cls': ToRef1.__name__},  # bad field names
            {'id': ObjectId(), 'cls': ToRef1.__name__, 'e': '?'},  # too much fields
            ObjectId("5672d47b1d41c88dcd37ef05"),  # missing cls info
            42,  # Are you kidding ?
            '',  # Please stop...
            True  # I'm outa of that !
        ]:
            with pytest.raises(ValidationError):
                d.set('gref', v)

        d2 = MyDataProxy({'gref': None})
        assert d2.to_mongo() == {'in_mongo_gref': None}
        d2.from_mongo({'in_mongo_gref': None})
        assert d2.get('gref') is None

    def test_decimal(self):

        class MySchema(Schema):
            price = fields.DecimalField(attribute='in_mongo_price')

        MyDataProxy = data_proxy_factory('My', MySchema())
        d = MyDataProxy()
        d.load({'price': Decimal128('12.5678')})
        assert d.dump() == {'price': Decimal('12.5678')}
        assert d.to_mongo() == {'in_mongo_price': Decimal128('12.5678')}
        assert d.get('price') == Decimal('12.5678')

        d.load({'price': Decimal('12.5678')})
        assert d.dump() == {'price': Decimal('12.5678')}
        assert d.to_mongo() == {'in_mongo_price': Decimal128("12.5678")}
        assert d.get('price') == Decimal('12.5678')

        d.load({'price': '12.5678'})
        assert d.dump() == {'price': Decimal('12.5678')}
        assert d.to_mongo() == {'in_mongo_price': Decimal128("12.5678")}
        assert d.get('price') == Decimal('12.5678')

        d.load({'price': float('12.5678')})
        assert d.dump() == {'price': Decimal('12.5678')}
        assert d.to_mongo() == {'in_mongo_price': Decimal128("12.5678")}
        assert d.get('price') == Decimal('12.5678')

        d.set('price', Decimal128('11.1234'))
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_price': Decimal128('11.1234')}}

        d.set('price', Decimal("10.1234"))
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_price': Decimal128('10.1234')}}

        d.set('price', "9.1234")
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_price': Decimal128('9.1234')}}

        d.set('price', 8.1234)
        assert d.to_mongo(update=True) == {
            '$set': {'in_mongo_price': Decimal128('8.1234')}}

        d.from_mongo({'in_mongo_price': Decimal128('7.1234')})
        assert d._data == {
            'in_mongo_price': Decimal('7.1234')
        }

        with pytest.raises(ValidationError):
            d.set('price', 'str')
