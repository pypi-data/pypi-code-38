# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['botx', 'botx.models']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.5.4,<4.0.0',
 'aiojobs>=0.2.2,<0.3.0',
 'pydantic==0.28',
 'requests>=2.22,<3.0']

extras_require = \
{'doc': ['mkdocs>=1.0,<2.0', 'mkdocs-material>=4.4,<5.0'],
 'test': ['pytest>=4.5,<5.0',
          'pytest-cov>=2.7,<3.0',
          'pytest-asyncio>=0.10.0,<0.11.0',
          'responses>=0.10.6,<0.11.0',
          'aresponses>=1.1,<2.0']}

setup_kwargs = {
    'name': 'botx',
    'version': '0.11.1',
    'description': 'A little python library for building bots for Express',
    'long_description': '<h1 align="center">pybotx</h1>\n<p align="center">\n    <em>A little python library for building bots for Express</em>\n</p>\n<p align="center">\n    <a href="https://github.com/ExpressApp/pybotx/blob/master/LICENSE">\n        <img src="https://img.shields.io/github/license/Naereen/StrapDown.js.svg" alt="License">\n    </a>\n    <a href="https://github.com/ambv/black">\n        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">\n    </a>\n    <a href="https://pypi.org/project/botx/">\n        <img src="https://badge.fury.io/py/botx.svg" alt="Package version">\n    </a>\n</p>\n\n\n---\n\n# Introduction\n\n`pybotx` is a toolkit for building bots for Express providing a mechanism for simple integration with your favourite web frameworks.\n\nMain features:\n\n * Simple integration with your web apps.\n * Synchronous API as well as asynchronous.\n * 100% test coverage.\n * 100% type annotated codebase.\n\n---\n\n## Requirements\n\nPython 3.6+\n\n`pybotx` use the following libraries:\n\n* <a href="https://github.com/samuelcolvin/pydantic" target="_blank">Pydantic</a> for the data parts.\n* <a href="https://github.com/kennethreitz/requests" target="_blank">Requests</a> for making synchronous calls to BotX API.\n* <a href="https://github.com/aio-libs/aiohttp" target="_blank">Aiohttp</a> for making asynchronous calls to BotX API.\n* <a href="https://github.com/aio-libs/aiojobs" target="_blank">Aiojobs</a> for dispatching asynchronous tasks.\n\n## Installation\n```bash\n$ pip install botx\n```\n\nYou will also need a web framework to create bots as the current BotX API only works with webhooks. \nThis documentation will use <a href="https://github.com/tiangolo/fastapi" target="_blank">FastAPI</a> for the examples bellow.\n```bash\n$ pip install fastapi uvicorn \n```\n\n## Example\n\nLet\'s create a simple echo bot. \n\n* Create a file `main.py` with following content:\n```Python3\nfrom botx import Bot, Message, Status\nfrom fastapi import FastAPI\nfrom starlette.middleware.cors import CORSMiddleware\nfrom starlette.status import HTTP_202_ACCEPTED\n\nbot = Bot(disable_credentials=True)\n\n\n@bot.default_handler\ndef echo_handler(message: Message, bot: Bot):\n    bot.answer_message(message.body, message)\n\n\napp = FastAPI()\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["*"],\n    allow_credentials=True,\n    allow_methods=["*"],\n    allow_headers=["*"],\n)\n\n\n@app.get("/status", response_model=Status)\ndef bot_status():\n    return bot.status\n\n\n@app.post("/command", status_code=HTTP_202_ACCEPTED)\ndef bot_command(message: Message):\n    bot.execute_command(message.dict())\n```\n<details markdown="1">\n<summary>Or use <code>async def</code></summary>\n\n```Python3 hl_lines="1 6 10 11 23 24 28 33 34"\nfrom botx import AsyncBot, Message, Status\nfrom fastapi import FastAPI\nfrom starlette.middleware.cors import CORSMiddleware\nfrom starlette.status import HTTP_202_ACCEPTED\n\nbot = AsyncBot(disable_credentials=True)\n\n\n@bot.default_handler\nasync def echo_handler(message: Message, bot: Bot):\n    await bot.answer_message(message.body, message)\n\n\napp = FastAPI()\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["*"],\n    allow_credentials=True,\n    allow_methods=["*"],\n    allow_headers=["*"],\n)\n\napp.add_event_handler("startup", bot.start)\napp.add_event_handler("shutdown", bot.stop)\n\n\n@app.get("/status", response_model=Status)\nasync def bot_status():\n    return bot.status\n\n\n@app.post("/command", status_code=HTTP_202_ACCEPTED)\nasync def bot_command(message: Message):\n    await bot.execute_command(message.dict())\n```\n</details>\n\n* Deploy a bot on your server using uvicorn and set the url for the webhook in Express.\n```bash\n$ uvicorn main:app --host=0.0.0.0\n```\n\nThis bot will send back every your message.\n\n## License\n\nThis project is licensed under the terms of the MIT license.',
    'author': 'Michael Morozov',
    'author_email': 'mmorozov@ccsteam.ru',
    'url': 'https://github.com/ExpressApp/pybotx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
