# -*- coding: utf-8 -*-
from .interfaces import IPostgresData
from collective.easyform import easyformMessageFactory as _
from collective.easyform.actions import Action
from collective.easyform.actions import ActionFactory
from collective.easyform.api import get_context
from collective.easyform.api import get_schema
from collective.easyform.api import OrderedDict
from DateTime import DateTime
from logging import getLogger
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.supermodel.exportimport import BaseHandler
from psycopg2 import Binary
from psycopg2 import connect as pgconnect
from zope.interface import implementer
from zope.schema import getFieldsInOrder

import psycopg2.extensions
import six


psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

logger = getLogger('collective.easyform')


@implementer(IPostgresData)
class PostgresData(Action):
    __doc__ = IPostgresData.__doc__

    def __init__(self, **kw):
        for i, f in IPostgresData.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
        super(PostgresData, self).__init__(**kw)

    def getColumns(self):
        """ 
        Returns a list of tuples (column names, column type name) 
        in correct order of the fields in the form
        """

        context = get_context(self)
        showFields = getattr(self, 'showFields', [])
        if showFields is None:
            showFields = []
        columns = [
            (name, type(field).__name__)
            for name, field in getFieldsInOrder(get_schema(context))
        ]
        return columns

    def getpg_datatype(self, type):
        '''maps field/python types to corresponding postgres data types
           fine tuning using postgres tools might be done
        '''
        type_mapper = {
            'Boolean': 'boolean',
            'NoneType': 'null',
            'Float': 'numeric',
            'Int': 'int',
            'Decimal': 'numeric',
            'TextLine': 'character varying',
            'Text': 'text',
            'Datetime': 'timestamp',
            'RichText': 'text',
            'NamedBlobFile': 'bytea',
            'NamedBlobImage': 'bytea',
            'Set': 'text[]',
        }
        return type_mapper.get(type, 'Text')

    def create_pgtable(self, data, dbcon):
        ''' generates a CREATE TABLE statement for postgressql data base 
         and executes it. 
         A serial column "id" as primary key is inserted at the top of the table.
         Among other goodies, this allows to edit data directly using tools
         like pgadmin4 etc..
         data structure: {fieldname : (field value, python datatype of field)}
        '''
        stmt = ('CREATE TABLE public."{}"\n (_id_ serial primary key').format(
            self.postgres_table_name
        )

        for key, value in six.iteritems(data):
            try:
                stmt += ',\n{} {}'.format(key, self.getpg_datatype(value[1]))
            except Exception as e:
                pass
        stmt += ');'
        curs = dbcon.cursor()
        # psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, curs)
        curs.execute(stmt)
        dbcon.commit()
        curs.close()

    def generate_insert_stmt(self, data):

        sqlstmt = u'INSERT INTO public."{}"('.format(self.postgres_table_name)
        i = 0
        for key, value in six.iteritems(data):
            if i != 0:
                sqlstmt += u', '
            i += 1
            sqlstmt += u'{}'.format(key)
        sqlstmt += ') VALUES (' + '%s, ' * (i - 1) + '%s);'
        sqldata = ()
        for key, value in six.iteritems(data):
            val = value[0]
            if value[0] is None:
                val = None
            elif isinstance(value[0], set):
                val = list(value[0])
            elif isinstance(value[0], RichTextValue):
                val = value[0].output
            elif isinstance(value[0], NamedBlobImage):
                tmpblob = value[0]._blob._p_blob_uncommitted  # temp file
                val = Binary(open(tmpblob, 'rb').read())
            elif isinstance(value[0], NamedBlobFile):
                tmpblob = value[0]._blob._p_blob_uncommitted  # temp file
                val = Binary(open(tmpblob, 'rb').read())
            sqldata = sqldata + (val,)
        return sqlstmt, sqldata

    def InsertDB(self, context, data):
        db_con = self.postgres_con
        table_name = self.postgres_table_name
        dbcon = pgconnect(db_con)
        # check if database table exists
        curs = dbcon.cursor()
        curs.execute(
            "select * from information_schema.tables\
             where table_name=%s",
            (table_name,),
        )

        if not curs.rowcount:
            self.create_pgtable(data, dbcon)
        curs.close()
        curs = dbcon.cursor()
        sqlstmt, sqldata = self.generate_insert_stmt(data)
        try:
            curs.execute(sqlstmt, sqldata)
            dbcon.commit()
            return
        except Exception as e:

            logger.info(
                u'----------- insert statement tried: \n {}\n\{}\n\n -----\n'.format(
                    sqlstmt, sqldata
                )
            )
            raise e
        finally:
            curs.close()
            dbcon.close()

    def onSuccess(self, fields, request):
        """
        saves data  in Postgresdb.
        """
        data = OrderedDict()
        columns = self.getColumns()
        for tup in columns:
            if tup[1] in ('Float', 'Decimal') and self.decimal_separator:
                # treat both '.' and ',' as decimal separator
                # overriding form widget behaviour, convenient for forms on mobile!
                val = request.form['form.widgets.{}'.format(tup[0])].replace(
                    ',', '.'
                )
                if val == u'':
                    val = None
                else:
                    val = float(val)
            else:
                val = fields[tup[0]]
            data[tup[0]] = (val, tup[1])
        if self.ExtraData:
            for f in self.ExtraData:
                if f == 'dt':
                    data[f] = (str(DateTime()), 'Datetime')
                else:
                    data[f] = (getattr(request, f, ''), 'Text')
        context = get_context(self)
        ret = self.InsertDB(context, data)


PostgresDataAction = ActionFactory(
    PostgresData,
    _(u'label_postgresdata_action', default=u'Postgres Data'),
    'collective.easyform.AddPostgresData',
)
PostgresDataHandler = BaseHandler(PostgresData)
