import os
from invoke import task


@task
def create(_, name, force=False):
    """ Creates a project with procedures, services, settings and urls. """
    print(f"gen {name}")
    if os.path.exists(name) and force is False:
        print("that module already exists: ", name)
    else:
        if not os.path.isdir(name):
            os.makedirs(name)
        with open(os.path.join(name, "__init__.py"), "w") as file:
            file.write("")
        with open(os.path.join(name, "settings.py"), "w") as file:
            file.write(
                """''' add your settings here '''
import logging

def extend(settings):
    logging.info('extending settings')
    return settings
"""
            )
        with open(os.path.join(name, "urls.py"), "w") as file:
            file.write(
                """''' add your tornado routes here '''
import logging

def extend(urls):
    logging.info('extending urls')
    return urls
"""
            )
        with open(os.path.join(name, "procedures.py"), "w") as file:
            file.write(
                """''' an example function and exposing it through __all__ '''

__all__=['add']

def add(a:int, b:int)->int:
    return a+b
"""
            )
        with open(os.path.join(name, "services.py"), "w") as file:
            file.write(
                """''' an example service '''
import asyncio
import time
from bluemax import context

async def clock():
    ''' Will broadcast every 5 seconds '''
    while True:
        context.broadcast('time', {'now': time.time()})
        await asyncio.sleep(5)
"""
            )
