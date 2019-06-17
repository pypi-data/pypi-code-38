from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware
from dataclasses import dataclass, field
from types import SimpleNamespace as SN
from typing import Sequence
from .routes import (
    authentication as authenticationRoutes, permissions as permissionRoutes,
    health as healthRoutes
)
from .config import defaultSettings
from .middleware import logRequest, allowCors, authentication as authenticationMiddleware


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

        self["settings"] = baseSettings

        self.add_endpoint(
            "/sign-up/",
            authenticationRoutes.SignUpEndpoint,
        )
        self.add_endpoint(
            "/log-in/",
            authenticationRoutes.LogInEndpoint,
        )
        self.add_endpoint(
            "/log-out/",
            authenticationRoutes.LogOutEndpoint,
        )
        self.add_endpoint(
            "/me/",
            authenticationRoutes.MeEndpoint,
        )
        self.add_endpoint(
            "/healthy/",
            healthRoutes.HealthCheckEndpoint,
        )

    def add_endpoint(self, path, handlerClass, name=None):
        self.router.add_route(
            "*", path,
            handlerClass(settings=SN(**self["settings"])).handle
        )
        self.router.add_route(
            "get", f"/documentation{path}",
            handlerClass(
                settings=SN(**self["settings"]),
                name=name,
                path=path,
            ).handleDocumentation
        )

    def run_app(self):
        web.run_app(self)
