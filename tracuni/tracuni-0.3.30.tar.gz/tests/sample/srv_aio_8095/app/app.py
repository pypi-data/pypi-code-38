import asyncio

from app.core.app import BaseApp
from app.core.http_client import HttpClient
from app.core.http_server import HttpServer
from app.handlers.http_router import HttpRouter
from app.core.component import Component
from app.core.amqp_server import AMQPServer
from app.handlers.amqp_handler import AmqpHandler
from app.models.tasks_db import DbTasks


from tracuni import *


class Application(BaseApp):
    def __init__(self, config: dict, loop: asyncio.AbstractEventLoop):
        super(Application, self).__init__(config=config, loop=loop)
        self.attach_component(
            'db_tasks',
            DbTasks(config['db']),
            stop_after=['http_srv']
        )
        self.attach_component(
            "http_cln",
            HttpClient()
        )
        self.attach_component(
            "http_srv",
            HttpServer(
                self,
                config["system"]["host"],
                config["system"]["port"],
                HttpRouter,
                skip_trace=config["logging"]["skip_trace"]
            )
        )
        self.attach_component(
            'amqp_srv',
            AMQPServer(
                self,
                config['rabbit'],
                AmqpHandler
            )
        )
        rule_set = (
            Rule(
                destination=Destination(
                    section=DestinationSection.SPAN_TAGS,
                    name="some",
                ),
                pipeline=(
                    lambda _: "some",
                ),
                origins=(
                    Origin(
                        section=OriginSection.REUSE,
                        getter="custom_remote_endpoint_name",
                    ),
                ),
                stage=Stage.PRE,
            ),
            # Rule(
            #     destination=Destination(
            #         section=DestinationSection.ALL,
            #         name="",
            #     ),
            #     pipeline=(PipeCommand.SKIP_LEVELS_BELOW,),
            #     origins=tuple(),
            # )
        )  # type: RuleSet
        self.attach_component(
            'tracer_uni',
            fab_tracer(Component)(
                self,
                config['logging'],
                config['statsd'],
                # config_system=config['system'],
                # custom_schema={
                #     Variant(
                #         span_side=SpanSide.IN,
                #         api_kind=APIKind.HTTP,
                #     ): rule_set,
                # }  # type: Schema
            )
        )
