import os
import re
import shutil
import tempfile
import logging
import itertools as it
from binascii import b2a_hex
from datetime import datetime
from cStringIO import StringIO
from ConfigParser import ConfigParser
from shutil import rmtree
from collections import defaultdict
from contextlib import contextmanager

os.environ['HGRCPATH'] = ''  # disable loading .hgrc
from mercurial import ui, hg, cmdutil, commands, scmutil, copies
from mercurial import copies as cp
from mercurial.error import RepoLookupError, RevlogError
from mercurial.node import nullid

import tg
from paste.deploy.converters import asbool
from pymongo.errors import DuplicateKeyError
from tg import tmpl_context as c

from ming.base import Object
from ming.orm import Mapper
from ming.utils import LazyProperty

from allura import model as M
from allura.lib import helpers as h
from allura.model.repository import (
    topological_sort,
    GitLikeTree,
    zipdir,
    Commit,
    CommitDoc,
    TreeDoc,
)

log = logging.getLogger(__name__)


class Repository(M.Repository):
    tool_name='Hg'
    repo_id='hg'
    type_s='Hg Repository'
    class __mongometa__:
        name='hg-repository'

    @LazyProperty
    def _impl(self):
        return HgImplementation(self)

    def merge_command(self, merge_request):
        '''Return the command to merge a given commit into a given target branch'''
        cmd = 'hg checkout %s\nhg pull -r %s %s' % (
            merge_request.target_branch,
            merge_request.downstream.commit_id,
            merge_request.downstream_repo.clone_url_first(anon=False, username=c.user.username),
        )
        cmd += '\nhg merge -r {}\nhg commit -m "Merge {}"'.format(
            merge_request.downstream.commit_id,
            merge_request.source_branch,
        )
        return cmd

    @contextmanager
    def _tmp_clone(self):
        tmp_path = tempfile.mkdtemp()
        # !$ hg doesn't like unicode as urls
        _, tmp_repo = hg.clone(
            HgUI(),
            {},
            self.full_fs_path.encode('utf-8'),
            tmp_path.encode('utf-8'),
            update=False)
        try:
            yield tmp_repo.local()
        finally:
            shutil.rmtree(tmp_path, ignore_errors=True)

    def _merge(self, mr, tmp_repo, _ui):
        """Common code for :meth can_merge: and :meth merge:

        Returns a tuple (has_conflicts_flag, exception_or_none).
        """
        # switch to target branch and update working copy to it
        commands.branch(_ui, tmp_repo, mr.target_branch)
        commands.update(_ui, tmp_repo, mr.target_branch)
        # pull source branch
        commands.pull(
            _ui,
            tmp_repo,
            source=mr.downstream_repo.full_fs_path,
            branch=[mr.source_branch])
        if mr.source_branch == mr.target_branch:
            merge_args = (_ui, tmp_repo)
        else:
            merge_args = (_ui, tmp_repo, mr.source_branch)
        try:
            # merge can return 0 or False if there are no conflicts
            conflicts = bool(commands.merge(*merge_args))
        except hg.error.Abort as e:
            if getattr(e, 'message', None) == 'nothing to merge':
                conflicts = False
            else:
                return True, e
        return conflicts, None

    def can_merge(self, mr):
        """
        Given merge request `mr` determine if it can be merged w/o conflicts.
        """
        with self._tmp_clone() as tmp_repo:
            has_conflicts, _ = self._merge(mr, tmp_repo, HgUI())
            return not has_conflicts

    def merge(self, mr):
        with self._tmp_clone() as tmp_repo:
            _ui = HgUI()
            has_conflicts, exc = self._merge(mr, tmp_repo, _ui)
            if not has_conflicts:
                msg = 'Merge {} branch {} into {}\n\n{}'.format(
                    mr.downstream_repo.url(),
                    mr.source_branch,
                    mr.target_branch,
                    h.absurl(mr.url()))
                author = h.really_unicode(
                    c.user.display_name or c.user.username)
                commands.commit(_ui, tmp_repo, message=msg, user=author)
                commands.push(
                    _ui,
                    tmp_repo,
                    dest=self.full_fs_path,
                    new_branch=True,
                    branch=[mr.target_branch])
            else:
                exc = exc or Exception("Can't merge %s" % mr.url())
                raise exc

    def rev_to_commit_id(self, rev):
        return self._impl.rev_parse(rev)


class HgUI(ui.ui):
    '''Hg UI subclass that suppresses reporting of untrusted hgrc files.'''
    def __init__(self, *args, **kwargs):
        super(HgUI, self).__init__(*args, **kwargs)
        self._reportuntrusted = False


class HgImplementation(M.RepositoryImplementation):
    re_hg_user = re.compile('(.*) <(.*)>')

    def __init__(self, repo):
        self._repo = repo

    @LazyProperty
    def _hg(self):
        try:
            return hg.repository(HgUI(), self._repo.full_fs_path)
        except hg.error.RepoError as e:
            log.error('Error looking up repo at %s: %s',
                    self._repo.full_fs_path, e)
            return None

    def branchtags(self):
        '''Return a dict where branch names map to the tipmost head of
        the branch, open heads come before closed.

        It's re-implementation of hg API method, which was removed in latest versions.
        '''
        bt = {}
        for bn, heads in self._hg.branchmap().iteritems():
            head = None
            for i in range(len(heads)-1, -1, -1):
                _head = heads[i]
                if 'close' not in self._hg.changelog.read(_head)[5]:
                    head = _head
                    break
            # no open heads were found
            if head is None:
                head = heads[-1]
            bt[bn] = head
        return bt

    def init(self):
        fullname = self._setup_paths()
        log.info('hg init %s', fullname)
        if os.path.exists(fullname):
            shutil.rmtree(fullname)
        repo = hg.repository(
            ui.ui(), self._repo.full_fs_path, create=True)
        self.__dict__['_hg'] = repo
        self._setup_special_files()
        self._repo.set_status('ready')

    def clone_from(self, source_url):
        '''Initialize a repo as a clone of another'''
        self._repo.set_status('cloning')
        log.info('Initialize %r as a clone of %s',
                 self._repo, source_url)
        try:
            fullname = self._setup_paths(create_repo_dir=False)
            if os.path.exists(fullname):
                shutil.rmtree(fullname)
            # !$ hg doesn't like unicode as urls
            srcpeer, destpeer = hg.clone(
                ui.ui(),
                {},
                source_url.encode('utf-8'),
                self._repo.full_fs_path.encode('utf-8'),
                update=False)
            self.__dict__['_hg'] = destpeer.local()
            self._setup_special_files(source_url)
        except:
            self._repo.set_status('ready')
            raise

    def commit(self, rev):
        '''Return a Commit object.  rev can be _id or a branch/tag name'''
        result = Commit.query.get(_id=rev)
        if result is None:
            try:
                impl = self._hg[str(rev)]
                result = Commit.query.get(_id=impl.hex())
            except Exception, e:
                log.exception(e)
        if result is None:
            return None
        result.set_context(self._repo)
        return result

    def real_parents(self, ci):
        """Return all parents of a commit, excluding the 'null revision' (a
        fake revision added as the parent of the root commit by the Hg api).
        """
        return [p for p in ci.parents() if p]

    def all_commit_ids(self):
        """Return a list of commit ids, starting with the head(s) and ending
        with the root (first commit) of the tree.
        """
        graph = {}
        to_visit = [ self._hg[hd] for hd in self._hg.heads() ]
        while to_visit:
            obj = to_visit.pop()
            if obj.hex() in graph: continue
            parents = self.real_parents(obj)
            graph[obj.hex()] = set(
                p.hex() for p in parents
                if p.hex() != obj.hex())
            to_visit += parents
        return reversed([ ci for ci in topological_sort(graph) ])

    def new_commits(self, all_commits=False):
        graph = {}
        to_visit = [ self._hg[hd] for hd in self._hg.heads() ]
        while to_visit:
            obj = to_visit.pop()
            if obj.hex() in graph: continue
            if not all_commits:
                # Look up the object
                if Commit.query.find(dict(_id=obj.hex())).count():
                    graph[obj.hex()] = set() # mark as parentless
                    continue
            parents = self.real_parents(obj)
            graph[obj.hex()] = set(
                p.hex() for p in parents
                if p.hex() != obj.hex())
            to_visit += parents
        return list(topological_sort(graph))

    def refresh_commit_info(self, oid, seen, lazy=True):
        ci_doc = CommitDoc.m.get(_id=oid)
        if ci_doc and lazy: return False
        obj = self._hg[oid]
        # Save commit metadata
        mo = self.re_hg_user.match(obj.user())
        if mo:
            user_name, user_email = mo.groups()
        else:
            user_name = user_email = obj.user()
        user = Object(
            name=h.really_unicode(user_name),
            email=h.really_unicode(user_email),
            date=datetime.utcfromtimestamp(obj.date()[0]))
        fake_tree = self._tree_from_changectx(obj)
        args = dict(
            tree_id=fake_tree.hex(),
            committed=user,
            authored=user,
            message=h.really_unicode(obj.description() or ''),
            child_ids=[],
            parent_ids=[ p.hex() for p in self.real_parents(obj)
                                 if p.hex() != obj.hex() ])
        if ci_doc:
            ci_doc.update(args)
            ci_doc.m.save()
        else:
            ci_doc = CommitDoc(dict(args, _id=oid))
            try:
                ci_doc.m.insert(safe=True)
            except DuplicateKeyError:
                if lazy: return False
        self.refresh_tree_info(fake_tree, seen, lazy)
        return True

    def refresh_tree_info(self, tree, seen, lazy=True):
        if lazy and tree.hex() in seen: return
        seen.add(tree.hex())
        doc = TreeDoc(dict(
                _id=tree.hex(),
                tree_ids=[],
                blob_ids=[],
                other_ids=[]))
        for name, t in tree.trees.iteritems():
            self.refresh_tree_info(t, seen, lazy)
            doc.tree_ids.append(
                dict(name=h.really_unicode(name), id=t.hex()))
        for name, oid in tree.blobs.iteritems():
            doc.blob_ids.append(
                dict(name=h.really_unicode(name), id=oid))
        doc.m.save(safe=False)
        return doc

    def _commit_info(self, ctx):
        """Returns dict with info about commit

        :param ctx: hg's change context
        """
        branches = defaultdict(list)
        for name, head in self.branchtags().iteritems():
            branches[self._hg[head].hex()].append(name)
        user = ctx.user()
        match = self.re_hg_user.match(user)
        if match:
            name, email = match.groups()
        else:
            name, email = (user or '--none--', '')
        return {
            'id': ctx.hex(),
            'message': h.really_unicode(ctx.description() or '--none--'),
            'authored': {
                    'name': h.really_unicode(name),
                    'email': h.really_unicode(email),
                    'date': datetime.utcfromtimestamp(ctx.date()[0]),
                },
            'committed': {
                    'name': h.really_unicode(name),
                    'email': h.really_unicode(email),
                    'date': datetime.utcfromtimestamp(ctx.date()[0]),
                },
            'refs': branches[ctx.hex()] + ctx.tags(),
            'parents': [pctx.hex() for pctx in ctx.parents() if pctx.rev() > -1],
            'size': None,
            'rename_details': {},
        }

    def log(self, revs=None, path=None, exclude=None, id_only=True, **kw):
        path = path.strip('/').encode('utf-8') if path else None
        revs = ['%s:0' % r for r in revs or []]
        pats = ['path:%s' % path] if path else []
        exclude = exclude or []
        match = scmutil.match(self._hg[None], pats=pats)
        noop = lambda ctx, fns: None
        change_revs = cmdutil.walkchangerevs(self._hg, match, {'rev': revs, 'prune': exclude}, noop)
        for ctx in change_revs:
            if id_only:
                yield ctx.hex()
            else:
                rename_details = {}
                if path and path in ctx.files() and ctx[path].renamed():
                    rename_details['path'] = '/' + ctx[path].renamed()[0]
                    rename_details['commit_url'] = self._repo.url_for_commit(
                        ctx.hex()
                    )
                commit = self._commit_info(ctx)
                commit.update({
                    'size': int(ctx[path].size()) if path in ctx else None,
                    'rename_details': rename_details,
                })
                yield commit
                if rename_details:
                    # we do not need to show commits before rename
                    break

    def open_blob(self, blob):
        fctx = self._hg[blob.commit._id][h.really_unicode(blob.path()).encode('utf-8')[1:]]
        return StringIO(fctx.data())

    def blob_size(self, blob):
        fctx = self._hg[blob.commit._id][h.really_unicode(blob.path()).encode('utf-8')[1:]]
        return fctx.size()

    def _setup_hooks(self, source_path=None):
        'Set up the hg changegroup hook'
        hgrc = os.path.join(self._repo.fs_path, self._repo.name, '.hg', 'hgrc')
        cp = ConfigParser()
        cp.read(hgrc)
        if not cp.has_section('hooks'):
            cp.add_section('hooks')
        url = self._repo.refresh_url()
        cp.set('hooks','; = [the next line is required for site integration, do not remove/modify]', '')
        cp.set('hooks','changegroup.sourceforge','curl -s %s' % url)
        with open(hgrc, 'w') as fp:
            cp.write(fp)
        os.chmod(hgrc, 0755)

    def _tree_from_changectx(self, changectx):
        '''Build a fake git-like tree from a changectx and its manifest'''
        root = GitLikeTree()
        for filepath in changectx.manifest():
            fctx = changectx[filepath]
            oid = b2a_hex(fctx.filenode())
            root.set_blob(filepath, oid)
        return root

    def symbolics_for_commit(self, commit):
        try:
            ctx = self._hg[commit._id]
        except RepoLookupError as e:
            return [], []
        return [ctx.branch()], ctx.tags()

    def rev_parse(self, rev):
        try:
            return self._hg[rev].hex()
        except RepoLookupError as e:
            return None

    def compute_tree_new(self, commit, tree_path='/'):
        ctx = self._hg[commit._id]
        fake_tree = self._tree_from_changectx(ctx)
        fake_tree = fake_tree.get_tree(tree_path)
        tree = self.refresh_tree_info(fake_tree, set())
        return tree._id

    def tarball(self, commit, path=None):
        """
        :param path: is currently ignored.  Can't request a snapshot of a subdirectory

        Makes a hg archive at `tmpdest`
            then zips that into `dest/tmpfilename`
            then renames that to `dest/filename`

        Could try modifying commands.archive(...) call to pass type='zip' and avoid temp files, although it would use
        python's zipfile implementation.  And also would need to set HgUI's setting for ui.archivemeta to False,
        to omit .hg_archival.txt
        """
        if not os.path.exists(self._repo.tarball_path):
            os.makedirs(self._repo.tarball_path)
        if not os.path.exists(self._repo.tarball_tmpdir):
            os.makedirs(self._repo.tarball_tmpdir)
        archive_name = self._repo.tarball_filename(commit)
        dest = os.path.join(self._repo.tarball_path, archive_name)
        tmpdest = os.path.join(self._repo.tarball_tmpdir, archive_name)
        filename = os.path.join(self._repo.tarball_path, '%s%s' % (archive_name, '.zip'))
        tmpfilename = os.path.join(self._repo.tarball_path, '%s%s' % (archive_name, '.tmp'))
        # We need to convert dest to str here, since commands.archive and
        # shutil.* don't play nicely with unicode. See [#7757] for details
        dest = h.really_unicode(dest).encode('utf-8')
        rmtree(dest, ignore_errors=True)
        tmpdest = h.really_unicode(tmpdest).encode('utf-8')
        rmtree(tmpdest, ignore_errors=True)
        try:
            commands.archive(HgUI(), self._hg, tmpdest, rev=commit, prefix='')
            basedir = os.path.basename(tmpdest)
            zipdir(tmpdest, tmpfilename, exclude=basedir + '/.hg_archival.txt')
            os.rename(tmpfilename, filename)
        finally:
            rmtree(dest, ignore_errors=True)
            rmtree(tmpdest, ignore_errors=True)
            if os.path.exists(tmpfilename):
                os.remove(tmpfilename)

    def is_empty(self):
        return not self._hg or self._hg.heads() == ['\x00'*20]

    def is_file(self, path, rev=None):
        return path.strip('/') in self._hg[rev]

    @LazyProperty
    def head(self):
        return self._hg[self._hg.tags()['tip']].hex()

    @LazyProperty
    def heads(self):
        return [Object(name=None, object_id=self._hg[v].hex()) for v in self._hg.heads()]

    @LazyProperty
    def branches(self):
        return [Object(name=branch, object_id=self._hg[head].hex())
                for branch, head in self.branchtags().items()]

    @LazyProperty
    def tags(self):
        return [Object(name=k, object_id=self._hg[v].hex()) for k,v in self._hg.tags().items()]

    def set_default_branch(self, name):
        if not name:
            return
        self._repo.default_branch_name = name

    def _get_last_commit(self, commit_id, paths):
        # walkchangerevs appears to occasionally, randomly throw either a
        # RevlogError or an mpatch.mpatchError complaining about corrupt
        # repo data.  However, it's not reproducable and even just retrying
        # the call once immediately is enough to clear the error.
        # http://stackoverflow.com/questions/17073368/mercurial-complains-repository-is-corrupt-when-its-not
        # seems to indicate it may be related to optimizations in the network
        # stack, but I wasn't able to apply that solution, so this retry loop
        # is a work-around.
        for attempt in xrange(1, 3):
            try:
                ctx = cmdutil.walkchangerevs(
                        self._hg,
                        scmutil.match(self._hg[None], pats=['path:%s' % p for p in paths]),
                        {'rev': ['%s:0' % commit_id]},
                        lambda ctx, fns: None,
                    ).next()
            except StopIteration:
                return None, set()
            except Exception as e:
                # only catch these two types; unfortunately, can't seem to
                # import mpatchError because it's raised in an .so library
                if not (isinstance(e, RevlogError) or type(e).__name__ == 'mpatchError'):
                    raise
                if attempt == 2:
                    log.exception('Error in mercurial repo: %s on %s in %s', e, commit_id, self._repo.full_fs_path)
                    return None, set()
                else:
                    log.error('Potentially spurious error (retrying): %s on %s in %s', e, commit_id, self._repo.full_fs_path)
            else:
                return ctx.hex(), set(ctx.files())

    def get_changes(self, commit_id):
        return self._hg[commit_id].files()

    def paged_diffs(self, commit_id, start=0, end=None, onlyChangedFiles=False):
        result = {'added': [], 'removed': [], 'changed': [], 'copied': [], 'renamed': [], 'total': 0}
        # equivalent to `hg status --change <commit_id>`, but using hg API
        node2 = self._hg[commit_id].node()
        node1 = self._hg[node2].p1().node()

        status = self._hg.status(node1, node2)

        if asbool(tg.config.get('scm.commit.hg.detect_copies', False)):
            _copies = copies.pathcopies(self._hg[node1], self._hg[node2])
            for k, v in _copies.iteritems():
                result['copied'].append({
                    'new': h.really_unicode(k),
                    'old': h.really_unicode(v),
                    'ratio': 1,
                })

        # reformat status to apply pagination
        files = []
        for name in status[0]:
            s = ('M', h.really_unicode(name))
            files.append(s)
        for name in status[1]:
            s = ('A', h.really_unicode(name))
            files.append(s)
        for name in status[2]:
            s = ('R', h.really_unicode(name))
            files.append(s)
        result['total'] = len(files)
        for s, name in files[start:end]:
            if s == 'A':
                result['added'].append(name)
            elif s == 'M':
                result['changed'].append(name)
            elif s == 'R':
                result['removed'].append(name)

        for r in result['copied'][:]:
            if r['old'] in result['removed']:
                result['removed'].remove(r['old'])
                result['copied'].remove(r)
                result['renamed'].append(r)
            try:
                result['added'].remove(r['new'])
            except ValueError:
                # Was already removed probably because it was copied with the 'hg copy' command.
                pass

        return result

    def _outgoing(self, ui, repo, dest, opts):
        """This is inspired heavily by hg.outgoing function (from 3.0)

        The changes are:
            - yields the list of commits, instead of printing them to stdout
            - does not handle subrepos
            - uses default options for "force" and "bundle" if not provided
            - does not trigger hooks
            - newest_first = True by default
        """
        if 'force' not in opts:
            opts['force'] = False
        if 'bundle' not in opts:
            opts['bundle'] = None
        if 'newest_first' not in opts:
            opts['newest_first'] = True
        limit = hg.cmdutil.loglimit(opts)
        o, other = hg._outgoing(ui, repo, dest, opts)
        if not o:
            return

        if opts.get('newest_first'):
            o.reverse()
        commits = []
        count = 0
        for n in o:
            if limit is not None and count >= limit:
                break
            parents = [p for p in repo.changelog.parents(n) if p != hg.node.nullid]
            if opts.get('no_merges') and len(parents) == 2:
                continue
            count += 1
            yield repo[n]

    def merge_request_commits(self, mr):
        """
        Return list of commits to be merged

        Must be called within mr.push_downstream_context()
        """
        dest = mr.app.repo.full_fs_path
        opts = {'branch': [mr.source_branch],
                'rev': [mr.downstream.commit_id]}
        commits = self._outgoing(HgUI(), self._hg, dest, opts)
        # don't show children of downstream commit id
        not_top = lambda ci: ci.hex() != mr.downstream.commit_id
        commits = it.dropwhile(not_top, commits)
        return map(self._commit_info, commits)


Mapper.compile_all()
