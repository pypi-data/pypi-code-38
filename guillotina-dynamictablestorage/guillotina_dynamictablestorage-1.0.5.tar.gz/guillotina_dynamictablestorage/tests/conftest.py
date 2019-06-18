import os


os.environ['DATABASE'] = 'postgresql'

pytest_plugins = [
    'aiohttp.pytest_plugin',
    'guillotina.tests.fixtures',
    'guillotina_dynamictablestorage.tests.fixtures'
]
