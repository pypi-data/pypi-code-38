# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Patch object
# :Created:   Fri Oct  3 01:13:20 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017 Lele Gaifax
#

import logging


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

MAX_PATCHID_LEN = 100


class DependencyError(Exception):
    "Indicate some problem with the dependencies."


def compute_checksum(language, script, depends, preceeds, brings, drops, conditions,
                     onerror, revision, mimetype):
    """Compute a checksum from the script and its metadata.

    This is mainly needed to avoid repeated beautification of the same script.
    """

    from hashlib import md5

    return md5(b'#'.join((language.encode('ascii', 'ignore'),
                          script.encode('ascii', 'ignore'),
                          repr(depends).encode('ascii', 'ignore'),
                          repr(preceeds).encode('ascii', 'ignore'),
                          repr(brings).encode('ascii', 'ignore'),
                          repr(drops).encode('ascii', 'ignore'),
                          repr(conditions).encode('ascii', 'ignore'),
                          repr(revision).encode('ascii', 'ignore'),
                          repr(mimetype).encode('ascii', 'ignore')))).digest()


class Patch(object):
    """
    Represent a single `patch`, that is some kind of arbitrary script
    written in some language, curried with some metadata.
    """

    def __init__(self, patchid, description, script, language, revision,
                 depends, preceeds, brings, drops, conditions, onerror='abort',
                 mimetype=None, always=False, autocommit=False,
                 source=None, line=None):
        self.patchid = patchid
        """The unique ID of this patch"""

        self.description = description
        """The description of the script"""

        self.script = script
        """The script itself, possibly empty for placeholders"""

        self.language = language
        "The language of the script, currently either 'sql' or 'python'"

        self.revision = revision
        """The revision of the script"""

        self.depends = depends
        "List of tuples (ID,rev) of the patches this one depends on"

        self.preceeds = preceeds
        "List of tuples (ID,rev) of the patches that depend on this one"

        self.brings = brings
        "List of tuples (ID,rev) of the patches this one updates"

        self.drops = drops
        "List of tuples (ID,None) of the patches this one drops"

        self.conditions = conditions
        "List of *conditions* that must be verified before patch application"

        self.onerror = onerror
        """
        Behaviour on errors: 'abort' means just that, 'skip' to jump to the
        next patch, 'ignore' to ignore the error considering the patch as fully
        applied
        """

        self.mimetype = mimetype
        "Optional mime type, to select a more specific Pygments beautifier."

        self.always = always
        "Whether the patch shall be executed always at each run, rather than only once."

        self.autocommit = autocommit
        "Whether the patch shall be executed in autocommit mode."

        self.checksum = compute_checksum(language, script, depends, preceeds, brings, drops,
                                         conditions, onerror, revision, mimetype)
        "Checksum of the script, to track changes"

        self.source = source
        "The source file that defined this script."

        self.line = line
        "The line number where the script is defined."

    def __str__(self):
        "Return a description of the patch, for logging purposes."

        kind = 'placeholder ' if self.is_placeholder else ''
        if self.is_migration:
            kind += 'patch'
        else:
            kind += 'script'
        return '%s "%s@%d"' % (kind, self.patchid, self.revision)

    def __repr__(self):
        return '<%s>' % self

    def __hash__(self):
        return hash((self.patchid, self.revision))

    def __eq__(self, other):
        return (isinstance(other, Patch)
                and self.patchid == other.patchid
                and self.revision == other.revision)

    def __lt__(self, other):
        return (self.patchid, self.revision) < (other.patchid, other.revision)

    @property
    def as_dict(self):
        res = dict(
            ID=self.patchid,
            language=self.language,
            revision=self.revision,
            script=self.script,
            source=self.source,
            line=self.line,
        )
        if self.patchid != self.description:
            res['description'] = self.description

        def rr(d):
            if d[1]:
                return '%s@%d' % d
            else:
                return d[0]

        if self.always:
            res['always'] = self.always
        if self.depends:
            res['depends'] = [rr(d) for d in self.depends]
        if self.preceeds:
            res['preceeds'] = [rr(p) for p in self.preceeds]
        if self.brings:
            res['brings'] = [rr(b) for b in self.brings]
        if self.drops:
            res['drops'] = [rr(d) for d in self.drops]
        if self.conditions:
            res['conditions'] = [c for c in self.conditions]
        if self.onerror != 'abort':
            res['onerror'] = self.onerror
        if self.autocommit:
            res['autocommit'] = self.autocommit

        return res

    @property
    def is_migration(self):
        return bool(self.brings or self.drops)

    @property
    def is_placeholder(self):
        return not self.script

    def adjustUnspecifiedRevisions(self, pm):
        """
        Replace the non-specified revision numbers with the current known version of the patch.

        Perform also some sanity checks: all `depends`, `brings` and `preceeds` must exist at
        this point.
        """

        for i, (pid, rev) in enumerate(self.depends):
            p = pm[pid]
            if p is None:
                if self.is_migration:
                    logger.debug('%s (defined in %s at line %s)'
                                 ' depends on "%s@%s",'
                                 ' which does not exist: applying anyway',
                                 self, self.source, self.line, pid, rev)
                    continue
                raise DependencyError('%s (defined in %s at line %s)'
                                      ' depends on "%s@%s",'
                                      ' which does not exist.'
                                      % (self, self.source, self.line, pid, rev))
            if rev is None:
                self.depends[i] = (pid, p.revision)

        for i, (pid, rev) in enumerate(self.brings):
            p = pm[pid]
            if p is None:
                logger.debug('%s (defined in %s at line %s)'
                             ' brings to "%s@%s",'
                             ' which does not exist: applying anyway'
                             % (self, self.source, self.line, pid, rev))
                continue
            if rev is None:
                self.brings[i] = (pid, p.revision)

        for i, (pid, rev) in enumerate(self.preceeds):
            p = pm[pid]
            if p is None:
                if self.is_migration:
                    logger.debug('%s (defined in %s at line %s) preceeds "%s@%s",'
                                 ' which does not exist: applying anyway'
                                 % (self, self.source, self.line, pid, rev))
                else:
                    raise DependencyError('%s (defined in %s at line %s) preceeds "%s@%s",'
                                          ' which does not exist.'
                                          % (self, self.source, self.line, pid, rev))
            if rev is None:
                self.preceeds[i] = (pid, pm[pid].revision)

    def beautify(self):
        "Compute a beautified and highlighted HTML version of the script."

        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, get_lexer_for_mimetype
        from pygments.formatters import get_formatter_by_name

        logger.debug("HTMLifying %s", self)

        if self.mimetype:
            lexer = get_lexer_for_mimetype(self.mimetype, encoding="utf-8")
        else:
            lexer = get_lexer_by_name(self.language, encoding="utf-8")
        formatter = get_formatter_by_name('html', linenos="inline",
                                          # produce Unicode
                                          encoding=None)
        return highlight(self.script, lexer, formatter)

    def verifyConditions(self, context):
        """
        Verify pre-conditions, returning False if even only one isn't satisfied.
        """

        if self.conditions is None:
            return True

        for c in self.conditions:
            if not context.verifyCondition(c):
                return False

        return True

    def isApplicable(self, context):
        if not self.always and self.revision == context[self.patchid]:
            return False, "already applied"

        lang_context = context.forLanguage(self.language)
        if lang_context is None:
            logger.warning('No language context for %r', self.language)
            assert self.language == 'test'
            return True, None

        if not self.verifyConditions(lang_context):
            return False, "does not satisfy the conditions"

        return lang_context.isApplicable(self)


def parse_deps(deps):
    """Parse textual dependencies.

    `deps` is the textual representation of the dependencies specified in the ``depends``,
    ``brings``, ``drops`` and ``preceeds`` fields.

    `deps` may contain something like ``patchid@10``, to specify the revision 10 of the given
    patch. When the revision is not specified it's set to None, and later adjusted to be the
    current revision of the patch.

    Multiple dependencies may be separated by a comma.
    """

    result = []

    if deps:
        if isinstance(deps, str):
            deps = deps.split(',')
        for dep in deps:
            dep = dep.strip()
            if not dep:
                raise ValueError("empty patch ID, spurious comma?")
            if '@' in dep:
                depid, deprev = dep.split('@')
                deprev = int(deprev)
                if deprev < 1:
                    raise ValueError("invalid revision: %r" % dep)
            else:
                depid = dep
                deprev = None

            result.append((depid.lower(), deprev))

    # For purely aesthetic reasons, order dependencies alphabetically
    result.sort()

    return result


def make_patch(patchid, script, options, description=None):
    """Create a new Patch instance given its description.

    :param patchid: the unique id of the patch
    :param script: the text of the script
    :param options: a dictionary with all the options
    :param description: optional, original title of the script
    :rtype: a :py:class:`metapensiero.sphinx.patch.Patch` instance
    """

    description = options.get('description', description or patchid)
    language = options.get('language', 'sql')
    revision = int(options.get('revision', 1))
    if revision < 1:
        raise ValueError("Invalid revision, must be greater than 0")

    try:
        depends = parse_deps(options.get('depends', ''))
    except ValueError as e:
        raise ValueError("Error in script's depends option: %s" % str(e))

    try:
        preceeds = parse_deps(options.get('preceeds', ''))
    except ValueError as e:
        raise ValueError("Error in script's preceeds option: %s" % str(e))

    try:
        brings = parse_deps(options.get('brings', ''))
    except ValueError as e:
        raise ValueError("Error in script's brings option: %s" % str(e))
    if not script and brings:
        raise ValueError("Placeholder script cannot bring anything")

    try:
        drops = parse_deps(options.get('drops', ''))
    except ValueError as e:
        raise ValueError("Error in script's drops option: %s" % str(e))
    else:
        for depid, deprev in drops:
            if deprev is not None:
                raise ValueError("Error in script's drops option:"
                                 " dependency %r carries a revision"
                                 % depid)

    conditions = options.get('conditions', None)
    onerror = options.get('onerror', 'abort')
    mimetype = options.get('mimetype', None)
    always = options.get('always', False)
    autocommit = 'autocommit' in options

    if conditions:
        if isinstance(conditions, str):
            conditions = [c.strip() for c in conditions.split(',')]
    else:
        conditions = []

    if mimetype is None:
        if language == 'python':
            mimetype = 'application/x-python'
        elif language == 'sql':
            mimetype = 'text/x-sql'

    return Patch(patchid, description, script, language, revision,
                 depends, preceeds, brings, drops, conditions, onerror, mimetype,
                 always, autocommit, options.get('source'), options.get('line'))
