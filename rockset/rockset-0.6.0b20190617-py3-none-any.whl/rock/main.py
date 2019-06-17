# -*- coding: utf-8 -*-
import sys

from docopt import docopt
from rockset import version
from rockset.credentials import Credentials
from rockset.exception import AuthError

def main(args=None):
    # init args from sys
    if args is None:
        args = sys.argv[1:]

    usage = """
Command line interface to Rockset 

Usage: 
    rock [--version] [-h]
    rock help <command>
    rock [-v | -vv | -vvv] [-o=FORMAT] [-p=PROFILE] <command> [<args>...]

Commands:
    * Basic:
        create                          create a new resource
        describe                        get detailed information about a resource
        delete                          drop an existing resource
        list                            list resources of a given type
        sql                             run a SQL query from command-line or enter SQL REPL

    * Collection:
        get                             retrieve documents from a collection
        rm                              remove a document from a collection
        setstate                        sets the state of a collection to READY or PAUSED
        upload                          upload local files to a collection

    * Other:
        configure                       setup auth credentials via API keys
        help                            more information on a specific command
        play                            play a game of {rock,paper,scissors}

Resources:
    * collection                        a dataset, comprised of documents
    * integration                       credentials that connect Rockset to an external service
    * workspace                         organizational container for collections, can be nested like folders

Options:
    --version                           display rockset version and exit
    -h, --help                          print help message and exit
    -v, --verbose                       increase output verbosity
    -vv                                 increase output verbosity, two levels
    -vvv                                increase output verbosity, three levels
    -o, --format=FORMAT          select output format; one of {json,text,yaml} [default: text]
    -p, --profile=PROFILE       select name of the credentials profile to use
"""
    parsed_args = docopt(usage, argv=args, help=False, version=version(), options_first=True)

    if parsed_args['help']:
        return main(args=[parsed_args['<command>'], '--help'])

    alias_to_command = {
        'setup': 'configure',
        'drop': 'delete',
        'ls': 'list',
        'query': 'sql',
    }

    # setup command and args
    command = parsed_args['<command>']
    if command in alias_to_command:
        command = alias_to_command[command]
    argv = [command] + parsed_args['<args>']

    # setup credentials
    Credentials().setup()

    # process the command - delayed imports save load time for every run
    if command == 'configure':
        from rockset.rock.commands.configure import Configure
        command_cls = Configure
    elif command == 'create':
        from rockset.rock.commands.create import Create
        command_cls = Create
    elif command == 'describe':
        from rockset.rock.commands.describe import Describe
        command_cls = Describe
    elif command == 'setstate':
        from rockset.rock.commands.setstate import SetState
        command_cls = SetState
    elif command == 'delete':
        from rockset.rock.commands.drop import Drop
        command_cls = Drop
    elif command == 'list':
        from rockset.rock.commands.list import List
        command_cls = List
    elif command == 'upload':
        from rockset.rock.commands.upload import Upload
        command_cls = Upload
    elif command == 'get':
        from rockset.rock.commands.get import Get
        command_cls = Get
    elif command == 'rm':
        from rockset.rock.commands.remove import Remove
        command_cls = Remove
    elif command == 'sql':
        from rockset.rock.commands.sqlquery import SQLQuery
        command_cls = SQLQuery
    elif command == 'play':
        from rockset.rock.commands.play import Play
        command_cls = Play
    else:
        print(usage)
        return 0

    # catch exceptions in constructor
    try:
        c = command_cls(**parsed_args)
    except AuthError as e:
        print('Error: {}'.format(str(e)), file=sys.stderr)
        print('Hint: Use "rock configure" to update your credentials.',
            file=sys.stderr)
        return 1
    except Exception as e:
        print('Error: {} {}'.format(type(e).__name__, str(e)), file=sys.stderr)
        return 1

    # let Command.main_go() deal with all exceptions here
    return c.main(argv)


if __name__ == '__main__':
    main()
