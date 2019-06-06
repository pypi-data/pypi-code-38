from .cli import command, arg, optarg_cql, arg_filter, arg_parent, arg_cql, arg_message, arg_expand
import pyaml, sys

cw_command = command.add_subcommands('cw', help="comala workflows")

def print_info(page, result):
    pyaml.p(dict(
        id = page.id,
        spacekey = page.spacekey,
        title = page.title,
        cwInfo = result))

@cw_command('info',
    arg_cql,
    arg_expand
)
def cw_info(config):
    """get workflow information about given pages
    """
    confluence = config.getConfluenceAPI()
    first = True
    for page in confluence.getPages(pages=config.cql):
        if not first:
            print "---"
        result = confluence.cwInfo(page, config.expand)
        first = False
        print_info(page, result)

@cw_command('approve', arg_cql, arg_message,
    arg('-n', '--name', help="approval name")
)
def cw_approve(config):
    """approve a page
    """
    confluence = config.getConfluenceAPI()

    message = config.get('message', '')
    if message == '-':
        message = sys.stdin.read()

    first = True
    for page in confluence.getPages(pages=config.cql):
        if not first:
            print "---"
        first = False
        if not config.name:
            result = confluence.cwInfo(page,expand='approvals')

            if 'approvals' not in result:
                result['message'] = 'approvals not in result'
                print_info(page, result)
                continue

            if len(result['approvals']) > 1:
                names = ", ".join([ a['name'] for a in result['approvals'] ])
                raise RuntimeError("please pass --name with one of %s" % (names,))

            if result['state']['final']:
                print_info(page, result)
                continue

            if len(result['approvals']) != 1:
                result['message'] = 'ambigious approvals, specify one with -n'
                print_info(page, result)
                continue

            name = result['approvals'][0]['name']

        else:
            name = config.name

        result = confluence.cwApprove(page, name=name, note=message)
        print_info(page, result)


@cw_command('reject', arg_cql, arg_message,
    arg('-n', '--name', help="approval name"),
)
def cw_reject(config):
    """reject a page
    """
    confluence = config.getConfluenceAPI()

    message = config.get('message', '')
    if message == '-':
        message = sys.stdin.read()

    first = True
    for page in confluence.getPages(pages=config.cql):
        if not first:
            print "---"
        first = False
        if not config.name:
            result = confluence.cwInfo(page,expand='approvals')
            if len(result['approvals']) > 1:
                names = ", ".join([ a['name'] for a in result['approvals'] ])
                raise RuntimeError("please pass --name with one of %s" % (names,))

            if result['state']['final']:
                print_info(page, result)
                continue

            if len(result['approvals']) != 1:
                result['message'] = 'ambigious approvals, specify one with -n'
                print_info(page, result)
                continue

            name = result['approvals'][0]['name']

        else:
            name = config.name

        result = confluence.cwReject(page, name=name, note=message)

        print_info(page, result)
