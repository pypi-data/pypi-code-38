import json
from inspect import getdoc
from aiohttp import web


async def handleDocumentation(handler):
    docs = {"description": getdoc(handler)}

    docs["methods"] = {
        methodName: methodClass().describe()
        for methodName, methodClass in handler.methods().items()
    }

    return web.Response(
        text=json.dumps(docs), headers={"Content-Type": "application/json"}
    )
