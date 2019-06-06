import sys, re
from .cli import command, arg, arg_cql, arg_filter
import pyaml
from ..confluence_api import ConfluenceError

@command('labels',
    arg_cql,
    arg_filter,
    arg('-a', '--add', action="append", help="label to add"),
    arg('-r', '--remove', action="append", help="label to remove"),
    arg('-q', '--quiet', action="store_true", help="do not show labels of the page"),
    )
def cmd_page_prop_get(config):
    confluence = config.getConfluenceAPI()
    results = []
    config['cql'] = confluence.resolveCQL(config['cql'])
    first = True
    for pp in confluence.getPages(**config.dict('cql', 'filter')):
        if first:
            first = False
        else:
            print "---"

        if config.get('add'):
            results.append(confluence.addLabels(pp.id, config['add']))
        if config.get('remove'):
            try:
                results.append(confluence.deleteLabels(pp.id, config['remove']))
            except ConfluenceError as e:
                print "Warning: %s" % e
                continue

        pyaml.p(pp.dict('id', 'spacekey', 'title', 'labels'))
