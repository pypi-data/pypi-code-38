#!/usr/bin/env python
from __future__ import absolute_import, print_function

import hashlib
import os
import random
import shutil
import stat
import struct
import sys
import tempfile
import time
import unittest

import silenttestrunner

# Load the local remotefilelog, not the system one
sys.path[0:0] = [os.path.join(os.path.dirname(__file__), '..')]
from mercurial.node import nullid
from mercurial import (
    pycompat,
    ui as uimod,
)
from hgext.remotefilelog import (
    basepack,
    constants,
    datapack,
)

class datapacktestsbase(object):
    def __init__(self, datapackreader, paramsavailable):
        self.datapackreader = datapackreader
        self.paramsavailable = paramsavailable

    def setUp(self):
        self.tempdirs = []

    def tearDown(self):
        for d in self.tempdirs:
            shutil.rmtree(d)

    def makeTempDir(self):
        tempdir = pycompat.bytestr(tempfile.mkdtemp())
        self.tempdirs.append(tempdir)
        return tempdir

    def getHash(self, content):
        return hashlib.sha1(content).digest()

    def getFakeHash(self):
        return b''.join(pycompat.bytechr(random.randint(0, 255))
                        for _ in range(20))

    def createPack(self, revisions=None, packdir=None):
        if revisions is None:
            revisions = [(b"filename", self.getFakeHash(), nullid, b"content")]

        if packdir is None:
            packdir = self.makeTempDir()

        packer = datapack.mutabledatapack(uimod.ui(), packdir, version=2)

        for args in revisions:
            filename, node, base, content = args[0:4]
            # meta is optional
            meta = None
            if len(args) > 4:
                meta = args[4]
            packer.add(filename, node, base, content, metadata=meta)

        path = packer.close()
        return self.datapackreader(path)

    def _testAddSingle(self, content):
        """Test putting a simple blob into a pack and reading it out.
        """
        filename = b"foo"
        node = self.getHash(content)

        revisions = [(filename, node, nullid, content)]
        pack = self.createPack(revisions)
        if self.paramsavailable:
            self.assertEqual(pack.params.fanoutprefix,
                             basepack.SMALLFANOUTPREFIX)

        chain = pack.getdeltachain(filename, node)
        self.assertEqual(content, chain[0][4])

    def testAddSingle(self):
        self._testAddSingle(b'')

    def testAddSingleEmpty(self):
        self._testAddSingle(b'abcdef')

    def testAddMultiple(self):
        """Test putting multiple unrelated blobs into a pack and reading them
        out.
        """
        revisions = []
        for i in range(10):
            filename = b"foo%d" % i
            content = b"abcdef%d" % i
            node = self.getHash(content)
            revisions.append((filename, node, self.getFakeHash(), content))

        pack = self.createPack(revisions)

        for filename, node, base, content in revisions:
            entry = pack.getdelta(filename, node)
            self.assertEqual((content, filename, base, {}), entry)

            chain = pack.getdeltachain(filename, node)
            self.assertEqual(content, chain[0][4])

    def testAddDeltas(self):
        """Test putting multiple delta blobs into a pack and read the chain.
        """
        revisions = []
        filename = b"foo"
        lastnode = nullid
        for i in range(10):
            content = b"abcdef%d" % i
            node = self.getHash(content)
            revisions.append((filename, node, lastnode, content))
            lastnode = node

        pack = self.createPack(revisions)

        entry = pack.getdelta(filename, revisions[0][1])
        realvalue = (revisions[0][3], filename, revisions[0][2], {})
        self.assertEqual(entry, realvalue)

        # Test that the chain for the final entry has all the others
        chain = pack.getdeltachain(filename, node)
        for i in range(10):
            content = b"abcdef%d" % i
            self.assertEqual(content, chain[-i - 1][4])

    def testPackMany(self):
        """Pack many related and unrelated objects.
        """
        # Build a random pack file
        revisions = []
        blobs = {}
        random.seed(0)
        for i in range(100):
            filename = b"filename-%d" % i
            filerevs = []
            for j in range(random.randint(1, 100)):
                content = b"content-%d" % j
                node = self.getHash(content)
                lastnode = nullid
                if len(filerevs) > 0:
                    lastnode = filerevs[random.randint(0, len(filerevs) - 1)]
                filerevs.append(node)
                blobs[(filename, node, lastnode)] = content
                revisions.append((filename, node, lastnode, content))

        pack = self.createPack(revisions)

        # Verify the pack contents
        for (filename, node, lastnode), content in sorted(blobs.items()):
            chain = pack.getdeltachain(filename, node)
            for entry in chain:
                expectedcontent = blobs[(entry[0], entry[1], entry[3])]
                self.assertEqual(entry[4], expectedcontent)

    def testPackMetadata(self):
        revisions = []
        for i in range(100):
            filename = b'%d.txt' % i
            content = b'put-something-here \n' * i
            node = self.getHash(content)
            meta = {constants.METAKEYFLAG: i ** 4,
                    constants.METAKEYSIZE: len(content),
                    b'Z': b'random_string',
                    b'_': b'\0' * i}
            revisions.append((filename, node, nullid, content, meta))
        pack = self.createPack(revisions)
        for name, node, x, content, origmeta in revisions:
            parsedmeta = pack.getmeta(name, node)
            # flag == 0 should be optimized out
            if origmeta[constants.METAKEYFLAG] == 0:
                del origmeta[constants.METAKEYFLAG]
            self.assertEqual(parsedmeta, origmeta)

    def testGetMissing(self):
        """Test the getmissing() api.
        """
        revisions = []
        filename = b"foo"
        lastnode = nullid
        for i in range(10):
            content = b"abcdef%d" % i
            node = self.getHash(content)
            revisions.append((filename, node, lastnode, content))
            lastnode = node

        pack = self.createPack(revisions)

        missing = pack.getmissing([(b"foo", revisions[0][1])])
        self.assertFalse(missing)

        missing = pack.getmissing([(b"foo", revisions[0][1]),
                                   (b"foo", revisions[1][1])])
        self.assertFalse(missing)

        fakenode = self.getFakeHash()
        missing = pack.getmissing([(b"foo", revisions[0][1]),
                                   (b"foo", fakenode)])
        self.assertEqual(missing, [(b"foo", fakenode)])

    def testAddThrows(self):
        pack = self.createPack()

        try:
            pack.add(b'filename', nullid, b'contents')
            self.assertTrue(False, "datapack.add should throw")
        except RuntimeError:
            pass

    def testBadVersionThrows(self):
        pack = self.createPack()
        path = pack.path + b'.datapack'
        with open(path, 'rb') as f:
            raw = f.read()
        raw = struct.pack('!B', 255) + raw[1:]
        os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
        with open(path, 'wb+') as f:
            f.write(raw)

        try:
            pack = self.datapackreader(pack.path)
            self.assertTrue(False, "bad version number should have thrown")
        except RuntimeError:
            pass

    def testMissingDeltabase(self):
        fakenode = self.getFakeHash()
        revisions = [(b"filename", fakenode, self.getFakeHash(), b"content")]
        pack = self.createPack(revisions)
        chain = pack.getdeltachain(b"filename", fakenode)
        self.assertEqual(len(chain), 1)

    def testLargePack(self):
        """Test creating and reading from a large pack with over X entries.
        This causes it to use a 2^16 fanout table instead."""
        revisions = []
        blobs = {}
        total = basepack.SMALLFANOUTCUTOFF + 1
        for i in pycompat.xrange(total):
            filename = b"filename-%d" % i
            content = filename
            node = self.getHash(content)
            blobs[(filename, node)] = content
            revisions.append((filename, node, nullid, content))

        pack = self.createPack(revisions)
        if self.paramsavailable:
            self.assertEqual(pack.params.fanoutprefix,
                             basepack.LARGEFANOUTPREFIX)

        for (filename, node), content in blobs.items():
            actualcontent = pack.getdeltachain(filename, node)[0][4]
            self.assertEqual(actualcontent, content)

    def testPacksCache(self):
        """Test that we remember the most recent packs while fetching the delta
        chain."""

        packdir = self.makeTempDir()
        deltachains = []

        numpacks = 10
        revisionsperpack = 100

        for i in range(numpacks):
            chain = []
            revision = (b'%d' % i, self.getFakeHash(), nullid, b"content")

            for _ in range(revisionsperpack):
                chain.append(revision)
                revision = (
                    b'%d' % i,
                    self.getFakeHash(),
                    revision[1],
                    self.getFakeHash()
                )

            self.createPack(chain, packdir)
            deltachains.append(chain)

        class testdatapackstore(datapack.datapackstore):
            # Ensures that we are not keeping everything in the cache.
            DEFAULTCACHESIZE = numpacks // 2

        store = testdatapackstore(uimod.ui(), packdir)

        random.shuffle(deltachains)
        for randomchain in deltachains:
            revision = random.choice(randomchain)
            chain = store.getdeltachain(revision[0], revision[1])

            mostrecentpack = next(iter(store.packs), None)
            self.assertEqual(
                mostrecentpack.getdeltachain(revision[0], revision[1]),
                chain
            )

            self.assertEqual(randomchain.index(revision) + 1, len(chain))

    # perf test off by default since it's slow
    def _testIndexPerf(self):
        random.seed(0)
        print("Multi-get perf test")
        packsizes = [
            100,
            10000,
            100000,
            500000,
            1000000,
            3000000,
        ]
        lookupsizes = [
            10,
            100,
            1000,
            10000,
            100000,
            1000000,
        ]
        for packsize in packsizes:
            revisions = []
            for i in pycompat.xrange(packsize):
                filename = b"filename-%d" % i
                content = b"content-%d" % i
                node = self.getHash(content)
                revisions.append((filename, node, nullid, content))

            path = self.createPack(revisions).path

            # Perf of large multi-get
            import gc
            gc.disable()
            pack = self.datapackreader(path)
            for lookupsize in lookupsizes:
                if lookupsize > packsize:
                    continue
                random.shuffle(revisions)
                findnodes = [(rev[0], rev[1]) for rev in revisions]

                start = time.time()
                pack.getmissing(findnodes[:lookupsize])
                elapsed = time.time() - start
                print ("%s pack %d lookups = %0.04f" %
                       (('%d' % packsize).rjust(7),
                        ('%d' % lookupsize).rjust(7),
                        elapsed))

            print("")
            gc.enable()

        # The perf test is meant to produce output, so we always fail the test
        # so the user sees the output.
        raise RuntimeError("perf test always fails")

class datapacktests(datapacktestsbase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        datapacktestsbase.__init__(self, datapack.datapack, True)
        unittest.TestCase.__init__(self, *args, **kwargs)

# TODO:
# datapack store:
# - getmissing
# - GC two packs into one

if __name__ == '__main__':
    if pycompat.iswindows:
        sys.exit(80)    # Skip on Windows
    silenttestrunner.main(__name__)
