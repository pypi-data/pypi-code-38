from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.dialects.postgresql.base import PGDialect

def isMssqlDialect(engine):
    return isinstance(engine.dialect, MSDialect)

def isPostGreSQLDialect(engine):
    return isinstance(engine.dialect, PGDialect)

def ensureSchemaExists(engine, schemaName):
    # Ensure the schema exists

    if isinstance(engine.dialect, MSDialect):
        if list(engine.execute("SELECT SCHEMA_ID('%s')" % schemaName))[0][0] is None:
            engine.execute("CREATE SCHEMA [%s]" % schemaName)

    elif isinstance(engine.dialect, PGDialect):
        engine.execute(
            'CREATE SCHEMA IF NOT EXISTS "%s" ' % schemaName)

    else:
        raise Exception('unknown dialect %s' % engine.dialect)

class AlembicEnvBase:
    def __init__(self, targetMetadata):
        from peek_platform.util.LogUtil import setupPeekLogger
        setupPeekLogger()

        self._config = context.config
        self._targetMetadata = targetMetadata
        self._schemaName = targetMetadata.schema

    def _includeObjectFilter(self, object, name, type_, reflected, compare_to):
        # If it's not in this schema, don't include it
        if hasattr(object, 'schema') and object.schema != self._schemaName:
            return False

        return True

    def run(self):
        """Run migrations in 'online' mode.
    
        In this scenario we need to create an Engine
        and associate a connection with the context.
    
        """
        connectable = engine_from_config(
            self._config.get_section(self._config.config_ini_section),
            prefix='sqlalchemy.',
            poolclass=pool.NullPool)

        with connectable.connect() as connection:
            ensureSchemaExists(connectable, self._schemaName)

            context.configure(
                connection=connection,
                target_metadata=self._targetMetadata,
                include_object=self._includeObjectFilter,
                include_schemas=True,
                version_table_schema=self._schemaName
            )

            with context.begin_transaction():
                context.run_migrations()
