# Copyright © 2019 Roel van der Goot
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
"""Module collection provides class GetCollectionIncludedEnvironment."""

from asyncio import Event, create_task, gather


class GetCollectionIncludedEnvironment:
    """Class GetCollectionIncludedEnvironment is the execution environment for
    the included part of a GET /{collection} response.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, collection, ids, env):
        self.collection = collection
        self.ids = ids
        self.query = env.query
        self.tasks = []
        self.connection = env.connection
        self.lock = env.lock
        self.included_by_id = {}
        self.event = Event()

    def create_tasks(self):
        """Create all tasks for querying the database to create the included
        part of a GET /{collection} response.
        """
        self.tasks = [
            create_task(self.collection.get_collection_included(self, self.ids))
        ]
        query_fields = self.query['fields']
        if self.collection in query_fields:
            self.tasks.extend([
                create_task(rel.get_collection_included(self, self.ids))
                for rel in query_fields[self.collection]
                if rel in self.collection.table.remote_relationships
            ])
        else:
            self.tasks.extend([
                create_task(rel.get_collection_included(self, self.ids))
                for rel in self.collection.table.remote_relationships
            ])

    async def run(self):
        """Executes the GET /{collection} included tasks."""
        self.create_tasks()
        await gather(*self.tasks)


class GetObjectIncludedEnvironment:
    """Class GetObjectIncludedEnvironment is the execution environment for
    the included part of a GET /{collection}/{id} response.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, object_id, collection, ids, env):
        self.object_id = object_id
        self.collection = collection
        self.ids = ids
        self.query = env.query
        self.tasks = []
        self.connection = env.connection
        self.lock = env.lock
        self.included_by_id = {}
        self.event = Event()

    def create_tasks(self):
        """Create all tasks for querying the database to create the included
        part of a GET /{collection} response.
        """
        self.tasks = [
            create_task(self.collection.get_object_included(self, self.ids))
        ]
        query_fields = self.query['fields']
        if self.collection in query_fields:
            self.tasks.extend([
                create_task(rel.get_object_included(self, self.ids))
                for rel in query_fields[self.collection]
                if rel in self.collection.table.remote_relationships
            ])
        else:
            self.tasks.extend([
                create_task(rel.get_object_included(self, self.ids))
                for rel in self.collection.table.remote_relationships
            ])

    async def run(self):
        """Executes the GET /{collection} included tasks."""
        self.create_tasks()
        await gather(*self.tasks)
