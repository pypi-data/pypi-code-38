import ast
import json
from datetime import datetime
from swissarmykit.db.database import RecordModel
from peewee import *

from sale.app.request_lib.FileThread import FileTask
from swissarmykit.utils.timer import Timer
from swissarmykit.db.redisconnect import RedisConnect

try: from definitions_prod import *
except Exception as e: pass # Surpass error. Note: Create definitions_prod.py


class BaseModel(RecordModel):
    db_name = appConfig.DATABASE_NAME

    class Meta:
        database = RecordModel.get_db(appConfig.DATABASE_NAME)

    @classmethod
    def update_or_create(cls, data=None, ids_name='url', return_obj=False):

        if data.get('data') and isinstance(data.get('data'), dict):
            data['data'] = json.dumps(data.get('data'))

        # This is deprecate approach, please don't use html inside main table. It slow performance.
        if 'html' in data.keys() and not data.get('html'):
            raise Exception('html can not be empty, should skip instead of updating to database.')

        return super(BaseModel, cls).update_or_create(data=data, ids_name=ids_name, return_obj=return_obj)

    @classmethod
    def get_html_by_id(cls, id=1, output=False):
        item = cls.get_one().where(cls.html_id == id).first()
        html = item.get_html()

        if output:
            html_path = '%s/%s_id_%d.html' % (appConfig.get_desktop_path(), cls.get_table_name(), id)
            FileUtils.to_html_file(html_path, item.get_html())
            print('INFO: output to html: %s' % html_path)

        return item.html

    @classmethod
    def update_html_to_0(cls):
        sql = 'UPDATE %s SET html_id = 0;' % cls.get_table_name()
        return cls.execute_sql(sql=sql)

    @classmethod
    def delete_all_html(cls):
        task = FileTask(0, cls.get_table_name())
        task.delete_all()
        cls.update_html_to_0()
        print('INFO: Delete all folder %s' % task.get_path())

    @classmethod
    def delete_all_cache(cls):
        redis = RedisConnect()
        redis.delete_namespace(cls.get_table_name())
        print('INFO: Delete all cache: namespace: %s' % cls.get_table_name())

    @classmethod
    def load_all_cache(cls):
        redis = RedisConnect()

        timer = Timer(cls.count())
        for item in cls.select():
            if item.html_id:
                redis.set(item.get_cache_key(), item.get_html())
                timer.check()
        print('INFO: Done load cache %s' % cls.get_table_name())

    @classmethod
    def output_html_by_id(cls, id=1, html_path=None):
        item = cls.get_one().where(cls.html_id == id).first()
        html = item.get_html()

        if not html_path:
            html_path = '%s/%s_id_%d.html' % (appConfig.get_desktop_path(), cls.get_table_name(), id)
        FileUtils.to_html_file(html_path, html)
        print('INFO: output to html: %s' % html_path)
        return html

    def set_data_null(self):
        return self.update_or_create(data={'id': self.id, 'html_id': 0, 'data': None, 'meta_id': 0}, ids_name='id')

    def get_data(self, is_extra_col=False, get_valid_function=None):
        ''' ref: data of this obj.'''
        s = self.extra if is_extra_col else self.data
        if s:
            if get_valid_function:
                data = get_valid_function(s)
            else:
                data = s
            try:
                quote = data[1]
                if quote == '"':
                    return json.loads(data)
                if quote == "'":
                    return ast.literal_eval(data)
            except:
                return {}
        return {}

    def save_extra_html(self, html):
        self.save_extra('longtext', html)

    def get_extra_html(self):
        return self.get_extra('longtext')


    def get_extra_col(self):
        return self.get_data(is_extra_col=True)

    def save_extra_col(self, data):
        return self.save_data(data, is_extra_column=True)


    def save_data(self, data, is_extra_column=False):
        col_key = 'extra' if is_extra_column else 'data'
        data_ = {
            'id'  : self.id,
            col_key: json.dumps(data) if isinstance(data, dict) else data,
        }
        return self.update_or_create(data=data_, ids_name='id')

    def get_file_task(self):
        return FileTask(self.id, self.get_table_name())

    def get_html(self, level=1): # type: (int) -> str
        if self.html_id:
            return FileTask(id=self.id, table=self.get_table_name()).load(level=level)
        else:
            return ''

    def get_html_2(self):
        return self.get_html(level=2)

    def get_html_3(self):
        return self.get_html(level=3)

    def save_html_2(self, html):
        return self.save_html(html, level=2)

    def save_html_3(self, html):
        return self.save_html(html, level=3)

    def get_cache_key(self):
        return '%s:%d' % (self.get_table_name(), self.id)

    @classmethod
    def reload_meta_data(cls):
        task = FileTask(0, cls.get_table_name())
        size, files = task.get_info()
        _file_meta.update_or_create(data={'table': cls.get_table_name(), 'files': files, 'size': size},
                                    ids_name='table')
        print('INFO: %s - %d - %d' % (cls.get_table_name(), files, size))

    def save_html(self, html, level=1):  # type: (str, int) -> BaseModel
        '''
        This function is not class method, because it need id of object.
        '''
        if not html:
            return 0

        if FileTask(id=self.id, table=self.get_table_name(), html=html).save(level=level):
            return self.update_or_create(data={'id': self.id, 'html_id': 1}, ids_name='id')
        return False

    @classmethod
    def get_tmp_class(cls, class_name='', level=1): # type: (str, int) -> BaseModel
        class_name = 'zz_tmp_' + class_name + '_' + str(level)
        clazz =  cls.get_class(class_name)
        return clazz

    @classmethod
    def get_class(cls, class_name='', create_table=True): # type: (str, bool) -> BaseModel

        class modelTemplate(cls):
            id = IntegerField(primary_key=True)
            url = CharField()
            name = CharField()
            html_id = SmallIntegerField(default=0)
            data = TextField()
            extra = TextField()
            images = TextField()
            meta_id = BigIntegerField()

        # noinspection PyTypeChecker
        class_: RecordModel = type(class_name, (modelTemplate,), {})
        if create_table:
            class_.create_table_if_not_exists()
        return class_


'''
CREATE TABLE `_file_meta` (
  `id` int(11)  unsigned NOT NULL AUTO_INCREMENT,
  `table` varchar(255) NOT NULL,
  `files` int(11) DEFAULT NULL,
  `size` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`table`),
  UNIQUE KEY `table` (`table`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''

class _file_meta(BaseModel):
    ''' Make this class is simple as much as possible.
    Only insert, no update, because the database will be larger.

    '''
    id = IntegerField()
    table = CharField()        # Option: for debugging
    files = IntegerField()
    size = BigIntegerField()

if __name__ == '__main__':
    from definitions_prod import *
    # print(appConfig)
    # test = BaseModel.get_class('test_auto')
    # print(test.add_extra_column_if_not_exists())
    # item = test.get_first_rows()
    # item.save_extra('text', '000')
    # print(item.get_extra())
    # item.save_html('tesa')
    # test = ModelGenerator.get_class('test_auto')
    # extra_column.dump_on_query_by_id([1,3,4])
    # test.dump_sql_of_this_table()

    # test.add_extra_column_if_not_exists()


