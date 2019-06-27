"""
Server's support for templates.

The server.template namespace contains two independent subsystems:

1. Multiple Template Engines: support for pluggable template backends,
   built-in backends and backend-independent APIs
2. Server Template Language: Server's own template engine, including its
   built-in loaders, context processors, tags and filters.

Ideally these subsystems would be implemented in distinct packages. However
keeping them together made the implementation of Multiple Template Engines
less disruptive .

Here's a breakdown of which modules belong to which subsystem.

Multiple Template Engines:

- server.template.backends.*
- server.template.loader
- server.template.response

Server Template Language:

- server.template.base
- server.template.context
- server.template.context_processors
- server.template.loaders.*
- server.template.debug
- server.template.defaultfilters
- server.template.defaulttags
- server.template.engine
- server.template.loader_tags
- server.template.smartif

Shared:

- server.template.utils

"""

# Multiple Template Engines

from .engine import Engine
from .utils import EngineHandler

engines = EngineHandler()

__all__ = ('Engine', 'engines')


# Server Template Language

# Public exceptions
from .base import VariableDoesNotExist                                  # NOQA isort:skip
from .context import ContextPopException                                # NOQA isort:skip
from .exceptions import TemplateDoesNotExist, TemplateSyntaxError       # NOQA isort:skip

# Template parts
from .base import (                                                     # NOQA isort:skip
    Context, Node, NodeList, Origin, RequestContext, Template, Variable,
)

# Library management
from .library import Library                                            # NOQA isort:skip


__all__ += ('Template', 'Context', 'RequestContext')
