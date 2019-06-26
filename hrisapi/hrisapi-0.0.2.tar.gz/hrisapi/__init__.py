import concurrent.futures

from basescript import BaseScript
from tornadoql import TornadoQL, GraphQLHandler
from redis import Redis
import memoize
import memoize.redis

from . import schema
from . import zoho_schema


class TornadoQL(TornadoQL):
    def __init__(self, *args, **kwargs):

        self.threadpool = kwargs.pop("threadpool", None)
        self.memoizer = kwargs.pop("memoizer", None)
        self.cache_duration = kwargs.pop("cache_duration", 0)

        super().__init__(*args, **kwargs)

    def make_app(self):
        app = super().make_app()
        app.threadpool = self.threadpool
        app.memoizer = self.memoizer
        app.cache_duration = self.cache_duration
        return app


class ZOHOGraphQLHandler(GraphQLHandler):
    @property
    def middleware(self):
        return []

    @property
    def context(self):
        c = super().context

        app = self.application

        zoho_auth_key = self.request.headers.get("Authorization", "").split(" ", 1)[-1]
        threadpool = app.threadpool
        memoizer = app.memoizer
        cache_duration = app.cache_duration

        loader_params = dict(
            auth_key=zoho_auth_key,
            threadpool=threadpool,
            memoizer=memoizer,
            cache_duration=cache_duration,
        )

        c["auth_key"] = zoho_auth_key
        c["threadpool"] = threadpool
        c["memoizer"] = memoizer
        c["employee_loader"] = zoho_schema.EmployeeLoader(**loader_params)
        c["holidays_loader"] = zoho_schema.HolidaysLoader(**loader_params)
        c["idmappings_loader"] = zoho_schema.IDMappingsLoader(**loader_params)
        c["timezone_loader"] = zoho_schema.TimezoneLoader()
        c["cache_duration"] = cache_duration

        return c


class ZOHOTornadoQL(TornadoQL):
    GRAPHQL_HANDLER = ZOHOGraphQLHandler


class HRISAPIScript(BaseScript):
    DESC = "Human Resource Information Systems API"
    THREADPOOL_SIZE = 128
    CACHE_DURATION = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.memoizer = memoize.Memoizer(self._get_memoizer_store())
        self.threadpool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.THREADPOOL_SIZE
        )

        self.tornadoql_kwargs = dict(
            threadpool=self.threadpool,
            memoizer=self.memoizer,
            log=self.log,
            cache_duration=self.args.cache_duration,
        )

        if getattr(self.args, "port"):
            self.tornadoql_kwargs["port"] = self.args.port

    def _get_memoizer_store(self):
        loc = self.args.redis_loc

        if not loc:
            return {}

        loc = loc + (":" * (2 - loc.count(":")))
        kwargs = dict(zip(["host", "port", "db"], loc.split(":", 2)))

        if not kwargs["host"]:
            del kwargs["host"]

        if kwargs["port"]:
            kwargs["port"] = int(kwargs["port"])
        else:
            del kwargs["port"]

        if kwargs["db"]:
            kwargs["db"] = int(kwargs["db"])
        else:
            del kwargs["db"]

        db = Redis(**kwargs, password=self.args.redis_password)
        store = memoize.redis.wrap(db)
        return store

    def run(self):
        pass

    def cmd_schema(self):
        _schema = schema.make_schema()
        print(_schema)

    def cmd_runserver(self):
        _schema = schema.make_schema()
        TornadoQL(_schema, **self.tornadoql_kwargs).start()

    def cmd_runserver_zoho(self):
        _schema = zoho_schema.make_schema()
        ZOHOTornadoQL(_schema, **self.tornadoql_kwargs).start()

    def define_baseargs(self, parser):
        super().define_baseargs(parser)

        parser.add_argument("--threadpool-size", type=int, default=self.THREADPOOL_SIZE)
        parser.add_argument("--cache-duration", type=int, default=self.CACHE_DURATION)
        parser.add_argument("--redis-password", type=str, default=None)
        parser.add_argument(
            "--redis-loc",
            type=str,
            default=None,
            help="""host[:port[:db]]
                egs:
                    localhost                 => localhost:6379:0
                    localhost:6379            => localhost:6379:0
                    :6379                     => localhost:6379:0
                    ::0                       => localhost:6379:0
                    localhost:6379:0          => localhost:6379:0
                    ::                        => localhost:6379:0
                """,
        )

    def _define_schema_cmd(self, subcommands):
        schema_cmd = subcommands.add_parser("schema", help="Show the Schema")
        schema_cmd.set_defaults(func=self.cmd_schema)

    def _define_runserver_cmd(self, subcommands):
        cmd = subcommands.add_parser("runserver", help="Run server")
        cmd.add_argument("--port", type=int, default=8888)
        cmd.set_defaults(func=self.cmd_runserver)

        subcmd = cmd.add_subparsers()

        zoho_cmd = subcmd.add_parser("zoho", help="Run ZOHO API Interface")
        zoho_cmd.set_defaults(func=self.cmd_runserver_zoho)

    def define_subcommands(self, subcommands):
        super().define_subcommands(subcommands)

        self._define_schema_cmd(subcommands)
        self._define_runserver_cmd(subcommands)


def main():
    HRISAPIScript().start()


if __name__ == "__main__":
    main()
