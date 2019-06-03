#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2015 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
import bson.json_util
from girder import constants
from girder import events
from girder.api import access
from girder.api.rest import Resource, loadmodel
from girder.api.rest import filtermodel, RestException
from girder.api.describe import Description
from girder.constants import AccessType
from girder.plugin import GirderPlugin
from girder.models.collection import Collection
from girder.models.folder import Folder


MONKEYBRAINS_FIELD = 'monkeybrains'
MONKEYBRAINS_INFOPAGE_FIELD = 'monkeybrainsInfoPage'


class Monkeybrains(Resource):

    @access.public
    @filtermodel(model=Collection)
    @loadmodel(model='collection', level=AccessType.WRITE)
    def setCollectionMonkeybrains(self, collection, params):
        self.requireParams((MONKEYBRAINS_FIELD, ), params)
        monkeybrains = params[MONKEYBRAINS_FIELD]
        if not monkeybrains:
            del collection[MONKEYBRAINS_FIELD]
        else:
            collection[MONKEYBRAINS_FIELD] = monkeybrains
        Collection().updateCollection(collection)
        return collection
    setCollectionMonkeybrains.description = (
        Description('Set monkeybrains activation state for the collection.')
        .param('id', 'The collection ID', paramType='path')
        .param('monkeybrains', 'Boolean: monkeybrains activation state for ' +
               'this collection.', required=True, dataType='boolean')
        .errorResponse('ID was invalid.')
        .errorResponse('Write permission denied on the collection.', 403))


class DatasetEvents(Resource):
    @access.public
    @loadmodel(model='collection', level=AccessType.READ)
    def getDatasetEvents(self, collection, params):
        """
        Get the individual events in a dataset, which are defined as folders
        having metadata keys (scan_date, subject_id, scan_weight_kg, DOB) and
        that live under the passed in collection.
        Handle setting monkeybrains for any resource that supports them.
        :param collection: parent collection of sought events.
        :return resource: the loaded resource document.
        """
        # return these metadata keys
        metadata_keys = ['folder_type', 'scan_age', 'sex', 'scan_date',
                         'subject_id', 'dob', 'scan_weight_kg']
        key_d = {'meta.'+key: 1 for key in metadata_keys}
        key_d['parentId'] = 1
        key_d['baseParentId'] = 1
        key_d['_id'] = 1
        # look at folders in this collection with the scan_date metadata key
        condition_d = {'baseParentId': {'$oid': collection['_id']},
                       'meta.scan_date': {'$exists': True}}
        initial = {}
        reduc = "function (curr, result) {}"
        finalize = "function (curr, result) {}"
        try:
            key = bson.json_util.loads(bson.json_util.dumps(key_d))
            condition = bson.json_util.loads(bson.json_util.dumps(condition_d))
        except ValueError:
            raise RestException('The query parameter must be a JSON object.')
        document = \
            Folder().collection.group(key, condition, initial, reduc, finalize)
        return document
    getDatasetEvents.description = (
        Description('Get datasetEvents for the collection.')
        .param('id', 'The collection ID', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the collection.', 403))


def updateCollection(event):
    params = event.info['params']
    if MONKEYBRAINS_FIELD in params and MONKEYBRAINS_INFOPAGE_FIELD in params:
        # ok to force here because rest.put.collection call requires WRITE
        collection = Collection().load(params['_id'], force=True)
        infoPage = params[MONKEYBRAINS_INFOPAGE_FIELD]
        collection[MONKEYBRAINS_INFOPAGE_FIELD] = infoPage
        Collection().updateCollection(collection)
        event.info['returnVal'][MONKEYBRAINS_INFOPAGE_FIELD] = infoPage


class MonkeybrainsPlugin(GirderPlugin):
    DISPLAY_NAME = 'Monkeybrains Plugin'

    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        monkeybrains = Monkeybrains()
        info['apiRoot'].collection.route('PUT', (':id', 'monkeybrains'),
                                         monkeybrains.setCollectionMonkeybrains)
        datasetEvents = DatasetEvents()
        info['apiRoot'].collection.route('GET', (':id', 'datasetEvents'),
                                         datasetEvents.getDatasetEvents)

        Collection().exposeFields(level=constants.AccessType.READ, fields=[MONKEYBRAINS_FIELD,
                                  MONKEYBRAINS_INFOPAGE_FIELD])
        events.bind('rest.put.collection/:id.after',
                    'monkeybrains_updateCollection', updateCollection)
