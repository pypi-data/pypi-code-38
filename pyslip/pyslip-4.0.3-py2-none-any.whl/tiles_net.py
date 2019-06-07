"""
A server Tiles object for pySlip tiles.

All server tile sources should inherit from this class.
For example, see open_street_map.py.
"""

import sys
import os
import io
import time
import math
import threading
import traceback
import urllib
import urllib.request as request
import queue
import wx
import pyslip.tiles as tiles
import pyslip.sys_tile_data as std
import pyslip.log as log

try:
    log = log.Log('pyslip.log')
except AttributeError:
    # means log already set up
    pass

# set how old disk-cache tiles can be before we re-request them from the
# server.  this is the number of days old a tile is before we re-request.
# if 'None', never re-request tiles after first satisfied request.
RefreshTilesAfterDays = 60

# define the error messages for various failures
StatusError = {401: 'Looks like you need to be authorised for this server.',
               404: 'You might need to check the tile addressing for this server.',
               429: 'You are asking for too many tiles.',
              }

################################################################################
# Worker class for server tile retrieval
################################################################################

class TileWorker(threading.Thread):
    """Thread class that gets request from queue, loads tile, calls callback."""

    def __init__(self, id_num, server, tilepath, requests, callback,
                 error_tile, content_type, rerequest_age, error_image):
        """Prepare the tile worker.

        id_num         a unique numer identifying the worker instance
        server         server URL
        tilepath       path to tile on server
        requests       the request queue
        callback       function to call after tile available
        error_tile     image of error tile
        content_type   expected Content-Type string
        rerequest_age  number of days in tile age before re-requesting
                       (0 means don't update tiles)
        error_image    the image to return on some error

        Results are returned in the callback() params.
        """

        threading.Thread.__init__(self)

        self.id_num = id_num
        self.server = server
        self.tilepath = tilepath
        self.requests = requests
        self.callback = callback
        self.error_tile_image = error_tile
        self.content_type = content_type
        self.rerequest_age = rerequest_age
        self.error_image = error_image
        self.daemon = True

    def run(self):
        while True:
            # get zoom level and tile coordinates to retrieve
            (level, x, y) = self.requests.get()

            # try to retrieve the image
            error = False
            pixmap = self.error_image
            try:
                tile_url = self.server + self.tilepath.format(Z=level, X=x, Y=y)
                response = request.urlopen(request.Request(tile_url))
                content_type = response.info().get_content_type()
                if content_type == self.content_type:
                    data = io.BytesIO(response.read())
                    pixmap = wx.Image(data, content_type).ConvertToBitmap()
                else:
                    # show error tile, don't cache returned error tile
                    error = True
            except Exception as e:
                error = True
                log('%s exception getting tile (%d,%d,%d)'
                        % (type(e).__name__, level, x, y))

            # call the callback function passing level, x, y and pixmap data
            # error is False if we want to cache this tile on-disk
            wx.CallAfter(self.callback, level, x, y, pixmap, error)

            # finally, remove request from queue
            self.requests.task_done()

###############################################################################
# Class for a server tile source.  Extend the BaseTiles class.
###############################################################################

class Tiles(tiles.BaseTiles):
    """A tile object to source server tiles for the widget."""

    # maximum number of outstanding requests per server
    MaxServerRequests = 2

    # maximum number of in-memory cached tiles
    MaxLRU = 1000

    # allowed file types and associated values
    AllowedFileTypes = {
                        'png': 'PNG',
                        'jpg': 'JPG',
                       }

    # the number of seconds in a day
    SecondsInADay = 60 * 60 * 24

    def __init__(self, levels, tile_width, tile_height, tiles_dir, max_lru,
                 servers, url_path, max_server_requests,
                 refetch_days=RefreshTilesAfterDays):
        """Initialise a Tiles instance.

        levels               a list of level numbers that are to be served
        tile_width           width of each tile in pixels
        tile_height          height of each tile in pixels
        tiles_dir            path to on-disk tile cache directory
        max_lru              maximum number of cached in-memory tiles
        servers              list of tile servers
        url_path             path on server to each tile
        max_server_requests  maximum number of requests per server
        refetch_days         fetch new server tile if older than this in days
                             (0 means don't ever update tiles)
        """

        # prepare the tile cache directory, if required
        # we have to do this *before* the base class initialization!
        for level in levels:
            level_dir = os.path.join(tiles_dir, '%d' % level)
            if not os.path.isdir(level_dir):
                os.makedirs(level_dir)

        # perform the base class initialization
        super().__init__(levels, tile_width, tile_height, tiles_dir, max_lru)

        # save params not saved in super()
        self.servers = servers
        self.url_path = url_path
        self.max_requests = max_server_requests

        # callback must be set by higher-level copde
        self.callback = None

        # calculate a re-request age, if specified
        self.rerequest_age = None
        if refetch_days:
            self.rerequest_age = (time.time() - refetch_days*self.SecondsInADay)

        # tiles extent for tile data (left, right, top, bottom)
        self.extent = (-180.0, 180.0, -85.0511, 85.0511)

        # figure out tile filename extension from 'url_path'
        tile_extension = os.path.splitext(url_path)[1][1:]
        tile_extension_lower = tile_extension.lower()      # ensure lower case

        # determine the file bitmap type
        try:
            self.filetype = self.AllowedFileTypes[tile_extension_lower]
        except KeyError as e:
            raise TypeError("Bad tile_extension value, got '%s', "
                            "expected one of %s"
                            % (str(tile_extension),
                               str(self.AllowedFileTypes.keys())))

        # compose the expected 'Content-Type' string on request result
        # if we get here we know the extension is in self.AllowedFileTypes
        if tile_extension_lower == 'jpg':
            self.content_type = 'image/jpeg'
        elif tile_extension_lower == 'png':
            self.content_type = 'image/png'

        # set the list of queued unsatisfied requests to 'empty'
        self.queued_requests = {}

        # prepare the "pending" and "error" images
        self.pending_tile_image = std.getPendingImage()
        self.pending_tile = self.pending_tile_image.ConvertToBitmap()

        self.error_tile_image = std.getErrorImage()
        self.error_tile = self.error_tile_image.ConvertToBitmap()

        # test the tile server, get tile at (0, 0, 0)
        test_url = self.servers[0] + self.url_path.format(Z=0, X=0, Y=0)
        try:
            request.urlopen(test_url)
        except urllib.error.HTTPError as e:
            # if it's fatal, log it and die
            status_code = e.code
            log('Error: test_url=%s, status_code=%s'
                    % (test_url, str(status_code)))
            error_msg = StatusError.get(status_code, None)
            if status_code:
                msg = '\n'.join(['You got a %d error from: %s' % (status_code, test_url),
                                 error_msg])
                log(msg)
                raise RuntimeError(msg)

            log('%s exception doing simple connection to: %s'
                    % (type(e).__name__, test_url))
            log(''.join(traceback.format_exc()))
            raise RuntimeError

        # set up the request queue and worker threads
        self.request_queue = queue.Queue()  # entries are (level, x, y)
        self.workers = []
        for server in self.servers:
            for num_thread in range(self.max_requests):
                worker = TileWorker(num_thread, server, self.url_path,
                                    self.request_queue, self.tile_is_available,
                                    self.error_tile, self.content_type,
                                    self.rerequest_age, self.error_tile)
                self.workers.append(worker)
                worker.start()

    def UseLevel(self, level):
        """Prepare to serve tiles from the required level.

        level  the required level

        Return True if level change occurred, else False if not possible.
        """

        # first, CAN we zoom to this level?
        if level not in self.levels:
            return False

        # get tile info
        info = self.GetInfo(level)
        if info is None:
            return False

        # OK, save new level
        self.level = level
        (self.num_tiles_x, self.num_tiles_y, self.ppd_x, self.ppd_y) = info

        # flush any outstanding requests.
        # we do this to speed up multiple-level zooms so the user doesn't
        # sit waiting for tiles to arrive that won't be shown.
        self.FlushRequests()

        return True

    def GetTile(self, x, y):
        """Get bitmap for tile at tile coords (x, y) and current level.

        x  X coord of tile required (tile coordinates)
        y  Y coord of tile required (tile coordinates)

        Returns bitmap object for the tile image.
        Tile coordinates are measured from map top-left.

        We override the existing GetTile() method to add code to retrieve
        tiles from the servers if not in on-disk cache.

        We also check the date on the tile from disk-cache.  If "too old",
        return old tile after starting the process to get new tile from servers.
        """

        try:
            # get tile from cache
            tile = self.cache[(self.level, x, y)]
            if self.tile_on_disk(self.level, x, y):
                tile_date = self.cache.tile_date((self.level, x, y))
                if self.rerequest_age and (tile_date < self.rerequest_age):
                    self.get_server_tile(self.level, x, y)
        except KeyError as e:
            # not cached, start process of getting tile from 'net, return 'pending' image
            self.get_server_tile(self.level, x, y)
            tile = self.pending_tile

        return tile

    def GetInfo(self, level):
        """Get tile info for a particular level.

        level  the level to get tile info for

        Returns (num_tiles_x, num_tiles_y, ppd_x, ppd_y) or None if 'level'
        doesn't exist.

        Note that ppd_? may be meaningless for some tiles, so its
        value will be None.

        This method is for server tiles.  It will be overridden for GMT tiles.
        """

        # is required level available?
        if level not in self.levels:
            return None

        # otherwise get the information
        self.num_tiles_x = int(math.pow(2, level))
        self.num_tiles_y = int(math.pow(2, level))

        return (self.num_tiles_x, self.num_tiles_y, None, None)

    def FlushRequests(self):
        """Delete any outstanding tile requests."""

        # if we are serving server tiles ...
        if self.servers:
            with self.request_queue.mutex:
                self.request_queue.queue.clear()
            self.queued_requests.clear()

    def get_server_tile(self, level, x, y):
        """Start the process to get a server tile.

        level, x, y  identify the required tile

        If we don't already have this tile (or getting it), queue a request and
        also put the request into a 'queued request' dictionary.  We
        do this since we can't peek into a queue to see what's there.
        """

        tile_key = (level, x, y)
        if tile_key not in self.queued_requests:
            # add tile request to the server request queue
            self.request_queue.put(tile_key)
            self.queued_requests[tile_key] = True

    def tile_on_disk(self, level, x, y):
        """Return True if tile at (level, x, y) is on-disk."""

        tile_path = self.cache.tile_path((level, x, y))
        return os.path.exists(tile_path)

    def setCallback(self, callback):
        """Set the "tile available" callback.

        callback  reference to object to call when tile is found.
        """

        self.callback = callback

    def tile_is_available(self, level, x, y, image, error):
        """Callback routine - a 'net tile is available.

        level   level for the tile
        x       x coordinate of tile
        y       y coordinate of tile
        image   tile image data
        error   True if image is 'error' image, don't cache in that case
        """

        # put image into in-memory cache, but error images don't go to disk
        self.cache[(level, x, y)] = image
        if not error:
            self.cache._put_to_back((level, x, y), image)

        # remove the request from the queued requests
        # note that it may not be there - a level change can flush the dict
        try:
            del self.queued_requests[(level, x, y)]
        except KeyError:
            pass

        # tell the world a new tile is available
        if self.callback:
            self.callback(level, x, y, image, True)
        else:
            msg = f'tile_is_available: self.callback is NOT SET!'
            log.error(msg)
            raise RuntimeError(msg)

    def SetAgeThresholdDays(self, num_days):
        """Set the tile refetch threshold time.

        num_days  number of days before refetching tiles

        If 'num_days' is 0 refetching is inhibited.
        """

        # update the global in case we instantiate again
        global RefreshTilesAfterDays
        RefreshTilesAfterDays = num_days

        # recalculate this instance's age threshold in UNIX time
        self.rerequest_age = (time.time() -
                                  RefreshTilesAfterDays * self.SecondsInADay)
