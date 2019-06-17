#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax creative information
I don't really like this separation, but there are so many creative endpoints...
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class Creative(BaseAPI):
    """Beeswax Creative API class"""

    paths = ['creative']

    def __init__(self, *args, **kwargs):
        super(Creative, self).__init__(*args, **kwargs)
        self.addons = CreativeAddon(self._dal)
        self.approvals = CreativeApproval(self._dal)
        self.assets = CreativeAsset(self._dal)
        self.bulk_upload = CreativeBulkUpload(self._dal)
        self.line_items = CreativeLineItemAssociation(self._dal)
        self.templates = CreativeTemplates(self._dal)

    def retrieve(self, creative_id, **kwargs):
        """
        :type creative_id: int
        :param dict kwargs: advertiser_id, alternative_id, creative_name, creative_type, creative_template_id, active,
            create_date, update_date
        """
        parameters = dict(creative_id=creative_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: creative_id, advertiser_id, alternative_id, creative_name, creative_type,
            creative_template_id, active, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, advertiser_id, creative_name, creative_type, secure, creative_template_id, active, **kwargs):
        """
        :type advertiser_id: int
        :type creative_name: str
        :type creative_type: str
        :type secure: bool
        :type creative_template_id: int
        :type active: bool
        :param dict kwargs: alternative_id, width, height, sizeless, click_url, creative_assets, primary_asset,
            secondary_asset, native_offer, creative_content, creative_content_tag, creative_rule_id, creative_rule_key,
            attributes, scripts, pixels, events, creative_addons, creative_thumbnail_url, start_date, end_date, notes
        """
        parameters = dict(advertiser_id=advertiser_id, creative_name=creative_name, creative_type=creative_type,
                          secure=secure, creative_template_id=creative_template_id, active=active, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, creative_id, **kwargs):
        """
        :type creative_id: int
        :param dict kwargs: advertiser_id, alternative_id, creative_name, width, height, sizeless, secure, click_url,
            creative_assets, primary_asset, secondary_asset, native_offer, creative_content, creative_content_tag,
            creative_template_id, creative_rule_id, creative_rule_key, attributes, pixels, scripts, events,
            creative_addons, creative_thumbnail_url, start_date, end_date, notes, active
        """
        parameters = dict(creative_id=creative_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, creative_id):
        """
        :type creative_id: int
        """
        parameters = dict(creative_id=creative_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class CreativeAddon(BaseAPI):
    """Beeswax Creative Add-On API class"""

    paths = ['creative_addon']

    def create(self, creative_addon_name, is_global, active, creative_addon_type, creative_addon_content, **kwargs):
        """
        :type creative_addon_name: str
        :type is_global: bool
        :type active: bool
        :type creative_addon_type: str
        :type creative_addon_content: str
        :param dict kwargs: advertiser_id, include_by_default, creative_type, secure, cpm_cost, notes
        """
        parameters = dict(creative_addon_name=creative_addon_name, creative_addon_type=creative_addon_type,
                          active=active, creative_addon_content=creative_addon_content, **kwargs)
        parameters['global'] = is_global
        return self._call('POST', data=ujson.dumps(parameters))


class CreativeApproval(BaseAPI):
    """Beeswax Creative Approval API class"""

    paths = ['creative_approval_queue']

    def __init__(self, *args, **kwargs):
        super(CreativeApproval, self).__init__(*args, **kwargs)
        self.history = CreativeApprovalHistory(self._dal)

    def retrieve(self, creative_approval_id, **kwargs):
        """
        :type creative_approval_id: int
        :param dict kwargs: creative_id, vendor_id, action, request_date, request_status, approved, update_date
        """
        parameters = dict(creative_approval_id=creative_approval_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: creative_approval_id, creative_id, vendor_id, action, request_date, request_status,
            approved, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class CreativeApprovalHistory(BaseAPI):
    """Beeswax Creative Approval History API class"""

    paths = ['creative_approval_queue_history']

    def retrieve(self, creative_approval_queue_history_id, **kwargs):
        """
        :type creative_approval_queue_history_id: int
        :param dict kwargs: creative_approval_id, creative_id, vendor_id, action, request_date, request_status,
            approved, update_date
        """
        parameters = dict(creative_approval_queue_history_id=creative_approval_queue_history_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: creative_approval_queue_history_id, creative_approval_id, creative_id, vendor_id, action,
            request_date, request_status, approved, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class CreativeAsset(BaseAPI):
    """Beeswax Creative Asset API class"""

    paths = ['creative_asset']

    def __init__(self, *args, **kwargs):
        super(CreativeAsset, self).__init__(*args, **kwargs)
        self.video = CreativeVideoAsset(self._dal)

    def retrieve(self, creative_asset_id, **kwargs):
        """
        :type creative_asset_id: int
        :param dict kwargs: advertiser_id, creative_asset_name, active, asset_type, mime_type
        """
        parameters = dict(creative_asset_id=creative_asset_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: creative_asset_id, advertiser_id, creative_asset_name, active, asset_type, mime_type
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, creative_asset_name, size_in_bytes, active, **kwargs):
        """
        :type creative_asset_name: str
        :type size_in_bytes: int
        :type active: bool
        :param dict kwargs: advertiser_id, notes
        """
        parameters = dict(creative_asset_name=creative_asset_name, size_in_bytes=size_in_bytes, active=active, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))


class CreativeVideoAsset(BaseAPI):
    """Beeswax Creative Video Asset API class"""

    paths = ['video_asset']

    def create(self, advertiser_id, creative_asset_name, size_in_bytes, active, video_encoding_profile, **kwargs):
        """
        :type advertiser_id: int
        :type creative_asset_name: str
        :type size_in_bytes: int
        :type active: bool
        :type video_encoding_profile: str
        :param dict kwargs: notes
        """
        parameters = dict(advertiser_id=advertiser_id, creative_asset_name=creative_asset_name, active=active,
                          size_in_bytes=size_in_bytes, video_encoding_profile=video_encoding_profile, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))


class CreativeBulkUpload(BaseAPI):
    """Beeswax Creative Bulk Upload API class"""

    paths = ['creative_bulk_upload']

    def retrieve(self, cbu_id, **kwargs):
        """
        :type cbu_id: int
        :param dict kwargs: advertiser_id, active, creative_template_id, create_date, update_date
        """
        parameters = dict(cbu_id=cbu_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: cbu_id, advertiser_id, active, creative_template_id, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, file_path, advertiser_id, size_in_bytes, active, bulk_type, **kwargs):
        """
        :type file_path: str?
        :type advertiser_id: int
        :type size_in_bytes: int
        :type active: bool
        :type bulk_type: str
        :param dict kwargs: creative_name_prefix, secure, click_url, creative_thumbnail_url, creative_content,
            creative_template_id, creative_rule_id, creative_rule_key, pixels, scripts, creative_addons
        """
        # todo: check this works, not sure if files should be byte packed or not...
        parameters = dict(
            advertiser_id=advertiser_id, size_in_bytes=size_in_bytes, active=active, bulk_type=bulk_type, **kwargs)
        upload_request_data = self._call('POST', data=ujson.dumps(parameters))
        return self._dal.call('POST', self.paths + ['upload', upload_request_data['payload']['id']], files=file_path)


class CreativeLineItemAssociation(BaseAPI):
    """Beeswax Creative LineItem Association API class"""

    paths = ['creative_line_item']

    def retrieve(self, cli_id, **kwargs):
        """
        :type cli_id: int
        :param dict kwargs: creative_id, line_item_id, start_date, end_date, active
        """
        parameters = dict(cli_id=cli_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: cli_id, creative_id, line_item_id, start_date, end_date, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, creative_id, line_item_id, active, **kwargs):
        """
        :type creative_id: int
        :type line_item_id: int
        :type active: bool
        :param dict kwargs: weighting, start_date, end_date
        """
        parameters = dict(creative_id=creative_id, line_item_id=line_item_id, active=active, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, cli_id, **kwargs):
        """
        :type cli_id: int
        :param dict kwargs: weighting, start_date, end_date, active
        """
        parameters = dict(cli_id=cli_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class CreativeTemplates(BaseAPI):
    """Beeswax Creative Template API class"""

    paths = ['creative_template']

    def retrieve(self, creative_template_id, **kwargs):
        """
        :type creative_template_id: int
        :param dict kwargs: creative_template_name, creative_type, is_video, is_global, active
        """
        parameters = dict(creative_template_id=creative_template_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: creative_template_id, creative_template_name, creative_type, is_video, is_global, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, creative_template_name, is_global, rendering_key, creative_template_content, active, **kwargs):
        """
        :type creative_template_name: str
        :type is_global: bool
        :type rendering_key: str
        :type creative_template_content: str
        :type active: bool
        :param dict kwargs: creative_attributes, creative_type, is_video, notes
        """
        parameters = dict(creative_template_name=creative_template_name, rendering_key=rendering_key,
                          creative_template_content=creative_template_content, active=active, **kwargs)
        parameters['global'] = is_global
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, creative_template_id, **kwargs):
        """
        :type creative_template_id: int
        :param dict kwargs: creative_template_name, global, rendering_key, creative_template_content,
            creative_attributes, is_video, notes, active
        """
        parameters = dict(creative_template_id=creative_template_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))
