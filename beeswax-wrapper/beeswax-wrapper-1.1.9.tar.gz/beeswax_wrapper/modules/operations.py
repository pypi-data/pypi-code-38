#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax operational objects
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class Advertiser(BaseAPI):
    """Beeswax Advertiser API class"""
    paths = ['advertiser']

    def retrieve(self, advertiser_id, **kwargs):
        """
        :type advertiser_id: int
        :param dict kwargs: alternative_id, advertiser_name, create_date, update_date, pretty, time
        """
        parameters = dict(advertiser_id=advertiser_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: advertiser_id, alternative_id, advertiser_name, create_date, update_date, pretty, time
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, advertiser_name, conversion_method_id, **kwargs):
        """
        :type advertiser_name: str
        :type conversion_method_id: int
        :param dict kwargs: alternative_id, attributes, default_click_url, notes, default_continent, default_currency,
            default_creative_thumbnail_url
        """
        parameters = dict(advertiser_name=advertiser_name, conversion_method_id=conversion_method_id, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, advertiser_id, **kwargs):
        """
        :type advertiser_id: int
        :param dict kwargs: alternative_id, advertiser_name, attributes, default_click_url, default_continent,
            default_currency, default_creative_thumbnail_url
        """
        parameters = dict(advertiser_id=advertiser_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, advertiser_id):
        """
        :type advertiser_id: int
        """
        parameters = dict(advertiser_id=advertiser_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class Campaign(BaseAPI):
    """Beeswax Campaign API class"""

    paths = ['campaign']

    def retrieve(self, campaign_id, **kwargs):
        """
        :type campaign_id: int
        :param dict kwargs: advertiser_id, alternative_id, campaign_name, bid_modifier_id, active, create_date,
            update_date
        """
        parameters = dict(campaign_id=campaign_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: campaign_id, advertiser_id, alternative_id, campaign_name, bid_modifier_id, active,
            create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, advertiser_id, campaign_name, campaign_budget, budget_type,
               start_date, active, **kwargs):
        """
        :type advertiser_id: int
        :type campaign_name: str
        :type campaign_budget: float|Decimal
        :type budget_type: str
        :type start_date: datetime.datetime
        :type active: bool
        :param dict kwargs: alternative_id, daily_budget, revenue_type, revenue_amount, pacing, bid_modifier_id,
            max_bid, end_date, frequency_cap, continents, currency, notes
        """
        parameters = dict(advertiser_id=advertiser_id, campaign_name=campaign_name, campaign_budget=campaign_budget,
                          budget_type=budget_type, start_date=start_date, active=active, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, campaign_id, **kwargs):
        """
        :type campaign_id: int
        :param dict kwargs: alternative_id, campaign_name, campaign_budget, daily_budget, budget_type, revenue_type,
            revenue_amount, pacing, bid_modifier_id, max_bid, start_date, end_date, frequency_cap, continents, notes,
            active
        """
        parameters = dict(campaign_id=campaign_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, campaign_id):
        """
        :type campaign_id: int
        """
        parameters = dict(campaign_id=campaign_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class Event(BaseAPI):
    """Beeswax Event API class"""

    paths = ['event']

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.tags = EventTag(self._dal)

    def retrieve(self, event_id, **kwargs):
        """
        :type event_id: int
        :param dict kwargs: event_name, advertiser_id, event_type_id, segment_id, create_date, update_date
        """
        parameters = dict(event_id=event_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: event_id, event_name, advertiser_id, event_type_id, segment_id, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, event_name, advertiser_id, value, **kwargs):
        """
        :type event_name: str
        :type advertiser_id: int
        :type value: str
        :param dict kwargs: event_type_id, segment_id, count_unique, click_window, view_window
        """
        parameters = dict(event_name=event_name, advertiser_id=advertiser_id, value=value, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, event_id, **kwargs):
        """
        :type event_id: int
        :param dict kwargs: event_name, advertiser_id, event_type_id, segment_id, value, count_unique, click_window,
            view_window
        """
        parameters = dict(event_id=event_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, event_id):
        """
        :type event_id: int
        """
        parameters = dict(event_id=event_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class EventTag(BaseAPI):
    """Beeswax Event Tag API class"""

    paths = ['event_tag']

    def retrieve(self, event_id, **kwargs):
        """
        :type event_id: int
        :param dict kwargs: event_name, advertiser_id, event_type_id, tag_type, format
        """
        parameters = dict(event_id=event_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: event_id, event_name, advertiser_id, event_type_id, tag_type, format
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class LineItem(BaseAPI):
    """Beeswax LineItem API class"""

    paths = ['line_item']

    def __init__(self, *args, **kwargs):
        super(LineItem, self).__init__(*args, **kwargs)
        self.flights = LineItemFlight(self._dal)

    def retrieve(self, line_item_id, **kwargs):
        """
        :type line_item_id: int
        :param dict kwargs: campaign_id, advertiser_id, alternative_id, line_item_type_id, line_item_name,
            bid_modifier_id, start_date, end_date, create_date, update_date
        """
        parameters = dict(line_item_id=line_item_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: line_item_id, campaign_id, advertiser_id, alternative_id, line_item_type_id, line_item_name,
            bid_modifier_id, start_date, end_date, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, advertiser_id, line_item_type_id, line_item_name, line_item_budget, budget_type, bidding,
               start_date, active, **kwargs):
        """
        :type advertiser_id: int
        :type line_item_type_id: int
        :type line_item_name: str
        :type line_item_budget: float|Decimal
        :type budget_type: str
        :type bidding: bool
        :type start_date: datetime.datetime
        :type active: bool
        :param dict kwargs: campaign_id, alternative_id, targeting_template_id, daily_budget, revenue_type,
            revenue_amount, pacing, bid_modifier_id, max_bid, end_date, currency, frequency_cap, notes
        """
        parameters = dict(advertiser_id=advertiser_id, line_item_type_id=line_item_type_id,
                          line_item_name=line_item_name, line_item_budget=line_item_budget, budget_type=budget_type,
                          bidding=bidding, start_date=start_date, active=active, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, line_item_id, **kwargs):
        """
        :type line_item_id: int
        :param dict kwargs: campaign_id, advertiser_id, alternative_id, line_item_type_id, targeting_template_id,
            line_item_name, line_item_budget, daily_budget, budget_type, revenue_type, revenue_amount, pacing,
            bid_modifier_id, max_bid, bidding, start_date, end_date, frequency_cap, notes, active
        """
        parameters = dict(line_item_id=line_item_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, line_item_id):
        """
        :type line_item_id: int
        """
        parameters = dict(line_item_id=line_item_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class LineItemFlight(BaseAPI):
    """Beeswax LineItem Flights API class"""

    paths = ['line_item_flight']

    def retrieve(self, flight_id, **kwargs):
        """
        :type flight_id: int
        :param dict kwargs: flight_name, start_date, end_date, alternative_id, active
        """
        parameters = dict(flight_id=flight_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: flight_id, flight_name, start_date, end_date, alternative_id, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, start_date, line_item_id, **kwargs):
        """
        :type start_date: datetime.datetime
        :type line_item_id: int
        :param dict kwargs: flight_name, budget, end_date, alternative_id, notes, active
        """
        parameters = dict(start_date=start_date, line_item_id=line_item_id, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, start_date, **kwargs):
        """
        :type start_date: datetime.datetime
        :param dict kwargs: flight_id, flight_name, budget, end_date, alternative_id, notes, active
        """
        parameters = dict(start_date=start_date, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, flight_id):
        parameters = dict(flight_id=flight_id)
        return self._call('DELETE', data=ujson.dumps(parameters))
