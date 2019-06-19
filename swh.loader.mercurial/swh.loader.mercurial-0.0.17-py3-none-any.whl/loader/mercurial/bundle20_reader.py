# Copyright (C) 2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""This document contains code for extracting all of the data from
Mercurial version 2 bundle file. It is referenced by
bundle20_loader.py

"""

# =============================================================================
# =============================================================================
#                                  BACKGROUND
# =============================================================================
# =============================================================================
#
# https://www.mercurial-scm.org/wiki/BundleFormat says:
# "The new bundle format design is described on the BundleFormat2 page."
#
# https://www.mercurial-scm.org/wiki/BundleFormat2#Format_of_the_Bundle2_Container says:                # noqa
# "The latest description of the binary format can be found as comment in the
# Mercurial source code."
#
# https://www.mercurial-scm.org/repo/hg/file/default/mercurial/help/internals/bundles.txt says:         # noqa
# "The 'HG20' format is not yet documented here. See the inline comments in
# 'mercurial/exchange.py' for now."
#
# -----------------------------------------------------------------------------
# Avi says:
# -----------------------------------------------------------------------------
#
# All of the above official(?) statements seem to be quite wrong.
#
# The mercurial-scm wiki is a cluster#@*& of missing pages, bad links, wrong
# information, obsolete information, undecipherable names, and half-started
# leavings that only sort of look like content. I don't understand who or what
# it's there for. I think that means it's not there for me?
#
# https://www.mercurial-scm.org/wiki/BundleFormat2#New_header is wrong and
# bizarre, and there isn't any other information on the page.
#
#
# https://www.mercurial-scm.org/repo/hg/file/de86a6872d06/mercurial/help/internals/changegroups.txt     # noqa
# (`hg help internals.changegroups`) is very close to what we need.
# It is accurate, current, and thorough.
# It describes much of the internal structure, which is super helpful if you
# know in advance which info can be trusted, but it doesn't describe any of the
# file-level details, including the file headers and that the entire bundle
# is broken into overlaid 4KB chunks starting from just after the bundle
# header, nor does it describe what any of the component elements are used for,
# nor does it explain the meta-message segment in the blob deltas, nor does it
# explain the file flags occasionally appended to manifest file hashes. Also it
# says: "The [delta data] format is described more fully in 'hg help
# internals.bdiff'", which is also wrong. As far as I can tell, that
# file has never existed.
#
# It does however have one potentially extremely useful note buried in the
# middle that, in hindsight, could have significant implications for complexity
# and performance in future Mercurial loading work.
#
# It says: "In version 1, the delta is always applied against the previous node
# from the changegroup or the first parent if this is the first entry in the
# changegroup."
#
# If the next version of HG support for SWH can reliably get version 1 data,
# then it could be implemented entirely without worrying about ballooning
# memory utilization, which would shrink the code significantly and probably be
# faster too. So maybe HG10 bundles instead of HG20 bundles are superior for
# this task? But then I read that servers can optionally disable serving
# version 1 content, and I like to think that this loader could eventually
# be applied directly to a network stream without an intermediate phase for
# cloning and local bundling, so...It seemed like a good idea at the time?
#
# -----------------------------------------------------------------------------
# Other notes and thoughts:
# -----------------------------------------------------------------------------
# 1)
# This is a relatively minor detail, but
# Mercurial nodes are not content-addressable like Git's are.
#
# https://www.mercurial-scm.org/wiki/Nodeid explains: "If you modify a file,
# commit the change, and then modify it to restore the original contents, the
# contents are the same but the history is different, so the file will get a
# new nodeid. This history-sensitivity is obtained by calculating the nodeid
# from the concatenation of the parent nodeids with the file's contents..."
#
# The result is that we always have to collect and hash everything at least
# once in order to know if we've seen something like it before, because nothing
# tells us that the node we're looking at is unique. We can use node ids for
# linking disparate elements together (e.g. commit to manifest) but not for
# determining whether two elements in the same group are identical in all but
# descendency. So there's no way to save time on duplicate hashing. Well...
# there is the copied_file blob metadata, but, lol.
#
# 2)
# Most of the code complexity is due to dealing with 'version 2' changegroups,
# for which we need to keep track of the entire history of all updates made
# to a given file or working directory tree structure, because a revision
# delta could be applied over any of the prior revisions all the way back to
# rev 0, according to whenever files were branched/merged/uncommitted/etc. For
# very large repositories with a lot of churn, this can quickly expand to
# require multiple gigabytes of space, possibly exceeding RAM availability if
# one desires to keep as much data resident in memory as possible to boost
# performance. mozilla-unified, for instance, produces some 2 million+ blobs
# (1.6 million+ unique). Nested umpteen subdirectory levels deep, those blobs
# balloon into a quantity of directory subtrees that rapidly exceeds an 8GB RAM
# laptop's ability to keep them all active without a good amount of care and
# pruning. The code here tries to strike a balance between memory utilization
# and performance.
#
# This problem is also referenced in the last paragraph of the previous
# section, where potentially this problem wouldn't exist for 'version 1' data
# if we can reliably get it. Can we? Either that or not use bundles at all,
# which has other costs.
#
# 3)
# If the list of changed files stored by the changesets had indicated which
# of those changed files were added or modified and which ones were removed,
# this code could be much faster. Right now we have to perform a huge number of
# substring replacements (see the apply_revdata method) to produce a complete
# file manifest for each commit (as a string!!!) in order to know how to get
# the set of removed files from the next delta. We can intuit from every
# manifest delta which files were modified or added, but I believe there's no
# way to intuit which files were removed without actually having the complete
# prior state and without the list of removals being explicitly given. If you
# have an explicit list of all the files that were removed for any given commit
# changegroup, and you combine that with the delta updates in the manifest
# changegroups which detail the set of files that have been added or modified,
# then you wouldn't even have to apply any of the string deltas to get a
# complete understanding of the set of differences between one manifest and the
# next. Not having this effective speed boost is rather unfortunate; it would
# require only one extra stored byte per commit to differentiate removals and
# would make extracting bundles lightning fast.
# ============================================================================
##

import itertools
import struct

from binascii import unhexlify
from collections import OrderedDict
from datetime import datetime

from .chunked_reader import ChunkedFileReader
from .objects import SelectiveCache


def unpack(fmt_str, source):
    """Utility function for fetching the right number of bytes from a stream to
    satisfy a struct.unpack pattern.

    args:
        fmt_str: a struct.unpack string pattern
                 (e.g. '>I' for 4 bytes big-endian)
        source: any IO object that has a read(<size>) method which
                returns an appropriate sequence of bytes
    """
    ret = struct.unpack(fmt_str, source.read(struct.calcsize(fmt_str)))
    if len(ret) == 1:
        return ret[0]
    return ret


class Bundle20Reader(object):
    """Parser for extracting data from Mercurial Bundle20 files.
    NOTE: Currently only works on uncompressed HG20 bundles, but checking for
    COMPRESSION=<2chars> and loading the appropriate stream decompressor
    at that point would be trivial to add if necessary.

    args:
        bundlefile (str): name of the binary repository bundle file
        cache_filename (str): path to the disk cache used (transited
                              to the SelectiveCache instance)
        cache_size (int): tuning parameter for the upper RAM limit used by
                    historical data caches. The default is defined in the
                    SelectiveCache class.

    """
    NAUGHT_NODE = b'\x00' * 20

    def __init__(self, bundlefile, cache_filename, cache_size=None):
        self.bundlefile = bundlefile
        self.cache_filename = cache_filename
        bfile = open(bundlefile, 'rb', buffering=200*1024*1024)

        btype = bfile.read(4)  # 'HG20'
        if btype != b'HG20':
            raise Exception(bundlefile,
                            b'Not an HG20 bundle. First 4 bytes:' + btype)
        bfile.read(4)  # '\x00\x00\x00\x00'

        self.params = self.read_bundle_header(bfile)
        # print('PARAMETERS', self.params)
        self.num_commits = self.params[b'nbchanges']

        self.filereader = ChunkedFileReader(bfile)

        self.cache_size = cache_size
        self.blobs_offset = None
        self.changes_offset = self.filereader.tell()
        self.changes_next_offset = None
        self.manifests_offset = None
        self.manifests_next_offset = None
        self.id_to_info = {}

    def read_bundle_header(self, bfile):
        """Parse the file header which describes the format and parameters.
        See the structure diagram at the top of the file for more insight.

        args:
            bfile: bundle file handle with the cursor at the start offset of
                   the content header (the 9th byte in the file)

        returns:
            dict of decoded bundle parameters
        """
        unpack('>I', bfile)  # header length
        chg_len = unpack('>B', bfile)  # len('CHANGEGROUP') == 11
        bfile.read(chg_len)  # should say 'CHANGEGROUP'
        unpack('>I', bfile)  # probably \x00\x00\x00\x00

        n_mandatory, n_advisory = unpack('>BB', bfile)  # parameter counts
        mandatory_params = [
                    (key_len, val_len)
                    for key_len, val_len
                    in [unpack('>BB', bfile) for i in range(n_mandatory)]
                    ]
        advisory_params = [
                    (key_len, val_len)
                    for key_len, val_len
                    in [unpack('>BB', bfile) for i in range(n_advisory)]
                    ]
        params = {}

        for key_len, val_len in mandatory_params+advisory_params:
            key = unpack('>%ds' % key_len, bfile)
            val = int(unpack('>%ds' % val_len, bfile))
            params[key] = val

        return params

    def revdata_iterator(self, bytes_to_read):
        """A chunk's revdata section is a series of start/end/length/data_delta
        content updates called RevDiffs that indicate components of a text diff
        applied to the node's basenode. The sum length of all diffs is the
        length indicated at the beginning of the chunk at the start of the
        header.
        See the structure diagram at the top of the file for more insight.

        args:
            bytes_to_read: int total number of bytes in the chunk's revdata
        yields:
            (int, int, read iterator) representing a single text diff component
        """
        while bytes_to_read > 0:
            start_offset = unpack('>I', self.filereader)
            end_offset = unpack('>I', self.filereader)
            blocklen = unpack('>I', self.filereader)
            delta_it = self.filereader.read_iterator(blocklen)
            bytes_to_read -= (12 + blocklen)
            yield (start_offset, end_offset, delta_it)  # RevDiff

    def read_chunk_header(self):
        """The header of a RevChunk describes the id ('node') for the current
        change, the commit id ('linknode') associated with this change,
        the parental heritage ('p1' and 'p2'), and the node to which the
        revdata updates will apply ('basenode'). 'linknode' is the same as
        'node' when reading the commit log because any commit is already
        itself. 'basenode' for a changeset will be NAUGHT_NODE, because
        changeset chunks include complete information and not diffs.
        See the structure diagram at the top of the file for more insight.

        returns:
            dict of the next delta header
        """
        header = self.filereader.read(100)
        header = {
            'node': header[0:20],
            'p1': header[20:40],
            'p2': header[40:60],
            'basenode': header[60:80],
            'linknode': header[80:100]
        }
        return header

    def read_revchunk(self):
        """Fetch a complete RevChunk.
        A RevChunk contains the collection of line changes made in a particular
        update. header['node'] identifies which update. Commits, manifests, and
        files all have these. Each chunk contains an indicator of the whole
        chunk size, an update header, and then the body of the update as a
        series of text diff components.
        See the structure diagram at the top of the file for more insight.

        returns:
            tuple(dict, iterator) of (header, chunk data) if there is another
            chunk in the group, else None
        """
        size = unpack('>I', self.filereader) - 104
        if size >= 0:
            header = self.read_chunk_header()
            return (header, self.revdata_iterator(size))
        else:
            return None  # NullChunk

    def extract_commit_metadata(self, data):
        """Converts the binary commit metadata format into a dict.

        args:
            data: bytestring of encoded commit information

        returns:
            dict of decoded commit information
        """
        parts, message = data.split(b'\n\n', 1)
        parts = parts.split(b'\n')
        commit = {}
        commit['message'] = message
        commit['manifest'] = unhexlify(parts[0])
        commit['user'] = parts[1]
        tstamp, tz, *extra = parts[2].split(b' ')
        commit['time'] = datetime.fromtimestamp(float(tstamp))
        commit['time_offset_seconds'] = int(tz)
        if extra:
            commit['extra'] = b' '.join(extra)
        commit['changed_files'] = parts[3:]
        return commit

    def skip_sections(self, num_sections=1):
        """Skip past <num_sections> sections quickly.

        args:
            num_sections: int number of sections to skip
        """
        for i in range(num_sections):
            size = unpack('>I', self.filereader)
            while size >= 104:
                self.filereader.seek(size - 4, from_current=True)
                size = unpack('>I', self.filereader)

    def apply_revdata(self, revdata_it, prev_state):
        """Compose the complete text body for a change from component deltas.

        args:
            revdata_it: output from the revdata_iterator method
            prev_state: bytestring the base complete text on which the new
                        deltas will be applied
        returns:
            (bytestring, list, list) the new complete string and lists of added
            and removed components (used in manifest processing)
        """
        state = []
        added = []
        removed = []
        next_start = 0

        for delta_start, delta_end, rev_diff_it in revdata_it:
            removed.append(prev_state[delta_start:delta_end])
            added.append(b''.join(rev_diff_it))

            state.append(prev_state[next_start:delta_start])
            state.append(added[-1])
            next_start = delta_end

        state.append(prev_state[next_start:])
        state = b''.join(state)

        return (state, added, removed)

    def skim_headers(self):
        """Get all header data from a change group but bypass processing of the
        contained delta components.

        yields:
            output of read_chunk_header method for all chunks in the group
        """
        size = unpack('>I', self.filereader) - 104
        while size >= 0:
            header = self.read_chunk_header()
            self.filereader.seek(size, from_current=True)
            yield header
            size = unpack('>I', self.filereader) - 104

    def group_iterator(self):
        """Bundle sections are called groups. These are composed of one or more
        revision chunks of delta components. Iterate over all the chunks in a
        group and hand each one back.

        yields:
            see output of read_revchunk method
        """
        revchunk = self.read_revchunk()
        while revchunk:  # A group is terminated by a NullChunk
            yield revchunk  # (header, revdata_iterator)
            revchunk = self.read_revchunk()

    def yield_group_objects(self, cache_hints=None, group_offset=None):
        """Bundles are sectioned into groups: the log of all commits, the log
        of all manifest changes, and a series of logs of blob changes (one for
        each file). All groups are structured the same way, as a series of
        revisions each with a series of delta components. Iterate over the
        current group and return the completed object data for the current
        update by applying all of the internal delta components to each prior
        revision.

        args:
            cache_hints: see build_cache_hints (this will be built
                 automatically if not pre-built and passed in)
            group_offset: int file position of the start of the desired group

        yields:
            (dict, bytestring, list, list) the output from read_chunk_header
                followed by the output from apply_revdata
        """
        if group_offset is not None:
            self.filereader.seek(group_offset)

        if cache_hints is None:
            cache_hints = self.build_cache_hints()

        data_cache = SelectiveCache(max_size=self.cache_size,
                                    cache_hints=cache_hints,
                                    filename=self.cache_filename)

        # Loop over all revisions in the group
        data = b''
        for header, revdata_it in self.group_iterator():
            node = header['node']
            basenode = header['basenode']

            data = data_cache.fetch(basenode) or b''

            data, added, removed = self.apply_revdata(revdata_it, data)

            data_cache.store(node, data)

            yield (header, data, added, removed)  # each RevChunk

    def extract_meta_from_blob(self, data):
        """File revision data sometimes begins with a metadata section of
        dubious value. Strip it off and maybe decode it. It seems to be mostly
        useless. Why indicate that a file node is a copy of another node? You
        can already get that information from the delta header.

        args:
            data: bytestring of one revision of a file, possibly with metadata
                embedded at the start

        returns:
            (bytestring, dict) of (the blob data, the meta information)
        """
        meta = {}
        if data.startswith(b'\x01\n'):
            empty, metainfo, data = data.split(b'\x01\n', 2)
            metainfo = b'\x01\n' + metainfo + b'\x01\n'
            if metainfo.startswith(b'copy:'):
                # direct file copy (?)
                copyinfo = metainfo.split(b'\n')
                meta['copied_file'] = copyinfo[0][6:]
                meta['copied_rev'] = copyinfo[1][9:]
            elif metainfo.startswith(b'censored:'):
                # censored revision deltas must be full-replacements (?)
                meta['censored'] = metainfo
            else:
                # no idea
                meta['text'] = metainfo
        return data, meta

    def seek_changelog(self):
        """Seek to the beginning of the change logs section.
        """
        self.filereader.seek(self.changes_offset)

    def seek_manifests(self):
        """Seek to the beginning of the manifests section.
        """
        if self.manifests_offset is None:
            self.seek_changelog()
            self.skip_sections(1)  # skip past commits
            self.manifests_offset = self.filereader.tell()
        else:
            self.filereader.seek(self.manifests_offset)

    def seek_filelist(self):
        """Seek to the beginning of the file changes section.
        """
        if self.blobs_offset is None:
            self.seek_manifests()
            self.skip_sections(1)  # skip past manifests
            self.blobs_offset = self.filereader.tell()
        else:
            self.filereader.seek(self.blobs_offset)

    def yield_all_blobs(self):
        """Gets blob data from the bundle.

        yields:
            (bytestring, (bytestring, int, dict)) of
                (blob data, (file name, start offset of the file within the
                bundle, node header))
        """
        self.seek_filelist()

        # Loop through all files that have commits
        size = unpack('>I', self.filereader)
        while size > 0:
            file_name = self.filereader.read(size-4)
            file_start_offset = self.filereader.tell()
            # get all of the blobs for each file
            for header, data, *_ in self.yield_group_objects():
                blob, meta = self.extract_meta_from_blob(data)
                yield blob, (file_name, file_start_offset, header)
            size = unpack('>I', self.filereader)

    def yield_all_changesets(self):
        """Gets commit data from the bundle.

        yields:
            (dict, dict) of (read_chunk_header output,
                 extract_commit_metadata output)
        """
        self.seek_changelog()
        for header, data, *_ in self.yield_group_objects():
            changeset = self.extract_commit_metadata(data)
            yield (header, changeset)

    def yield_all_manifest_deltas(self, cache_hints=None):
        """Gets manifest data from the bundle.
        In order to process the manifests in a reasonable amount of time, we
        want to use only the deltas and not the entire manifest at each change,
        because if we're processing them in sequential order (we are) then we
        already have the previous state so we only need the changes.

        args:
            cache_hints: see build_cache_hints method

        yields:
            (dict, dict, dict) of (read_chunk_header output,
                extract_manifest_elements output on added/modified files,
                extract_manifest_elements on removed files)
        """
        self.seek_manifests()
        for header, data, added, removed in self.yield_group_objects(
            cache_hints=cache_hints
        ):
            added = self.extract_manifest_elements(added)
            removed = self.extract_manifest_elements(removed)
            yield (header, added, removed)

    def build_manifest_hints(self):
        """Just a minor abstraction shortcut for the build_cache_hints method.

        returns:
            see build_cache_hints method
        """
        self.seek_manifests()
        return self.build_cache_hints()

    def build_cache_hints(self):
        """The SelectiveCache class that we use in building nodes can accept a
        set of key counters that makes its memory usage much more efficient.

        returns:
            dict of key=a node id, value=the number of times we
            will need data from that node when building subsequent nodes
        """
        cur_pos = self.filereader.tell()
        hints = OrderedDict()
        prev_node = None
        for header in self.skim_headers():
            basenode = header['basenode']
            if (basenode != self.NAUGHT_NODE) and (basenode != prev_node):
                # If the base isn't immediately prior, then cache it once more.
                hints[basenode] = hints.get(basenode, 0) + 1
            prev_node = header['node']
        self.filereader.seek(cur_pos)
        return hints

    def extract_manifest_elements(self, data):
        """Parses data that looks like a manifest. In practice we only pass in
        the bits extracted from the application of a manifest delta describing
        which files were added/modified or which ones were removed.

        args:
            data: either a string or a list of strings that, when joined,
              embodies the composition of a manifest.

              This takes the form
              of repetitions of (without the brackets)::

                b'<file_path>\x00<file_node>[flag]\\n' ...repeat...

              where ``[flag]`` may or may not be there depending on
              whether the file is specially flagged as executable or
              something

        returns:
            dict: ``{file_path: (file_node, permissions), ...}`` where
            permissions is given according to the flag that optionally exists
            in the data
        """
        elements = {}
        if isinstance(data, str):
            data = data.split(b'\n')
        else:
            data = itertools.chain.from_iterable(
                [chunk.split(b'\n') for chunk in data]
            )

        for line in data:
            if line != b'':
                f = line.split(b'\x00')

                node = f[1]
                flag_bytes = node[40:]

                elements[f[0]] = (
                    unhexlify(node[:40]),
                    b'l' in flag_bytes,
                    b'755' if (b'x' in flag_bytes) else b'644'
                )

        return elements
