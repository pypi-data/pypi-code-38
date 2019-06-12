'''mapLayout.py - takes care of initialising map blocks with obstacles and
 images.'''

import codecs
from hashlib import sha512
import io
import logging
import os
import random

import pygame

from trosnoth import data
from trosnoth.model import maptree
from trosnoth.utils import unrepr

from trosnoth.data import getPath, user, makeDirs
import trosnoth.data.blocks

log = logging.getLogger(__name__)

BLOCK_FILES = {
    'ForwardInterfaceMapBlock': 'fwd',
    'BackwardInterfaceMapBlock': 'bck',
    'TopBodyMapBlock': 'top',
    'BottomBodyMapBlock': 'btm',
}


class LayoutDatabase(object):
    '''
    Represents a database which stores information on block layouts.
    Contains several LayoutDatastores which will be queried in their order of
    priority when a block is needed.
    '''

    def __init__(self, blocks=(), pathGetter=None, custom=True):
        if pathGetter is None:
            pathGetter = self.getDefaultPath
        self.pathGetter = pathGetter
        self.datastores = []
        self._addDatastoreWithBlocks(blocks)
        self._addDatastoreByPaths(
            getPath(trosnoth.data.blocks), getPath(user, 'blocks'))
        if custom:
            self._addDatastoreByPaths(getPath(trosnoth.data.blocks, 'custom'))

    def getDefaultPath(self, *bits):
        return data.getPath(data, *bits)

    def _addDatastoreWithBlocks(self, blocks):
        if len(blocks) == 0:
            return

        store = LayoutDatastore(pathGetter=self.pathGetter)
        self.datastores.append(store)
        for block in blocks:
            store.addLayoutAtFilename(block)

    def _addDatastoreByPaths(self, *paths):
        for path in paths:
            try:
                makeDirs(path)
            except OSError:
                log.warning('Could not create datastore path')
                return

        store = LayoutDatastore(pathGetter=self.pathGetter)
        self.datastores.append(store)

        # Read map blocks from files.
        for path in paths:
            filenames = os.listdir(path)

            # Go through all files in the blocks directory.
            for fn in filenames:
                # Check for files with a .block extension.
                if os.path.splitext(fn)[1] == '.block':
                    store.addLayoutAtFilename(os.path.join(path, fn))
        return store

    def getFundamentalKey(self, key):
        '''
        If a block with the given key exists in the database, returns None,
        otherwise returns a fundamental form of the key which should be used
        when asking a remote server for a copy of the block. This is done so
        that only one request is sent for map blocks which are mirror images of
        one another.
        '''
        kind, checksum, reversed = key
        for ds in self.datastores:
            if (kind, checksum) in ds.layoutsByKey:
                return None
        return (kind, checksum, False)

    def getLayoutByKey(self, key):
        '''
        Returns a BlockLayout from its key, or None if no such layout is known.
        '''
        for ds in self.datastores:
            result = ds.getLayoutByKey(key)
            if result is not None:
                return result
        return None

    def getLayoutByFilename(self, filename, reversed=False):
        '''
        Returns a BlockLayout from its filename, or None if no such layout is
        known.
        '''
        for ds in self.datastores:
            result = ds.getLayoutByFilename(filename, reversed=reversed)
            if result is not None:
                return result
        return None

    def getLayoutByName(self, name):
        for ds in self.datastores:
            result = ds.getLayoutByName(name)
            if result is not None:
                return result
        return None

    def getRandomLayout(self, kind, blocked):
        for ds in self.datastores:
            if len(ds.layouts[kind, blocked]) > 0:
                return random.choice(ds.layouts[kind, blocked])
        raise ValueError(
            'No layouts found of kind %r with blocked %r' % (kind, blocked))

    def getRandomSymmetricalLayout(self, kind, blocked):
        for ds in self.datastores:
            if len(ds.symmetricalLayouts[kind, blocked]) > 0:
                return random.choice(ds.symmetricalLayouts[kind, blocked])
        raise ValueError(
            'No symmetrical layouts found of kind %r with blocked %r' % (
                kind, blocked))

    def randomiseBlock(self, block, oppBlock=None):
        '''Takes a map block and gives it and the
        corresponding opposite block a layout depending on its block type
        and whether it has a barrier.
        '''
        if oppBlock is not block:
            # The block is not symmetrical.
            layout = self.getRandomLayout(block.kind, block.blocked)
            layout.applyTo(block)
            if oppBlock is not None:
                layout.mirrorLayout.applyTo(oppBlock)
        else:
            # The block is symmetrical.
            layout = self.getRandomSymmetricalLayout(block.kind, block.blocked)
            layout.applyTo(block)

    def allLayouts(self):
        '''
        Iterates through all map block layouts in this datastore.
        '''
        for ds in self.datastores:
            yield from ds.layoutsByKey.values()


class LayoutDatastore(object):
    '''Represents a database which stores information on block layouts.'''

    def __init__(self, pathGetter):
        '''(paths) - initialises the database and loads the blocks from the
        specified paths.'''
        self.pathGetter = pathGetter

        # Set up database.
        self.layouts = {}
        self.layoutsByFilename = {}
        self.layoutsByName = {}
        self.layoutsByKey = {}          # Keyed by (kind, checksum)
        self.symmetricalLayouts = {}
        for b in True, False:
            for a in 'fwd', 'bck', 'top', 'btm':
                self.layouts[a, b] = []
            for a in 'top', 'btm':
                self.symmetricalLayouts[a, b] = []

    def addLayoutAtFilename(self, filepath):
        # Remember the filename.
        self.filename = os.path.split(filepath)[1]

        # Read the file and create the block
        f = open(filepath, 'rb')
        try:
            contents = f.read()
        finally:
            f.close()

        self.checksum = sha512(contents).hexdigest()

        try:
            contentDict = unrepr.unrepr(contents.decode('utf-8'))
        except Exception as e:
            log.warning(
                'Error decoding map block %r: %s: %s', filepath,
                e.__class__.__name__, e)
            return False
        self.addLayout(filepath, **contentDict)
        return True

    def addLayout(
            self, filepath, graphics, blockType='TopBodyMapBlock',
            blocked=False, obstacles=[], platforms=[], symmetrical=False):
        '''
        Registers a layout with the given parameters.
        '''
        graphicsIO = io.BytesIO()
        if isinstance(graphics, str):
            graphics = graphics.encode('ascii')
        graphicsIO.write(codecs.decode(graphics, 'base64'))

        blockType = BLOCK_FILES[blockType]

        newLayout = OldBlockLayout()
        newLayout.setProperties(
            symmetrical, self.checksum, blockType, filepath, graphicsIO)

        # Add the layout to the database.
        self.layouts[blockType, blocked].append(newLayout)
        self.layoutsByFilename[self.filename] = newLayout
        name = os.path.basename(self.filename)
        self.layoutsByName[name] = newLayout
        self.layoutsByKey[(blockType, self.checksum)] = newLayout

        if symmetrical:
            self.symmetricalLayouts[blockType, blocked].append(newLayout)
        else:
            if blockType == 'fwd':
                blockType = 'bck'
            elif blockType == 'bck':
                blockType = 'fwd'

            self.layouts[blockType, blocked].append(newLayout.mirrorLayout)

        base, ext = os.path.splitext(filepath)
        newLayoutPath = base + '.trosblock'
        if os.path.isfile(newLayoutPath):
            newLayout.setNewLayout(self.loadNewLayoutFile(newLayoutPath))
        else:
            log.warning('File not found: %r', newLayoutPath)

    def loadNewLayoutFile(self, filename):
        with open(filename, 'r') as f:
            data = unrepr.unrepr(f.read())
        return maptree.BlockLayout(data)

    def getLayoutByKey(self, key):
        '''
        Returns a BlockLayout from its key, or None if no such layout is known.
        '''
        kind, checksum, reversed = key
        try:
            layout = self.layoutsByKey[(kind, checksum)]
        except KeyError:
            return None
        if reversed:
            return layout.mirrorLayout
        return layout

    def getLayoutByFilename(self, filename, reversed=False):
        '''
        Returns a BlockLayout from its filename, or None if no such layout is
        known.
        '''
        try:
            layout = self.layoutsByFilename[filename]
        except KeyError:
            return None
        if reversed:
            return layout.mirrorLayout
        return layout

    def getLayoutByName(self, name):
        return self.layoutsByName.get(name)


class OldBlockLayout(object):
    '''Represents the layout of a block. Saves the positions of all obstacles
    within the block as well as a graphic of the block.'''

    def __init__(self):
        '''() - initialises a blank block layout.'''
        self.filename = None
        self.name = None
        self.graphics = None
        self.mirrorLayout = self
        self.reversed = False
        self.kind = None
        self.graphicsIO = None
        self._pandaTexture = None
        self.newLayout = None

    def setNewLayout(self, newLayout):
        self.newLayout = newLayout
        if self.mirrorLayout is not self:
            self.mirrorLayout.newLayout = newLayout

    def getPandaTexture(self, panda):
        '''
        Cache the Panda3D texture object for this block layout to save time and
        memory.
        '''
        from panda3d.core import Texture, Filename

        if not self._pandaTexture:
            # Write the graphics to a file because that's what panda requires.
            # NamedTemporaryFile sometimes returns a path with wrong casing on
            # Windows, so do it Panda's way instead.
            pandaFile = Filename.temporary('', '')
            f = open(pandaFile.toOsSpecific(), 'wb')
            try:
                with f:
                    f.write(self.graphicsIO.getvalue())
                self._pandaTexture = panda.loader.loadTexture(pandaFile.getFullpath())
            finally:
                os.unlink(f.name)
            self._pandaTexture.setWrapU(Texture.WM_clamp)
            self._pandaTexture.setWrapV(Texture.WM_clamp)
        return self._pandaTexture

    @property
    def forwardLayout(self):
        if self.reversed:
            return self.mirrorLayout
        else:
            return self

    @property
    def key(self):
        '''
        Returns a key by which this block layout may be uniquely identified.
        The block may be obtained from the LayoutDatabase using its
        .getLayoutByKey() method.
        '''
        return (self.kind, self.checksum, self.reversed)

    def setProperties(
            self, symmetrical, checksum, blockType, filename, graphicsIO):
        '''
        symmetrical     Boolean - is this block symmetrical? If set to True,
                        this block will also create a block which is the exact
                        mirror of this block.
        '''
        self.checksum = checksum
        self.kind = blockType
        self.filename = filename
        self.name = os.path.basename(filename)
        self.graphicsIO = graphicsIO

        # Set up the graphic.
        self.graphics = StreamBlockGraphics(graphicsIO)

        # If it's not symmetrical, create a mirror block.
        if symmetrical:
            self.mirrorLayout = self
        else:
            self.mirrorLayout = OldBlockLayout()
            self.mirrorLayout.reversed = True
            self.mirrorLayout.mirrorLayout = self
            self.mirrorLayout.checksum = checksum
            self.mirrorLayout.graphics = StreamBlockGraphics(graphicsIO, True)
            self.mirrorLayout.kind = self.kind
            self.mirrorLayout.filename = self.filename
            self.mirrorLayout.name = self.name
            self.mirrorLayout.graphicsIO = self.graphicsIO

    def applyTo(self, block):
        '''Applies this layout to the specified map block.'''
        block.layout = self
        block.graphics = self.graphics
        block.blocked = self.newLayout.blocked


class BaseBlockGraphics(object):
    '''Defers loading of graphic until needed.'''

    def __init__(self, reversed):
        self._miniGraphics = {}
        self._rawGraphic = None
        self._graphic = None
        self._reversed = reversed

    def getMini(self, app, scale):
        try:
            result = self._miniGraphics[scale]
        except KeyError:
            width = int(self.getGraphic(app).get_rect().width / scale + 0.5)
            height = int(self.getGraphic(app).get_rect().height / scale + 0.5)

            result = pygame.transform.smoothscale(
                self._rawGraphic, (width, height))
            self._miniGraphics[scale] = result

        return result

    def getGraphic(self, app):
        if self._graphic is not None:
            return self._graphic

        # Load the graphic.
        self._rawGraphic = pygame.image.load(self._getFile(), 'png')

        if self._reversed:
            # Flip the graphic.
            self._rawGraphic = pygame.transform.flip(
                self._rawGraphic, True, False)

        self._graphic = self._rawGraphic.convert_alpha()

        return self._graphic


class StreamBlockGraphics(BaseBlockGraphics):
    def __init__(self, stream, reversed=False):
        BaseBlockGraphics.__init__(self, reversed)
        self._stream = stream

    def _getFile(self):
        result = io.BytesIO(self._stream.getvalue())
        return result
