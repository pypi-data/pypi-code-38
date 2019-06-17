import requests
import attr
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Iterable

from .templates import query_update, query_conditional_read, query_insert, query_read

# from ..database.model import taskSchema
from ..config import GraphQLConfig

# from ..database.transactions import deserialization
from ..database.model.schema import Task, taskSchema, deserialization


class Request:
    j2_env = Environment(
        loader=FileSystemLoader("./template"), autoescape=select_autoescape(["j2"])
    )

    @staticmethod
    def url():
        return GraphQLConfig.GraphQL_URL

    @classmethod
    def run_query(cls, query):
        """A function to use requests.post to make the API call. Note the json section."""
        request = requests.post(
            cls.url(), json={"query": query}, headers={"Connection": "close"}
        )
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception(
                "Query failed to run by returning code of {}. {}".format(
                    request.status_code, query
                )
            )

    @classmethod
    def updates(cls, table_name, id, patches):
        j2_template = cls.j2_env.from_string(query_update)
        query = j2_template.render(table_name=table_name, id=id, patches=patches)
        return cls.run_query(query)

    @classmethod
    def read(
        cls,
        table_name: str,
        select: str,
        condition: str,
        returns: Iterable[str],
        operator="_eq",
    ):
        """
        Read from taskDB.

        select & condition can be none.
        """

        def parse(response):
            return [[row[key] for key in row] for row in response["data"][table_name]]

        def flat_list(l: "nested_list") -> "List[T]":
            result = []

            def _flatten(l):
                for item in l:
                    if isinstance(item, list):
                        _flatten(item)
                    else:
                        result.append(item)

            _flatten(l)
            return result

        def format_handler(s: str):
            if (s[0] == '"' and s[-1:] == '"') or (s[0] == "'" and s[-1:] == "'"):
                return s[1:-1]
            else:
                return s

        if select is not None and condition is not None:
            j2_template = cls.j2_env.from_string(query_conditional_read)
            query = j2_template.render(
                table_name=table_name,
                select=select,
                operator=operator,
                condition=format_handler(condition),
                returns=returns,
            )
            return flat_list(parse(cls.run_query(query)))
        else:
            j2_template = cls.j2_env.from_string(query_read)
            query = j2_template.render(table_name=table_name, returns=returns)
            return cls.run_query(query)

    @classmethod
    def read_tasks(cls, select, where):
        j2_template = cls.j2_env.from_string(query_conditional_read)
        query = j2_template.render(
            table_name="tasks",
            select=select,
            operator="_in",
            condition=where,
            returns=taskSchema.declared_fields.keys(),
        )
        response = cls.run_query(query)
        tmp = []

        for t in response["data"]["tasks"]:
            tmp.append(deserialization(t))

        return tmp

    @classmethod
    def by_resource_id(cls, id):
        return cls.read(
            table_name="resources", select="id", condition=str(id), returns=["urls"]
        )

    @classmethod
    def insert(cls, table_name: str, inserts: dict):
        j2_template = cls.j2_env.from_string(query_insert)
        query = j2_template.render(table_name=table_name, inserts=inserts)
        return cls.run_query(query)

    @classmethod
    def insert_task(cls, task):
        response = cls.insert(table_name="tasks", inserts=_serilize(task))
        return response["data"]["insert_tasks"]["returning"][0]["id"]

    @classmethod
    def update_task(cls, task):
        response = Request.updates(
            table_name="tasks", id=task.id, patches=_serilize(task)
        )
        return response["data"]["update_tasks"]["returning"][0]["id"]


def _to_graphql_style_array(l: list) -> str:
    return "{" + ",".join(str(i) for i in l) + "}"


def _serilize(task: Task):
    result = dict()
    task_dict = attr.asdict(task)
    for k, v in task_dict.items():
        if v is None:
            continue
        if isinstance(v, list):
            result[k] = _to_graphql_style_array(v)
        else:
            result[k] = v
    return result
