import stream, importlib
from stream import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model

from datetime import datetime
import os

def get_client():
    return stream.connect(
        os.environ.get('STREAMIO_KEY', '..'),
        os.environ.get('STREAMIO_SECRET', '..')
    )

def get_serializer_class(serializer_path):
    bits = serializer_path.split('.')
    class_name = bits.pop()
    module_string = (".").join(bits)
    mod = importlib.import_module(module_string)
    return getattr(mod, class_name)

class StreamObject:
    """
from example_app.models import todo
from streamio.streamio import get_client, StreamObject
item = Todo.objects.all().order_by('?').first()
StreamObject(get_client(), i).perform_action(actor="1", action="test_action")
    """

    def __init__(self, object):
        self.client = get_client()
        self.collection_name = object.collection.lower()
        self.object = object
        self.object_id = str(object.id)

    def generate_foreign_key(self, verb, is_onceoff_action = False, date_field = None):

        if is_onceoff_action == True:
            return "{}:{}".format(self.collection_name, verb)

        timestamp = datetime.now().isoformat()
        if date_field is not None:
            timestamp = getattr(self.object, date_field).isoformat()

        return "{}:{}:{}".format(
            self.collection_name,
            verb,
            timestamp
        )

    def get_to_feeds(self):
        feed_mapping = getattr(self.object, 'feed_related_mapping', None)
        to_mapping = []
        if feed_mapping is not None:
            for feed_slug, id_field in feed_mapping:
                id = getattr(self.object, id_field, None)
                if id is not None:
                    is_list = isinstance(id, list)
                    if is_list:
                        for item in id:
                            to_field = '{}:{}'.format(feed_slug, item)
                            to_mapping.append(to_field)
                    else:
                        to_field = '{}:{}'.format(feed_slug, id)
                        to_mapping.append(to_field)
        return to_mapping

    def get(self):
        return self.client.collections.get(
            self.collection_name,
            self.object_id
        )

    def perform_action(self, actor_id, verb, time = None, is_onceoff_action = False, date_field = None):
        actor_id = str(actor_id)
        user_reference = self.client.users.create_reference(actor_id)
        object_reference = self.client.collections.create_reference(
            self.collection_name,
            self.object_id
        )
        activity_id = self.generate_foreign_key(
            verb,
            is_onceoff_action=is_onceoff_action,
            date_field=date_field
        )
        activity_data = {
            "actor": user_reference,
            "verb": verb,
            "object": object_reference,
            "foreign_id": activity_id,
        }
        to_feeds = self.get_to_feeds()
        if to_feeds:
            activity_data['to'] = to_feeds

        if time is not None:
            activity_data["time"] = time

        feed = self.client.feed("user", actor_id)
        return feed.add_activity(activity_data)

    def enrich(self, serializer = None, force_update = False):

        if serializer is None:
            serializer_class_string = self.object.enrichment_serializer
            serializer = get_serializer_class(serializer_class_string)

        serialized = serializer(self.object).data
        try:
            return self.client.collections.add(
                self.collection_name,
                serialized,
                id=self.object_id
            )
        except exceptions.StreamApiException as e:
            if force_update:
                return self.client.collections.update(
                    self.collection_name,
                    self.object_id,
                    serialized
                )
            else:
                return self.get()

class StreamUser:
    """
    """

    def __init__(self, user_id):
        self.client = get_client()
        self.user_id = str(user_id)

    def get_or_create(data = {}):
        # data = {"name": "Jack", "profile_picture": "https://goo.gl/XSLLTA"}
        user = self.client.users.add(
            self.user_id,
            data,
            get_or_create=True
        )

    def perform_action(self, object, verb, time = None):
        actor_id = self.user_id
        user_reference = self.client.users.create_reference(actor_id)
        object_reference = self.client.collections.create_reference(
            object.collection,
            str(object.id)
        )
        activity_data = {
            "actor": user_reference,
            "verb": verb,
            "object": object_reference,
        }
        if time is not None:
            activity_data["time"] = time

        feed = self.client.feed("user", actor_id)
        feed.add_activity(activity_data)

    def get_feed(self, enrich=True):
        feed = self.client.feed("user", self.user_id)
        return feed.get(enrich=enrich)

    def enrich(self, data, force_update = False):
        return self.get_or_create_user(data)
        # todo: upsert
