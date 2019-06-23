from hatano.conduct import Conductor
from hatano.clean import clean

from hatano.actions import init
from hatano.actions import make
from hatano.actions import remove
from hatano.actions import show
from hatano.actions import edit

import argparse

__version__ = '1.0.3'
__author__ = 'Tripleko LLC'
__author_email__ = 'jared@tripleko.com'
__description__ = 'Microframework for Lambda/API gateway'


def handle():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")
    actions = ["mk", "edit", "rm", "init", "deploy", "update", "clean", "show"]
    actionparsers = {}
    for action in actions:
        p = subparsers.add_parser(action)
        actionparsers[action] = p
    
    objects = ["stage", "function"]
    objectparsers = {}
    for action in actionparsers:

        if action == "init":
            p = actionparsers[action]
            p.add_argument("name")
            p.add_argument("--runtime", required=True)
            continue

        if action in {"deploy", "update", "clean"}:
            p = actionparsers[action]
            p.add_argument("stage")
            if action in {"deploy", "update"}:
                p.add_argument("--function", "-f", nargs="+")
                p.add_argument("--bucket", "-b", action="store_true")
            continue

        if action not in {"mk", "edit", "rm"}:
            continue

        _parser = actionparsers[action]
        _subparsers = _parser.add_subparsers(dest="object")
        for obj in objects:
            q = _subparsers.add_parser(obj)
    
            if obj == "stage":
                q.add_argument("stage")
                q.add_argument("--source", default="src")
                q.add_argument("--bucket")
                q.add_argument("--domain")
                q.add_argument("--cert")
    
            elif obj == "function":
                q.add_argument("function")
                if action in {"mk", "edit"}:
                    q.add_argument("--handler", required=True)
                    q.add_argument("--method", required=True)
                    q.add_argument("--path", required=True)
        
    
    args = parser.parse_args()

    if args.action == "deploy":
        C = Conductor(args)
        C.deploy()

    elif args.action == "update":
        C = Conductor(args)
        C.update()

    elif args.action == "clean":
        clean(args)

    elif args.action == "init":
        init(args)

    elif args.action == "mk":
        make(args)

    elif args.action == "edit":
        edit(args)

    elif args.action == "rm":
        remove(args)

    elif args.action == "show":
        show(args)
