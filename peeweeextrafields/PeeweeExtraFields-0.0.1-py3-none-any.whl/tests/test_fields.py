import os
import unittest

from peewee import *

from PeeweeExtraFields import *

package_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(package_dir, 'LocalDB')
local_db = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = local_db

    @classmethod
    def recreate_tables(cls):
        local_db.connect(reuse_if_open=True)
        table_list = local_db.get_tables()

        for model in cls.__subclasses__():
            if model.__name__.lower() not in table_list:
                local_db.create_tables([model])


class PassMD5Table(BaseModel):
    id = PrimaryKeyField()
    pass_md5 = PasswordMD5Field()


class PassSHA1Table(BaseModel):
    id = PrimaryKeyField()
    pass_sha1 = PasswordSHA1Field()


class MacTable(BaseModel):
    id = PrimaryKeyField()
    mac = MACField()


class SasTable(BaseModel):
    id = PrimaryKeyField()
    sas = SASField()


class I36Table(BaseModel):
    id = PrimaryKeyField()
    i36 = IntegerBase36Field()


class TestPeeweeExtraFields(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        BaseModel.recreate_tables()

    @classmethod
    def tearDownClass(cls) -> None:
        local_db.close()
        os.remove(db_path)


class TestDBCreation(TestPeeweeExtraFields):
    def test_table_creation_success(self):
        table_list = local_db.get_tables()
        self.assertIn(member='i36table', container=table_list)
        self.assertIn(member='passmd5table', container=table_list)
        self.assertIn(member='passsha1table', container=table_list)
        self.assertIn(member='mactable', container=table_list)
        self.assertIn(member='sastable', container=table_list)


class TestMacField(TestPeeweeExtraFields):
    def test_str_mac_creation_success(self):
        value = 'a5:A5:a5:A5:a5:A5'
        new = MacTable.create(mac=value)
        new.save()
        new_id = new.id
        self.assertEqual(MacTable.get_by_id(new_id).mac, value.lower())

    def test_int_mac_creation_success(self):
        value = 182130867283365
        new = MacTable.create(mac=value)
        new.save()
        new_id = new.id
        self.assertEqual(MacTable.get_by_id(new_id).mac, 'a5:A5:a5:A5:a5:A5'.lower())

    def test_mac_creation_failure(self):
        exception = None
        value = 'a!:A5:a5:A5:a5:A5'
        try:
            MacTable.create(mac=value)
        except Exception as error:
            exception = error

        self.assertEqual(str(exception), "invalid literal for int() with base 16: 'a!A5a5A5a5A5'")


class TestSasField(TestPeeweeExtraFields):
    def test_str_sas_creation_success(self):
        value = 'a5:A5:a5:A5:a5:A5'
        new = SasTable.create(sas=value)
        new.save()
        new_id = new.id
        self.assertEqual(SasTable.get_by_id(new_id).sas, value.lower())

    def test_int_sas_creation_success(self):
        value = 182130867283365
        new = SasTable.create(sas=value)
        new.save()
        new_id = new.id
        self.assertEqual(SasTable.get_by_id(new_id).sas, 'a5:A5:a5:A5:a5:A5'.lower())

    def test_sas_creation_failure(self):
        exception = None
        value = 'a!:A5:a5:A5:a5:A5'
        try:
            SasTable.create(sas=value)
        except Exception as error:
            exception = error

        self.assertEqual(str(exception), "invalid literal for int() with base 16: 'a!A5a5A5a5A5'")


class TestI36Field(TestPeeweeExtraFields):
    def test_1_str_i36_creation_success(self):
        value = 'ABCDEFGHIJ'
        new = I36Table.create(i36=value)
        new.save()
        new_id = new.id
        self.assertEqual(I36Table.get_by_id(new_id).i36, value.upper())

    def test_2_str_i36_creation_success(self):
        value = 'KLMNOPQRST'
        new = I36Table.create(i36=value)
        new.save()
        new_id = new.id
        self.assertEqual(I36Table.get_by_id(new_id).i36, value.upper())

    def test_3_str_i36_creation_success(self):
        value = 'UVWXYZ0123'
        new = I36Table.create(i36=value)
        new.save()
        new_id = new.id
        self.assertEqual(I36Table.get_by_id(new_id).i36, value.upper())

    def test_int_i36_creation_success(self):
        value = 88454623
        new = I36Table.create(i36=value)
        new.save()
        new_id = new.id
        self.assertEqual(I36Table.get_by_id(new_id).i36, '1GNW0V')

    def test_i36_creation_failure(self):
        exception = None
        value = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789!'
        try:
            I36Table.create(i36=value)
        except Exception as error:
            exception = error

        self.assertEqual(str(exception), "invalid literal for int() with base 36: 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789!'")


class TestMD5PasswordField(TestPeeweeExtraFields):
    def test_md5_check_success(self):
        password = 'password'
        new = PassMD5Table.create(pass_md5=password)
        new.save()
        new_id = new.id
        result = PassMD5Table.get_by_id(new_id)
        self.assertTrue(check_password(encrypted=result.pass_md5, raw_password=password))

    def test_md5_check_failure(self):
        password = 'password'
        new = PassMD5Table.create(pass_md5=password)
        new.save()
        new_id = new.id
        result = PassMD5Table.get_by_id(new_id)
        self.assertFalse(check_password(encrypted=result.pass_md5, raw_password='pawosrd'))


class TestSHA1PasswordField(TestPeeweeExtraFields):
    def test_sha1_check_success(self):
        password = 'password'
        new = PassSHA1Table.create(pass_sha1=password)
        new.save()
        new_id = new.id
        result = PassSHA1Table.get_by_id(new_id)
        self.assertTrue(check_password(encrypted=result.pass_sha1, raw_password=password))

    def test_sha1_check_failure(self):
        password = 'password'
        new = PassSHA1Table.create(pass_sha1=password)
        new.save()
        new_id = new.id
        result = PassSHA1Table.get_by_id(new_id)
        self.assertFalse(check_password(encrypted=result.pass_sha1, raw_password='pawosrd'))
