# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import copy
import io
import json
import logging
import pprint

from .entity_json import parse_json_stream
from .utils import validate_response_is_ok

logger = logging.getLogger(__name__)


class EntityBase:
    """
    This is the common baseclass for all the classes that represents various server-side objects (Pipe, System,
    Dataset, etc)
    """
    def __init__(self, connection, raw_jsondata):
        self._connection = connection
        self._raw_jsondata = {} # we initially set this to an empty dict since it is used by the __repr__()-method.
        if raw_jsondata is None:
            raise AssertionError("The raw_jsondata parameter was None! That makes no sense!")
        if not isinstance(raw_jsondata, dict):
            raise AssertionError(
                "The raw_jsondata isn't a dict! That makes no sense! type(raw_jsondata):'%s' raw_jsondata:'%s'" % (
                    type(raw_jsondata), raw_jsondata))
        self._raw_jsondata = raw_jsondata

    def update_raw_jsondata_from_url(self, url):
        """Utility-method for updating this object with new information from the specified url. This is typically
        used by a subclass when it knows that an operation has resulted in a change in the state, or when it knows
        that it needs up-to-date information (example: ScheduledTash.get_running_task())
        """
        response = self._connection.do_get_request(url)
        validate_response_is_ok(response)
        self.update_raw_jsondata(response.text)

    def update_raw_jsondata(self, new_raw_jsondata):
        if isinstance(new_raw_jsondata, str):
            new_raw_jsondata = json.loads(new_raw_jsondata)
        self._raw_jsondata = new_raw_jsondata

    def __repr__(self):
        return "%(typename)s(id=%(id)r)" % dict(
            typename=self.type,
            id=self.id,
        )

    @property
    def id(self):
        theid = self._raw_jsondata.get("_id") or self._raw_jsondata.get("id")
        if not theid:
            theid = "*no id found! Known info: %s*" % (self.get_debug_info(), )
        return theid

    @property
    def subjectidentifier(self):
        return self._raw_jsondata.get("subjectidentifier")

    @property
    def type(self):
        thetype = self._raw_jsondata.get("type")
        if thetype:
            return thetype
        return self.config.get("type", self.__class__.__name__)

    @property
    def config(self):
        return self.get_config()

    def get_config(self, do_transit_decoding=False):
        return self.as_json_object(do_transit_decoding=do_transit_decoding).get("config", {})

    def as_json(self):
        """Returns a json string representation of this object"""
        return json.dumps(self._raw_jsondata, indent=4)

    def as_json_object(self, do_transit_decoding=False):
        """Returns a json object representation of this object"""
        if do_transit_decoding:
            dummy_stream = io.BytesIO(json.dumps([self._raw_jsondata]).encode("utf-8"))
            entities = list(parse_json_stream(dummy_stream))
            assert len(entities) == 1
            jsondata_with_transit_decoded_values = entities[0]
            return jsondata_with_transit_decoded_values
        else:
            return copy.deepcopy(self._raw_jsondata)


    def get_debug_info(self):
        return "self._raw_jsondata:%s" % (pprint.pformat(self._raw_jsondata),)

    @property
    def cached_response_info(self):
        return self._raw_jsondata.get("cached_response_info")
