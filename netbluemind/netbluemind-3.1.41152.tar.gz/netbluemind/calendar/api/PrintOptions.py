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

class PrintOptions :
    def __init__( self):
        self.view = None
        self.format = None
        self.dateBegin = None
        self.dateEnd = None
        self.color = None
        self.showDetail = None
        self.layout = None
        self.calendars = None
        self.tagsFilter = None
        pass

class __PrintOptionsSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = PrintOptions()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.calendar.api.PrintOptionsPrintView import PrintOptionsPrintView
        from netbluemind.calendar.api.PrintOptionsPrintView import __PrintOptionsPrintViewSerDer__
        viewValue = value['view']
        instance.view = __PrintOptionsPrintViewSerDer__().parse(viewValue)
        from netbluemind.calendar.api.PrintOptionsPrintFormat import PrintOptionsPrintFormat
        from netbluemind.calendar.api.PrintOptionsPrintFormat import __PrintOptionsPrintFormatSerDer__
        formatValue = value['format']
        instance.format = __PrintOptionsPrintFormatSerDer__().parse(formatValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dateBeginValue = value['dateBegin']
        instance.dateBegin = __BmDateTimeSerDer__().parse(dateBeginValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dateEndValue = value['dateEnd']
        instance.dateEnd = __BmDateTimeSerDer__().parse(dateEndValue)
        colorValue = value['color']
        instance.color = serder.BOOLEAN.parse(colorValue)
        showDetailValue = value['showDetail']
        instance.showDetail = serder.BOOLEAN.parse(showDetailValue)
        from netbluemind.calendar.api.PrintOptionsPrintLayout import PrintOptionsPrintLayout
        from netbluemind.calendar.api.PrintOptionsPrintLayout import __PrintOptionsPrintLayoutSerDer__
        layoutValue = value['layout']
        instance.layout = __PrintOptionsPrintLayoutSerDer__().parse(layoutValue)
        from netbluemind.calendar.api.PrintOptionsCalendarMetadata import PrintOptionsCalendarMetadata
        from netbluemind.calendar.api.PrintOptionsCalendarMetadata import __PrintOptionsCalendarMetadataSerDer__
        calendarsValue = value['calendars']
        instance.calendars = serder.ListSerDer(__PrintOptionsCalendarMetadataSerDer__()).parse(calendarsValue)
        tagsFilterValue = value['tagsFilter']
        instance.tagsFilter = serder.SetSerDer(serder.STRING).parse(tagsFilterValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.calendar.api.PrintOptionsPrintView import PrintOptionsPrintView
        from netbluemind.calendar.api.PrintOptionsPrintView import __PrintOptionsPrintViewSerDer__
        viewValue = value.view
        instance["view"] = __PrintOptionsPrintViewSerDer__().encode(viewValue)
        from netbluemind.calendar.api.PrintOptionsPrintFormat import PrintOptionsPrintFormat
        from netbluemind.calendar.api.PrintOptionsPrintFormat import __PrintOptionsPrintFormatSerDer__
        formatValue = value.format
        instance["format"] = __PrintOptionsPrintFormatSerDer__().encode(formatValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dateBeginValue = value.dateBegin
        instance["dateBegin"] = __BmDateTimeSerDer__().encode(dateBeginValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dateEndValue = value.dateEnd
        instance["dateEnd"] = __BmDateTimeSerDer__().encode(dateEndValue)
        colorValue = value.color
        instance["color"] = serder.BOOLEAN.encode(colorValue)
        showDetailValue = value.showDetail
        instance["showDetail"] = serder.BOOLEAN.encode(showDetailValue)
        from netbluemind.calendar.api.PrintOptionsPrintLayout import PrintOptionsPrintLayout
        from netbluemind.calendar.api.PrintOptionsPrintLayout import __PrintOptionsPrintLayoutSerDer__
        layoutValue = value.layout
        instance["layout"] = __PrintOptionsPrintLayoutSerDer__().encode(layoutValue)
        from netbluemind.calendar.api.PrintOptionsCalendarMetadata import PrintOptionsCalendarMetadata
        from netbluemind.calendar.api.PrintOptionsCalendarMetadata import __PrintOptionsCalendarMetadataSerDer__
        calendarsValue = value.calendars
        instance["calendars"] = serder.ListSerDer(__PrintOptionsCalendarMetadataSerDer__()).encode(calendarsValue)
        tagsFilterValue = value.tagsFilter
        instance["tagsFilter"] = serder.SetSerDer(serder.STRING).encode(tagsFilterValue)
        return instance

