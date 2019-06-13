import pytest
from pachelm.core import PachydermAdminContext
from pachelm.migration import PachydermMigration
from pachelm.cli import VERSION

test_migrations = lambda ctx: [ctx.find_migration('test-input'), ctx.find_migration('test-pipeline')]
example_migrations = lambda ctx: [ctx.find_migration('example'), ctx.find_migration('example-pipeline')]
migrationsDir = './tests/migrations'
configsDir = './tests/configs'

def init_tearup_teardown_by_migrations(ctx, migrations, msg):
    print('initializing...(%s_stuff)' % (msg))
    ctx.tear_up(migrations)
    def finalizer():
        ctx.tear_down(reversed(migrations))
        print("Teardown %s stuffs..." % (msg))
    return finalizer


@pytest.fixture(scope='session')
def ctx(request):
    print('instantiate integration test context...')
    ctx = PachydermAdminContext(VERSION, migrationsDir, configsDir)
    finalizer = init_tearup_teardown_by_migrations(ctx, test_migrations(ctx), 'test')
    request.addfinalizer(finalizer)
    return ctx 

@pytest.fixture(scope='session')
def example_ctx(request):
    print('instantiate example context...')
    ctx = PachydermAdminContext(VERSION, migrationsDir, configsDir)
    finalizer = init_tearup_teardown_by_migrations(ctx, example_migrations(ctx), 'example')
    request.addfinalizer(finalizer)
    return ctx 