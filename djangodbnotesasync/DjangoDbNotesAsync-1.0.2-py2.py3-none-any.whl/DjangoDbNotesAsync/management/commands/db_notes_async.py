# coding: utf-8

"""
将django models中注释，同步到mysql数据库中
"""
import os
from django.db.models import ManyToOneRel, OneToOneRel, UUIDField, DateTimeField, FloatField, GenericIPAddressField, \
    IntegerField, CharField, DecimalField, DateField, ManyToManyRel
from django.db import connections
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.fields.reverse_related import ForeignObjectRel

INSTALLED_VALID_APPS = []

error_info = []

app_src_dir = os.path.dirname(settings.BASE_DIR)
cursor = connections['default'].cursor()


class DbNotesAsync(BaseCommand):

    @classmethod
    def field_info(cls, field):
        """获取字段信息"""
        field_decimal_places = None
        field_length = None
        if isinstance(field, UUIDField):
            field_type = 'char'
            field_length = 32
        elif isinstance(field, DateTimeField):
            field_type = 'datetime'
        elif isinstance(field, DateField):
            field_type = 'date'
        elif isinstance(field, FloatField):
            field_type = 'float'
        elif isinstance(field, GenericIPAddressField):
            field_type = 'char'
            field_length = 39
        elif isinstance(field, IntegerField):
            field_type = 'int'
        elif isinstance(field, CharField):
            field_type = 'varchar'
            field_length = field.max_length
        elif isinstance(field, DecimalField):
            field_type = 'decimal'
            field_length = field.max_digits
            field_decimal_places = field.decimal_places
        else:
            field_type = 'invalid'
            field_length = -9999999     # 表示无效的值

        return field_type, field_length, field_decimal_places

    @classmethod
    def main_handlers(cls):
        """
        主处理handler
        """
        for app_name in settings.INSTALLED_APPS:
            if os.path.exists('{}/{}/models.py'.format(app_src_dir, app_name)):
                INSTALLED_VALID_APPS.append(app_name)
        content_types = ContentType.objects.filter(app_label__in=INSTALLED_VALID_APPS).order_by('id')

        for item in content_types:
            model_obj = item.model_class()
            if model_obj:
                db_table = model_obj._meta.db_table
                table_note = model_obj._meta.verbose_name or model_obj.__doc__
                cls.add_table_notes_to_db(db_table=db_table, table_note=table_note)
                for field in model_obj._meta.get_fields():
                    if not (isinstance(field, ManyToOneRel) or isinstance(field, OneToOneRel)
                            or isinstance(field, UUIDField) or isinstance(field, ManyToManyRel)
                            or isinstance(field, ForeignObjectRel)
                    ) and field.help_text:
                        field_type, field_length, field_decimal_places = cls.field_info(field)
                        if field_length == -9999999:
                            continue
                        cls.add_field_notes_to_db(db_table=db_table, column=field.name,
                                                  field_type=field_type, field_length=field_length,
                                                  field_decimal_places=field_decimal_places,
                                                  comment=field.help_text)
        for item in error_info:
            print('错误信息: ', item)
        return INSTALLED_VALID_APPS

    @staticmethod
    def add_table_notes_to_db(db_table, table_note):
        """添加表的注释"""
        table_note = table_note.replace("\n", "").replace(" ", "")
        if table_note:
            sql = """alter table `{db_table}` comment "{table_note}" """.format(db_table=db_table, table_note=table_note)
            try:
                cursor.execute(sql)
            except Exception as e:
                print('修改表{}发生异常，注释为为: {}，异常原因: {}'.format(db_table, table_note, e))
            print('表:【{}】, 注释信息为: 【{}】, 添加成功......'.format(db_table, table_note))
        return

    @staticmethod
    def add_field_notes_to_db(db_table, column, field_type, field_length, comment, field_decimal_places=None):
        """添加字段注释"""
        if not comment:
            return
        if field_type in ['int', 'double', 'float', 'date', 'datetime']:
            column_data = '`{column}` {field_type}'.format(column=column, field_type=field_type)
        elif field_type == 'decimal' and field_decimal_places:
            column_data = '`{column}` {field_type}({field_length}, {field_decimal_places})'.\
                format(column=column, field_type=field_type, field_length=field_length,
                       field_decimal_places=field_decimal_places)
        else:
            column_data = '`{column}` {field_type}({field_length})'.format(column=column, field_type=field_type,
                                                                           field_length=field_length)

        sql = """alter table `{db_table}` modify column {column_data} COMMENT "{comment}" """.\
            format(db_table=db_table, column_data=column_data, comment=comment)
        try:
            cursor.execute(sql)
        except Exception as e:
            error_info.append('表: {}, 字段: {}, 注释信息: {}, sql: {}，原因: {}'.format(db_table, column,
                                                                               comment, sql, e))
        print('表:【{}】, 字段: 【{}】, 注释信息: 【{}】, 添加成功......'.format(db_table, column, comment))
        return

    def handle(self, *args, **options):
        """"""
        self.main_handlers()


Command = DbNotesAsync
