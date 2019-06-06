"""\
Confluence Tool is for doing batch operations in confluence.

Run for inital configuration::

   ct -b BASE_URL -u USERNAME config

Run for updating configuration::

   ct -b BASE_URL -u USERNAME config --update-password

These two commands configure _default_ Configuration.  If you need multiple
confiugrations, you can name them with :option:`ct -c` option::

   ct -c doc -b BASE_URL -u USERNAME config

Run a command using this config by speficying :option:`ct -c`::

   ct -c doc show --ls 'space = FOO'
"""
from argdeco import CommandDecorator, arg, mutually_exclusive, group

command = CommandDecorator(
    arg('-c', '--config',      help="provide optional configuration name (default: 'default')", default='default'),
    arg('-C', '--config-file', help="configuration file (default ~/.confluence-tool.yaml)"),
    arg('-b', '--baseurl',     help="confluence Base URL, e.g. http://example.com/confluence"),
    arg('-u', '--username',    help="username for logging in (if not present, tried to read from netrc)"),
    arg('-p', '--password',    help="password for logging in (if not present, tried to read from netrc)"),
    arg('-d', '--debug',       action="store_true", help="get more information on exceptions"),
    arg('-q', '--quiet',       action="store_true", help="be quiet"),
    prog='ct',
)

arg_cql = positional_arg_cql = arg('cql', help="SPACE:title, pageID or CQL, run 'ct help-cql' for more help")
optarg_cql = positional_optarg_cql = arg('cql', nargs="?", help="SPACE:title, pageID or CQL, 'ct help-cql' for more help")

arg_pagename = arg('pagename', help="SPACE:title")

arg_expand  = arg('-e', '--expand', help="values to expand")
arg_filter  = arg('-f', '--filter', help="page property filter run 'ct page-prop-filtering -h' for more help")
arg_state   = arg('-s', '--state', help="get all pages for corresponding state 'ct cw-states -h' for more help")
arg_status   = arg('-S', '--status', help="get all pages for corresponding status")
arg_write_format = arg('-w', '--write', help="format to write", choices=['format', 'yaml', 'json'], default="yaml")
arg_format  = arg('-F', '--format', help="format string for formatting the output.  May be either mustache or format string")
arg_page_type  = arg('-T', '--page-type', choices=['page', 'blogpost'], help="page type", default='page')
arg_parent  = arg('-p', '--parent', help="specify parent for a page, which might be created")
arg_message = arg('-m', '--message', help="add a note or message")
arg_add_label = arg('-l', '--label', action="append", help="add these labels to the page")
arg_label   = arg('-l', '--label', help="with label(s)")
arg_field   = arg('field', nargs="*", help='field to dump')

arg_parent = arg('-p', '--parent', help="specify parent for a page, which might be created")
#def arg_parent(parser, namespace, values, option_string=None):

@command('help-cql')
def cql_help(config):
    """\
    How to query pages
    ~~~~~~~~~~~~~~~~~~

    You can pass [CQL] queries to many commands (indicated by parameter cql).
    In many queries you have to specify the ID, which originally needs an extra
    step to find it out.  So there is a convenience syntax for most common
    queries.

    [CQL]: https://developer.atlassian.com/confdev/confluence-server-rest-api/advanced-searching-using-cql

    Here you find a little translation of convenience syntax to CQL:

    - `<QUERY> ">>"` -> `ancestor = <ID of result of QUERY>`
    - `<QUERY> ">"`  -> `parent   = <ID of result of QUERY>`
    - `<SPACE> ":" <TITLE>` -> `space = <SPACE> and title = "<TITLE>"`
    - `":" <TITLE>`   -> `title = "<TITLE>"`
    - `<PAGE_ID>`  -> `ID = <PAGE_ID>`
    - `<PAGE_URI>` -> `ID = <page ID from PAGE_URI>`

    Examples:

     - `"IT:Some title>>"` to find all descendent pages of page with title
       "Some title" in space "IT"

     - `"IT:Some title"` to find page titled "Some title" in space "IT"

    """
    command['help-cql'].print_help()

@command('help-cw-states')
def comala_workflow_states(config):
    """How to filter page versions for specific state.

    If you want to get the Approved version of all pages, a simple
    `... and state = "Approved"` gives you only the pages currently in state
    Approved, but will not return the Approved version of pages, which are
    currently in a different state.

    The filter "--state <STATENAME>" will provide you the last version of the
    corresponding state.
    """
    command['cw-states'].print_help()

@command('help-page-prop-filtering')
def page_prop_filtering(config):
    """How to filter pages using page properties.

    Addionally to CQL queries, you can filter results (on client side) using
    page property filters.

    These filters are pretty simple, but helpful :)

    Page property filters are passes with `-F` command line option, and you can
    repeat this option to pass multiple filters, which all have to match against
    a page.
    l
    - `-F <NAME>==<VALUE>`  Value must be in property named `<NAME>`.  If
      property is a list, then this is true, if `<VALUE>` is one of the list
      values.  (works like labels in CQL).

    - `-F <NAME>!=<VALUE>`  Value must not be in property named `<NAME>`.

    - `-F '!<NAME>'`  Matches if property `<NAME>` is not present in page

    - `-F '<NAME>?'`  Matches if property `<NAME>` is present in page

    """

    command['page-prop-filtering'].print_help()

import pyaml, re, sys

method_args = [
    arg('url', help="url start with / or /rest/ will be prepended"),
    arg('--stream', help="get raw data", default=False, action="store_true"),
    arg('--progress', help="write out progress to stderr", default=False, action="store_true"),
    arg('--output-file', '-o', help="output file"),
    arg('--header', '-H', help="header data in yaml format, can be repeated", action="append", default=[]),
    arg('params', nargs="*", help="parameters to pass to url")
]

def _handle_method(method, config, data=None, json=None):
    """
    Send data to confluence with %(method)s method.

    Simple request:

        ct %(method_)s /rest/api/space -

    """

    PARAM = re.compile(r'(.*?)=(.*)')

    params = {}
    for item in config.get('params'):
        if item == '-':
            data = sys.stdin.read()
            try:
                json = yaml.loads(inputdata)
                data = None
            except:
                pass

        m = PARAM.search(item)
        if m:
            (name, value) = m.groups()
            params[name] = value

    headers = {}
    for item in config.get('header', []):
        for k,v in yaml.loads(item).items():
            headers[k] = v

    url = config.get('url')

    output_file = config.get('output_file')
    if output_file and output_file != '-':
        outstream = open(output_file, 'wb')
    else:
        outstream = sys.stdout

    progress = config.get('progress')

    if 1:
        if not url.startswith('/'):
            url = '/rest/'+url

        confluence = config.getConfluenceAPI()

        result = confluence.request(method, url, stream=config.get('stream'), json=json, data=data, **params)
        if config.get('stream'):
            _len = 0
            for data in result.iter_content(chunk_size=1024*1024):
                outstream.write(data)

                _len += len(data)
                if progress:
                    sys.stderr.write("\r%s bytes" % _len)
        else:
            pyaml.p(result)


@command('post', *method_args)
def post_method(config):
    return _handle_method('POST', config)
post_method.__doc__ = _handle_method.__doc__ % dict(method='POST', method_='post')


@command('get', *method_args)
def get_method(config):
    return _handle_method('GET', config)
get_method.__doc__ = _handle_method.__doc__ % dict(method='GET', method_='get')


@command('put', *method_args)
def get_method(config):
    return _handle_method('PUT', config)
get_method.__doc__ = _handle_method.__doc__ % dict(method='PUT', method_='put')


@command('delete', *method_args)
def get_method(config):
    return _handle_method('DELETE', config)
get_method.__doc__ = _handle_method.__doc__ % dict(method='DELETE', method_='delete')

