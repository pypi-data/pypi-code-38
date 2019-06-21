# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Implementation of docutils ``script`` directive
# :Created:   Fri Oct  3 00:34:12 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2019 Lele Gaifax
#

from collections import defaultdict
import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

from sphinx import addnodes, errors, version_info as sphinx_version
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.nodes import make_refnode

from .locale import gettext as _
from .patch import MAX_PATCHID_LEN, make_patch, DependencyError


logger = logging.getLogger(__name__)


class BaseError(errors.ExtensionError):
    "Indicates that something is wrong with a script"
    category = "PatchDB error"


class ScriptError(BaseError):
    "Something's wrong in a script directive"


class CircularIncludeError(BaseError):
    "Circular include detected"


class ScriptDependencyError(BaseError):
    "Script's dependencies have problems"


class Script(nodes.topic):
    pass


def visit_script_node(self, node):
    self.visit_topic(node)


def depart_script_node(self, node):
    self.depart_topic(node)


def load_file(env, scriptid, lineno, encoding, filename):
    "Load given `filename`, returning its content and the relative path."

    from io import open
    from os import sep
    from os.path import dirname, normpath, join

    if filename.startswith('/') or filename.startswith(sep):
        rel_fn = filename[1:]
    else:
        docdir = dirname(env.doc2path(env.docname, base=None))
        rel_fn = normpath(join(docdir, filename))

    try:
        fn = join(env.srcdir, rel_fn)
    except UnicodeDecodeError:
        # the source directory is a bytestring with non-ASCII
        # characters; let's try to encode the rel_fn in the
        # file system encoding
        from sys import getfilesystemencoding
        rel_fn = rel_fn.encode(getfilesystemencoding())
        fn = join(env.srcdir, rel_fn)

    try:
        f = open(fn, 'r', encoding=encoding)
        text = f.read()
        f.close()
    except (IOError, OSError):
        raise ScriptError(
            _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
              ' include file %(filename)r not found or unreadable')
            % dict(scriptid=scriptid, docname=env.docname, lineno=lineno,
                   filename=filename))
    except UnicodeError:
        raise ScriptError(
            _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
              ' could not read included file %(filename)r with encoding'
              ' %(encoding)r, try setting a different :encoding: option')
            % dict(scriptid=scriptid, docname=env.docname, lineno=lineno,
                   filename=filename, encoding=encoding))

    return text, fn, rel_fn


def expand_includes(env, scriptid, lineno, encoding, text, _seen=None):
    "Replace lines like ``;;INCLUDE:filename`` with the content of `filename`."

    if _seen is None:
        _seen = set()

    def replace(match):
        fname = match.group(1)
        content, fn, rel_fn = load_file(env, scriptid, lineno, encoding, fname)
        if fn in _seen:
            raise CircularIncludeError(
                _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
                  ' circular include of file %(filename)r')
                % dict(scriptid=scriptid, docname=env.docname, lineno=lineno,
                       filename=fname))
        _seen.add(fn)
        return expand_includes(env, scriptid, lineno, encoding, content, _seen)

    return re.sub(r"^;;INCLUDE:\s*(.+)$", replace, text, flags=re.MULTILINE)


class ScriptContents(nodes.container):
    pass


class ScriptDirective(Directive):
    "Implementation of the ``script`` directive."

    # Take note about scripts already seen in this session
    already_seen_this_session = set()

    # One mandatory argument, the script ID; an optional one, its title,
    # where spaces are allowed
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    # It has a content body
    has_content = True

    # Allowed options
    option_spec = {
        'always': lambda arg: directives.choice(arg, (
            'first',
            'last',
        )),
        'autocommit': directives.flag,
        'brings': directives.unchanged_required,
        'conditions': directives.unchanged_required,
        'depends': directives.unchanged_required,
        'description': directives.unchanged_required,
        'drops': directives.unchanged_required,
        'encoding': directives.encoding,
        'file': directives.path,
        'language': lambda arg: directives.choice(arg, (
            'python',
            'sql',
        )),
        'mimetype': lambda arg: directives.choice(arg, (
            'application/x-python',
            'application/x-python3',
            'text/x-mysql',
            'text/x-plpgsql',
            'text/x-postgresql',
            'text/x-python',
            'text/x-python3',
            'text/x-sql',
            'text/x-sqlite3-console',
        )),
        'onerror': directives.unchanged_required,
        'preceeds': directives.unchanged_required,
        'revision': directives.nonnegative_int,
        }

    def run(self):
        """Implement ``script`` directive.

        The ``script`` directive introduces a piece of code, taken from its
        body, that shall be executed on some target. This content gets
        beautified with `pygments` and inserted in the document tree as a
        ``raw`` node.

        The language of the script is mandatory, and must be specified as
        ``language`` in the `options` argument. Currently it can be one of
        following:

        - *python*
        - *sql*
        """

        name = self.name
        arguments = self.arguments
        lineno = self.lineno
        state = self.state
        document = state.document
        source = document.current_source
        env = document.settings.env

        if not arguments:
            error = document.reporter.error(
                _('Missing mandatory ID for the directive "%s".') % (name),
                line=lineno)
            return [error]

        scriptid = arguments[0].lower()
        options = self.options
        content = self.content

        if len(scriptid) > MAX_PATCHID_LEN:
            raise ScriptError(
                _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
                  ' ID is too long, maximum allowed length is %(maxlen)d characters!')
                % dict(scriptid=scriptid, docname=env.docname, lineno=lineno,
                       maxlen=MAX_PATCHID_LEN))

        if '@' in scriptid:
            raise ScriptError(
                _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
                  ' ID contains "@", not allowed')
                % dict(scriptid=scriptid, docname=env.docname, lineno=lineno))

        if content and 'file' in options:
            raise ScriptError(
                _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
                  ' content and :file: option are mutually exclusive')
                % dict(scriptid=scriptid, docname=env.docname, lineno=lineno))

        encoding = options.get('encoding', env.config.source_encoding)

        if 'file' in options:
            if not document.settings.file_insertion_enabled:
                return [document.reporter.warning(_('File insertion disabled'),
                                                  line=lineno)]

            filename = options['file']
            text, fn, rel_fn = load_file(env, scriptid, lineno, encoding, filename)

            env.note_dependency(rel_fn)
        else:
            text = '\n'.join(content)

        text = expand_includes(env, scriptid, lineno, encoding, text)

        scripts = env.domaindata['patchdb']['scripts']

        # Sanity check
        if scriptid in self.already_seen_this_session \
           or scriptid in scripts and scripts[scriptid]['docname'] != env.docname:
            raise ScriptError(
                _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
                  ' ID is not unique, there is another one in "%(other)s"!')
                % dict(scriptid=scriptid, docname=env.docname, lineno=lineno,
                       other=scripts[scriptid]['docname']))

        self.already_seen_this_session.add(scriptid)

        for option in ('brings', 'depends', 'drops', 'preceeds', 'conditions'):
            if option in options:
                elt = nodes.Element()
                vl = ViewList(options[option].splitlines())
                self.state.nested_parse(vl, self.content_offset, elt)
                if isinstance(elt.children[0], nodes.bullet_list):
                    options[option] = [c.astext() for c in elt.children[0]]

        try:
            patch = make_patch(scriptid, text, options, description=arguments[0])
        except ValueError as e:
            raise ScriptError(
                _('Script "%(scriptid)s" in "%(docname)s" at line %(lineno)d:'
                  ' bad option (%(error)s)')
                % dict(scriptid=scriptid, docname=env.docname, lineno=lineno, error=e))

        patch.source = source
        patch.line = lineno

        # Insert the html version of the script in a raw node
        if scriptid in scripts and patch.checksum == scripts[scriptid]['patch'].checksum:
            htmltext = scripts[scriptid]['htmltext']
        else:
            try:
                htmltext = patch.beautify()
            except ImportError:
                htmltext = text

        html = nodes.raw(text, htmltext)
        html['format'] = 'html'

        caption = nodes.caption(scriptid, _("Script ID: "))
        caption += nodes.strong(scriptid, "“%s”" % scriptid)

        title_text = patch.description
        if patch.revision > 1:
            title_text += _(" (revision %(revno)d)") % dict(revno=patch.revision)
        text_nodes, messages = state.inline_text(title_text, lineno)
        title = nodes.title(title_text, '', *text_nodes)

        # Place a topic, that will be the target of the references
        # to this script
        topic = Script('', title, classes=["script"])
        topic['scriptid'] = scriptid
        topicid = nodes.make_id('script ' + scriptid)
        name = nodes.fully_normalize_name(caption.astext())
        if not state.document.has_name(name):
            topic['names'].append(name)
        topic['ids'] = [topicid]

        if scriptid not in scripts or patch.checksum != scripts[scriptid]['patch'].checksum:
            scripts[scriptid] = dict(
                patch=patch, htmltext=htmltext, docname=env.docname)

        if patch.description != scriptid:
            topic += caption

        topic += html

        indexnode = addnodes.index()
        if sphinx_version >= (1, 4):
            indexnode['entries'] = [('single', scriptid, topicid, name, None)]
        else:
            indexnode['entries'] = [('single', scriptid, topicid, name)]

        return [indexnode, topic]


class ScriptContentsDirective(Directive):
    "Implementation of the ``scriptcontents`` directive."

    has_content = False
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'class': directives.class_option,
        'local': directives.flag,
        }

    def run(self):
        arguments = self.arguments
        options = self.options
        lineno = self.lineno
        state = self.state

        document = state.document

        if arguments:
            title_text = arguments[0]
            text_nodes, messages = state.inline_text(title_text, lineno)
            title = nodes.title(title_text, '', *text_nodes)
        else:
            if 'local' in options:
                title = None
            else:
                title = nodes.title('', _('Script index'))

        topic = nodes.topic(classes=['contents'])

        cls = options.get('class')
        if cls:
            topic.set_class(cls)

        if title:
            name = title.astext()
            topic += title
        else:
            name = _('Scripts')

        name = nodes.fully_normalize_name(name)
        if not document.has_name(name):
            topic['names'].append(name)
        document.note_implicit_target(topic)

        contents = ScriptContents()
        contents.local = 'local' in options
        contents.docname = document.settings.env.docname

        topic += contents

        return [topic]


def add_scripts_crossrefs(app, doctree, fromdocname):
    env = app.builder.env

    scripts = env.domaindata['patchdb']['scripts']
    if not scripts:
        return

    revdeps = defaultdict(list)
    for pid in scripts:
        patch = scripts[pid]['patch']
        for dp, dv in patch.depends:
            revdeps[dp].append((pid, None))

    get_relative_uri = app.builder.get_relative_uri

    def add_detail(dlist, detname, detvalue, strike_missing=False):
        if detvalue:
            item = nodes.definition_list_item()
            term = nodes.term('', detname)
            if len(detvalue) > 1:
                value = nodes.bullet_list()
                for v in detvalue:
                    sid, rev = v
                    li = nodes.list_item()
                    try:
                        docname = scripts[sid]['docname']
                    except KeyError:
                        if strike_missing:
                            p = nodes.paragraph('', '')
                            p += nodes.inline(sid, sid, classes=['strike'])
                            li += p
                            value += li
                        else:
                            raise DependencyError(sid)
                    else:
                        refid = nodes.make_id("script " + sid)
                        refuri = get_relative_uri(fromdocname, docname) + '#' + refid
                        ref = nodes.paragraph('', '')
                        reftxt = sid
                        if rev is not None:
                            reftxt += _(' (revision %(revno)d)') % dict(revno=rev)
                        ref += nodes.reference('', reftxt, refid=refid, refuri=refuri)
                        li += ref
                        value += li
            else:
                sid, rev = detvalue[0]
                try:
                    docname = scripts[sid]['docname']
                except KeyError:
                    if strike_missing:
                        value = nodes.paragraph('', '')
                        value += nodes.inline(sid, sid, classes=['strike'])
                    else:
                        raise DependencyError(sid)
                else:
                    refid = nodes.make_id("script " + sid)
                    refuri = get_relative_uri(fromdocname, docname) + '#' + refid
                    value = nodes.paragraph('', '')
                    reftxt = sid
                    if rev is not None:
                        reftxt += _(' (revision %(revno)d)') % dict(revno=rev)
                    value += nodes.reference('', reftxt, refid=refid, refuri=refuri)
            defn = nodes.definition('', value)
            item += term
            item += defn

            dlist += item

    # Add scripts details
    for node in doctree.traverse(Script):
        patch = scripts[node['scriptid']]['patch']

        dlist = nodes.definition_list()

        is_a_patch = bool(patch.brings) or bool(patch.drops)
        try:
            add_detail(dlist, _('Depends on'), patch.depends, strike_missing=is_a_patch)
            add_detail(dlist, _('Preceeds'), patch.preceeds, strike_missing=is_a_patch)
            add_detail(dlist, _('Brings'), patch.brings, strike_missing=is_a_patch)
            add_detail(dlist, _('Drops'), patch.drops, strike_missing=is_a_patch)
            rdeps = revdeps.get(patch.patchid, None)
            if rdeps:
                add_detail(dlist, _('Direct dependants'), sorted(rdeps))
        except DependencyError as e:
            raise ScriptDependencyError(
                _('The %(scriptid)s (defined in %(docname)s at line %(lineno)s)'
                  ' references an unknown script "%(other)s"')
                % dict(scriptid=patch, docname=patch.source, lineno=patch.line, other=e))

        if patch.conditions:
            item = nodes.definition_list_item()
            if len(patch.conditions) > 1:
                item += nodes.term('', _('Conditions'))
                clist = nodes.bullet_list()
                for c in patch.conditions:
                    li = nodes.list_item()
                    li += nodes.paragraph('', c)
                    clist += li
                item += nodes.definition('', clist)
            else:
                item += nodes.term('', _('Condition'))
                item += nodes.definition('', nodes.paragraph('', patch.conditions[0]))
            dlist += item

        if patch.always:
            item = nodes.definition_list_item()
            item += nodes.term('', _('Execute always'))
            if patch.always == 'first':
                value = nodes.paragraph('', _("Before any other script"))
            elif patch.always == 'last':
                value = nodes.paragraph('', _("After any other script"))
            else:
                value = nodes.paragraph('', patch.always)
            item += nodes.definition('', value)
            dlist += item

        if patch.onerror != 'abort':
            item = nodes.definition_list_item()
            item += nodes.term('', 'errors policy')
            if patch.onerror == 'skip':
                value = nodes.paragraph('', _("Go on with the next script,"
                                              " skipping any succeding statements"
                                              " of the failing script"))
            elif patch.onerror == 'ignore':
                value = nodes.paragraph('', _("Ignore the error and keeps going"
                                              " with the remaining statements in the"
                                              " script"))
            else:
                value = nodes.paragraph('', patch.onerror)
            item += nodes.definition('', value)
            dlist += item

        node += dlist

    # Fill script indexes
    sids = scripts.keys()

    for node in doctree.traverse(ScriptContents):
        entries = []
        for sid in sorted(sids):
            docname = scripts[sid]['docname']
            if node.local and node.docname != docname:
                continue
            patch = scripts[sid]['patch']
            refid = nodes.make_id("script " + sid)
            refuri = get_relative_uri(fromdocname, docname) + '#' + refid
            ref = nodes.reference('', patch.description,
                                  refdocname=docname,
                                  refid=refid,
                                  refuri=refuri)
            entry = nodes.paragraph('', '', ref)
            item = nodes.list_item('', entry)
            entries.append(item)
        if entries:
            node.replace_self(nodes.bullet_list('', *entries))


def mark_as_dirty(app, env):
    "Mark the script collection as dirty, will be dumped at end."

    app.patchdb_dump_scripts = True


def dump_scripts_collection(app, env):
    "Dump the collected scripts into a new pickle archive."

    from .manager import patch_manager

    scripts = env.domaindata['patchdb']['scripts']
    if not scripts or not app.config.patchdb_storage:
        return

    # Better safe than sorry: check dependencies and report anomalies
    for sid in scripts:
        patch = scripts[sid]['patch']
        if patch.depends:
            for i, (pid, rev) in enumerate(patch.depends):
                if pid not in scripts:
                    logger.warning(
                        _('The %(scriptid)s (defined in %(docname)s at line %(lineno)s)'
                          ' depends an unknown script "%(other)s"')
                        % dict(scriptid=patch, docname=patch.source, lineno=patch.line,
                               other=pid))
        if patch.brings:
            for i, (pid, rev) in enumerate(patch.brings):
                if pid not in scripts:
                    raise ScriptDependencyError(
                        _('The %(scriptid)s (defined in %(docname)s at line %(lineno)s)'
                          ' brings an unknown script "%(other)s"')
                        % dict(scriptid=patch, docname=patch.source, lineno=patch.line,
                               other=pid))

    if not getattr(app, 'patchdb_dump_scripts', False):
        return

    mgr = patch_manager(app.config.patchdb_storage, overwrite=True)

    for sid in scripts:
        mgr[sid] = scripts[sid]['patch']
    mgr.save()


def purge_doc(app, env, docname):
    "Remove references to scripts defined in purged document."

    scripts = env.domaindata['patchdb']['scripts']
    if not scripts:
        return

    obsolete_ids = [sid for sid in scripts if scripts[sid]['docname'] == docname]
    for sid in obsolete_ids:
        del scripts[sid]


class ScriptRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['patchdb:script'] = target
        title, target = super(ScriptRole, self).process_link(
            env, refnode, has_explicit_title, title, target)
        target = nodes.make_id("script " + target)
        return title, target


class PatchDBDomain(Domain):
    name = 'patchdb'
    label = 'PatchDB'

    object_types = {
        'script': ObjType('script', 'script'),
    }

    directives = {
        'script': ScriptDirective,
        'scriptcontents': ScriptContentsDirective,
    }

    roles = {
        'script': ScriptRole(lowercase=True),
    }

    data_version = 1
    initial_data = {'scripts': {}}

    def get_objects(self):
        for scriptid, script in self.data['scripts'].items():
            yield (scriptid, script['patch'].description, 'script',
                   script['docname'], scriptid, 1)

    def resolve_xref(self, env, fromdocname, builder, type, target, node, contnode):
        ref = node.get('patchdb:script')
        script = self.data['scripts'].get(nodes.fully_normalize_name(ref))
        if script:
            return make_refnode(builder, fromdocname, script['docname'], target,
                                contnode, script['patch'].description)
        else:
            logger.warning(_('Reference to an unknown script: %(scriptid)r')
                           % dict(scriptid=ref), location=node)


def setup(app):
    import sys

    app.add_domain(PatchDBDomain)

    app.add_node(Script,
                 html=(visit_script_node, depart_script_node),
                 latex=(visit_script_node, depart_script_node),
                 text=(visit_script_node, depart_script_node))
    app.add_node(ScriptContents)

    app.connect('env-purge-doc', purge_doc)
    app.connect('env-updated', dump_scripts_collection)
    app.connect('doctree-read', mark_as_dirty)
    app.connect('doctree-resolved', add_scripts_crossrefs)
