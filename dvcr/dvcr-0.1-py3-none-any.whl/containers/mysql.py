import time

from dvcr.containers.base import BaseContainer


class MySQL(BaseContainer):
    def __init__(
        self, image="mysql", tag="latest", port=3306, environment=None, network=None
    ):
        """ Constructor for MySQL """
        super(MySQL, self).__init__(port=port, image=image, tag=tag, network=network)

        if not environment:
            environment = {}
        if "MYSQL_ALLOW_EMPTY_PASSWORD" not in environment:
            environment["MYSQL_ALLOW_EMPTY_PASSWORD"] = "yes"
        if "MYSQL_ROOT_PASSWORD" not in environment:
            environment["MYSQL_ROOT_PASSWORD"] = "root"

        self.user = environment.get("MYSQL_USER", "root")
        self.password = environment.get("MYSQL_PASSWORD", "root")
        self.db = environment.get("MYSQL_DATABASE", "mysql")

        self._container = self._client.containers.run(
            image=image + ":" + tag,
            command=[
                "--default-authentication-plugin=mysql_native_password",
                "--explicit_defaults_for_timestamp=1",
                "--local-infile=1",
            ],
            detach=True,
            name="mysql",
            network=self._network.name,
            ports={port: port},
            environment=environment,
        )

        self.register_post_wait_hook(fn=self.grant, user_or_role=self.user)

    @property
    def sql_alchemy_conn(self):

        return "mysql://{user}:{pwd}@{host}:{port}/{db}".format(
            user=self.user,
            pwd=self.password,
            host=self._container.name,
            port=self.port,
            db=self.db,
        )

    def execute_query(self, query, database="", data=None):

        response = self._container.exec_run(
            cmd=[
                "mysql",
                "--local-infile=1",
                "-u" + self.user,
                "-p" + self.password,
                database,
                "-e",
                query
            ],
            socket=True if data else False,
            stdin=True if data else False,
        )

        if data:
            socket = response.output

            socket.settimeout(1)
            socket.sendall(string=data)

            socket.close()

        time.sleep(1)

        return self

    def create_database(self, name):

        self.execute_query(query="CREATE DATABASE {};".format(name))

        self.use_database(name=name)

        return self

    def use_database(self, name):

        self.db = name

        return self

    def create_table(self, database, table, columns):
        self.create_database(name=database)

        cols = ", ".join([col + " " + dtype for col, dtype in columns])

        self.execute_query(
            database=database,
            query="CREATE TABLE {table} ({columns});".format(table=table, columns=cols),
        )

        return self

    def grant(self, user_or_role, priv_type="ALL PRIVILEGES", object_type="*.*"):

        query = "GRANT {priv_type} ON {object_type} TO {user_or_role};".format(
            priv_type=priv_type, object_type=object_type, user_or_role=user_or_role
        )

        self.execute_query(query=query)

    def load_data(self, source_file_path, database, table):

        with open(source_file_path, "rb") as _file:
            print("Loading data from " + source_file_path)
            self.execute_query(
                query="LOAD DATA LOCAL INFILE '/dev/stdin' INTO TABLE {table} FIELDS TERMINATED BY ',';".format(
                    table=table
                ),
                database=database,
                data=_file.read(),
            )

        return self
