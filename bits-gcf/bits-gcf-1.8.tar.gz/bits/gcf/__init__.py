"""Google Cloud Functions helper classes."""

import base64
import datetime
import json
# import logging

from google.cloud import datastore
from google.cloud import pubsub_v1
from google.cloud import storage


class Google(object):
    """Google Class."""

    class Datastore(object):
        """Google Datastore class."""

        def __init__(self, project=None):
            """Initialize a class instance."""
            # Instantiate a client
            self.client = datastore.Client(project)
            self.datastore = datastore

        def chunks(self, l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]

        def create_entities(self, records, kind, key='id'):
            """Return a dict of datastore entities."""
            entities = {}
            for record in records:
                # get the key value for the entity
                rid = record[key]
                # create the entity key
                entity_key = self.client.key(kind, rid)
                # create entity
                entity = self.datastore.Entity(entity_key)
                # update entity data
                for k in record:
                    entity[k] = record[k]
                # store entity in the dictionary
                entities[rid] = entity
            return entities

        def list_entities(self, kind):
            """Return a list of all entities of a given kind."""
            query = self.client.query(kind=kind)
            return list(query.fetch())

        def list_entities_dict(self, kind):
            """Return a dict of all entities of a given kind."""
            entities = {}
            entity_list = self.list_entities(kind)
            for entity in entity_list:
                entity_key = entity.key.id
                if not entity_key:
                    entity_key = entity.key.name
                entities[entity_key] = entity
            return entities

        def _get_entities_to_add(self, old, new):
            """Return al ist of entities to add."""
            add = []
            for key in new:
                if key not in old:
                    add.append(new[key])
            return add

        def _get_entities_to_delete(self, old, new):
            """Return a list of entities to delete."""
            delete = []
            for key in old:
                if key not in new:
                    delete.append(old[key].key)
            return delete

        def _get_entities_to_update(self, old, new):
            """Return a list of entities to update."""
            update = []
            for key in new:
                if key not in old:
                    continue
                if old[key] != new[key]:
                    update.append(new[key])
            return update

        def update_collection(self, kind, old, new):
            """Update a datastore collection."""
            # get entities to add
            add = self._get_entities_to_add(old, new)
            print('%s entities to add: %s' % (kind, len(add)))

            # get entities to delete
            delete = self._get_entities_to_delete(old, new)
            print('%s entities to delete: %s' % (kind, len(delete)))

            # get entities to update
            update = self._get_entities_to_update(old, new)
            print('%s entities to update: %s' % (kind, len(update)))

            # add new entities
            done = 0
            for chunk in self.chunks(add, 500):
                done += len(chunk)
                print('Adding %s [%s/%s] %s entities...' % (len(chunk), done, len(add), kind))
                self.client.put_multi(chunk)

            # delete extra entities
            done = 0
            for chunk in self.chunks(delete, 500):
                done += len(chunk)
                print('Deleting %s [%s/%s] %s entities...' % (len(chunk), done, len(delete), kind))
                self.client.delete_multi(chunk)

            # update changed entities
            done = 0
            for chunk in self.chunks(update, 500):
                done += len(chunk)
                print('Updating %s [%s/%s] %s entities...' % (len(chunk), done, len(update), kind))
                self.client.put_multi(chunk)

    class PubSub(object):
        """Google PubSub class."""

        def __init__(self):
            """Initialize a class instance."""

        def get_pubsub_message_json_data(self, data):
            """Return the json body from the pubsub message."""
            # get the body text
            body_text = None
            if 'data' in data:
                body_text = base64.b64decode(data['data']).decode('utf-8')

            # convert the text to json
            message_data = None
            if body_text:
                message_data = json.loads(body_text)

            return message_data

        def notify_pubsub(
            self,
            project,
            topic,
            bodystring,
        ):
            """Send a PubSub notifiction to a specific project/topic."""
            # format the message data
            data = (u'%s' % (bodystring)).encode('utf-8')

            # create publisher
            publisher = pubsub_v1.PublisherClient()

            # create topic path
            topic_path = publisher.topic_path(project, topic)

            # create a future to publish the message
            future = publisher.publish(topic_path, data=data)

            # log the message
            print('Published to %s as message %s' % (
                # bodyString,
                topic,
                future.result())
            )

    class Storage(object):
        """Google Storage class."""

        def __init__(self):
            """Initialize a class instance."""

        def generate_json_object_name(self, base, prefix):
            """Return an object name for a new JSON file in GCS."""
            # get current date in iso format
            now = datetime.datetime.now()
            isodate = datetime.datetime.isoformat(now)

            # create object name
            name = '%s/%s_%s.json' % (
                base,
                prefix,
                isodate,
            )

            return name

        def get_gcs_object_as_json(self, bucketname, filename):
            """Return the media from a gcs object as JSON."""
            # get file as a string
            filestring = self.get_gcs_object_as_string(bucketname, filename)

            # convert string to json
            print('Converting %s to JSON...' % (filename))
            json_data = json.loads(filestring)
            print('Successfully converted %s to JSON.' % (filename))

            return json_data

        def get_gcs_object_as_string(self, bucketname, filename):
            """Return the media from a gcs object as a string."""
            # create storage client
            storage_client = storage.Client()

            # set the bucket
            bucket = storage_client.bucket(bucketname)

            # create the blob
            blob = bucket.blob(filename)

            # download the blob
            path = 'gs://%s/%s' % (bucketname, filename)
            print('Downloading %s as string...' % (path))
            filestring = blob.download_as_string()
            print('Successfully downloaded %s as string.' % (path))

            return filestring

        def save_json_data_to_gcs_object(
            self,
            bucketname,
            dirPath,
            prefix,
            data,
        ):
            """Save a JSON object to an object in GCS."""
            print('Converting %s/%s JSON to string...' % (dirPath, prefix))
            jsonString = json.dumps(data, sort_keys=True)
            print('Successfully converted %s/%s JSON to string.' % (dirPath, prefix))

            objectName = self.save_json_string_to_gcs_object(
                bucketname,
                dirPath,
                prefix,
                jsonString,
            )
            return objectName

        def save_json_string_to_gcs_object(
            self,
            bucketname,
            dirPath,
            prefix,
            jsonstring,
        ):
            """Save a JSON string to an object in GCS."""
            # create storage client
            storage_client = storage.Client()

            # set the bucket
            bucket = storage_client.bucket(bucketname)

            # generate the object name
            objectName = self.generate_json_object_name(dirPath, prefix)

            # create the blob
            blob = bucket.blob(objectName)

            # upload the blob
            print('Uploading %s from string...' % (objectName))
            blob.upload_from_string(jsonstring, content_type='application/json')
            print('Successfully uploaded %s from string.' % (objectName))

            return objectName


class Workday(object):
    """Workday Class."""

    def get_entry_org_units(self, entry):
        """Return the orgunit string for the given Workday entry."""
        # define org unit fields from entry
        org_unit_fields = [
            'Dept_Hier_Lvl1_Name',
            'Dept_Hier_Lvl2_Name',
            'Dept_Hier_Lvl3_Name',
            'Dept_Hier_Lvl4_Name',
            'Dept_Hier_Lvl5_Name',
        ]

        # get a list of all non-empty orgunits
        org_units = []
        for field in org_unit_fields:
            ou = entry.get(field)
            if not ou:
                continue
            org_units.append(ou)

        return org_units

    def get_entry_org_unit_string(self, entry):
        """Return the orgunit string for the given Workday entry."""
        # get orgunit segments from values
        org_units_list = self.get_entry_org_units(entry)

        org_units = []
        for ou in org_units_list:
            if ou == 'The Broad Institute':
                continue
            org_units.append(ou)

        # assemble orgunit string
        org_unit = ' > '.join(org_units)

        return org_unit
