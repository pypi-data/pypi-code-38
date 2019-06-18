from stackifyapm.utils.module_import import import_string

_cls_registers = {
    "stackifyapm.instrumentation.packages.botocore.BotocoreInstrumentation",
    "stackifyapm.instrumentation.packages.cassandra.CassandraInstrumentation",
    "stackifyapm.instrumentation.packages.django.template.DjangoTemplateInstrumentation",
    "stackifyapm.instrumentation.packages.django.template.DjangoTemplateSourceInstrumentation",
    "stackifyapm.instrumentation.packages.elasticsearch.ElasticsearchConnectionInstrumentation",
    "stackifyapm.instrumentation.packages.elasticsearch.ElasticsearchInstrumentation",
    "stackifyapm.instrumentation.packages.jinja2.Jinja2Instrumentation",
    "stackifyapm.instrumentation.packages.mysql.MySQLInstrumentation",
    "stackifyapm.instrumentation.packages.psycopg2.Psycopg2Instrumentation",
    "stackifyapm.instrumentation.packages.psycopg2.Psycopg2RegisterTypeInstrumentation",
    "stackifyapm.instrumentation.packages.pylibmc.PyLibMcInstrumentation",
    "stackifyapm.instrumentation.packages.pymongo.PyMongoBulkInstrumentation",
    "stackifyapm.instrumentation.packages.pymongo.PyMongoCursorInstrumentation",
    "stackifyapm.instrumentation.packages.pymongo.PyMongoInstrumentation",
    "stackifyapm.instrumentation.packages.pymssql.PyMSSQLInstrumentation",
    "stackifyapm.instrumentation.packages.pyodbc.PyODBCInstrumentation",
    "stackifyapm.instrumentation.packages.python_memcached.PythonMemcachedInstrumentation",
    "stackifyapm.instrumentation.packages.redis.RedisInstrumentation",
    "stackifyapm.instrumentation.packages.redis.RedisPipelineInstrumentation",
    "stackifyapm.instrumentation.packages.requests.RequestsInstrumentation",
    "stackifyapm.instrumentation.packages.sqlite.SQLiteInstrumentation",
    "stackifyapm.instrumentation.packages.urllib.UrllibInstrumentation",
    "stackifyapm.instrumentation.packages.urllib2.Urllib2Instrumentation",
    "stackifyapm.instrumentation.packages.urllib3.Urllib3Instrumentation",
    "stackifyapm.instrumentation.packages.zlib.ZLibInstrumentation",

    # custom thread instrumentation for async support
    "stackifyapm.instrumentation.packages.thread.ThreadInstrumentation",

    # custom instrumentation
    "stackifyapm.instrumentation.packages.custom.CustomInstrumentation",

    # stackify log api instrumentation
    "stackifyapm.instrumentation.packages.stackify.StackifyInstrumentation",
}


def register(cls):
    cls and cls.strip() and _cls_registers.add(cls)


_instrumentation_singletons = {}


def get_instrumentation_objects():
    for cls_str in _cls_registers:
        if cls_str not in _instrumentation_singletons:
            cls = import_string(cls_str)
            _instrumentation_singletons[cls_str] = cls()

        obj = _instrumentation_singletons[cls_str]
        yield obj
