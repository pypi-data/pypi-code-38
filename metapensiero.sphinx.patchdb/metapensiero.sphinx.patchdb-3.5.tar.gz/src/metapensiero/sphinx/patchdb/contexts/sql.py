# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Generic SQL script execution context
# :Created:   sab 31 mag 2014 13:00:48 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016, 2017 Lele Gaifax
#

from collections import deque, namedtuple
from datetime import datetime
from hashlib import md5 as hash_factory

from sqlparse.tokens import Comment, Keyword, Literal, Name, Punctuation, Whitespace
from sqlparse import tokens
from sqlparse.keywords import SQL_REGEX
from sqlparse.utils import consume

from ..states import State
from . import logger
from . import ExecutionContext, ExecutionError


def split_script(script):
    """Split the `script` into the single SQL statements.

    The script may be composed zero or more SQL statements, separated by two consecutive
    semicomma ``;;`` on a line by their own::

      CREATE DOMAIN integer_t INTEGER
      ;;
      CREATE DOMAIN string_t VARCHAR(20)

    Empty statements are discarded.
    """

    statements = []

    lines = []
    for line in script.splitlines():
        if line.strip() == ';;':
            statement = '\n'.join(lines)
            if statement.strip():
                statements.append(statement + '\n')
            lines = []
        else:
            lines.append(line)
    statement = '\n'.join(lines)
    if statement.strip():
        statements.append(statement + '\n')

    return statements


ValuableToken = namedtuple('ValuableToken', 'pos, type, value')


def valuable_tokens(statement):
    "Iterate over `statement`'s tokens, ignoring whitespace and comments."

    # This is basically the sqlparse<0.2 Lexer().get_tokens_unprocessed()
    # Version 0.2+ does not return the position

    iterable = enumerate(statement)
    for pos, char in iterable:
        for rexmatch, action in SQL_REGEX:
            m = rexmatch(statement, pos)

            if not m:
                continue
            elif isinstance(action, tokens._TokenType):
                consume_pos = m.end() - pos - 1
                if not (action in Whitespace or action in Comment):
                    yield ValuableToken(pos, action, m.group())
            elif callable(action):
                ttype, value = action(m.group())
                consume_pos = len(value) - 1
                if not (ttype in Whitespace or ttype in Comment):
                    yield ValuableToken(pos, ttype, value)

            consume(iterable, consume_pos)
            break
        else:
            yield ValuableToken(pos, tokens.Error, char)


def statement_starts_with(statement, expected_tokens):
    """Determine whether `statement` starts with the given set of `expected_tokens`.

    Return ``None`` if not, otherwise the remaining tokens.
    """

    tokens = valuable_tokens(statement)

    for etoken in expected_tokens:
        this = next(tokens, None)
        if this is None:
            return None
        ttype = this.type
        tvalue = this.value.upper()

        if isinstance(etoken, tuple):
            etoken = [etoken]

        for etype, evalue in etoken:
            if ttype == etype and tvalue == evalue:
                break
        else:
            tokens = None
            break

    return tokens


class SqlContext(ExecutionContext):
    """
    Generic SQL execution context.

    This is still somewhat abstract, subclasses must reimplement
    at least :method:`makeConnection()` and :method:`setupContext()`.
    """

    language_name = 'sql'

    GET_PATCH_REVISION_STMT = ("SELECT revision"
                               " FROM patchdb"
                               " WHERE patchid = %s")
    "The SQL statement used to get the applied revision of a given patch"

    INSERT_PATCH_STMT = ("INSERT INTO patchdb (patchid, revision, applied)"
                         " VALUES (%s, %s, %s)")
    "The SQL statement used to register the execution a new patch"

    UPDATE_PATCH_STMT = ("UPDATE patchdb"
                         " SET revision = %s, applied = %s"
                         " WHERE patchid = %s")
    "The SQL statement used to update the information of a given patch"

    GET_LAST_APPLIED_STMT = ("SELECT patchid, revision"
                             " FROM patchdb"
                             " ORDER BY applied DESC"
                             " LIMIT 1")
    "The SQL statement used to fetch the latest applied patch info"

    DELETE_PATCH_STMT = "DELETE FROM patchdb WHERE patchid = %s"
    "The SQL statement used to delete a given patch"

    def __init__(self, **args):
        """Initialize the instance.

        Open the DB connection and execute the setup, if needed.
        """

        ExecutionContext.__init__(self)

        self.makeConnection(**args)
        self.setupContext()

        self._patches = None

    def __getitem__(self, patchid):
        """
        Get the applied revision of a given `patchid`, or None.
        """

        return self.patches.get(patchid)

    def __setitem__(self, patchid, revision):
        """
        Cache the given `revision` as the last applied version of `patchid`.
        """

        self.patches[patchid] = revision

    @property
    def patches(self):
        """
        Extract the applied patches info from the database, returning a
        dictionary mapping a patch id to its revision.
        """

        if self._patches is None:
            cursor = self.connection.cursor()
            cursor.execute("SELECT patchid, revision"
                           " FROM patchdb")
            patches = cursor.fetchall()
            cursor.close()
            self.commitTransaction()

            self._patches = dict((patchid, revision) for patchid, revision in patches)

        return self._patches

    @property
    def state(self):
        "A tuple representing the latest applied patch."

        cursor = self.connection.cursor()
        cursor.execute("SELECT patchid, revision"
                       " FROM patchdb"
                       " ORDER BY patchid")

        hash = hash_factory()
        update = hash.update
        patchid = None
        for patchid, revision in cursor:
            signature = '%s@%s' % (patchid, revision)
            update(signature.encode('utf-8'))
        cursor.close()

        if patchid is not None:
            cursor = self.connection.cursor()
            cursor.execute(self.GET_LAST_APPLIED_STMT)
            last = cursor.fetchone()
            cursor.close()
            self.commitTransaction()

            return State(hash.hexdigest(), last[0], last[1])
        else:
            self.commitTransaction()

    def isApplicable(self, patch):
        """Check for CREATE scripts, that are surely *not* idempotent.
        Exclude also patches which dependants do not yet exist.
        """

        if not patch.is_migration and self[patch.patchid]:
            for stmt in split_script(patch.script):
                stmt = self.prepareStatement(stmt)
                # If it's not a fake CREATE DOMAIN
                if stmt is not None:
                    if statement_starts_with(stmt, ((Keyword.DDL, 'CREATE'),)):
                        return False, "contains a CREATE statement and it's already present"
        elif patch.is_migration:
            if all(self[depid] is None for depid, deprev in patch.depends):
                return False, "all dependants do not exists yet"
        return True, None

    def apply(self, patch, options=None):
        """
        Try to execute the given `patch` script, which may be
        composed by one or more SQL statements separated by two
        consecutive semicomma ``;;`` on a line by their own::

          CREATE DOMAIN integer_t INTEGER
          ;;
          CREATE DOMAIN string_t VARCHAR(20)

        If everything goes well, update the persistent status of
        the given `patch`, storing its `revision` in the ``patchdb``
        table in the database.
        """

        if options is not None and options.dry_run:
            ExecutionContext.apply(self, patch, options)
        else:
            cursor = self.connection.cursor()
            stmts = split_script(patch.script)

            last_good_point = None
            current_line = 1
            for i, stmt in enumerate(stmts):
                if stmt:
                    stmt_lines = stmt.count('\n')
                    stmt = self.prepareStatement(self.replaceUserVariables(stmt))
                    if not stmt:
                        continue

                    logger.debug("Executing '%s ...'" % stmt[:50])

                    try:
                        cursor.execute(stmt)
                        current_line += stmt_lines + 1
                        last_good_point = i+1
                        self.savePoint(last_good_point)
                    except Exception as e:
                        errmsg, syntaxerror, nonexistingobj = self.classifyError(e)

                        if ((nonexistingobj
                             and patch.onerror != 'ignore'
                             and self.shouldIgnoreNonExistingObjectError(
                                 stmt.lstrip().lower()))):
                            onerror = 'ignore'
                        else:
                            onerror = patch.onerror

                        if last_good_point:
                            self.rollbackPoint(last_good_point)
                        else:
                            self.rollbackTransaction()

                        if len(stmts) > 1:
                            details = "statement at line %d of " % current_line
                        else:
                            details = ""

                        if onerror == 'abort' or syntaxerror:
                            logger.critical("Execution of %s%s generated an"
                                            " error: %s", details, patch, errmsg)
                            logger.debug("Statement: %s", stmt)
                            raise ExecutionError("Execution of %s%s generated an"
                                                 " error: %s" %
                                                 (details, patch, errmsg))
                        elif onerror == 'ignore':
                            logger.info("Ignoring error generated by %s%s: %s",
                                        details, patch, errmsg)
                        elif onerror == 'skip':
                            logger.info("Skipping succeding statements due to"
                                        " error executing %s%s: %s",
                                        details, patch, errmsg)
                            break

        self.applied(patch, options is not None and options.dry_run)

    def prepareStatement(self, statement):
        """Possibly adjust the given `statement` before execution.

        This implementation simply returns `statement.strip()`.
        Subclasses may apply arbitrary transformations to it, or return
        ``None`` to discard its execution.
        """

        return statement.strip()

    def classifyError(self, exc):
        """Determine the kind of error given its exception.

        Return a tuple (message, syntaxerror, nonexistingobj).
        """

        raise NotImplementedError('Subclass responsibility')

    def shouldIgnoreNonExistingObjectError(self, stmt):
        """Determine whether the “non existing object” error should be ignored."""

        return statement_starts_with(stmt, ((Keyword.DDL, 'DROP'),))

    def _recordAppliedInfo(self, pid, rev, dry_run, _utcnow=datetime.utcnow):
        """Persist the knowledge on the database."""

        if not dry_run:
            cursor = self.connection.cursor()

            cursor.execute(self.GET_PATCH_REVISION_STMT, (pid,))
            rec = cursor.fetchone()
            if rev is None:  # drop
                if rec is not None:
                    logger.debug('Deleting "%s@%s" from the database', pid, rec[0])
                    cursor.execute(self.DELETE_PATCH_STMT, (pid,))
            else:
                if rec is None:
                    logger.debug('Inserting "%s@%s" into the database', pid, rev)
                    cursor.execute(self.INSERT_PATCH_STMT, (pid, rev, _utcnow()))
                else:
                    logger.debug('Updating "%s@%s" in the database', pid, rev)
                    cursor.execute(self.UPDATE_PATCH_STMT, (rev, _utcnow(), pid))
        else:
            logger.debug('Dry run mode, assuming "%s@%s" as done', pid, rev)

        self[pid] = rev

    def applied(self, patch, dry_run):
        """Register the given `patch` as *applied*.

        Update the persistent knowledge about the given `patch`, storing it's revision on the
        database. The same is done on all the patches this script may have upgraded.
        """

        if patch.brings:
            for pid, rev in patch.brings:
                self._recordAppliedInfo(pid, rev, dry_run)
        self._recordAppliedInfo(patch.patchid, patch.revision, dry_run)
        if patch.drops:
            for pid, rev in patch.drops:
                self._recordAppliedInfo(pid, None, dry_run)
        if not dry_run:
            self.commitTransaction()

    def makeConnection(self, **args):
        """Open the connection with the database."""

        raise NotImplementedError('Subclass responsibility')

    def closeConnection(self):
        self.connection.close()

    def setupContext(self):
        """Possibly create the tables used for persistent knowledge."""

        raise NotImplementedError('Subclass responsibility')

    def savePoint(self, point):
        """Possibly commit the work up to this point."""

    def rollbackPoint(self, point):
        """Possibly rollback to point."""

    def commitTransaction(self):
        """Complete current transaction."""
        self.connection.commit()

    def rollbackTransaction(self):
        """Rollback current transaction."""
        self.connection.rollback()

    def backup(self, backups_dir):
        logger.warning("%s does not implement the backup method!", type(self).__name__)

    def restore(self, backup):
        raise NotImplementedError("%s does not implement the restore method!"
                                  % type(self).__name__)


def is_create_domain(statement):
    "Determine whether the given `statement` is a ``CREATE DOMAIN``."

    return statement_starts_with(statement,
                                 ((Keyword.DDL, 'CREATE'),
                                  (Keyword, 'DOMAIN')))


def is_create_or_alter_table(statement):
    "Determine whether the given `statement` is a ``CREATE TABLE`` or an ``ALTER TABLE``."

    return statement_starts_with(statement,
                                 ([(Keyword.DDL, 'CREATE'), (Keyword.DDL, 'ALTER')],
                                  (Keyword, 'TABLE')))


def replace_fake_domains(statement, tokens, domains):
    maybe_schema_name = next(tokens, None)
    if maybe_schema_name is None:
        return statement

    maybe_dot = next(tokens, None)
    if maybe_dot is None:
        return statement

    if maybe_dot.type == Punctuation and maybe_dot.value == '.':
        table_name = next(tokens, None)
        if table_name is None:
            return statement

    fake_domains = []
    last2 = deque(maxlen=2)
    for token in tokens:
        if not (token.type in Name or token.type in Literal.String.Symbol):
            if len(last2) == 2 and last2[0].type in Name and (
                    last2[1].type in Name or last2[1].type in Literal.String.Symbol):
                fake_domains.append((last2[1].pos, last2[1].value))
        last2.append(token)

    statement = list(statement)
    for pos, name in reversed(fake_domains):
        if name[0] not in '`"':
            name = name.lower()
        if name in domains:
            statement[pos:pos+len(name)] = list(domains[name])

    return ''.join(statement)


class FakeDataDomainsMixin(object):
    "Mixin implementing poor man's `data domains` for simplicistic databases."

    data_domains = {}

    def prepareStatement(self, statement):
        """Handle user defined data domains.

        Intercept ``CREATE DOMAIN`` statements and handle them directly,
        replace known domains in ``CREATE TABLE`` statements.
        """

        iscd = is_create_domain(statement)
        if iscd:
            name = next(iscd).value
            definition = statement[statement.find(name) + len(name) + 1:]
            if name[0] not in '`"':
                name = name.lower()
            self.data_domains[name] = definition
            return None

        if self.data_domains:
            isct = is_create_or_alter_table(statement)
            if isct:
                statement = replace_fake_domains(statement, isct, self.data_domains)

        return statement
