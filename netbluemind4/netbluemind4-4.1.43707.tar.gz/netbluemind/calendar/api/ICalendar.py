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
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

ICalendar_VERSION = "4.1.43707"

class ICalendar(BaseEndpoint):
    def __init__(self, apiKey, url ,containerUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendars/{containerUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}',containerUid)

    def filteredChangesetById (self, since , arg1 ):
        postUri = "/_filteredChangesetById";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemVersion import ItemVersion
        from netbluemind.core.container.model.ItemVersion import __ItemVersionSerDer__
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(__ItemVersionSerDer__()), response)
    def update (self, uid , event , sendNotifications ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        __data__ = __VEventSeriesSerDer__().encode(event)
        __encoded__ = json.dumps(__data__)
        queryParams = {    'sendNotifications': sendNotifications   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updates (self, changes ):
        postUri = "/_mupdates";
        __data__ = None
        __encoded__ = None
        from netbluemind.calendar.api.VEventChanges import VEventChanges
        from netbluemind.calendar.api.VEventChanges import __VEventChangesSerDer__
        __data__ = __VEventChangesSerDer__().encode(changes)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerUpdatesResult import ContainerUpdatesResult
        from netbluemind.core.container.model.ContainerUpdatesResult import __ContainerUpdatesResultSerDer__
        return self.handleResult__(__ContainerUpdatesResultSerDer__(), response)
    def delete (self, uid , sendNotifications ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   'sendNotifications': sendNotifications   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def changeset (self, since ):
        postUri = "/_changeset";
        __data__ = None
        __encoded__ = None
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def changesetById (self, since ):
        postUri = "/_changesetById";
        __data__ = None
        __encoded__ = None
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        __encoded__ = None
        from netbluemind.calendar.api.VEventQuery import VEventQuery
        from netbluemind.calendar.api.VEventQuery import __VEventQuerySerDer__
        __data__ = __VEventQuerySerDer__().encode(query)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
    def getReminder (self, dtalarm ):
        postUri = "/_remimder";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        __data__ = __BmDateTimeSerDer__().encode(dtalarm)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.Reminder import Reminder
        from netbluemind.calendar.api.Reminder import __ReminderSerDer__
        return self.handleResult__(serder.ListSerDer(__ReminderSerDer__()), response)
    def create (self, uid , event , sendNotifications ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        __data__ = __VEventSeriesSerDer__().encode(event)
        __encoded__ = json.dumps(__data__)
        queryParams = {    'sendNotifications': sendNotifications   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getCompleteById (self, id ):
        postUri = "/{id}/completeById";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__VEventSeriesSerDer__()), response)
    def all (self):
        postUri = "/_all";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def getVersion (self):
        postUri = "/_version";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(serder.LONG, response)
    def multipleGet (self, uids ):
        postUri = "/_mget";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
    def count (self, arg0 ):
        postUri = "/_count";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Count import Count
        from netbluemind.core.container.api.Count import __CountSerDer__
        return self.handleResult__(__CountSerDer__(), response)
    def touch (self, uid ):
        postUri = "/{uid}/_touch";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def list (self):
        postUri = "/_list";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
    def sortedIds (self, sorted ):
        postUri = "/_sorted";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.SortDescriptor import SortDescriptor
        from netbluemind.core.container.model.SortDescriptor import __SortDescriptorSerDer__
        __data__ = __SortDescriptorSerDer__().encode(sorted)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.LONG), response)
    def sync (self, since , changes ):
        postUri = "/_sync";
        __data__ = None
        __encoded__ = None
        from netbluemind.calendar.api.VEventChanges import VEventChanges
        from netbluemind.calendar.api.VEventChanges import __VEventChangesSerDer__
        __data__ = __VEventChangesSerDer__().encode(changes)
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def itemChangelog (self, uid , arg1 ):
        postUri = "/{uid}/_itemchangelog";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.LONG.encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemChangelog import ItemChangelog
        from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
        return self.handleResult__(__ItemChangelogSerDer__(), response)
    def multipleDeleteById (self, arg0 ):
        postUri = "/_multipleDelete";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updateById (self, id , value ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        __data__ = __VEventSeriesSerDer__().encode(value)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__VEventSeriesSerDer__()), response)
    def containerChangelog (self, arg0 ):
        postUri = "/_changelog";
        __data__ = None
        __encoded__ = None
        __data__ = serder.LONG.encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
        from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
        return self.handleResult__(__ContainerChangelogSerDer__(), response)
    def deleteById (self, id ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def reset (self):
        postUri = "/_reset";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def createById (self, id , event ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        __data__ = __VEventSeriesSerDer__().encode(event)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
    def getByIcsUid (self, uid ):
        postUri = "/_icsuid/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICalendar_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VEventSeries import VEventSeries
        from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
