# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path

import magic
from prettytable import PrettyTable

WHITELIST = [
    {"t": "gzip compressed data", "ext": ".gz"},
    {"t": "PNG image data", "ext": ".png"},
    {"t": "Python script", "ext": ".py"},
    {"t": "ASCII text", "ext": [".txt", ".py"]},
]


def check_type(ifile: Path) -> tuple:
    f = magic.Magic(mime=True)
    try:
        return (
            magic.from_file(str(ifile)).split(",")[0].strip(),
            f.from_file(str(ifile)),
        )
    except UnicodeDecodeError:
        return ("---", "---")
    except PermissionError:
        return ("cannot open", "---")


def check_ok(checked: str, ext: str, whitelist: dict) -> str:
    status = "Unknown"
    if not ext or "cannot open" in checked:
        pass
    else:
        for entry in whitelist:
            if ext in entry["ext"]:
                if checked not in entry["t"]:
                    status = "Mismatch"
                else:
                    status = "Match"
                    return status
    return status


def cli(p: Path, args: argparse):
    t = PrettyTable(["File Name", "File Type", "MIME Type", "Status"])
    t.align = "l"
    t.header_style = "upper"
    c = 0  # count number of files
    g = 0  # count good files
    b = 0  # count bad files
    u = 0  # count unknown files
    if args.whitelist:
        with open(args.whitelist) as f:
            whitelist = json.load(f)
    else:
        whitelist = WHITELIST

    for dirs in list(p.glob("**/**")):
        for ifile in dirs.iterdir():
            if ifile.is_file():
                checked, mime = check_type(ifile)
                ext = ifile.suffix
                ok = check_ok(checked, ext, whitelist)
                if ok == "Match" and not args.no_good:
                    g += 1
                    t.add_row([ifile, checked, mime, ok])
                elif ok == "Mismatch" and not args.no_bad:
                    b += 1
                    t.add_row([ifile, checked, mime, ok])
                elif ok == "Unknown" and not args.no_unknown:
                    u += 1
                    t.add_row([ifile, checked, mime, ok])
                c += 1

    print(f"Analyzed {c} files")
    if not args.no_good:
        print(f"Matched: {g}")
    if not args.no_bad:
        print(f"Mismatched: {b}")
    if not args.no_unknown:
        print(f"Unknown: {u}")
    print(t.get_string(sortby="Status"))


def get_args():
    p = argparse.ArgumentParser(description="Module 2 thing")
    p.add_argument("directory", help="The directory where analysis will start")
    p.add_argument("-ng", "--no-good", action="count", help="Do not show matches")
    p.add_argument("-nb", "--no-bad", action="count", help="Do not show mismatches")
    p.add_argument("-nu", "--no-unknown", action="count", help="Do not show unknown")
    p.add_argument(
        "-w", "--whitelist", help="Path to custom whitelist"
    )
    return p.parse_args()


def main():
    args = get_args()
    p = Path(args.directory)
    if p.is_dir():
        cli(p, args)
    else:
        print(f"Path {p} not found.")

if __name__ == "__main__":
    main()
