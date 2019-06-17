#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax objects
honestly i couldn't think of a good name for this file, so extenstions it is...
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class BidModifier(BaseAPI):
    """Beeswax Bid Modifier API class"""

    paths = ['bid_modifier']

    def retrieve(self, bid_modifier_id, **kwargs):
        """
        :type bid_modifier_id: int
        :param dict kwargs: advertiser_id, alternative_id, bid_modifier_name, active
        """
        parameters = dict(bid_modifier_id=bid_modifier_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: bid_modifier_id, advertiser_id, alternative_id, bid_modifier_name, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, bid_modifier_name, bid_modifier_terms, active, **kwargs):
        """
        :type bid_modifier_name: str
        :type bid_modifier_terms: str
        :type active: bool
        :param dict kwargs: advertiser_id, alternative_id, notes
        :return:
        """
        parameters = dict(
            bid_modifier_name=bid_modifier_name, bid_modifier_terms=bid_modifier_terms, active=active, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, bid_modifier_id, active, **kwargs):
        """
        :type bid_modifier_id: int
        :type active: bool
        :param dict kwargs: alternative_id, bid_modifier_name, bid_modifier_terms, notes
        """
        parameters = dict(bid_modifier_id=bid_modifier_id, active=active, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, bid_modifier_id):
        """
        :type bid_modifier_id: int
        """
        parameters = dict(bid_modifier_id=bid_modifier_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class CustomList(BaseAPI):
    """Beeswax Custom Lists API class"""

    paths = ['custom_list']

    def retrieve(self, list_id, **kwargs):
        """
        :type list_id: int
        :param dict kwargs: list_name, list_type, active, create_date, update_date
        """
        parameters = dict(list_id=list_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: list_id, list_name, list_type, active, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, list_name, list_type, **kwargs):
        """
        :type list_name: str
        :type list_type: str
        :param dict kwargs: delimiter
        """
        parameters = dict(list_name=list_name, list_type=list_type, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, list_id, **kwargs):
        """
        :type list_id: int
        :param dict kwargs: list_name, list_type, delimiter, alternative_id, notes, active
        """
        parameters = dict(list_id=list_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, custom_list_id):
        """
        :type custom_list_id: int
        """
        parameters = dict(custom_list_id=custom_list_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class ListItem(BaseAPI):
    """Beeswax List Item API class"""

    paths = ['list_item']

    def __init__(self, *args, **kwargs):
        super(ListItem, self).__init__(*args, **kwargs)
        self.bulk_uploads = ListItemsBulkUpload(self._dal)

    def retrieve(self, list_item_id, **kwargs):
        """
        :type list_item_id: int
        :param dict kwargs: list_id, list_item, active
        """
        parameters = dict(list_item_id=list_item_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: list_item_id, list_id, list_item, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, list_id, list_item, **kwargs):
        """
        :type list_id: int
        :type list_item: int
        :param dict kwargs: value, active
        """
        parameters = dict(list_id=list_id, list_item=list_item, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, list_item_id, **kwargs):
        """
        :type list_item_id: int
        :param dict kwargs: value, active
        """
        parameters = dict(list_item_id=list_item_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, list_item_id, list_id):
        """
        :type list_item_id: int
        :type list_id: int
        """
        parameters = dict(list_item_id=list_item_id, list_id=list_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class ListItemsBulkUpload(BaseAPI):
    """Beeswax List Items Bulk Upload API class"""

    paths = ['list_item_bulk']

    def create(self, list_id, list_items=None, file_path=None):
        assert list_items is not None or file_path is not None, 'Must set either list_items or file_path.'
        if list_items:
            parameters = dict(list_id=list_id, list_items=list_items)
            return self._call('POST', data=ujson.dumps(parameters))
        else:
            return self._dal.call('POST', self.paths + ['upload', list_id], files=file_path)


class NativeOffer(BaseAPI):
    """Beeswax Native Offer API class"""

    paths = ['native_offer']

    def retrieve(self, native_offer_id, advertiser_id, native_offer_name, **kwargs):
        """
        :type native_offer_id: int
        :type advertiser_id: int
        :type native_offer_name: str
        :param dict kwargs: alternative_id, icon_asset_id, logo_asset_id, active
        """
        parameters = dict(native_offer_id=native_offer_id, advertiser_id=advertiser_id,
                          native_offer_name=native_offer_name, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def create(self, advertiser_id, native_offer_name, *kwargs):
        """
        :type advertiser_id: int
        :type native_offer_name: str
        :param dict kwargs: alternative_id, creative_template_id, icon_asset_id, logo_asset_id, title_short,
            title_long, description_short, description_long, call_to_action, sponsored, store, likes, downloads,
            notes, active, phone, address, display_url, star_rating, price, sale_price, currency
        """
        parameters = dict(advertiser_id=advertiser_id, native_offer_name=native_offer_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, native_offer_id, advertiser_id, native_offer_name, **kwargs):
        """
        :param native_offer_id: int
        :param advertiser_id: int
        :param native_offer_name: str
        :param dict kwargs: alternative_id, creative_template_id, icon_asset_id, logo_asset_id, title_short,
            title_long, description_short, description_long, call_to_action, sponsored, store, likes, downloads,
            notes, active, phone, address, display_url, star_rating, price, sale_price, currency
        """
        parameters = dict(native_offer_id=native_offer_id, advertiser_id=advertiser_id,
                          native_offer_name=native_offer_name, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class PushQueue(BaseAPI):
    """Beeswax Push Queue API class"""

    paths = ['push_queue']

    def retrieve(self, push_id, **kwargs):
        """
        :type push_id: int
        :param dict kwargs: object_id, object_type, action, push_request_date, push_status, push_complete_date,
            update_date
        """
        parameters = dict(push_id=push_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: push_id, object_id, object_type, action, push_request_date, push_status,
            push_complete_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class Report(BaseAPI):
    """Beeswax Report API class"""

    paths = ['report_save']

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.queues = ReportQueue(self._dal)

    def retrieve(self, report_save_id, **kwargs):
        """
        :type report_save_id: int
        :param dict kwargs: report_name, report_id, advertiser_id, user_id, frequency, active, create_date, update_date
        """
        parameters = dict(report_save_id=report_save_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: report_save_id, report_name, report_id, advertiser_id, user_id, frequency, active,
            create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, report_name, report_id, **kwargs):
        """

        :type report_name: str
        :type report_id: int
        :param dict kwargs: request_details, report_format, advertiser_id, user_id, frequency, email_to, email_cc,
            active
        """
        parameters = dict(report_id=report_id, report_name=report_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, report_save_id, **kwargs):
        """
        :type report_save_id: int
        :param dict kwargs: report_name, report_id, request_details, report_format, advertiser_id, user_id, frequency,
            email_to, email_cc, active
        """
        parameters = dict(report_save_id=report_save_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, report_save_id):
        """
        :type report_save_id: int
        """
        parameters = dict(report_save_id=report_save_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class ReportQueue(BaseAPI):
    """Beeswax Report Queue API class"""

    paths = ['report_queue']

    def retrieve(self, report_queue_id):
        """
        :type report_queue_id: int
        """
        parameters = dict(report_queue_id=report_queue_id)
        return self._call('GET', data=ujson.dumps(parameters))

    def create(self, report_id, **kwargs):
        """

        :type report_id: int
        :param dict kwargs: report_name, request_details, report_format
        """
        parameters = dict(report_id=report_id, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))


class Strategy(BaseAPI):
    """Beeswax Segment Update API class"""

    paths = ['strategy']

    def retrieve(self, strategy_id, **kwargs):
        """
        :type strategy_id: int
        :param dict kwargs: line_item_type_id, strategy_name, active, default_strategy, create_date, update_date
        """
        parameters = dict(strategy_id=strategy_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: strategy_id, line_item_type_id, strategy_name, active, default_strategy, create_date,
            update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class TargetingTemplate(BaseAPI):
    """Beeswax Targeting Template API class"""

    paths = ['targeting_template']

    def retrieve(self, targeting_template_id, **kwargs):
        """
        :type targeting_template_id: int
        :param dict kwargs: template_name, alternative_id, strategy_id, active, create_date, update_date
        """
        parameters = dict(targeting_template_id=targeting_template_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: targeting_template_id, template_name, alternative_id, strategy_id, active, create_date,
            update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, template_name, **kwargs):
        """
        :type template_name: str
        :param dict kwargs: alternative_id, strategy_id, targeting, active
        """
        parameters = dict(template_name=template_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, targeting_template_id, **kwargs):
        """
        :type targeting_template_id: int
        :param dict kwargs: template_name, alternative_id, strategy_id, targeting, active
        """
        parameters = dict(targeting_template_id=targeting_template_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, targeting_template_id):
        """
        :type targeting_template_id: int
        """
        parameters = dict(targeting_template_id=targeting_template_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class Vendor(BaseAPI):
    """Beeswax Vendor API class"""

    paths = ['vendor']

    def __init__(self, *args, **kwargs):
        super(Vendor, self).__init__(*args, **kwargs)
        self.fees = VendorFee(self._dal)

    def retrieve(self, vendor_id, **kwargs):
        """
        :type vendor_id: int
        :param dict kwargs: vendor_name, global, create_date, update_date
        """
        parameters = dict(vendor_id=vendor_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: vendor_id, vendor_name, global, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, vendor_name, **kwargs):
        """
        :type vendor_name: str
        :param dict kwargs: fee_type, fee_amount, currency, global
        :return:
        """
        parameters = dict(vendor_name=vendor_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, vendor_id, **kwargs):
        """
        :type vendor_id: int
        :param dict kwargs: vendor_name, fee_type, fee_amount, global
        """
        parameters = dict(vendor_id=vendor_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, vendor_id):
        """
        :type vendor_id: int
        """
        parameters = dict(vendor_id=vendor_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class VendorFee(BaseAPI):
    """Beeswax Vendor Fee API class"""

    paths = ['vendor_fee']

    def retrieve(self, vendor_fee_id, **kwargs):
        """
        :type vendor_fee_id: int
        :param dict kwargs: vendor_id, vendor_fee_name, object_id, object_type, create_date, update_date
        """
        parameters = dict(vendor_fee_id=vendor_fee_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: vendor_fee_id, vendor_id, vendor_fee_name, object_id, object_type, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, vendor_id, object_id, object_type, **kwargs):
        """
        :type vendor_id: int
        :type object_id: int
        :type object_type: int
        :param dict kwargs: vendor_fee_name, fee_type, fee_amount, currency
        """
        parameters = dict(vendor_id=vendor_id, object_id=object_id, object_type=object_type, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, vendor_fee_id, **kwargs):
        """
        :type vendor_fee_id: int
        :param dict kwargs: vendor_fee_name, fee_type, fee_amount
        """
        parameters = dict(vendor_fee_id=vendor_fee_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, vendor_fee_id):
        """
        :type vendor_fee_id: int
        """
        parameters = dict(vendor_fee_id=vendor_fee_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class Misc(BaseAPI):
    """Beeswax Misc Endpoint API class"""

    paths = []  # custom endpoints so no common routing

    def resend_user_email(self, **kwargs):
        """
        :param dict kwargs: user_id, email
        """
        return self._dal.call('POST', ['resend_user_email'], data=ujson.dumps(kwargs))

    def search(self, **kwargs):
        """
        :param dict kwargs: object_id, object_type, object_name
        """
        return self._dal.call('GET', ['search'], data=ujson.dumps(kwargs))

    def user_lookup(self, **kwargs):
        return self._dal.call('GET', ['user_lookup'], data=ujson.dumps(kwargs))

    def view(self, view_name, **kwargs):
        """
        :type view_name: str
        """
        parameters = dict(view_name=view_name, **kwargs)
        return self._dal.call('GET', ['view'], data=ujson.dumps(parameters))

    def view_list(self, view_name, **kwargs):
        """
        :type view_name: str
        """
        parameters = dict(view_name=view_name, **kwargs)
        return self._dal.call('GET', ['view'], data=ujson.dumps(parameters))
