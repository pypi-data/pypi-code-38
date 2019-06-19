#
#   Copyright 2018 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import asyncio
import contextlib
import json
import logging
import time

from typing import Any, Dict, List, Optional, TYPE_CHECKING

import jquery_querybuilder_psycopg2  # type: ignore
import psycopg2  # type: ignore
import psycopg2.errorcodes  # type: ignore
import websockets  # type: ignore

from .errors import ClientLeakableError
from .query_rules_rule_set_parser import QueryRulesRuleSetParser

if TYPE_CHECKING:
    from .endpoint import Endpoint  # noqa


class JsonLiteral(str):
    pass


class Session:
    def __init__(self, endpoint: 'Endpoint', websocket: Any) -> None:
        self.endpoint = endpoint
        self.websocket = websocket

        self.logger = SessionLoggerAdapter(
            logging.getLogger(), {'session': self})

        self.remote_address = websocket.remote_address[0]
        if endpoint.application.args.trust_x_forwarded_for:
            xff = websocket.request_headers.get("X-Forwarded-For")
            if xff:
                self.remote_address = xff.split(',')[-1].strip()

        self.pg_session_data = {}  # type: Dict[str, Any]
        self.pg_session_data['remote-address'] = self.remote_address
        self.pg_session_data['claims'] = {}

        self.logger.info("Created new session")

    async def websocket_handler(self) -> None:
        self.send_database_readiness(self.endpoint.database_listener.ready)

        while True:
            try:
                wspg_msg_json = await self.websocket.recv()

            except websockets.ConnectionClosed as e:
                msg = "Websocket closed with code {}, reason {!r}"
                self.logger.info(msg.format(e.code, e.reason))
                return

            try:
                wspg_msg = json.loads(wspg_msg_json)

                if not isinstance(wspg_msg, dict):
                    raise TypeError("wspg_msg must be a dict")

                _type = wspg_msg.pop('type')
                if not isinstance(_type, str):
                    raise TypeError("type must be a str")

                _id = wspg_msg.pop('id')
                if not isinstance(_id, str):
                    raise TypeError("id must be a str")

                asyncio.ensure_future(self.wspg_handler(_type, _id, wspg_msg))

            except Exception as e:
                msg = "Exception whilst parsing WSPG message"

                self.logger.warning("{}: {!r}".format(msg, e))

                await self.websocket.close(4002, "Unparsable message")

    async def wspg_handler(self, _type: str, _id: str, wspg_msg: Dict[str, Any]) -> None:
        try:
            handler_result = await self._wspg_handler(_type, wspg_msg)

            if not isinstance(handler_result, JsonLiteral):
                handler_result = json.dumps(handler_result)

            # Hand craft the JSON because the result is already json-encoded
            succeeded_json = '{{"type": "succeeded", "id": {_id}, "result": {result}}}'.format(
                _id=json.dumps(_id),
                result=handler_result)

            await self.websocket.send(succeeded_json)

        except ClientLeakableError as e:
            msg = "Error whilst handling WSPG message"

            if self.endpoint.application.args.verbose:
                self.logger.exception(msg)
            else:
                self.logger.warning("{}: {!r}".format(msg, e))

            failed_object = {
                'type': "failed",
                'id': _id,
                'reason': str(e)
            }

            if e.detail:
                failed_object['detail'] = e.detail

            await self.websocket.send(json.dumps(failed_object))

        except Exception as e:
            msg = "Exception whilst handling WSPG message"

            if self.endpoint.application.args.verbose:
                self.logger.exception(msg)
            else:
                self.logger.warning("{}: {!r}".format(msg, e))

            failed_json = json.dumps({
                'type': "failed",
                'id': _id,
                'reason': "Internal server error"})

            await self.websocket.send(failed_json)

    def send_database_readiness(self, ready: bool) -> None:
        msg_json = json.dumps({
            'type': "database-readiness",
            'ready': ready})

        asyncio.ensure_future(self.websocket.send(msg_json))

    def send_notification(self, notification: Any) -> None:
        msg_json = json.dumps({
            'type': "notification",
            'channel': notification.channel,
            'payload': notification.payload})

        asyncio.ensure_future(self.websocket.send(msg_json))

    async def _wspg_handler(self, _type: str, wspg_msg: Dict[str, Any]) -> Any:
        method_name = "handle_{}".format(_type.replace('-', '_'))

        try:
            handler = getattr(self, method_name)
        except AttributeError:
            raise ClientLeakableError("Message type {!r} is not defined".format(_type)) from None

        with call_timing_logger(self.logger, "WSPG handler"):
            return await handler(wspg_msg)

    async def handle_select(self, wspg_msg: Dict[str, Any]) -> Optional[JsonLiteral]:
        if ('relation' in wspg_msg and 'function' in wspg_msg) or ('relation' not in wspg_msg and 'function' not in wspg_msg):
            raise ClientLeakableError("Exactly one of \"relation\" and \"function\" must be supplied")

        if 'relation' in wspg_msg:
            relation_sql = extract_wspg_msg_relation_sql(wspg_msg, self.endpoint)
        else:
            relation_sql = extract_wspg_msg_function_call_sql(wspg_msg, self.endpoint)

        query_rules = extract_wspg_msg_query_rules(wspg_msg)
        returning_columns = extract_wspg_msg_returning_columns(wspg_msg)
        order = extract_wspg_msg_order(wspg_msg)
        limit = extract_wspg_msg_limit(wspg_msg)
        _slice = extract_wspg_msg_slice(wspg_msg)

        return await self._select(
            relation_sql, query_rules, returning_columns, order, limit,
            _slice)

    async def _select(self, relation_sql: psycopg2.sql.Composable, query_rules: Optional[QueryRulesRuleSetParser], returning_columns: Optional[List[str]], order: Optional[List[Dict[str, str]]], limit: Optional[int], _slice: Optional[Dict]) -> Optional[JsonLiteral]:
        fetch_result = True

        if returning_columns is None:
            columns_sql = psycopg2.sql.SQL("*")
        elif returning_columns == []:
            columns_sql = psycopg2.sql.SQL("1")
            fetch_result = False
        else:
            columns_sql = psycopg2.sql.SQL(", ").join(
                [psycopg2.sql.Identifier(column) for column in returning_columns])

        slice_requires_inverted_order_directions = False

        if _slice:
            if not order:
                msg = "slice requires order"
                raise ClientLeakableError(msg)

            if _slice['direction'] == 'earlier':
                slice_requires_inverted_order_directions = True

            slice_relative_to = _slice.get('relative-to')

            if slice_relative_to is not None:
                slice_condition = build_slice_condition(_slice, order)

                if query_rules:
                    query_rules = psycopg2.sql.SQL("({}) AND ({})").format(
                        query_rules, slice_condition)
                else:
                    query_rules = slice_condition

        if query_rules:
            where_sql = psycopg2.sql.SQL("WHERE {}").format(query_rules)
        else:
            where_sql = psycopg2.sql.SQL("")

        if order:
            order_sqls = []
            for item in order:
                item_column = psycopg2.sql.Identifier(item['column'])

                item_direction = item['direction']

                if slice_requires_inverted_order_directions:
                    if item_direction == 'ascending':
                        item_direction = 'descending'
                    else:
                        item_direction = 'ascending'

                if item_direction == 'ascending':
                    item_direction = psycopg2.sql.SQL("ASC")
                else:
                    item_direction = psycopg2.sql.SQL("DESC")

                order_sqls.append(
                    psycopg2.sql.SQL("{column} {direction}").format(
                        column=item_column,
                        direction=item_direction))

            order_sql = psycopg2.sql.SQL("ORDER BY {}").format(
                psycopg2.sql.SQL(", ").join(order_sqls))
        else:
            order_sql = psycopg2.sql.SQL("")

        if limit:
            limit_sql = psycopg2.sql.SQL("LIMIT {}").format(
                psycopg2.sql.Literal(limit))
        else:
            limit_sql = psycopg2.sql.SQL("")

        select_sql = psycopg2.sql.SQL("SELECT {columns} FROM {relation} {where} {order} {limit}").format(
            columns=columns_sql, relation=relation_sql, where=where_sql,
            order=order_sql, limit=limit_sql)

        return await self._execute_sql(select_sql, fetch_result)

    async def handle_insert(self, wspg_msg: Dict[str, Any]) -> Optional[JsonLiteral]:
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg, self.endpoint)
        rows = extract_wspg_msg_rows(wspg_msg)
        returning_columns = extract_wspg_msg_returning_columns(wspg_msg)

        return await self._insert(relation_sql, rows, returning_columns)

    async def _insert(self, relation_sql: psycopg2.sql.Composable, rows: List[Dict], returning_columns: Optional[List[str]]) -> Optional[JsonLiteral]:
        columns = set()  # type: Set[str]
        for row in rows:
            columns.update(row)

        columns_sql = psycopg2.sql.SQL(", ").join(
            [psycopg2.sql.Identifier(column) for column in columns])

        values_sqls = []

        for row in rows:
            row_values = []

            for column in columns:
                if column in row:
                    value = psycopg2.sql.Literal(row[column])
                else:
                    value = psycopg2.sql.SQL("DEFAULT")

                row_values.append(value)

            values_sqls.append(psycopg2.sql.SQL("({})").format(
                psycopg2.sql.SQL(", ").join(row_values)))

        values_sql = psycopg2.sql.SQL(", ").join(values_sqls)

        fetch_result = True

        if returning_columns is None:
            returning_sql = psycopg2.sql.SQL("RETURNING *")
        elif returning_columns == []:
            returning_sql = psycopg2.sql.SQL("")
            fetch_result = False
        else:
            returning_sql = psycopg2.sql.SQL("RETURNING {}").format(
                psycopg2.sql.SQL(", ").join(
                    [psycopg2.sql.Identifier(column) for column in returning_columns]))

        insert_sql = psycopg2.sql.SQL("INSERT INTO {relation} ({columns}) VALUES {values} {returning}").format(
            relation=relation_sql, columns=columns_sql,
            values=values_sql, returning=returning_sql)

        return await self._execute_sql(insert_sql, fetch_result)

    async def handle_update(self, wspg_msg: Dict[str, Any]) -> Optional[JsonLiteral]:
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg, self.endpoint)
        updates = extract_wspg_msg_updates(wspg_msg)
        query_rules = extract_wspg_msg_query_rules(wspg_msg)
        returning_columns = extract_wspg_msg_returning_columns(wspg_msg)

        return await self._update(relation_sql, updates, query_rules, returning_columns)

    async def _update(self, relation_sql: psycopg2.sql.Composable, updates: Dict, query_rules: Optional[QueryRulesRuleSetParser], returning_columns: Optional[List[str]]) -> Optional[JsonLiteral]:
        updates_sqls = []
        for column, value in updates.items():
            updates_sql = psycopg2.sql.SQL("{}={}").format(
                psycopg2.sql.Identifier(column), psycopg2.sql.Literal(value))
            updates_sqls.append(updates_sql)

        updates_sql = psycopg2.sql.SQL(", ").join(updates_sqls)

        if query_rules:
            where_sql = psycopg2.sql.SQL("WHERE {}").format(query_rules)
        else:
            where_sql = psycopg2.sql.SQL("")

        fetch_result = True

        if returning_columns is None:
            returning_sql = psycopg2.sql.SQL("RETURNING *")
        elif returning_columns == []:
            returning_sql = psycopg2.sql.SQL("")
            fetch_result = False
        else:
            returning_sql = psycopg2.sql.SQL("RETURNING {}").format(
                psycopg2.sql.SQL(", ").join(
                    [psycopg2.sql.Identifier(column) for column in returning_columns]))

        update_sql = psycopg2.sql.SQL("UPDATE {relation} SET {updates} {where} {returning}").format(
            relation=relation_sql, updates=updates_sql, where=where_sql,
            returning=returning_sql)

        return await self._execute_sql(update_sql, fetch_result)

    async def handle_delete(self, wspg_msg: Dict[str, Any]) -> None:
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg, self.endpoint)
        query_rules = extract_wspg_msg_query_rules(wspg_msg)

        await self._delete(relation_sql, query_rules)

    async def _delete(self, relation_sql: psycopg2.sql.Composable, query_rules: Optional[QueryRulesRuleSetParser]) -> None:
        if query_rules:
            where_sql = psycopg2.sql.SQL("WHERE {}").format(query_rules)
        else:
            where_sql = psycopg2.sql.SQL("")

        delete_sql = psycopg2.sql.SQL("DELETE FROM {relation} {where}").format(
            relation=relation_sql, where=where_sql)

        await self._execute_sql(delete_sql, False)

    async def handle_listen(self, wspg_msg: Dict[str, Any]) -> None:
        channel = extract_wspg_msg_channel(wspg_msg)

        await self.endpoint.database_listener.listen(self, channel)

    async def handle_unlisten(self, wspg_msg: Dict[str, Any]) -> None:
        channel = extract_wspg_msg_channel(wspg_msg)

        await self.endpoint.database_listener.unlisten(self, channel)

    async def handle_unlisten_all(self, wspg_msg: Dict[str, Any]) -> None:
        await self.endpoint.database_listener.unlisten_all(self)

    async def handle_apply_jwt(self, wspg_msg: Dict[str, Any]) -> None:
        issuer = extract_wspg_msg_issuer(wspg_msg)
        token = extract_wspg_msg_token(wspg_msg)

        await self._apply_jwt(issuer, token)

    async def _apply_jwt(self, issuer: str, token: Optional[str]) -> None:
        jwt_issuer = self.endpoint.application.jwt_issuers.get(issuer)
        if not jwt_issuer:
            raise ClientLeakableError("JWT issuer {!r} is not defined".format(issuer))

        if token is None:
            if issuer in self.pg_session_data['claims']:
                del self.pg_session_data['claims'][issuer]

            return

        claims_set = jwt_issuer.decode(token)

        self.pg_session_data['claims'][issuer] = claims_set

    async def handle_get_canonical_representations(self, wspg_msg: Dict[str, Any]) -> JsonLiteral:
        types = extract_wspg_msg_types(wspg_msg)
        value = extract_wspg_msg_value(wspg_msg)

        return await self._get_canonical_representations(types, value)

    async def _get_canonical_representations(self, types, value):
        types_sql = psycopg2.sql.Literal(types)
        value_sql = psycopg2.sql.Literal(value)

        helper_call_sql = psycopg2.sql.SQL("SELECT wspg_private.get_canonical_representations({types}::regtype[], {value})::text").format(
            types=types_sql, value=value_sql)

        try:
            async with self.endpoint.db_pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(helper_call_sql)
                    return JsonLiteral((await cursor.fetchone())[0])

        except psycopg2.Error as e:
            raise client_leakable_error_from_psycopg2_error(e) from e

    async def _execute_sql(self, sql: psycopg2.sql.Composable, fetch_result: bool = True) -> Optional[JsonLiteral]:
        try:
            async with self.endpoint.db_pool.acquire() as connection:
                async with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    await self._restore_session_on_cursor(cursor)
                    return await self._execute_sql_on_cursor(cursor, sql, fetch_result)

        except psycopg2.Error as e:
            raise client_leakable_error_from_psycopg2_error(e) from e

    async def _execute_sql_on_cursor(self, cursor: Any, sql: psycopg2.sql.Composable, fetch_result: bool) -> Optional[JsonLiteral]:
        if fetch_result:
            sql = psycopg2.sql.SQL("WITH results AS ({}) SELECT COALESCE(jsonb_agg(to_jsonb(results)), '[]'::jsonb)::text AS result FROM results").format(sql)

        await cursor.execute(sql)

        if fetch_result:
            return JsonLiteral((await cursor.fetchall())[0]['result'])

        return None

    async def _restore_session_on_cursor(self, cursor: Any) -> None:
        restore_session_sql = psycopg2.sql.SQL("SELECT wspg_private.restore_session({})").format(
            psycopg2.sql.Literal(psycopg2.extras.Json(self.pg_session_data)))

        await cursor.execute(restore_session_sql)


class SessionLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):  # type: ignore
        template = "[{path} {remote_address}] {msg}"

        session = self.extra['session']

        msg = template.format(
            path=session.endpoint.path,
            remote_address=session.remote_address,
            msg=msg)
        return msg, kwargs


def extract_wspg_msg_relation_sql(wspg_msg: Dict[str, Any], endpoint) -> psycopg2.sql.Composable:
    schema = wspg_msg.get('schema')

    if not isinstance(schema, str) or not schema:
        raise ClientLeakableError("schema must be a string")

    verify_schema_is_acceptable(schema, endpoint)

    schema_identifier = psycopg2.sql.Identifier(schema)

    relation = wspg_msg.get('relation')

    if not isinstance(relation, str) or not relation:
        raise ClientLeakableError("relation must be a string")

    relation_identifier = psycopg2.sql.Identifier(relation)

    return psycopg2.sql.SQL("{}.{}").format(schema_identifier, relation_identifier)


def extract_wspg_msg_function_call_sql(wspg_msg: Dict[str, Any], endpoint) -> psycopg2.sql.Composable:
    schema = wspg_msg.get('schema')
    if not isinstance(schema, str) or not schema:
        raise ClientLeakableError("schema must be a string")

    verify_schema_is_acceptable(schema, endpoint)

    schema_identifier = psycopg2.sql.Identifier(schema)

    function = wspg_msg.get('function')
    if not isinstance(function, dict):
        raise ClientLeakableError("function must be a dictionary")

    function_name = function.get('name')
    if not isinstance(function_name, str) or not function_name:
        raise ClientLeakableError("function name must be a string")

    function_name_identifier = psycopg2.sql.Identifier(function_name)

    function_arguments = function.get('arguments')
    if function_arguments is None:
        function_arguments = []

    if not isinstance(function_arguments, list):
        raise ClientLeakableError("function arguments must be a list or null")

    argument_literals = [psycopg2.sql.Literal(argument) for argument in function_arguments]

    arguments_sql = psycopg2.sql.SQL(", ").join(argument_literals)

    return psycopg2.sql.SQL("{}.{}({})").format(schema_identifier, function_name_identifier, arguments_sql)


def verify_schema_is_acceptable(schema, endpoint):
    if schema not in endpoint.acceptable_schemas:
        raise ClientLeakableError("schema not in list of acceptable schemas")


def extract_wspg_msg_query_rules(wspg_msg: Dict[str, Any]) -> Optional[QueryRulesRuleSetParser]:
    query_rules = wspg_msg.get('query-rules')

    if query_rules is None:
        return None

    try:
        query_rules_parser = QueryRulesRuleSetParser(query_rules)
    except jquery_querybuilder_psycopg2.ParseError as e:
        raise ClientLeakableError("Failed to parse query-rules: {}".format(e))

    return query_rules_parser


def extract_wspg_msg_returning_columns(wspg_msg: Dict[str, Any]) -> Optional[List[str]]:
    returning_columns = wspg_msg.get('returning-columns')

    if returning_columns is None:
        return None

    if not isinstance(returning_columns, list):
        raise ClientLeakableError("returning-columns must be a list or null")

    for item in returning_columns:
        if not isinstance(item, str):
            raise ClientLeakableError("returning-columns list items must be strings")

    return returning_columns


def extract_wspg_msg_order(wspg_msg: Dict[str, Any]) -> Optional[List[Dict[str, str]]]:
    order = wspg_msg.get('order')

    if order is None:
        return None

    if not isinstance(order, list):
        raise ClientLeakableError("order must be a list or null")

    if len(order) < 1:
        raise ClientLeakableError("order list must not be empty")

    for item in order:
        if not isinstance(item, dict):
            raise ClientLeakableError("order list items must be dictionaries")

        item_column = item.get('column')
        if not isinstance(item_column, str) or not item_column:
            raise ClientLeakableError("column must be a string")

        item_direction = item.get('direction')
        if item_direction is None:
            item['direction'] = 'ascending'
        else:
            if not isinstance(item_direction, str) or not item_direction:
                raise ClientLeakableError("direction must be a string or null")

            if item_direction not in ('ascending', 'descending'):
                raise ClientLeakableError("direction must be one of \"ascending\", \"descending\"")

    return order


def extract_wspg_msg_limit(wspg_msg: Dict[str, Any]) -> Optional[int]:
    limit = wspg_msg.get('limit')

    if limit is None:
        return None

    if not isinstance(limit, int):
        raise ClientLeakableError("limit must be an integer or null")

    if limit < 1:
        raise ClientLeakableError("limit must be a non-zero positive integer")

    return limit


def extract_wspg_msg_slice(wspg_msg: Dict[str, Any]) -> Optional[Dict]:
    _slice = wspg_msg.get('slice')

    if _slice is None:
        return None

    if not isinstance(_slice, dict):
        raise ClientLeakableError("slice must be a dictionary or null")

    relative_to = _slice.get("relative-to")

    if relative_to is not None and not isinstance(relative_to, dict):
        raise ClientLeakableError("slice relative-to must be a dictionary or null")

    direction = _slice.get("direction")
    if direction is None:
        _slice['direction'] = 'later'
    else:
        if not isinstance(direction, str) or not direction:
            raise ClientLeakableError("slice direction must be a string or null")

        if direction not in ('earlier', 'later'):
            raise ClientLeakableError("direction must be one of \"earlier\", \"later\"")

        if direction == "earlier" and relative_to is None:
            raise ClientLeakableError("relative-to must be set when direction is \"earlier\"")

    return _slice


def extract_wspg_msg_rows(wspg_msg: Dict[str, Any]) -> List[Dict]:
    rows = wspg_msg.get('rows')

    if not isinstance(rows, list):
        raise ClientLeakableError("rows must be a list")

    if len(rows) < 1:
        raise ClientLeakableError("rows list must not be empty")

    for item in rows:
        if not isinstance(item, dict):
            raise ClientLeakableError("rows list items must be dictionaries")

        if len(item) < 1:
            raise ClientLeakableError("row dictionary must not be empty")

    return rows


def extract_wspg_msg_updates(wspg_msg: Dict[str, Any]) -> Dict:
    updates = wspg_msg.get('updates')

    if not isinstance(updates, dict):
        raise ClientLeakableError("updates must be a dictionary")

    if len(updates) < 1:
        raise ClientLeakableError("updates must not be empty")

    return updates


def extract_wspg_msg_channel(wspg_msg: Dict[str, Any]) -> str:
    channel = wspg_msg.get('channel')

    if not isinstance(channel, str) or not channel:
        raise ClientLeakableError("channel must be a string")

    return channel


def extract_wspg_msg_issuer(wspg_msg: Dict[str, Any]) -> str:
    issuer = wspg_msg.get('issuer')

    if not isinstance(issuer, str) or not issuer:
        raise ClientLeakableError("issuer must be a string")

    return issuer


def extract_wspg_msg_token(wspg_msg: Dict[str, Any]) -> Optional[str]:
    token = wspg_msg.get('token')

    if token is None:
        return None

    if not isinstance(token, str) or not token:
        raise ClientLeakableError("token must be a string or null")

    return token


def extract_wspg_msg_types(wspg_msg: Dict[str, Any]) -> List[str]:
    types = wspg_msg.get('types')

    if not isinstance(types, list):
        raise ClientLeakableError("types must be a list")

    for _type in types:
        if not isinstance(_type, str) or not _type:
            raise ClientLeakableError("types list items must be strings")

    return types


def extract_wspg_msg_value(wspg_msg: Dict[str, Any]) -> str:
    value = wspg_msg.get('value')

    if not isinstance(value, str):
        raise ClientLeakableError("value must be a string")

    return value


@contextlib.contextmanager
def call_timing_logger(logger, prefix):  # type: ignore
    start_time = time.time()
    try:
        yield
    finally:
        call_time = time.time() - start_time
        msg = "{} took {:.6f}s"
        logger.debug(msg.format(prefix, call_time))


# Generate result like:
# id > 2 or (id = 2 and (false))
# id > 2 or (id = 2 and (a > 19 or (a = 19 and (false))))
# id > 2 or (id = 2 and (a > 19 or (a = 19 and (b > 99 or (b=99 and (false))))))
def build_slice_condition(_slice, order):
    pre = []
    post = []

    for item in order:
        if item['column'] not in _slice['relative-to']:
            msg = "slice relative-to must contain column {}"
            raise ClientLeakableError(msg.format(item['column']))

        column = psycopg2.sql.Identifier(item['column'])
        value = _slice['relative-to'][item['column']]

        if item['direction'] == 'ascending':
            unequality_operator = ">"
        else:
            unequality_operator = "<"

        if _slice['direction'] == 'earlier':
            if unequality_operator == ">":
                unequality_operator = "<"
            else:
                unequality_operator = ">"

        if value is None:
            equality_condition = psycopg2.sql.SQL("{} IS NULL").format(column)
            if unequality_operator == "<":
                unequality_condition = psycopg2.sql.SQL("{} IS NOT NULL").format(column)
            else:
                unequality_condition = psycopg2.sql.SQL("FALSE")  # nothing is greater than NULL
        else:
            value_literal = psycopg2.sql.Literal(value)
            equality_condition = psycopg2.sql.SQL("{} = {}").format(column, value_literal)
            if unequality_operator == "<":
                unequality_condition = psycopg2.sql.SQL("{} < {}").format(column, value_literal)
            else:
                unequality_condition = psycopg2.sql.SQL("COALESCE({} > {}, TRUE)").format(column, value_literal)

        pre.append(psycopg2.sql.SQL("({} OR ({} AND ").format(unequality_condition, equality_condition))
        post.append(psycopg2.sql.SQL("))"))

    conditions = []
    conditions.extend(pre)
    conditions.append(psycopg2.sql.SQL("FALSE"))
    conditions.extend(post)

    return psycopg2.sql.Composed(conditions)


def client_leakable_error_from_psycopg2_error(e):
    if e.diag.message_primary:
        db_msg = e.diag.message_primary
        if e.diag.message_detail:
            db_msg += ": " + e.diag.message_detail
    else:
        db_msg = str(e).splitlines()[0]

    diagnostics = {}

    for attribute in dir(e.diag):
        if attribute.startswith("_"):
            continue

        diagnostics[attribute] = getattr(e.diag, attribute)

    try:
        sqlstate_name = psycopg2.errorcodes.lookup(e.diag.sqlstate)
    except KeyError:
        sqlstate_name = None

    diagnostics['sqlstate-name'] = sqlstate_name

    return ClientLeakableError(db_msg, {'postgresql': diagnostics})
