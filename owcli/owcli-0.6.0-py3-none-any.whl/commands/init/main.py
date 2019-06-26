"""Command1

Usage:
  {cli} <root> [-n <your_name>|--name <your_name>] [-m <mail_address>|--mail <mail_address>]
  {cli} (-h | --help)

Options:
  <root>                         Root directory.
  -n, --name <your_name>         Your name.
  -m, --mail <mail_address>      Your mail address.
  -h --help                      Show this screen.
"""
import os
import shutil
import sys

from owlmixin import OwlMixin, TOption

TEMPLATE_DIR = os.path.abspath(f"{os.path.dirname(__file__)}/../../template")
TEMPLATE_ENTRIES = os.listdir(TEMPLATE_DIR)


def exists_any(dst: str) -> bool:
    return any(map(lambda e: os.path.exists(f"{dst}/{e}"), TEMPLATE_ENTRIES))


def copy_recursively(tmpl_current: str, dst_current: str, root: str, depth: int = 0):
    for e in os.listdir(tmpl_current):
        if os.path.isdir(f"{tmpl_current}/{e}"):
            if e == "__pycache__":
                continue
            path_from_dst = root if e == "yourapp" else e
            print(f" {'  ' * depth}∟📂 {path_from_dst}")
            os.mkdir(f"{dst_current}/{path_from_dst}")
            copy_recursively(
                f"{tmpl_current}/{e}", f"{dst_current}/{path_from_dst}", root, depth + 1
            )
        else:
            print(f" {'  ' * depth}∟📄 {e}")
            shutil.copy(f"{tmpl_current}/{e}", f"{dst_current}/{e}")


def replace_in_file(path: str, before: str, after: str):
    with open(path, "r") as f:
        dt = f.read()
    with open(path, "w") as f:
        f.write(dt.replace(before, after))


class Args(OwlMixin):
    root: str
    name: TOption[str]
    mail: TOption[str]


def run(args: Args):
    dst = os.path.abspath(args.root)

    if exists_any(dst):
        print(f"There is more than one of {TEMPLATE_ENTRIES} in {dst}.")
        print("Remove them and try again.")
        sys.exit(1)

    print(f"------------------------")
    print(f"| Create entries...    |")
    print(f"------------------------")
    if not os.path.exists(dst):
        os.mkdir(dst)
    print(f"📂 {dst}")
    copy_recursively(TEMPLATE_DIR, dst, args.root, 0)

    replace_in_file(f"{dst}/{args.root}/main.py", "__yourapp", args.root)
    replace_in_file(f"{dst}/README.md", "__yourapp", args.root)
    replace_in_file(f"{dst}/setup.py", "__yourapp", args.root)
    args.name.map(lambda name: replace_in_file(f"{dst}/setup.py", "__yourname", name))
    args.mail.map(lambda address: replace_in_file(f"{dst}/setup.py", "__youraddress", address))

    print("")
    print(f"------------------------")
    print(f"| Next you have to ... |")
    print(f"------------------------")
    print(f"$ cd {args.root}")
    print(f"# Change python_version in Pipfile if you don't want to use specified version.")
    print(f"$ pipenv install")
    print(f"$ pipenv run python {args.root}/main.py --help")

