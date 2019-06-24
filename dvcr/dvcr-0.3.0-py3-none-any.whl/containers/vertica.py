from typing import Optional

from dvcr.containers.base import BaseContainer
from dvcr.network import Network


class Vertica(BaseContainer):
    def __init__(
        self,
        repo: str = "jbfavre/vertica",
        tag: str = "latest",
        port: int = 5433,
        name: str = "vertica",
        network: Optional[Network] = None,
    ):
        """ Constructor for Vertica """
        super(Vertica, self).__init__(port=port, repo=repo, tag=tag, name=name, network=network)

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name,
            network=self._network.name,
            ports={port: port},
        )

    def execute_query(self, query, path_or_buf=None):

        self.exec(
            cmd=[
                "/opt/vertica/bin/vsql",
                "-U",
                "dbadmin",
                "--echo-queries",
                "-c",
                query,
            ],
            path_or_buf=path_or_buf,
        )

        return self

    def create_schema(self, name):

        self.execute_query(query="CREATE SCHEMA IF NOT EXISTS {};".format(name))

        return self

    def create_table(self, schema, table, columns):
        self.create_schema(name=schema)

        cols = ", ".join(['"{}" {}'.format(col, dtype) for col, dtype in columns])

        self.execute_query(
            query="CREATE TABLE {schema}.{table} ({columns});".format(
                schema=schema, table=table, columns=cols
            )
        )

        return self

    def copy(self, schema, table, path_or_buf, header=True):

        if header:
            skip = 1
        else:
            skip = 0

        self.execute_query(
            query="COPY {schema}.{table} FROM LOCAL STDIN SKIP {skip} ABORT ON ERROR DELIMITER ',';".format(
                schema=schema, table=table, skip=skip
            ),
            path_or_buf=path_or_buf,
        )

        return self
