from hatano.deploy import deploy
from hatano.update import update
from hatano.clean import clean

from hatano.actions import init
from hatano.actions import add
from hatano.actions import remove
from hatano.actions import show
from hatano.actions import edit

import argparse

__version__ = '1.0.1'
__author__ = 'Jared Nishikawa'
__author_email__ = 'jared@tripleko.com'
__description__ = 'Microframework for Lambda/API gateway'


def handle():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")

    init_parser = subparsers.add_parser("init")

    deploy_parser = subparsers.add_parser("deploy")
    update_parser = subparsers.add_parser("update")
    clean_parser = subparsers.add_parser("clean")
    show_parser = subparsers.add_parser("show")

    add_parser = subparsers.add_parser("add")
    sub_addparsers = add_parser.add_subparsers(dest="object")

    stage_parser = sub_addparsers.add_parser("stage")
    stage_parser.add_argument("stage")
    stage_parser.add_argument("--copy")
    stage_parser.add_argument("--source", default="src")
    stage_parser.add_argument("--runtime", default="")
    stage_parser.add_argument("--domain", default="")
    stage_parser.add_argument("--cert", default="")

    func_parser = sub_addparsers.add_parser("function")
    func_parser.add_argument("name")
    func_parser.add_argument("--handler", required=True)
    func_parser.add_argument("--method", required=True)
    func_parser.add_argument("--path", required=True)
    func_parser.add_argument("--stage", required=True)

    edit_parser=subparsers.add_parser("edit")
    sub_editparsers = edit_parser.add_subparsers(dest="object")

    stage_edit_parser = sub_editparsers.add_parser("stage")
    stage_edit_parser.add_argument("stage")
    stage_edit_parser.add_argument("--copy")
    stage_edit_parser.add_argument("--source", default="")
    stage_edit_parser.add_argument("--runtime", default="")
    stage_edit_parser.add_argument("--domain", default="")
    stage_edit_parser.add_argument("--cert", default="")

    func_edit_parser = sub_editparsers.add_parser("function")
    func_edit_parser.add_argument("name")
    func_edit_parser.add_argument("--handler", default="")
    func_edit_parser.add_argument("--method", default="")
    func_edit_parser.add_argument("--path", default="")
    func_edit_parser.add_argument("--stage", required=True)

    rm_parser = subparsers.add_parser("rm")
    sub_rmparsers = rm_parser.add_subparsers(dest="object")

    stage_rm_parser = sub_rmparsers.add_parser("stage")
    stage_rm_parser.add_argument("stage")

    func_rm_parser = sub_rmparsers.add_parser("function")
    func_rm_parser.add_argument("function")
    func_rm_parser.add_argument("--stage", required=True)

    deploy_parser.add_argument("stage")
    update_parser.add_argument("stage")
    clean_parser.add_argument("stage")

    args = parser.parse_args()

    if args.action == "deploy":
        deploy(args)

    elif args.action == "update":
        update(args)

    elif args.action == "clean":
        clean(args)

    elif args.action == "init":
        init(args)

    elif args.action == "add":
        add(args)

    elif args.action == "edit":
        edit(args)

    elif args.action == "rm":
        remove(args)

    elif args.action == "show":
        show(args)
