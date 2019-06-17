from __future__ import unicode_literals
from __future__ import print_function

import datetime as dt
import functools
import humanize
import itertools
import logging
import os
import re
import rockset
import threading
import traceback

from collections import namedtuple
from codecs import open
from cli_helpers.tabular_output import TabularOutputFormatter
from cli_helpers.tabular_output.preprocessors import (align_decimals,
                                                      format_numbers)
import click
click.disable_unicode_literals_warning = True
try:
    import setproctitle
except ImportError:
    setproctitle = None

from prompt_toolkit import CommandLineInterface, Application, AbortAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.buffer import AcceptAction
from prompt_toolkit.document import Document
from prompt_toolkit.enums import DEFAULT_BUFFER, EditingMode
from prompt_toolkit.filters import Always, HasFocus, IsDone
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.layout.processors import (
    ConditionalProcessor,
    HighlightMatchingBracketProcessor)
from prompt_toolkit.shortcuts import create_prompt_layout, create_eventloop

from pygments.lexers.sql import PostgresLexer
from pygments.token import Token
from rockset.sql.exception import (OperationalError, ProgrammingError)
from time import time, sleep
try:
    from urlparse import urlparse, unquote, parse_qs
except ImportError:
    from urllib.parse import urlparse, unquote, parse_qs

from .completion_refresher import CompletionRefresher
from .config import (
    config_location,
    ensure_dir_exists,
    get_casing_file,
    get_config,
    load_config,
    root_config_location)
from .encodingutils import utf8tounicode
from .encodingutils import text_type
from .key_bindings import rscli_bindings
from .rsbuffer import RSBuffer
from .rscompleter import RSCompleter
from .rsexecute import RSExecute
from .rsstyle import style_factory
from .rstoolbar import create_toolbar_tokens_func



# Query tuples are used for maintaining history
MetaQuery = namedtuple(
    'Query',
    [
        'query',            # The entire text of the command
        'successful',       # True If all subqueries were successful
        'total_time',       # Time elapsed executing the query
        'meta_changed',     # True if any subquery executed create/alter/drop
        'ws_changed',       # True if any subquery changed the workspace
        'path_changed',     # True if any subquery changed the search path
        'mutated',          # True if any subquery executed insert/update/delete
    ])
MetaQuery.__new__.__defaults__ = ('', False, 0, False, False, False, False)

OutputSettings = namedtuple(
    'OutputSettings',
    'table_format dcmlfmt floatfmt missingval expanded max_width case_function'
)
OutputSettings.__new__.__defaults__ = (
    None, None, None, '<null>', False, None, lambda x: x
)


class RSCli(object):
    # constants
    default_prompt = '\\a@\\s:\\w> '
    max_len_prompt = 30

    def __init__(self, rsexecute=None, rsclirc_file=None,
            auto_vertical_output=False, less_chatty=None, prompt=None,
            row_limit=None, single_connection=False):

        # Init command handler
        self.rsexecute = rsexecute

        # Load config.
        c = self.config = get_config(rsclirc_file)

        # Init logger and pager
        self.logger = logging.getLogger(__name__)
        self.initialize_logging()
        self.set_default_pager(c)
        self.output_file = None

        # Init settings
        self.multi_line = c['main'].as_bool('multi_line')
        self.multiline_mode = c['main'].get('multi_line_mode', 'psql')
        self.vi_mode = c['main'].as_bool('vi')
        self.auto_expand = auto_vertical_output or c['main'].as_bool('auto_expand')
        self.expanded_output = c['main'].as_bool('expand')
        if row_limit is not None:
            self.row_limit = row_limit
        else:
            self.row_limit = c['main'].as_int('row_limit')
        self.min_num_menu_lines = c['main'].as_int('min_num_menu_lines')
        self.multiline_continuation_char = c['main']['multiline_continuation_char']
        self.table_format = c['main']['table_format']
        self.syntax_style = c['main']['syntax_style']
        self.cli_style = c['colors']
        self.wider_completion_menu = c['main'].as_bool('wider_completion_menu')
        self.less_chatty = bool(less_chatty) or c['main'].as_bool('less_chatty')
        self.null_string = c['main'].get('null_string', '<null>')
        self.prompt_format = prompt if prompt is not None else c['main'].get(
            'prompt', self.default_prompt)
        self.on_error = c['main']['on_error'].upper()
        self.decimal_format = c['data_formats']['decimal']
        self.float_format = c['data_formats']['float']
        self.timing_enabled = True
        self.now = dt.datetime.today()
        self.query_history = []

        # Initialize completer and completion refresher
        self.completion_refresher = CompletionRefresher()
        smart_completion = c['main'].as_bool('smart_completion')
        keyword_casing = c['main']['keyword_casing']
        self.settings = {
            'casing_file': get_casing_file(c),
            'generate_casing_file': c['main'].as_bool('generate_casing_file'),
            'generate_aliases': c['main'].as_bool('generate_aliases'),
            'asterisk_column_order': c['main']['asterisk_column_order'],
            'qualify_columns': c['main']['qualify_columns'],
            'case_column_headers': c['main'].as_bool('case_column_headers'),
            'search_path_filter': c['main'].as_bool('search_path_filter'),
            'single_connection': single_connection,
            'less_chatty': less_chatty,
            'keyword_casing': keyword_casing,
        }
        completer = RSCompleter(smart_completion, settings=self.settings)
        self.completer = completer
        self._completer_lock = threading.Lock()
        self.eventloop = create_eventloop()
        self.cli = None

    def initialize_logging(self):
        log_file = self.config['main']['log_file']
        if log_file == 'default':
            log_file = os.path.join(root_config_location(), 'log')
        ensure_dir_exists(log_file)
        log_level = self.config['main']['log_level']

        # Disable logging if value is NONE by switching to a no-op handler.
        # Set log level to a high value so it doesn't even waste cycles getting called.
        if log_level.upper() == 'NONE':
            handler = logging.NullHandler()
        else:
            handler = logging.FileHandler(os.path.expanduser(log_file))

        level_map = {'CRITICAL': logging.CRITICAL,
                     'ERROR': logging.ERROR,
                     'WARNING': logging.WARNING,
                     'INFO': logging.INFO,
                     'DEBUG': logging.DEBUG,
                     'NONE': logging.CRITICAL
                     }
        log_level = level_map[log_level.upper()]

        formatter = logging.Formatter(
            '%(asctime)s (%(process)d/%(threadName)s) '
            '%(name)s %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        root_logger = logging.getLogger(__name__)
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level)

        root_logger.debug('Initializing rscli logging.')
        root_logger.debug('Log file %r.', log_file)

    def set_default_pager(self, config):
        configured_pager = config['main'].get('pager')
        os_environ_pager = os.environ.get('PAGER')

        if configured_pager:
            self.logger.info(
                'Default pager found in config file: "{}"'.format(configured_pager))
            os.environ['PAGER'] = configured_pager
        elif os_environ_pager:
            self.logger.info('Default pager found in PAGER environment variable: "{}"'.format(
                os_environ_pager))
            os.environ['PAGER'] = os_environ_pager
        else:
            self.logger.info(
                'No default pager found in environment. Using os default pager')

        # Set default set of less recommended options, if they are not already set.
        # They are ignored if pager is different than less.
        if not os.environ.get('LESS'):
            os.environ['LESS'] = '-SRXF'

    def change_table_format(self, pattern, **_):
        try:
            if pattern not in TabularOutputFormatter().supported_formats:
                raise ValueError()
            self.table_format = pattern
            yield (None, None, None,
                   'Changed table format to {}'.format(pattern))
        except ValueError:
            msg = 'Table format {} not recognized. Allowed formats:'.format(
                pattern)
            for table_type in TabularOutputFormatter().supported_formats:
                msg += "\n\t{}".format(table_type)
            msg += '\nCurrently set to: %s' % self.table_format
            yield (None, None, None, msg)

    def info_connection(self, **_):
        yield (None, None, None, 'You are connected to workspace "%s" at '
            'api_server "%s".' % (self.rsexecute.workspace,
            self.rsexecute.api_server))

    def change_ws(self, pattern, **_):
        if pattern:
            # Get all the parameters in pattern, handling double quotes if any.
            infos = re.findall(r'"[^"]*"|[^"\'\s]+', pattern)
            # Now removing quotes.
            list(map(lambda s: s.strip('"'), infos))

            infos.extend([None] * (3 - len(infos)))
            api_server, api_key, workspace = infos
            try:
                self.rsexecute.connect(api_server=api_server, api_key=api_key,
                    workspace=workspace)
            except OperationalError as e:
                click.secho(str(e), err=True, fg='red')
                click.echo("Previous connection kept")
        else:
            self.rsexecute.connect()

        yield (None, None, None, 'You are now connected to workspace "%s" at '
            'api_server "%s"' % (self.rsexecute.workspace,
            self.rsexecute.api_server))

    def execute_from_file(self, pattern, **_):
        if not pattern:
            message = '\\i: missing required argument'
            return [(None, None, None, message, '', False)]
        try:
            with open(os.path.expanduser(pattern), encoding='utf-8') as f:
                query = f.read()
        except IOError as e:
            return [(None, None, None, str(e), '', False)]

        on_error_resume = (self.on_error == 'RESUME')
        return self.rsexecute.run(query, on_error_resume=on_error_resume)

    def write_to_file(self, pattern, **_):
        if not pattern:
            self.output_file = None
            message = 'File output disabled'
            return [(None, None, None, message, '', True)]
        filename = os.path.abspath(os.path.expanduser(pattern))
        if not os.path.isfile(filename):
            try:
                open(filename, 'w').close()
            except IOError as e:
                self.output_file = None
                message = str(e) + '\nFile output disabled'
                return [(None, None, None, message, '', False)]
        self.output_file = filename
        message = 'Writing to file "%s"' % self.output_file
        return [(None, None, None, message, '', True)]

    def connect(self, api_server, api_key, workspace, **kwargs):
        # Attempt to connect to Rockset
        try:
            rsexecute = RSExecute(api_server, api_key, workspace, **kwargs)
        except Exception as e:  # Connecting to Rockset could fail.
            self.logger.debug('Rockset connection failed: %r.', e)
            self.logger.debug("traceback: %r", traceback.format_exc())
            click.secho(str(e), err=True, fg='red')
            exit(1)
        self.rsexecute = rsexecute

    def execute_command(self, text, query):
        logger = self.logger

        try:
            output, query = self._evaluate_command(text)
        except KeyboardInterrupt:
            # Restart connection to rockset
            self.rsexecute.connect()
            logger.debug("cancelled query, sql: %r", text)
            click.secho("Query cancelled.", err=True, fg='red')
        except NotImplementedError:
            click.secho('Not yet implemented.', fg="yellow")
        except OperationalError as e:
            logger.error("operational error. sql: %r, error: %r", text, e)
            logger.debug("traceback: %r", traceback.format_exc())
            self._handle_server_closed_connection()
        except Exception as e:
            logger.error("exception encountered. sql: %r, error: %r", text, e)
            logger.error("%s", traceback.format_exc())
            click.secho(str(e), err=True, fg='red')
        else:
            try:
                if self.output_file and not text.startswith(('\\o ', '\\? ')):
                    try:
                        with open(self.output_file, 'a', encoding='utf-8') as f:
                            click.echo(text, file=f)
                            click.echo('\n'.join(output), file=f)
                            click.echo('', file=f)  # extra newline
                    except IOError as e:
                        click.secho(str(e), err=True, fg='red')
                else:
                    click.echo_via_pager('\n'.join(output))
            except KeyboardInterrupt:
                pass

            if self.timing_enabled:
                # Only add humanized time display if > 1 second
                if query.total_time > 1:
                    print('Time: %0.03fs (%s)' % (query.total_time,
                          humanize.time.naturaldelta(query.total_time)))
                else:
                    print('Time: %0.03fs' % query.total_time)

            # Check if we need to update completions, in order of most
            # to least drastic changes
            if query.ws_changed:
                with self._completer_lock:
                    self.completer.reset_completions()
                self.refresh_completions(persist_priorities='keywords')
            elif query.meta_changed:
                self.refresh_completions(persist_priorities='all')
            elif query.path_changed:
                logger.debug('Refreshing search path')
                with self._completer_lock:
                    self.completer.set_search_path(
                        self.rsexecute.search_path())
                logger.debug('Search path: %r',
                             self.completer.search_path)
        return query

    def run_cli(self):
        logger = self.logger

        history_file = self.config['main']['history_file']
        if history_file == 'default':
            history_file = os.path.join(config_location(), 'history')
        history = FileHistory(os.path.expanduser(history_file))
        self.refresh_completions(history=history,
                                 persist_priorities='none')

        self.cli = self._build_cli(history)

        if not self.less_chatty:
            print('Version:', rockset.version())
            print()

        try:
            while True:
                document = self.cli.run()

                # nothing to do if document is empty
                if not document.text.strip():
                    continue

                # The reason we check here instead of inside the rsexecute is
                # because we want to raise the Exit exception which will be
                # caught by the try/except block that wraps the rsexecute.run()
                # statement.
                if quit_command(document.text):
                    raise EOFError

                # Initialize default metaquery in case execution fails
                query = MetaQuery(query=document.text, successful=False)
                query = self.execute_command(document.text, query)
                self.now = dt.datetime.today()

                # Allow RSCompleter to learn user's preferred keywords, etc.
                with self._completer_lock:
                    self.completer.extend_query_history(document.text)

                self.query_history.append(query)

        except EOFError:
            if not self.less_chatty:
                print ('Goodbye!')

    def _build_cli(self, history):

        def set_vi_mode(value):
            self.vi_mode = value

        key_binding_manager = rscli_bindings(
            get_vi_mode_enabled=lambda: self.vi_mode,
            set_vi_mode_enabled=set_vi_mode)

        def prompt_tokens(_):
            prompt = self.get_prompt(self.prompt_format)
            if (self.prompt_format == self.default_prompt and
                    len(prompt) > self.max_len_prompt):
                prompt = self.get_prompt('\\s> ')

            return [(Token.Prompt, prompt)]

        def get_continuation_tokens(cli, width):
            continuation=self.multiline_continuation_char * (width - 1) + ' '
            return [(Token.Continuation, continuation)]

        get_toolbar_tokens = create_toolbar_tokens_func(
            lambda: self.vi_mode, self.completion_refresher.is_refreshing,
            self.rsexecute.failed_transaction,
            self.rsexecute.valid_transaction)

        layout = create_prompt_layout(
            lexer=PygmentsLexer(PostgresLexer),
            reserve_space_for_menu=self.min_num_menu_lines,
            get_prompt_tokens=prompt_tokens,
            get_continuation_tokens=get_continuation_tokens,
            get_bottom_toolbar_tokens=get_toolbar_tokens,
            display_completions_in_columns=self.wider_completion_menu,
            multiline=True,
            extra_input_processors=[
               # Highlight matching brackets while editing.
               ConditionalProcessor(
                   processor=HighlightMatchingBracketProcessor(chars='[](){}'),
                   filter=HasFocus(DEFAULT_BUFFER) & ~IsDone()),
            ])

        with self._completer_lock:
            buf = RSBuffer(
                auto_suggest=AutoSuggestFromHistory(),
                always_multiline=self.multi_line,
                multiline_mode=self.multiline_mode,
                completer=self.completer,
                history=history,
                complete_while_typing=Always(),
                accept_action=AcceptAction.RETURN_DOCUMENT)

            editing_mode = EditingMode.VI if self.vi_mode else EditingMode.EMACS

            application = Application(
                style=style_factory(self.syntax_style, self.cli_style),
                layout=layout,
                buffer=buf,
                key_bindings_registry=key_binding_manager.registry,
                on_exit=AbortAction.RAISE_EXCEPTION,
                on_abort=AbortAction.RETRY,
                ignore_case=True,
                editing_mode=editing_mode)

            cli = CommandLineInterface(application=application,
                                       eventloop=self.eventloop)

            return cli

    def _should_show_limit_prompt(self, status, cur):
        """returns True if limit prompt should be shown, False otherwise."""
        if not is_select(status):
            return False
        return self.row_limit > 0 and cur and cur.rowcount > self.row_limit

    def _evaluate_command(self, text):
        """Used to run a command entered by the user during CLI operation
        (Puts the E in REPL)

        returns (results, MetaQuery)
        """
        logger = self.logger
        logger.debug('sql: %r', text)

        all_success = True
        meta_changed = False  # CREATE, ALTER, DROP, etc
        mutated = False  # INSERT, DELETE, etc
        ws_changed = False
        path_changed = False
        output = []
        total = 0

        # Run the query.
        start = time()
        on_error_resume = self.on_error == 'RESUME'
        res = self.rsexecute.run(text, exception_formatter, on_error_resume)

        for title, cur, headers, status, sql, success in res:
            logger.debug("headers: %r", headers)
            logger.debug("rows: %r", cur)
            logger.debug("status: %r", status)
            threshold = self.row_limit
            if self._should_show_limit_prompt(status, cur):
                click.secho('The result set has more than %s rows.'
                            % threshold, fg='red')
                if not click.confirm('Do you want to continue?'):
                    click.secho("Aborted!", err=True, fg='red')
                    break

            if  self.auto_expand:
                max_width = self.cli.output.get_size().columns
            else:
                max_width = None

            expanded = self.expanded_output
            settings = OutputSettings(
                table_format=self.table_format,
                dcmlfmt=self.decimal_format,
                floatfmt=self.float_format,
                missingval=self.null_string,
                expanded=expanded,
                max_width=max_width,
                case_function=(
                    self.completer.case if self.settings['case_column_headers']
                    else lambda x: x
                )
            )
            formatted = format_output(title, cur, headers, status, settings)

            output.extend(formatted)
            total = time() - start

            # Keep track of whether any of the queries are mutating or changing
            # the workspace
            if success:
                mutated = mutated or is_mutating(status)
                ws_changed = ws_changed or has_change_ws_cmd(sql)
                meta_changed = meta_changed or has_meta_cmd(sql)
                path_changed = path_changed or has_change_path_cmd(sql)
            else:
                all_success = False

        meta_query = MetaQuery(text, all_success, total, meta_changed,
                               ws_changed, path_changed, mutated)

        return output, meta_query

    def _handle_server_closed_connection(self):
        """Used during CLI execution"""
        reconnect = click.prompt(
            'Connection reset. Reconnect (Y/n)',
            show_default=False, type=bool, default=True)
        if reconnect:
            try:
                self.rsexecute.connect()
                click.secho('Reconnected!\nTry the command again.', fg='green')
            except OperationalError as e:
                click.secho(str(e), err=True, fg='red')

    def refresh_completions(self, history=None, persist_priorities='all'):
        """ Refresh outdated completions

        :param history: A prompt_toolkit.history.FileHistory object. Used to
                        load keyword and identifier preferences

        :param persist_priorities: 'all' or 'keywords'
        """

        callback = functools.partial(self._on_completions_refreshed,
                                     persist_priorities=persist_priorities)
        self.completion_refresher.refresh(self.rsexecute,
            callback, history=history, settings=self.settings)
        return [(None, None, None,
                'Auto-completion refresh started in the background.')]

    def _on_completions_refreshed(self, new_completer, persist_priorities):
        self._swap_completer_objects(new_completer, persist_priorities)

        if self.cli:
            # After refreshing, redraw the CLI to clear the statusbar
            # "Refreshing completions..." indicator
            self.cli.request_redraw()

    def _swap_completer_objects(self, new_completer, persist_priorities):
        """Swap the completer object in cli with the newly created completer.

            persist_priorities is a string specifying how the old completer's
            learned prioritizer should be transferred to the new completer.

              'none'     - The new prioritizer is left in a new/clean state

              'all'      - The new prioritizer is updated to exactly reflect
                           the old one

              'keywords' - The new prioritizer is updated with old keyword
                           priorities, but not any other.
        """
        with self._completer_lock:
            old_completer = self.completer
            self.completer = new_completer

            if persist_priorities == 'all':
                # Just swap over the entire prioritizer
                new_completer.prioritizer = old_completer.prioritizer
            elif persist_priorities == 'keywords':
                # Swap over the entire prioritizer, but clear name priorities,
                # leaving learned keyword priorities alone
                new_completer.prioritizer = old_completer.prioritizer
                new_completer.prioritizer.clear_names()
            elif persist_priorities == 'none':
                # Leave the new prioritizer as is
                pass

            # When rscli is first launched we call refresh_completions before
            # instantiating the cli object. So it is necessary to check if cli
            # exists before trying the replace the completer object in cli.
            if self.cli:
                self.cli.current_buffer.completer = new_completer

    def get_completions(self, text, cursor_positition):
        with self._completer_lock:
            return self.completer.get_completions(
                Document(text=text, cursor_position=cursor_positition), None)

    def get_prompt(self, string):
        # shorten api_server
        api_server = self.rsexecute.api_server or '(none)'
        if api_server[:8] == 'https://':
            api_server = api_server[8:]
        elif api_server[:7] == 'http://':
            api_server = api_server[7:]
        if api_server[-11:] == '.rockset.io':
            api_server = api_server[:-11]

        # should be before replacing \\d
        string = string.replace('\\t', self.now.strftime('%x %X'))
        string = string.replace('\\a', self.rsexecute.account or '')
        string = string.replace('\\s', api_server)
        string = string.replace('\\w', self.rsexecute.workspace or '(none)')
        string = string.replace('\\#', "#" if (self.rsexecute.superuser) else ">")
        string = string.replace('\\n', "\n")
        return string

    def get_last_query(self):
        """Get the last query executed or None."""
        return self.query_history[-1][0] if self.query_history else None


@click.command()
@click.option('-k', '--api-key', 'api_key',
    help='API key to connect to Rockset.')
@click.option('-s', '--api-server', 'api_server',
    default='api-us-west-2.rockset.io',
    help='Host address of the Rockset API server.')
@click.option('-w', '--workspace', default='public',
    help='Workspace to connect to.')
@click.option('--auto-vertical-output', is_flag=True,
    help='Automatically switch to vertical output mode if the '
    'result is wider than the terminal width.')
@click.option('--row-limit', default=None, type=click.INT,
    help='Set threshold for row limit prompt. Use 0 to disable prompt.')
@click.option('--rsclirc', default=os.path.join(config_location(), 'config'),
    help='Location of rsclirc file.', type=click.Path(dir_okay=False))
@click.option('--prompt',
    help='Prompt format (Default: "\\a@\\s:\\w> ").')
@click.option('--single-connection', 'single_connection', is_flag=True,
    default=False,
    help='Do not use a separate connection for completions.')
@click.argument('target', default=None, nargs=1)
def cli(target, api_key, api_server, workspace,
        auto_vertical_output, row_limit, rsclirc, prompt, single_connection):
    return cli_main(target=target, api_key=api_key, api_server=api_server,
        workspace=workspace, auto_vertical_output=auto_vertical_output,
        row_limit=row_limit, rsclirc=rsclirc, prompt=prompt,
        single_connection=single_connection)

def cli_main(target=None, api_key=None, api_server=None, workspace=None,
        auto_vertical_output=None, row_limit=None, rsclirc=None, prompt=None,
        single_connection=None):
    # static config options
    less_chatty = False

    config_dir = os.path.dirname(config_location())
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # instantiate RSCli
    rscli = RSCli(rsclirc_file=rsclirc,
        auto_vertical_output=auto_vertical_output, less_chatty=less_chatty,
        prompt=prompt, row_limit=row_limit, single_connection=single_connection)

    # connect to target
    if target is not None:
        uri = urlparse(target)
        api_server = (uri.hostname or api_server)
        api_key = (uri.username or api_key)
        workspace = (uri.path[1:] or workspace)
    rscli.connect(api_server=api_server, api_key=api_key, workspace=workspace)
    rscli.logger.debug('Launch Params: \n'
            '\tAPI Server: %r'
            '\tAPI Key: %r'
            '\tWorkspace: %r'
            % (api_server, api_key[:4] + '*' * (len(api_key) - 4), workspace))


    # protect process line if api_key was specified in it
    if setproctitle:
        obfuscate_process_password()

    # lets go!
    rscli.run_cli()


def obfuscate_process_password():
    process_title = setproctitle.getproctitle()
    if '://' in process_title:
        process_title = re.sub(r"://([^:]*):([^@.]*)@", r"://xxx:xxx@",
            process_title)
        process_title = re.sub(r"://([^:@]*)@", r"://xxx:xxx@",
            process_title)
    if "--api-key " in process_title or "-k " in process_title:
        process_title = re.sub(r"--api-key (.+?)((\s[a-zA-Z]+=)|$)",
            r"--api_key xxx\2", process_title)
        process_title = re.sub(r"-k (.+?)((\s[a-zA-Z]+=)|$)",
            r"-k xxx\2", process_title)
    setproctitle.setproctitle(process_title)


def has_meta_cmd(query):
    """Determines if the completion needs a refresh by checking if the sql
    statement is an alter, create, drop, commit or rollback."""
    try:
        first_token = query.split()[0]
        if first_token.lower() in ('alter', 'create', 'drop', 'commit', 'rollback'):
            return True
    except Exception:
        return False

    return False


def has_change_ws_cmd(query):
    """Determines if the statement is a workspace switch such as 'use' or '\\c'"""
    try:
        first_token = query.split()[0]
        if first_token.lower() in ('use', '\\c', '\\connect'):
            return True
    except Exception:
        return False

    return False


def has_change_path_cmd(sql):
    """Determines if the search_path should be refreshed by checking if the
    sql has 'set search_path'."""
    return 'set search_path' in sql.lower()


def is_mutating(status):
    """Determines if the statement is mutating based on the status."""
    if not status:
        return False

    mutating = set(['insert', 'update', 'delete'])
    return status.split(None, 1)[0].lower() in mutating


def is_select(status):
    """Returns true if the first word in status is 'select'."""
    if not status:
        return False
    return status.split(None, 1)[0].lower() == 'select'


def quit_command(sql):
    return (sql.strip().lower() == 'exit'
            or sql.strip().lower() == 'quit'
            or sql.strip() == r'\q'
            or sql.strip() == ':q')


def exception_formatter(e):
    return click.style(utf8tounicode(str(e)), fg='red')


def format_output(title, cur, headers, status, settings):
    output = []
    expanded = (settings.expanded or settings.table_format == 'vertical')
    table_format = ('vertical' if settings.expanded else
                    settings.table_format)
    max_width = settings.max_width
    case_function = settings.case_function
    formatter = TabularOutputFormatter(format_name=table_format)

    def format_array(val):
        if val is None:
            return settings.missingval
        if not isinstance(val, list):
            return val
        return '{' + ','.join(text_type(format_array(e)) for e in val) + '}'

    def format_arrays(data, headers, **_):
        data = list(data)
        for row in data:
            row[:] = [
                format_array(val) if isinstance(val, list) else val
                for val in row
            ]

        return data, headers

    output_kwargs = {
        'sep_title': 'RECORD {n}',
        'sep_character': '-',
        'sep_length': (1, 25),
        'missing_value': settings.missingval,
        'integer_format': settings.dcmlfmt,
        'float_format': settings.floatfmt,
        'preprocessors': (format_numbers, format_arrays),
        'disable_numparse': True,
        'preserve_whitespace': True
    }
    if not settings.floatfmt:
        output_kwargs['preprocessors'] = (align_decimals, )

    if title:  # Only print the title if it's not None.
        output.append(title)

    if cur:
        headers = [case_function(utf8tounicode(x)) for x in headers]
        if max_width is not None:
            cur = list(cur)
        column_types = None
        if hasattr(cur, 'description'):
            column_types = []
            for d in cur.description:
                column_types.append(d[1])
        formatted = formatter.format_output(cur, headers, **output_kwargs)
        if isinstance(formatted, (text_type)):
            formatted = iter(formatted.splitlines())
        first_line = next(formatted)
        formatted = itertools.chain([first_line], formatted)

        if (not expanded and max_width and len(first_line) > max_width and headers):
            formatted = formatter.format_output(
                cur, headers, format_name='vertical', column_types=None, **output_kwargs)
            if isinstance(formatted, (text_type)):
                formatted = iter(formatted.splitlines())

        output = itertools.chain(output, formatted)

    if status:  # Only print the status if it's not None.
        output = itertools.chain(output, [status])

    return output


if __name__ == "__main__":
    cli()
