#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
from netbluemind.python import serder

class ICalendarElement :
    def __init__( self):
        self.dtstart = None
        self.summary = None
        self.classification = None
        self.location = None
        self.description = None
        self.priority = None
        self.alarm = None
        self.status = None
        self.attendees = None
        self.organizer = None
        self.categories = None
        self.exdate = None
        self.rdate = None
        self.rrule = None
        self.url = None
        pass

class __ICalendarElementSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ICalendarElement()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtstartValue = value['dtstart']
        instance.dtstart = __BmDateTimeSerDer__().parse(dtstartValue)
        summaryValue = value['summary']
        instance.summary = serder.STRING.parse(summaryValue)
        from netbluemind.icalendar.api.ICalendarElementClassification import ICalendarElementClassification
        from netbluemind.icalendar.api.ICalendarElementClassification import __ICalendarElementClassificationSerDer__
        classificationValue = value['classification']
        instance.classification = __ICalendarElementClassificationSerDer__().parse(classificationValue)
        locationValue = value['location']
        instance.location = serder.STRING.parse(locationValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        priorityValue = value['priority']
        instance.priority = serder.INT.parse(priorityValue)
        from netbluemind.icalendar.api.ICalendarElementVAlarm import ICalendarElementVAlarm
        from netbluemind.icalendar.api.ICalendarElementVAlarm import __ICalendarElementVAlarmSerDer__
        alarmValue = value['alarm']
        instance.alarm = serder.ListSerDer(__ICalendarElementVAlarmSerDer__()).parse(alarmValue)
        from netbluemind.icalendar.api.ICalendarElementStatus import ICalendarElementStatus
        from netbluemind.icalendar.api.ICalendarElementStatus import __ICalendarElementStatusSerDer__
        statusValue = value['status']
        instance.status = __ICalendarElementStatusSerDer__().parse(statusValue)
        from netbluemind.icalendar.api.ICalendarElementAttendee import ICalendarElementAttendee
        from netbluemind.icalendar.api.ICalendarElementAttendee import __ICalendarElementAttendeeSerDer__
        attendeesValue = value['attendees']
        instance.attendees = serder.ListSerDer(__ICalendarElementAttendeeSerDer__()).parse(attendeesValue)
        from netbluemind.icalendar.api.ICalendarElementOrganizer import ICalendarElementOrganizer
        from netbluemind.icalendar.api.ICalendarElementOrganizer import __ICalendarElementOrganizerSerDer__
        organizerValue = value['organizer']
        instance.organizer = __ICalendarElementOrganizerSerDer__().parse(organizerValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value['categories']
        instance.categories = serder.ListSerDer(__TagRefSerDer__()).parse(categoriesValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        exdateValue = value['exdate']
        instance.exdate = serder.SetSerDer(__BmDateTimeSerDer__()).parse(exdateValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        rdateValue = value['rdate']
        instance.rdate = serder.SetSerDer(__BmDateTimeSerDer__()).parse(rdateValue)
        from netbluemind.icalendar.api.ICalendarElementRRule import ICalendarElementRRule
        from netbluemind.icalendar.api.ICalendarElementRRule import __ICalendarElementRRuleSerDer__
        rruleValue = value['rrule']
        instance.rrule = __ICalendarElementRRuleSerDer__().parse(rruleValue)
        urlValue = value['url']
        instance.url = serder.STRING.parse(urlValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtstartValue = value.dtstart
        instance["dtstart"] = __BmDateTimeSerDer__().encode(dtstartValue)
        summaryValue = value.summary
        instance["summary"] = serder.STRING.encode(summaryValue)
        from netbluemind.icalendar.api.ICalendarElementClassification import ICalendarElementClassification
        from netbluemind.icalendar.api.ICalendarElementClassification import __ICalendarElementClassificationSerDer__
        classificationValue = value.classification
        instance["classification"] = __ICalendarElementClassificationSerDer__().encode(classificationValue)
        locationValue = value.location
        instance["location"] = serder.STRING.encode(locationValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        priorityValue = value.priority
        instance["priority"] = serder.INT.encode(priorityValue)
        from netbluemind.icalendar.api.ICalendarElementVAlarm import ICalendarElementVAlarm
        from netbluemind.icalendar.api.ICalendarElementVAlarm import __ICalendarElementVAlarmSerDer__
        alarmValue = value.alarm
        instance["alarm"] = serder.ListSerDer(__ICalendarElementVAlarmSerDer__()).encode(alarmValue)
        from netbluemind.icalendar.api.ICalendarElementStatus import ICalendarElementStatus
        from netbluemind.icalendar.api.ICalendarElementStatus import __ICalendarElementStatusSerDer__
        statusValue = value.status
        instance["status"] = __ICalendarElementStatusSerDer__().encode(statusValue)
        from netbluemind.icalendar.api.ICalendarElementAttendee import ICalendarElementAttendee
        from netbluemind.icalendar.api.ICalendarElementAttendee import __ICalendarElementAttendeeSerDer__
        attendeesValue = value.attendees
        instance["attendees"] = serder.ListSerDer(__ICalendarElementAttendeeSerDer__()).encode(attendeesValue)
        from netbluemind.icalendar.api.ICalendarElementOrganizer import ICalendarElementOrganizer
        from netbluemind.icalendar.api.ICalendarElementOrganizer import __ICalendarElementOrganizerSerDer__
        organizerValue = value.organizer
        instance["organizer"] = __ICalendarElementOrganizerSerDer__().encode(organizerValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value.categories
        instance["categories"] = serder.ListSerDer(__TagRefSerDer__()).encode(categoriesValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        exdateValue = value.exdate
        instance["exdate"] = serder.SetSerDer(__BmDateTimeSerDer__()).encode(exdateValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        rdateValue = value.rdate
        instance["rdate"] = serder.SetSerDer(__BmDateTimeSerDer__()).encode(rdateValue)
        from netbluemind.icalendar.api.ICalendarElementRRule import ICalendarElementRRule
        from netbluemind.icalendar.api.ICalendarElementRRule import __ICalendarElementRRuleSerDer__
        rruleValue = value.rrule
        instance["rrule"] = __ICalendarElementRRuleSerDer__().encode(rruleValue)
        urlValue = value.url
        instance["url"] = serder.STRING.encode(urlValue)
        return instance

