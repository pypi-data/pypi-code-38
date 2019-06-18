"""
This module exposes EMS Service methods
"""
from dateutil.parser import parse
from dateutil.tz import gettz
from lxml import etree

from ems_client import EMSAPI, EMSAPIException
from ems_client.models import *


class Service(EMSAPI):
    def __init__(self):
        super(Service, self).__init__({
            'wsdl': 'Service.asmx?WSDL'
        })
        self._port = 'ServiceSoap'
        self.tzinfos = {
            'PT': gettz("America/Los Angeles"),
        }

    @staticmethod
    def _data_from_xml(data_type, xml):
        try:
            tree = etree.fromstring(xml)
        except Exception as ex:
            raise EMSAPIException('xml: %s' % str(ex))
        data = []

        for node in tree.xpath("/%s/Data" % data_type):
            datum = {}
            for element in node.xpath("*"):
                datum[element.tag] = element.text
            data.append(datum)

        return data

    def get_api_version(self):
        xml = self._request('GetAPIVersion')
        tree = etree.fromstring(xml)
        apiversion = {}
        for element in tree.xpath("/API/APIVersion/*"):
            apiversion[element.tag] = element.text

        return apiversion

    def get_statuses(self):
        data = self._data_from_xml("Statuses", self._request(
            'GetStatuses', {}))
        statuses = []
        for item in data:
            status = Status()
            status.description = item['Description']
            status.id = int(item['ID'])
            status.status_type_id = int(item['StatusTypeID'])
            status.display_on_web = (item['DisplayOnWeb'] == 'true')
            statuses.append(status)
        return statuses

    def get_event_types(self):
        data = self._data_from_xml("EventTypes", self._request(
            'GetEventTypes', {}))
        event_types = []
        for item in data:
            event_type = EventType()
            event_type.description = item['Description']
            event_type.id = int(item['ID'])
            event_type.display_on_web = (item['DisplayOnWeb'] == 'true')
            event_types.append(event_type)
        return event_types

    def get_all_rooms(self, building_id=-1):
        data = self._data_from_xml("Rooms", self._request(
            'GetAllRooms', {
                'BuildingID': building_id,
            }))
        rooms = []
        for item in data:
            room = Room()
            room.description = item['Description']
            room.dv_building = item['Building']
            room.active = True if item['Active'] == 'true' else False
            room.building_id = int(item['BuildingID'])
            room.room = item['Room']
            room.id = int(item['ID'])
            room.external_reference = item.get('ExternalReference')
            rooms.append(room)
        return rooms

    def get_buildings(self):
        data = self._data_from_xml("Buildings", self._request(
            'GetBuildings', {}))
        buildings = []
        for item in data:
            building = Building()
            building.description = item['Description']
            building.building_code = item['BuildingCode']
            building.id = int(item['ID'])
            building.time_zone_description = item['TimeZoneDescription']
            building.time_zone_abbreviation = item['TimeZoneAbbreviation']
            buildings.append(building)
        return buildings

    def get_service_order_details(self, start_date, end_date):
        data = self._data_from_xml("ServiceOrderDetails", self._request(
            'GetServiceOrderDetails', {
                'StartDate': start_date,
                'EndDate': end_date,
            }))
        details = []
        for item in data:
            detail = ServiceOrderDetail()
            detail.booking_date = parse(item['BookingDate']).date()
            detail.service_order_start_time = \
                parse(item['ServiceOrderStartTime']).time() \
                if item.get('ServiceOrderStartTime') else None
            detail.service_order_end_time = \
                parse(item['ServiceOrderEndTime']).time() \
                if item.get('ServiceOrderEndTime') else None
            detail.resource_description = item['ResourceDescription']
            detail.resource_external_reference = \
                item['ResourceExternalReference'] \
                if item['ResourceExternalReference'] is not None else ''
            detail.service_order_id = int(item['ServiceOrderID'])
            detail.booking_id = int(item['BookingID'])
            details.append(detail)
        return details

    def get_booking(self, booking_id):
        data = self._data_from_xml("Booking", self._request(
            'GetBooking', {
                'BookingID': booking_id,
            }))
        item = data.pop()
        booking = Booking()
        booking.booking_date = parse(item['BookingDate']).date()
        booking.room_description = item['RoomDescription']
        booking.time_event_start = \
            parse(item['TimeEventStart'] + ' ' + item['TimeZone'],
                  tzinfos=self.tzinfos) \
            if item.get('TimeEventStart') else None
        booking.time_event_end = \
            parse(item['TimeEventEnd'] + ' ' + item['TimeZone'],
                  tzinfos=self.tzinfos) \
            if item.get('TimeEventEnd') else None
        booking.group_name = item['GroupName']
        booking.event_name = item['EventName']
        booking.reservation_id = int(item['ReservationID'])
        booking.event_type_description = item['EventTypeDescription']
        booking.contact = item['Contact']
        booking.id = int(item['BookingID'])
        booking.building_id = int(item['BuildingID'])
        booking.time_booking_start = \
            parse(item['TimeBookingStart'] + ' ' + item['TimeZone'],
                  tzinfos=self.tzinfos) \
            if item.get('TimeBookingStart') else None
        booking.time_booking_end = \
            parse(item['TimeBookingEnd'] + ' ' + item['TimeZone'],
                  tzinfos=self.tzinfos) \
            if item.get('TimeBookingEnd') else None
        booking.time_zone = item['TimeZone']
        booking.building_code = item['BuildingCode']
        booking.dv_building = item['Building']
        booking.room_code = item['RoomCode']
        booking.dv_room = item['Room']
        booking.room_id = int(item['RoomID'])
        booking.status_id = int(item['StatusID'])
        booking.status_type_id = int(item['StatusTypeID'])
        return booking

    def get_bookings(self, start_date, end_date,
                     statuses=None, event_types=None):
        params = {
                'StartDate': start_date,
                'EndDate': end_date,
                'ViewComboRoomComponents': True,
            }
        if statuses is not None:
            params['Statuses'] = {'int': statuses}
        if event_types is not None:
            params['EventTypes'] = {'int': event_types}
        data = self._data_from_xml("Bookings", self._request(
            'GetBookings', params))
        bookings = []
        for item in data:
            booking = Booking()
            booking.booking_date = parse(item['BookingDate']).date()
            booking.room_description = item['RoomDescription']
            booking.time_event_start = \
                parse(item['TimeEventStart'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeEventStart') else None
            booking.time_event_end = \
                parse(item['TimeEventEnd'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeEventEnd') else None
            booking.group_name = item['GroupName']
            booking.event_name = item['EventName']
            booking.reservation_id = int(item['ReservationID'])
            booking.event_type_description = item['EventTypeDescription']
            booking.contact = item['Contact']
            booking.id = int(item['BookingID'])
            booking.building_id = int(item['BuildingID'])
            booking.time_booking_start = \
                parse(item['TimeBookingStart'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeBookingStart') else None
            booking.time_booking_end = \
                parse(item['TimeBookingEnd'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeBookingEnd') else None
            booking.time_zone = item['TimeZone']
            booking.building_code = item['BuildingCode']
            booking.dv_building = item['Building']
            booking.room_code = item['RoomCode']
            booking.dv_room = item['Room']
            booking.room_id = int(item['RoomID'])
            booking.status_id = int(item['StatusID'])
            booking.status_type_id = int(item['StatusTypeID'])
            booking.date_added = parse(item['DateAdded'])
            booking.date_changed = parse(item['DateChanged'])
            booking.contact_email_address = item.get('ContactEmailAddress',
                                                     None)
            bookings.append(booking)
        return bookings

    def get_bookings2(self, reservation_id, start_date, end_date,
                      statuses=None, event_types=None):
        params = {
                'ReservationID': reservation_id,
                'StartDate': start_date,
                'EndDate': end_date,
                'ViewComboRoomComponents': True,
            }
        if statuses is not None:
            params['Statuses'] = {'int': statuses}
        if event_types is not None:
            params['EventTypes'] = {'int': event_types}
        data = self._data_from_xml("Bookings", self._request(
            'GetBookings2', params))
        bookings = []
        for item in data:
            booking = Booking()
            booking.booking_date = parse(item['BookingDate']).date()
            booking.room_description = item['RoomDescription']
            booking.time_event_start = \
                parse(item['TimeEventStart'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeEventStart') else None
            booking.time_event_end = \
                parse(item['TimeEventEnd'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeEventEnd') else None
            booking.group_name = item['GroupName']
            booking.event_name = item['EventName']
            booking.reservation_id = int(item['ReservationID'])
            booking.event_type_description = item['EventTypeDescription']
            booking.contact = item['Contact']
            booking.id = int(item['BookingID'])
            booking.building_id = int(item['BuildingID'])
            booking.time_booking_start = \
                parse(item['TimeBookingStart'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeBookingStart') else None
            booking.time_booking_end = \
                parse(item['TimeBookingEnd'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeBookingEnd') else None
            booking.time_zone = item['TimeZone']
            booking.building_code = item['BuildingCode']
            booking.dv_building = item['Building']
            booking.room_code = item['RoomCode']
            booking.dv_room = item['Room']
            booking.room_id = int(item['RoomID'])
            booking.status_id = int(item['StatusID'])
            booking.status_type_id = int(item['StatusTypeID'])
            booking.date_added = parse(item['DateAdded'])
            booking.date_changed = parse(item['DateChanged'])
            booking.contact_email_address = item.get('ContactEmailAddress',
                                                     None)
            bookings.append(booking)
        return bookings

    def get_changed_bookings(self, start_date, end_date,
                             statuses=None, event_types=None):
        params = {
                'StartDate': start_date,
                'EndDate': end_date,
                'ViewComboRoomComponents': True,
            }
        if statuses is not None:
            params['Statuses'] = {'int': statuses}
        if event_types is not None:
            params['EventTypes'] = {'int': event_types}
        data = self._data_from_xml("Bookings", self._request(
            'GetChangedBookings', params))
        bookings = []
        for item in data:
            booking = Booking()
            booking.booking_date = parse(item['BookingDate']).date()
            booking.room_description = item['RoomDescription']
            booking.time_event_start = \
                parse(item['TimeEventStart'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeEventStart') else None
            booking.time_event_end = \
                parse(item['TimeEventEnd'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeEventEnd') else None
            booking.group_name = item['GroupName']
            booking.event_name = item['EventName']
            booking.reservation_id = int(item['ReservationID'])
            booking.event_type_description = item['EventTypeDescription']
            booking.contact = item['Contact']
            booking.id = int(item['BookingID'])
            booking.building_id = int(item['BuildingID'])
            booking.time_booking_start = \
                parse(item['TimeBookingStart'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeBookingStart') else None
            booking.time_booking_end = \
                parse(item['TimeBookingEnd'] + ' ' + item['TimeZone'],
                      tzinfos=self.tzinfos) \
                if item.get('TimeBookingEnd') else None
            booking.time_zone = item['TimeZone']
            booking.building_code = item['BuildingCode']
            booking.dv_building = item['Building']
            booking.room_code = item['RoomCode']
            booking.dv_room = item['Room']
            booking.room_id = int(item['RoomID'])
            booking.status_id = int(item['StatusID'])
            booking.status_type_id = int(item['StatusTypeID'])
            booking.date_added = parse(item['DateAdded'])
            booking.date_changed = parse(item['DateChanged'])
            bookings.append(booking)
        return bookings
