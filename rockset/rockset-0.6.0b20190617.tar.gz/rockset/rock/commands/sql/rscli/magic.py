from .main import RSCli
import sql.parse
import sql.connection
import logging

_logger = logging.getLogger(__name__)


def load_ipython_extension(ipython):
    """This is called via the ipython command '%load_ext rscli.magic'"""

    # first, load the sql magic if it isn't already loaded
    if not ipython.find_line_magic('sql'):
        ipython.run_line_magic('load_ext', 'sql')

    # register our own magic
    ipython.register_magic_function(rscli_line_magic, 'line', 'rscli')


def rscli_line_magic(line):
    _logger.debug('rscli magic called: %r', line)
    parsed = sql.parse.parse(line, {})
    conn = sql.connection.Connection.get(parsed['connection'])

    try:
        # A corresponding rscli object already exists
        rscli = conn._rscli
        _logger.debug('Reusing existing rscli')
    except AttributeError:
        # I can't figure out how to get the underylying Rockset connection
        # from the sqlalchemy connection, so just grab the url and make a
        # new connection
        rscli = RSCli()
        u = conn.session.engine.url
        _logger.debug('New rscli: %r', str(u))

        rscli.connect(u.database, u.host, u.username, u.port, u.password)
        conn._rscli = rscli

    # For convenience, print the connection alias
    print('Connected: {}'.format(conn.name))

    try:
        rscli.run_cli()
    except SystemExit:
        pass

    if not rscli.query_history:
        return

    q = rscli.query_history[-1]

    if not q.successful:
        _logger.debug('Unsuccessful query - ignoring')
        return

    if q.meta_changed or q.db_changed or q.path_changed:
        _logger.debug('Dangerous query detected -- ignoring')
        return

    ipython = get_ipython()
    return ipython.run_cell_magic('sql', line, q.query)
