
import time

from dvcr.containers.base import BaseContainer


class Vertica(BaseContainer):
    def __init__(self, image="jbfavre/vertica", tag="latest", port=5433, network=None):
        """ Constructor for Vertica """
        super(Vertica, self).__init__(port=port, image=image, tag=tag, network=network)

        self._container = self._client.containers.run(
            image=image + ":" + tag,
            detach=True,
            name="vertica",
            network=self._network.name,
            ports={port: port},
        )

    def execute_query(self, query, data=None):

        response = self._container.exec_run(
                cmd=["/opt/vertica/bin/vsql", "-U", "dbadmin", "-c", query],
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

    def create_schema(self, name):

        self.execute_query(query="CREATE SCHEMA {};".format(name))

        return self

    def create_table(self, schema, table, columns):
        self.create_schema(name=schema)

        cols = ", ".join([col + " " + dtype for col, dtype in columns])

        self.execute_query(
            query="CREATE TABLE {schema}.{table} ({columns});".format(
                schema=schema, table=table, columns=cols
            )
        )

        return self

    def copy(self, source_file_path, schema, table):

        with open(source_file_path, 'rb') as _file:

            self.execute_query(
                query="COPY {schema}.{table} FROM STDIN ABORT ON ERROR DELIMITER ',';".format(
                    schema=schema, table=table
                ),
                data=_file.read()
            )

        return self
