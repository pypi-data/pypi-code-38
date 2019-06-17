"""
Introduction
------------
Cursor objects are return by the Collection.query_ API.
A cursor simply binds the query to a particular collection and the
query is not executed server side until the application starts to fetch
results from the cursor.

.. note:: Cursors are never instantiated directly by the application \
and are always instantiated by Collection ``query()`` APIs.

Fetch all results
-----------------

Use the cursor's results() method to fetch all the results of the query
in one shot::

    results = mycollection.query(q).results()

The above technique will work well, if the number of results returned by the
query is limited, say because it employs a LIMIT clause.

For queries, that return a large number of results, please use the cursor
iterators as described below.

Iterators with automatic pagination
-----------------------------------

Cursor objects are iterables, so you can do something like::

    results = mycollection.query(q)
    for r in results:
        print(r)

Cursor objects support seamless automatic pagination to iterate over large
result sets. The cursor iterator will fetch and buffer a small portion of the
results and as the iterator reaches the end of the current batch of buffered
results, it will automatically issue the query with the appropriate pagination
parameters to buffer the next batch and seamlessly continue results iteration.

The default cursor iterator uses a batch size of 10,000. You can create a cursor
iterator with a different batch size by using the ``iter()`` method.

Example using the default cursor iterator::

    results = mycollection.query(q)
    for r in results:
        print(r)


Example using a custom cursor iterator with batch size 200::

    results = mycollection.query(q)
    for r in results.iter(200):
        print(r)

.. automethod:: rockset.Cursor.iter()

Async requests
--------------

Cursors support asyncio.Future to schedule and run queries concurrently
along with other async events in your application.

One can create an asyncio.Future from a cursor object using the
``Cursor.async_request()`` method. These futures are not scheduled in
any async threads and the application have to schedule them in an asyncio
event loop. Once the futures are scheduled and run to completion, then
the results of their respective queries can be accessed by calling
future.result(). The return value of future.result() will be identical
to calling Cursor.results() API on the original query.

For example::

    jims_future = people.query(F["first_name"] == "Jim").async_request()
    sfmerch_future = merchants.query(F["zipcode"] == "94107").async_request()

    # can schedule these asyncio.futures along with other futures
    # issue both queries concurrently and block until both of them finish
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(jims_future, sfmerch_future))

    all_jims = jims_future.result()
    all_sfmerchants = sfmerch_future.result()

Even if an future was originally issued by an async_requst() API call,
one can still call the blocking Cursor.results() API to fetch the results
synchronously. Cursor.results() will schedule the future, block until the
future finishes execution and then will return those results. A subsequent
future.result() call will return the query results immediately.

For example::

    jims_cursor = people.query(F["first_name"] == "Jim")
    jims_future = jims_cursor.async_request()

    # do a blocking results() will block on the future behind the scenes
    results = jims_cursor.results()

    # this will return immeidately without incurring any server round-trip
    results2 = jims_future.result()


.. automethod:: rockset.Cursor.async_request()

"""

from rockset.exception import ServerError
from rockset.query import LimitQuery, SubQuery
from rockset.swagger_client.api.queries_api import QueriesApi
from rockset.swagger_client.models.query_request import QueryRequest
from rockset.swagger_client.models.query_response import QueryResponse
import asyncio


class Cursor(object):
    """ Fetch the results of a query executed against a collection
    """

    def __init__(self, q=None, client=None):
        self.query = q
        self.client = client
        self.all_results = None
        self.future = None

    def _run(self, limit=None, skip=0):
        if self.all_results is not None:
            start = skip
            if limit is None:
                stop = None
            else:
                stop = skip + limit
            return self.all_results[start:stop]
        return self._run_query(limit, skip)

    def _run_query(self, limit=None, skip=0):
        # add limit, offset to query if required
        query = self.query
        if limit is not None:
            query = LimitQuery(
                    limit=limit,
                    skip=skip,
                    child=SubQuery(query, alias='subq')
                )

        # build the query request object
        qo = {}
        (sqltxt, params) = query.sql()
        qo = {'query': sqltxt, 'parameters': params.sqlparams()}

        # execute the query
        req = QueryRequest(sql=qo)
        results = QueriesApi(self.client).query(req)
        if not isinstance(results, QueryResponse):
            raise ServerError(
                message='invalid return message (type={} results={})'.
                format(type(results), results)
            )
        return results.get('results')

    def __iter__(self):
        return self.iter()

    def __str__(self):
        return str(self.results())

    def __getitem__(self, key):
        return self.results()[key]

    def iter(self, batch=10000):
        """ Returns an iterator that does seamless automatic pagination
        behind the scenes while fetching no more than the specified
        batch size number of results at a time.

        Args:
            batch (int): maximum number of results fetched at a time

        Returns:
            Iterator Object: Iterator that will return all the results with \
seamless automatic pagination
        """
        if batch <= 0:
            raise ValueError(
                'invalid cursor iterator batchsize. "{}" is not '
                'a positive integer.'.format(batch)
            )

        skip = 0
        while True:
            results = self._run(batch, skip)
            for r in results:
                yield r
            if ((batch is None) or (batch > len(results))):
                break
            skip += batch

    def results(self):
        """ Execute the query and fetch all the results in one shot.

        Returns:
            Array of dicts: All the query result documents
        """
        if self.all_results is None:
            self.all_results = self._run()

        return self.all_results

    def async_request(self):
        """ Returns an asyncio.Future object that can be scheduled in an
        asyncio event loop. Once scheduled and run to completion, the results
        can be fetched via the future.result() API. The return value of
        future.result() will be the same as the return value of Cursor.results()

        Returns:
            asyncio.Future: Returns a Future object that can be scheduled
            in an asyncio event loop and future.result() will hold the same
            return value as Cursor.results()
        """
        if self.future is not None:
            return self.future
        self.future = asyncio.Future()
        asyncio.ensure_future(self._issue())
        return self.future

    async def _issue(self):
        self.all_results = self._run()
        self.future.set_result(self.all_results)


__all__ = [
    'Cursor',
]
