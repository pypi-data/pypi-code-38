import pytest
from guillotina import testing
from guillotina._settings import app_settings
from guillotina.component import get_adapter
from guillotina.db.interfaces import IDatabaseManager


def base_settings_configurator(settings):
    if 'applications' in settings:
        settings['applications'].append('guillotina_dynamictablestorage')
    else:
        settings['applications'] = ['guillotina_dynamictablestorage']

    settings["storages"]['db']['type'] = 'prefixed-table'


testing.configure_with(base_settings_configurator)


@pytest.fixture()
async def dyn_storage(db, guillotina_main):
    storages = app_settings['storages']
    storage_config = storages['db']
    storage_config['storage_id'] = 'db'
    factory = get_adapter(guillotina_main.root, IDatabaseManager,
                          name=storage_config['type'],
                          args=[storage_config])
    factory._connection_managers.clear()
    return factory
