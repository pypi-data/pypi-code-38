# Copyright © 2018-2019 Roel van der Goot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Module application provides class Application."""

from asyncio import sleep

from aiohttp import web
from asyncpg.exceptions import (
    CannotConnectNowError,
    ConnectionDoesNotExistError,
)
from asyncpg.pool import create_pool

from ajsonapi.exceptions import ErrorsException
from ajsonapi.init import init
from ajsonapi.requests import (
    parse_collection_document_query,
    parse_collection_query,
    parse_object_document_query,
    parse_object_query,
    parse_related_resource_query,
    parse_relationship_document_query,
    parse_relationship_query,
)
from ajsonapi.responses import errors_response
from ajsonapi.table import create_all as table_create_all
from ajsonapi.uri.relationship import parse as parse_relationship


class Application:
    """JSON API web server.

    Default routes are derived from the specified object model.
    """

    def __init__(self, *args, **kwargs):
        self.app = web.Application(*args, **kwargs)
        self.pool = None

    async def connect_database(self, database):
        """Connects to the database.

        Args:
            database (str): URL to Postgres database. For example:
                'postgresql://user:password@localhost:5432/db'.

        Raises:
            NotImplementedError in case database doesn't start with
                'postgresql:'.
        """
        if not database.startswith('postgresql:'):
            raise NotImplementedError('Only postgres is currently supported.')
        while self.pool is None:
            try:
                self.pool = await create_pool(database)
            except (CannotConnectNowError,
                    ConnectionDoesNotExistError):  # pragma: no cover
                self.pool = None
                await sleep(.1)
        init(self.pool)

    async def disconnect_database(self):
        """Disconnects from the database."""
        await self.pool.close()

    async def create_tables(self):
        """Creates all tables in the database."""
        await table_create_all()

    def add_json_api_routes(self):
        """Add JSON API routes to the web application."""

        path = r'/{collection:[^/]*}'
        self.app.add_routes([
            web.get(path, self.get_collection),
            web.post(path, self.post_collection),
        ])

        path = r'/{collection:[^/]*}/{id:[0-9A-Fa-f-]*}'
        self.app.add_routes([
            web.get(path, self.get_object),
            web.delete(path, self.delete_object),
            web.patch(path, self.patch_object),
        ])

        path = (r'/{collection:[^/]*}/{id:[0-9A-Fa-f-]*}/'
                r'relationships/{relationship:[^/]*}')
        self.app.add_routes([
            web.get(path, self.get_relationship),
            web.patch(path, self.patch_relationship),
            web.post(path, self.post_relationship),
            web.delete(path, self.delete_relationship),
            web.put(path, self.put_relationship),
        ])

        path = (r'/{collection:[^/]*}/{id:[0-9A-Fa-f-]*}/'
                r'{related_resource:[^/]*}')
        self.app.add_routes([
            web.get(path, self.get_related_resource),
        ])

    async def get_collection(self, request):
        """Entry point for GET /{collection} requests.

        Args:
            request: The GET /{collection} request.
        """

        try:
            collection, query = parse_collection_query(request,
                                                       allow_include=True,
                                                       allow_fields=True,
                                                       allow_filter=True,
                                                       allow_sort=True)
            return await collection.get(query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def post_collection(self, request):
        """Entry point for GET /{collection} requests.

        Args:
            request: The POST /{collection} request.
        """

        try:
            collection, data, query = await parse_collection_document_query(
                request)
            return await collection.post(data, query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def get_object(self, request):
        """Entry point for GET /{collection}/{id} requests.

        Args:
            request: The GET /{collection}/{id} request.
        """
        try:
            object_, query = await parse_object_query(request,
                                                      allow_include=True,
                                                      allow_fields=True)
            return await object_.get(query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def delete_object(self, request):
        """Entry point for DELETE /{collection}/{id} requests.

        Args:
            request: The DELETE /{collection}/{id} request.
        """
        try:
            object_, _ = await parse_object_query(request)
            return await object_.delete()
        except ErrorsException as err:
            return errors_response(err.errors)

    async def patch_object(self, request):
        """Entry point for DELETE /{collection}/{id} requests.

        Args:
            request: The DELETE /{collection}/{id} request.
        """
        try:
            object_, data, query = await parse_object_document_query(request)
            return await object_.patch(data, query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def get_relationship(self, request):
        """Entry point for GET /{collection}/{id}/relationships/{relationship}
        requests.

        Args:
            request: The GET /{collection}/{id}/relationships/{relationship}
                request.

        Returns:
            Appropriate response for the request.
        """
        try:
            relationship, query = await parse_relationship_query(
                request, allow_include=True, allow_fields=True)
            return await relationship.get(query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def patch_relationship(self, request):
        """Entry point for PATCH
        /{collection}/{id}/relationships/{relationship} requests.

        Args:
            request: The PATCH /{collection}/{id}/relationships/{relationship}
                request.

        Returns:
            Appropriate response for the request.
        """
        try:
            relationship, data, query = await parse_relationship_document_query(
                request)
            return await relationship.patch(data, query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def post_relationship(self, request):
        """Entry point for POST
        /{collection}/{id}/relationships/{relationship} requests.

        Args:
            request: The POST /{collection}/{id}/relationships/{relationship}
                request.

        Returns:
            Appropriate response for the request.
        """
        try:
            relationship, data, query = await parse_relationship_document_query(
                request)
            return await relationship.post(data, query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def delete_relationship(self, request):
        """Entry point for DELETE
        /{collection}/{id}/relationships/{relationship} requests.

        Args:
            request: The DELETE /{collection}/{id}/relationships/{relationship}
                request.

        Returns:
            Appropriate response for the request.
        """
        try:
            relationship, data, query = await parse_relationship_document_query(
                request)
            return await relationship.delete(data, query)
        except ErrorsException as err:
            return errors_response(err.errors)

    async def put_relationship(self, request):
        """Entry point for PUT /{collection}/{id}/relationships/{relationship}
        requests.

        Args:
            request: The PUT /{collection}/{id}/relationships/{relationship}
                request.

        Returns:
            Appropriate response for the request.
        """
        relationship = parse_relationship(request)
        return relationship.put()

    async def get_related_resource(self, request):
        """Entry point for GET /{collection}/{id}/{related_resource} requests.

        Args:
            request: The GET /{collection}/{id}/{related_resource} request.

        Returns:
            Appropriate response for the request.
        """
        try:
            related, query = await parse_related_resource_query(
                request,
                allow_include=True,
                allow_fields=True,
                allow_filter=True,
                allow_sort=True)
            return await related.get(query)
        except ErrorsException as err:
            return errors_response(err.errors)
