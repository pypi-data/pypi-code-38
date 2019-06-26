import os
from pkg_resources import resource_filename

from girder import events
from girder.plugin import GirderPlugin
from girder.utility import config

from geobrowser_plugin.utils import itemAddedToCollection
from geobrowser_plugin.rest import (
    singleCollectionHandler,
    listCollectionHandler,
    forceRecomputeAllHandler,
    forceDeleteAllHandler
)


class GeoBrowserPlugin(GirderPlugin):
    DISPLAY_NAME = 'GeoBrowser Plugin'

    def load(self, info):
        events.bind('geometa.created', 'name',
                    itemAddedToCollection)
        # Add bind event for last item deleted in geometa collection
        # This is probably the wrong event
        # events.bind('model.item.remove', 'name',
        #             itemRemovedFromCollection)

        info['apiRoot'].collection.route(
            'GET',
            (':id', 'geobrowser'),
            singleCollectionHandler)

        info['apiRoot'].collection.route(
            'GET',
            ('geobrowser',),
            listCollectionHandler)

        info['apiRoot'].collection.route(
            'PUT',
            ('geobrowser',),
            forceRecomputeAllHandler)

        info['apiRoot'].collection.route(
            'DELETE',
            ('geobrowser',),
            forceDeleteAllHandler)

        if config.getConfig()['server']['mode'] == 'production':
            info['config']['/geobrowser'] = {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.realpath(
                    resource_filename(
                        'geobrowser_plugin',
                        'external_web_client')
                ),
                'tools.staticdir.index': 'index.html'
            }
