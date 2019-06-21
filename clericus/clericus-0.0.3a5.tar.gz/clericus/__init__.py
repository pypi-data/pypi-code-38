from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware
import json
from dataclasses import dataclass, field
from types import SimpleNamespace as SN
from typing import Sequence
from .routes import (
    authentication as authenticationRoutes, permissions as permissionRoutes,
    health as healthRoutes
)
from .config import defaultSettings
from .middleware import logRequest, allowCors, authentication as authenticationMiddleware

from .handler import newMethod, Endpoint, Method


class Clericus(web.Application):
    def __init__(self, settings=None, logging=True):
        baseSettings = defaultSettings()
        baseSettings.update(settings or {})
        middlewares = [
            normalize_path_middleware(append_slash=True),
            allowCors(origins=baseSettings["corsOrigins"]),
        ]

        if logging:
            middlewares.append(logRequest)

        middlewares.append(
            authenticationMiddleware(
                db=baseSettings["db"],
                secretKey=baseSettings["jwtKey"],
            ),
        )
        super().__init__(middlewares=middlewares, )

        self.documentation = []

        self["settings"] = baseSettings

        self.router.add_route(
            "GET",
            "/",
            self.documentationHandler,
        )

        self.addEndpoint(
            "/sign-up/",
            authenticationRoutes.SignUpEndpoint,
        )
        self.addEndpoint(
            "/log-in/",
            authenticationRoutes.LogInEndpoint,
        )
        self.addEndpoint(
            "/log-out/",
            authenticationRoutes.LogOutEndpoint,
        )
        self.addEndpoint(
            "/me/",
            authenticationRoutes.MeEndpoint,
        )
        self.addEndpoint(
            "/healthy/",
            healthRoutes.HealthCheckEndpoint,
        )

    def addEndpoint(self, path, handlerClass, name=None):
        cls = handlerClass(
            settings=SN(**self["settings"]),
            name=name,
            path=path,
        )
        self.router.add_route("*", path, cls.handle)
        self.router.add_route(
            "get",
            f"/documentation{path}",
            cls.handleDocumentation,
        )

        self.documentation.append(cls.describe())

    async def documentationHandler(self, request: web.Request) -> web.Response:
        return web.Response(
            text=json.dumps(self.describe()),
            headers={"Content-Type": "application/json"}
        )

    def describe(self):
        return {
            "endpoints": sorted(
                self.documentation,
                key=lambda k: k["path"],
            )
        }

    def runApp(self):
        web.run_app(self)
