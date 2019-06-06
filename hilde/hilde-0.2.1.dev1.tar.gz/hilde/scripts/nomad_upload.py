""" Summarize output from ASE.md class (in md.log) """

import subprocess
from argparse import ArgumentParser
from pathlib import Path
from hilde import Settings
from hilde.helpers import Timer


def upload_command(folder, token):
    cmd = (
        f"tar cf - {folder} | curl -XPUT -# -HX-Token:{token} "
        "-N -F file=@- http://nomad-repository.eu:8000 | "
        "xargs echo"
    )
    return cmd


def main():
    """ main routine """
    parser = ArgumentParser(description="Upload folder to Nomad")
    parser.add_argument("folders", nargs="+", help="folder containing data to upload")
    parser.add_argument("--token", help="Nomad token for uploads")
    parser.add_argument("--dry", action="store_true", help="only show command")
    args = parser.parse_args()

    timer = Timer()

    settings = Settings()

    token = args.token

    if "nomad" in settings:
        token = settings.nomad.token

    if token is None:
        exit("** Token is missing, chech your hilde.cfg or provide manually")

    # from ASE
    if not args.folders:
        exit("No folders specified -- another job well done!")

    for ii, folder in enumerate(args.folders):

        cmd = upload_command(folder, token)

        if args.dry:
            print(f"Upload command {ii+1}:\n{cmd}")
        else:
            print(f"Uploading folder {ii+1} of {len(args.folders)}")

            subprocess.check_call(cmd, shell=True)

    if not args.dry:
        timer(f"Nomad upload finished")


if __name__ == "__main__":
    main()
