import requests
import json
from primed_avro.schema import SchemaMeta, Schema


class ConfluentSchemaRegistryClient:
    def __init__(self, url):
        self.url = url

        # keeps a local cache of requested schema's
        self._schema_cache = {}

    def get_schema(self, subject, version="latest"):
        assert isinstance(subject, str)

        r = requests.get(
            "{url}/subjects/{subject}/versions/{version}".format(
                url=self.url, subject=subject, version=version
            ),
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        )

        if r.status_code == 200:
            js = r.json()

            if "error_code" in js:
                raise Exception(
                    "failed to retrieve schema, error_code: {error_code}, msg: {msg}".format(
                        error_code=js["error_code"], msg=js["msg"]
                    )
                )

            return SchemaMeta(**js)
        else:
            raise Exception(
                "failed to retrieve schema, status code: {status_code}".format(
                    status_code=r.status_code
                )
            )

    def create_schema(self, subject, schema):
        assert isinstance(schema, dict)
        assert isinstance(subject, str)

        r = requests.post(
            "{url}/subjects/{subject}/versions".format(url=self.url, subject=subject),
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            data=json.dumps({"schema": json.dumps(schema)}),
        )

        if r.status_code == 200:
            js = r.json()

            return SchemaMeta(id=js["id"], subject=subject, version=None, schema=schema)
        else:
            raise Exception(
                "failed to upsert schema, status code: {status_code}: {text}".format(
                    status_code=r.status_code, text=r.text
                )
            )

    def get_by_id(self, id):
        # verify that we haven't already requested this
        # particular schema
        if id not in self._schema_cache:
            # http://localhost:8089/schemas/ids/23
            r = requests.get(
                "{url}/schemas/ids/{id}".format(url=self.url, id=id),
                headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            )

            if r.status_code == 200:
                js = r.json()

                if "error_code" in js:
                    raise Exception(
                        "failed to retrieve schema, error_code: {error_code}, msg: {msg}".format(
                            error_code=js["error_code"], msg=js["msg"]
                        )
                    )

                self._schema_cache[id] = Schema(id=id, **js)
            else:
                raise Exception(
                    "failed to retrieve schema due to connection problems, status code: {status_code}".format(
                        status_code=r.status_code
                    )
                )

        return self._schema_cache[id]
