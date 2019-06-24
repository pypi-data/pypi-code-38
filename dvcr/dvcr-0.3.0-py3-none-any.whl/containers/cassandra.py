from typing import Optional, Iterable

from dvcr.containers.base import BaseContainer
from dvcr.network import Network


class Cassandra(BaseContainer):
    def __init__(
        self,
        repo: str = "cassandra",
        tag: str = "latest",
        port: int = 9042,
        environment: Optional[dict] = None,
        name: str = "cassandra",
        network: Optional[Network] = None,
    ):
        """ Constructor for Cassandra """
        super(Cassandra, self).__init__(
            port=port, repo=repo, tag=tag, name=name, network=network
        )

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name,
            network=self._network.name,
            ports={port: port},
            environment=environment,
        )

    def execute_query(self, query: str, keyspace: Optional[str] = None):

        cmd = ["cqlsh", "--execute", query]

        if keyspace:
            cmd += ["--keyspace", keyspace]

        self.exec(cmd=cmd)

    def create_keyspace(self, name: str):

        self._logger.info("Creating keyspace %s", name)

        query = """CREATE KEYSPACE {name}
                      WITH REPLICATION = {{ 
                       'class' : 'SimpleStrategy', 
                       'replication_factor' : 1 
                      }};""".format(
            name=name
        )

        self.execute_query(query=query)

        return self

    def create_table(
        self,
        keyspace: str,
        table: str,
        columns: Iterable[Iterable[str]],
        primary_key: Iterable[str],
    ):

        cols = ", ".join([col + " " + dtype for col, dtype in columns])

        pk = "PRIMARY KEY (" + ", ".join(primary_key) + ")"

        query = "CREATE TABLE {keyspace}.{table} ({columns}, {pk});".format(
            keyspace=keyspace, table=table, columns=cols, pk=pk
        )

        self.execute_query(query=query)

        return self

    def insert(self, keyspace: str, table: str, values: dict):

        cols = []
        vals = []

        for key, value in values.items():
            cols.append(key)
            vals.append("'" + value + "'" if isinstance(value, str) else str(value))

        query = """INSERT INTO {keyspace}.{table} ({columns}) VALUES ({values});""".format(
            keyspace=keyspace,
            table=table,
            columns=", ".join(cols),
            values=", ".join(vals),
        )

        self.execute_query(query=query, keyspace=keyspace)
