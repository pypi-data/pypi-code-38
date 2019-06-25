# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import time
import json
import logging

from . import entity_json

from .exceptions import TimeoutWhileWaitingForRunningIndexToFinishUpdatingException
from .entitybase import EntityBase
from .utils import validate_response_is_ok

logger = logging.getLogger(__name__)


class Dataset(EntityBase):
    """
    This class represents a dataset.
    """

    def __str__(self):
        result = super().__str__()
        return result

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_entities_as_response(self, since=None, limit=None, start=None, history=True, deleted=True,
                                 accept="application/json", reverse=False, uncommitted=None,
                                 subset=None, expected_node_id=None
                                 ):
        """
        :param since: The opaque value that can be used to efficiently skip already seen entities.

        :param limit: The "limit" parameter specifies the maximum number of entities to return.
                      If this is not specified, all available entities are returned.

        :param start: The "start" parameter is a positive integer that specified how many entities to skip from the
                      start of where the "since"-parameters starts. This is far less efficient than using the
                      "since"-parameter, but it can be manually set in a gui to explore the dataset. NOTE: Clients
                      should use the "since"-parameter whenever possible.

        :param history: If this is true (the default) all entities, including replaced ones, will be returned. \
                        If this is false, only the latest version of the entities will be returned.

        :param deleted: If this is True (the default) deleted entities will also be returned. \
                        If this is False, only the non-deleted entities will be returned.

        :param accept:  The value to use in the "Accept" header

        :param reverse: If this is False (the default) entities will returned with the oldest entity first. \
                        If this is True, the newest entity will be returned first.

        :param uncommitted: If true then the response may include uncommitted entities. This is only relevant if
                        the pipe that writes to the dataset have a circuit breaker enabled. Use this for debugging
                        purposes only.

        :param subset: If specified then the specified subset expression will be used to retrive entities in
                       the dataset via a secondary index. If the index does not exist, then 404 is returned.

        :param expected_node_id: If specified then it will be sent in the the X-Expected-Node-Id request header.
        """
        url = self._connection.get_dataset_entities_url(self.id)

        params = {}
        if since is not None:
            params["since"] = since
        if limit is not None:
            params["limit"] = limit
        if start is not None:
            params["start"] = start
        if history is not None:
            params["history"] = history
        if deleted is not None:
            params["deleted"] = deleted
        if reverse is not None:
            params["reverse"] = reverse
        if uncommitted is not None:
            params["uncommitted"] = uncommitted
        if subset is not None:
            params["subset"] = subset

        headers = {"ACCEPT": accept}
        if expected_node_id is not None:
            headers["X-Expected-Node-Id"] = expected_node_id

        # The entities are streamed from the server, so we have to enable streaming here.
        response = self._connection.do_get_request(url, stream=True, params=params, headers=headers)
        validate_response_is_ok(response)
        return response

    def get_entities_as_stream(self, since=None, limit=None, start=None, history=True, deleted=True,
                               accept="application/json", reverse=False, uncommitted=None,
                               subset=None, expected_node_id=None
                               ):
        """This returns a http stream for getting the entities of this dataset. (The returned object is a file-like
        stream from the 'requests' library, i.e response.raw)
        """
        response = self.get_entities_as_response(since=since, limit=limit, start=start, history=history,
                                                 deleted=deleted, accept=accept, reverse=reverse,
                                                 uncommitted=uncommitted,
                                                 subset=subset, expected_node_id=expected_node_id
                                                 )

        return response.raw

    def get_entities(self, since=None, limit=None, start=None, history=True, deleted=True, reverse=False,
                     uncommitted=None,
                     subset=None, expected_node_id=None
                     ):
        """This returns a generator for iterating over the entities of this dataset.

        Note: If you just need the raw bytes, consider using the get_entities_as_stream() method instead. That will be
        faster.
        """
        entities_stream = self.get_entities_as_stream(since=since, limit=limit, start=start, history=history,
                                                      deleted=deleted, reverse=reverse, uncommitted=uncommitted,
                                                      subset=subset, expected_node_id=expected_node_id
                                                      )
        return entity_json.parse_json_stream(entities_stream)

    def get_entity(self, entity_id, offset=None):
        """Returns the specified entity if it exist, or None if the entity does not exist.

        :param entity_id:
        """
        url = self._connection.get_dataset_entity_url(self.id)
        params = {"entity_id": entity_id}
        if offset is not None:
            params["offset"] = offset
        response = self._connection.do_get_request(url,
                                                   allowable_response_status_codes=[200, 404],
                                                   params=params)
        if response.status_code == 404:
            # No such element.
            return None
        return entity_json.parse_entity(response.text)

    def post_entities(self, entities, force=None):
        """This posts the specified entities to the dataset."""
        url = self._connection.get_dataset_entities_url(self.id)
        params = {}
        if force is not None:
            params["force"] = force
        response = self._connection.do_post_request(url,
                                                    headers={"Content-Type": "application/json"},
                                                    data=entity_json.entities_to_json(entities),
                                                    params=params)
        validate_response_is_ok(response)
        return response.json()

    @property
    def populated(self):
        return self._raw_jsondata["runtime"].get("populated") is True

    @property
    def num_entities_in_index(self):
        return self._raw_jsondata["runtime"]["count-index-exists"]

    @property
    def num_deleted_entities_in_index(self):
        return self._raw_jsondata["runtime"]["count-index-deleted"]

    @property
    def num_undeleted_entities_in_index(self):
            return self.num_entities_in_index - self.num_deleted_entities_in_index

    @property
    def num_entities_in_log(self):
        return self._raw_jsondata["runtime"]["count-log-exists"]

    @property
    def num_deleted_entities_in_log(self):
        return self._raw_jsondata["runtime"]["count-index-deleted"]

    def get_indexes(self):
        url = self._connection.get_dataset_indexes_url(self.id)
        response = self._connection.do_get_request(url)
        indexes = response.json()
        return indexes

    def wait_for_indexes_to_finish_updating(self, timeout=60, verbosity=0):
        starttime = time.monotonic()
        time_of_last_log_output = 0
        while True:
            indexes = self.get_indexes()
            for index in indexes:
                if index["status"] not in ["up-to-date", "orphaned"]:
                    # at least one index is still being updated
                    if verbosity > 0:
                        current_time = time.monotonic()
                        if (time.monotonic() - time_of_last_log_output) > 1:
                            print("The index '%s' on the dataset '%s' has status '%s' and has "
                                  "indexed %d/%d entities." % (
                                      index["expression"],
                                      index["dataset"],
                                      index["status"],
                                      index["progress"]["indexed"],
                                      index["progress"]["total"],
                                  ))
                            time_of_last_log_output = current_time

                    break
            else:
                # all indexes are done
                return

            elapsedtime = time.monotonic() - starttime
            if elapsedtime > timeout:
                raise TimeoutWhileWaitingForRunningIndexToFinishUpdatingException(
                    "Timed out while waiting for the index to finish updating! dataset:\n%s" % (
                        self.as_json(),))
            time.sleep(0.5)

    def delete(self):
        """Deletes this dataset from the sesam-node.
        """
        url = self._connection.get_dataset_url(self.id)
        response = self._connection.do_delete_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def run_operation(self,
                      operation,
                      operation_parameters=None,
                      allowable_response_status_codes=frozenset([200])):
        """Runs the specified operation on the dataset.
        :param operation: The operation to run.
        :param operation_parameters: A dict with operation parameters.
        :param allowable_response_status_codes: The http request status code(s) to accept (defaults to 200).
        """
        url = self._connection.get_dataset_url(self.id)
        postdata = {"operation": operation}
        if operation_parameters is not None:
            postdata.update(operation_parameters)

        response = self._connection.do_post_request(url, data=postdata)

        validate_response_is_ok(response, allowable_response_status_codes=allowable_response_status_codes)
        return response.json()
