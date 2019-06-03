from __future__ import absolute_import, unicode_literals

from json import dumps

__all__ = ['C8QL', 'C8QLQueryCache']

from c8.api import APIWrapper
from c8.cursor import Cursor
from c8.exceptions import (
    C8QLQueryExplainError,
    C8QLQueryValidateError,
    C8QLQueryExecuteError,
    C8QLQueryListError,
    C8QLQueryClearError,
    C8QLQueryKillError,
    C8QLFunctionCreateError,
    C8QLFunctionDeleteError,
    C8QLFunctionListError,
)
from c8.request import Request


class C8QL(APIWrapper):
    """C8QL (C8Db Query Language) API wrapper.

    :param connection: HTTP connection.
    :type connection: c8.connection.Connection
    :param executor: API executor.
    :type executor: c8.executor.Executor
    """

    def __init__(self, connection, executor):
        super(C8QL, self).__init__(connection, executor)

    def __repr__(self):
        return '<C8QL in {}>'.format(self._conn.fabric_name)

    # noinspection PyMethodMayBeStatic
    def _format_queries(self, body):
        """Format the list of queries.

        :param body: Response body.
        :type body: dict
        :return: Formatted body.
        :rtype: dict
        """
        for query in body:
            if 'bindVars' in query:
                query['bind_vars'] = query.pop('bindVars')
            if 'runTime' in query:
                query['runtime'] = query.pop('runTime')
        return body

    @property
    def cache(self):
        """Return the query cache API wrapper.

        :return: Query cache API wrapper.
        :rtype: c8.c8ql.C8QLQueryCache
        """
        return C8QLQueryCache(self._conn, self._executor)

    def explain(self, query, all_plans=False, max_plans=None, opt_rules=None):
        """Inspect the query and return its metadata without executing it.

        :param query: Query to inspect.
        :type query: str | unicode
        :param all_plans: If set to True, all possible execution plans are
            returned in the result. If set to False, only the optimal plan
            is returned.
        :type all_plans: bool
        :param max_plans: Total number of plans generated by the optimizer.
        :type max_plans: int
        :param opt_rules: List of optimizer rules.
        :type opt_rules: list
        :return: Execution plan, or plans if **all_plans** was set to True.
        :rtype: dict | list
        :raise c8.exceptions.C8QLQueryExplainError: If explain fails.
        """
        options = {'allPlans': all_plans}
        if max_plans is not None:
            options['maxNumberOfPlans'] = max_plans
        if opt_rules is not None:
            options['optimizer'] = {'rules': opt_rules}

        request = Request(
            method='post',
            endpoint='/query/explain',
            data={'query': query, 'options': options}
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryExplainError(resp, request)
            if 'plan' in resp.body:
                return resp.body['plan']
            else:
                return resp.body['plans']

        return self._execute(request, response_handler)

    def validate(self, query):
        """Parse and validate the query without executing it.

        :param query: Query to validate.
        :type query: str | unicode
        :return: Query details.
        :rtype: dict
        :raise c8.exceptions.C8QLQueryValidateError: If validation fails.
        """
        request = Request(
            method='post',
            endpoint='/query',
            data={'query': query}
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryValidateError(resp, request)
            body = resp.body
            body.pop('code', None)
            body.pop('error', None)
            if 'bindVars' in body:
                body['bind_vars'] = body.pop('bindVars')
            return body

        return self._execute(request, response_handler)

    def execute(self,
                query,
                count=False,
                bind_vars=None,
                cache=None,
                profile=None):
        """Execute the query and return the result cursor.

        :param query: Query to execute.
        :type query: str | unicode
        :param count: If set to True, the total document count is included in
            the result cursor.
        :type count: bool
        :param bind_vars: Bind variables for the query.
        :type bind_vars: dict
        :param cache: If set to True, the query cache is used. The operation
            mode of the query cache must be set to "on" or "demand".
        :type cache: bool
        :param profile: Return additional profiling details in the cursor,
            unless the query cache is used.
        :type profile: bool
        :return: Result cursor.
        :rtype: c8.cursor.Cursor
        :raise c8.exceptions.C8QLQueryExecuteError: If execute fails.
        """
        data = {'query': query, 'count': count}
        if bind_vars is not None:
            data['bindVars'] = bind_vars
        if cache is not None:
            data['cache'] = cache

        options = {}
        if profile is not None:
            options['profile'] = profile
        if options:
            data['options'] = options
        data.update(options)

        command = 'db._query({}, {}, {}).toArray()'.format(
            dumps(query),
            dumps(bind_vars),
            dumps(data),
        ) if self._is_transaction else None

        request = Request(
            method='post',
            endpoint='/cursor',
            data=data,
            command=command
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryExecuteError(resp, request)
            return Cursor(self._conn, resp.body)

        return self._execute(request, response_handler)

    def kill(self, query_id):
        """Kill a running query.

        :param query_id: Query ID.
        :type query_id: str | unicode
        :return: True if kill request was sent successfully.
        :rtype: bool
        :raise c8.exceptions.C8QLQueryKillError: If the send fails.
        """
        request = Request(
            method='delete',
            endpoint='/query/{}'.format(query_id)
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryKillError(resp, request)
            return True

        return self._execute(request, response_handler)

    def queries(self):
        """Return the currently running C8QL queries.

        :return: Running C8QL queries.
        :rtype: [dict]
        :raise c8.exceptions.C8QLQueryListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/query/current'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryListError(resp, request)
            return self._format_queries(resp.body)

        return self._execute(request, response_handler)

    def slow_queries(self):
        """Return a list of all slow C8QL queries.

        :return: Slow C8QL queries.
        :rtype: [dict]
        :raise c8.exceptions.C8QLQueryListError: If retrieval fails.
        """
        request = Request(
            method='get',
            endpoint='/query/slow'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryListError(resp, request)
            return self._format_queries(resp.body)

        return self._execute(request, response_handler)

    def clear_slow_queries(self):
        """Clear slow C8QL queries.

        :return: True if slow queries were cleared successfully.
        :rtype: bool
        :raise c8.exceptions.C8QLQueryClearError: If operation fails.
        """
        request = Request(
            method='delete',
            endpoint='/query/slow'
        )

        def response_handler(resp):
            if not resp.is_success:
                raise C8QLQueryClearError(resp, request)
            return True

        return self._execute(request, response_handler)

    


