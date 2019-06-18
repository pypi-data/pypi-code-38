from typing import Optional, Union, Tuple, List

from dvcr.containers.base import BaseContainer
from dvcr.network import Network


class Postgres(BaseContainer):
    def __init__(
        self,
        repo: str = "postgres",
        tag: str = "latest",
        port: int = 5432,
        environment: Optional[dict] = None,
        name: str = "postgres",
        network: Optional[Network] = None,
    ):
        """ Constructor for Postgres """
        super(Postgres, self).__init__(port=port, repo=repo, tag=tag, name=name, network=network)

        if not environment:
            environment = {"POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": ""}

        self.user = environment.get("POSTGRES_USER", "postgres")
        self.password = environment.get("POSTGRES_PASSWORD", "")
        self.db = environment.get("POSTGRES_DB", "postgres")

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name="postgres",
            network=self._network.name,
            ports={port: port},
            environment=environment,
        )

        self.sql_alchemy_conn = "postgresql://{user}:{pwd}@{host}:{port}/{db}".format(
            user=self.user,
            pwd=self.password,
            host=self._container.name,
            port=self.port,
            db=self.db,
        )

    def execute_query(self, query: str, path_or_buf: Union[str, bytes, None] = None):

        self.exec(
            cmd=["psql", "-U", "postgres", "-e", "--command", query],
            path_or_buf=path_or_buf,
        )

        return self

    def create_schema(self, name: str):

        self.execute_query(query="CREATE SCHEMA IF NOT EXISTS {};".format(name))

        return self

    def create_table(self, schema: str, table: str, columns: List[Tuple[str, str]]):
        self.create_schema(name=schema)

        cols = ", ".join([col + " " + dtype for col, dtype in columns])

        self.execute_query(
            query="CREATE TABLE {schema}.{table} ({columns});".format(
                schema=schema, table=table, columns=cols
            )
        )

        return self

    def copy(self, schema: str, table: str, path_or_buf: Union[str, bytes]):

        self.execute_query(
            query="COPY {schema}.{table} FROM STDIN DELIMITER ',';".format(
                schema=schema, table=table
            ),
            path_or_buf=path_or_buf,
        )

        return self
