#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax segment information
I don't really like this separation, but there are so many segment endpoints...
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class Segment(BaseAPI):
    """Beeswax Segment API class"""

    paths = ['segment']

    def __init__(self, *args, **kwargs):
        super(Segment, self).__init__(*args, **kwargs)
        self.tags = SegmentTag(self._dal)
        self.categories = SegmentCategoryAssociation(self._dal)
        self.sharing = SegmentSharing(self._dal)
        self.lookups = SegmentLookup(self._dal)
        self.updates = SegmentUpdate(self._dal)
        self.uploads = SegmentUpload(self._dal)

    def retrieve(self, segment_id, **kwargs):
        """
        :type segment_id: int
        :param dict kwargs: segment_key, segment_name, alternative_id, advertiser_id, segment_description
        """
        parameters = dict(segment_id=segment_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_id, segment_key, segment_name, alternative_id, advertiser_id, segment_description
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, segment_name, **kwargs):
        """
        :type segment_name: str
        :param dict kwargs: alternative_id, advertiser_id, segment_description, cpm_cost, ttl_days, aggregate_excludes
        """
        parameters = dict(segment_name=segment_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, segment_id, **kwargs):
        """
        :type segment_id: int
        :param dict kwargs: segment_name, alternative_id, advertiser_id, segment_description, cpm_cost,
            aggregate_excludes
        """
        parameters = dict(segment_id=segment_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class SegmentTag(BaseAPI):
    """Beeswax Segment Tag API class"""

    paths = ['segment_tag']

    def retrieve(self, segment_tag, **kwargs):
        """
        :type segment_tag: int
        :param dict kwargs: segment_name, advertiser_id, tag_type, format
        """
        parameters = dict(segment_tag=segment_tag, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_tag, segment_name, advertiser_id, tag_type, format
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class SegmentCategory(BaseAPI):
    """Beeswax Segment Category API class"""

    paths = ['segment_category']

    def __init__(self, *args, **kwargs):
        super(SegmentCategory, self).__init__(*args, **kwargs)
        self.segments = SegmentCategoryAssociation(self._dal)
        self.lookups = SegmentCategoryLookup(self._dal)
        self.sharing = SegmentCategorySharing(self._dal)

    def retrieve(self, segment_category_id, **kwargs):
        """
        :type segment_category_id: int
        :param dict kwargs: alternative_id, segment_category_key, segment_category_name, parent_category_key,
            advertiser_id
        """
        parameters = dict(segment_category_id=segment_category_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_category_id, alternative_id, segment_category_key, segment_category_name,
            parent_category_key, advertiser_id
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, segment_category_name, **kwargs):
        """
        :type segment_category_name: str
        :param dict kwargs: alternative_id, parent_category_key, advertiser_id
        """
        parameters = dict(segment_category_name=segment_category_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, segment_category_id, **kwargs):
        """
        :type segment_category_id: int
        :param dict kwargs: segment_category_name, alternativ_id, alternative_id, advertiser_id
        """
        parameters = dict(segment_category_id=segment_category_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, segment_category_id):
        """
        :type segment_category_id: int
        """
        parameters = dict(segment_category_id=segment_category_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class SegmentCategoryAssociation(BaseAPI):
    """Beeswax Segment Category Association API class"""

    paths = ['segment_category_association']

    def retrieve(self, segment_category_association_id, **kwargs):
        """
        :type segment_category_association_id: int
        :param dict kwargs: segment_category_key, segment_key
        """
        parameters = dict(segment_category_association_id=segment_category_association_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_category_association_id, segment_category_key, segment_key
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, segment_category_key, segment_key):
        """
        :type segment_category_key: int
        :type segment_key: int
        """
        parameters = dict(segment_category_key=segment_category_key, segment_key=segment_key)
        return self._call('POST', data=ujson.dumps(parameters))

    def delete(self, segment_category_association_id):
        """
        :type segment_category_association_id: int
        """
        parameters = dict(segment_category_association_id=segment_category_association_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class SegmentSharing(BaseAPI):
    """Beeswax Segment Sharing API class"""

    paths = ['segment_sharing']

    def retrieve(self, segment_sharing_id, **kwargs):
        """
        :type segment_sharing_id: int
        :param dict kwargs: segment_key, shared_account_id, active
        """
        parameters = dict(segment_sharing_id=segment_sharing_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_sharing_id, segment_key, shared_account_id, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, segment_key, shared_account_id, **kwargs):
        """
        :type segment_key: int
        :type shared_account_id: int
        :param dict kwargs: active, cpm_cost
        """
        parameters = dict(segment_key=segment_key, shared_account_id=shared_account_id, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, segment_sharing_id, **kwargs):
        """
        :type segment_sharing_id: int
        :param dict kwargs: segment_key, shared_account_id, active, cpm_cost
        """
        parameters = dict(segment_sharing_id=segment_sharing_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class SegmentCategorySharing(BaseAPI):
    """Beeswax Segment Category Sharing API class"""

    paths = ['segment_category_sharing']

    def retrieve(self, segment_category_sharing_id, **kwargs):
        """
        :type segment_category_sharing_id: int
        :param dict kwargs: segment_category_key, shared_account_id, active
        """
        parameters = dict(segment_category_sharing_id=segment_category_sharing_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_category_sharing_id, segment_category_key, shared_account_id, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, segment_category_key, shared_account_id, **kwargs):
        """
        :type segment_category_key: int
        :type shared_account_id: int
        :param dict kwargs: active, cpm_cost
        """
        parameters = dict(segment_category_key=segment_category_key, shared_account_id=shared_account_id, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, segment_category_sharing_id, **kwargs):
        """
        :type segment_category_sharing_id: int
        :param dict kwargs: segment_key, shared_account_id, active, cpm_cost
        """
        parameters = dict(segment_category_sharing_id=segment_category_sharing_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class SegmentLookup(BaseAPI):
    """Beeswax Segment Lookup API class"""

    paths = ['segment_lookup']

    def retrieve(self, segment_id, **kwargs):
        """
        :type segment_id: int
        :param dict kwargs: segment_key, segment_name, source
        """
        parameters = dict(segment_id=segment_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_id, segment_key, segment_name, source
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class SegmentCategoryLookup(BaseAPI):
    """Beeswax Segment Lookup API class"""

    paths = ['segment_category_lookup']

    def retrieve(self, segment_category_id, **kwargs):
        """
        :type segment_category_id: int
        :param dict kwargs: segment_category_key, segment_category_name, source
        """
        parameters = dict(segment_category_id=segment_category_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_category_id, segment_category_key, segment_category_name, source
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class SegmentUpload(BaseAPI):
    """Beeswax Segment Upload API class"""

    paths = ['segment_upload']

    def retrieve(self, segment_upload_id, **kwargs):
        """
        :type segment_upload_id: int
        :param dict kwargs: file_name, upload_status, upload_complete_date, create_date, update_date
        """
        parameters = dict(segment_upload_id=segment_upload_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: segment_upload_id, file_name, upload_status, upload_complete_date, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, user_id_type, **kwargs):
        """
        :type user_id_type: str
        :param dict kwargs: file_name, path_to_file, datacenter, file_format, segment_key_type, continent, overwrite,
            operation_type, segment_file_list
        """
        parameters = dict(user_id_type=user_id_type, **kwargs)
        if 'segment_file_list' in parameters:
            return self._call('POST', data=ujson.dumps(parameters))
        else:
            files = kwargs.pop('path_to_file')
            upload_request_data = self._call('POST', data=ujson.dumps(parameters))
            return self._dal.call('POST', self.paths + ['upload', upload_request_data['payload']['id']], files=files)


class SegmentUpdate(BaseAPI):
    """Beeswax Segment Update API class"""

    paths = ['segment_update']

    def create(self, user_data, **kwargs):
        """
        :type user_data: list
        :param dict kwargs: continent, segment_key_type, user_id_type
        """
        parameters = dict(user_data=user_data, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))
