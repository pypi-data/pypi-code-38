""" create a configuration file and working directory """

import shutil
from argparse import ArgumentParser
from pathlib import Path
from hilde import Settings, Configuration, DEFAULT_SETTINGS_FILE
from hilde import DEFAULT_GEOMETRY_FILE
from hilde import supported_tasks


def main():
    """ main routine """
    parser = ArgumentParser(description="create a configuration file and workdir")
    parser.add_argument("--settings", default=DEFAULT_SETTINGS_FILE, help="settings.in")
    parser.add_argument("-g", "--geometry", help="geometry file to use")
    parser.add_argument("-wd", "--workdir", default=".")
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()

    settings = Settings(settings_file=args.settings, config_file=None)
    configuration = Configuration()

    print("Summary of settings:")
    settings.print()

    for task in supported_tasks:
        if task in settings:
            break
    else:
        exit("Task could not be identified.")

    print(f"Task to be performed:  {task}")

    if "workdir" in settings[task]:
        workdir = settings[task].pop("workdir")
    else:
        workdir = args.workdir

    print(f"Working directory:     {workdir}")

    if Path(workdir).exists():
        print("**Error: Working directory exsits, chance of dataloss.")
    else:
        Path(workdir).mkdir()

    if args.dry:
        exit()

    # write settings without the configuration part
    settings_outfile = Path(workdir) / DEFAULT_SETTINGS_FILE
    settings.write(settings_outfile)
    print(f"Settings written to:   {settings_outfile}")

    # geometry
    if "file" in settings.geometry:
        geometry = settings.geometry.file
        outfile = Path(workdir) / geometry

    if args.geometry:
        geometry = args.geometry
        outfile = Path(workdir) / DEFAULT_GEOMETRY_FILE
        settings["geometry"]["file"] = DEFAULT_GEOMETRY_FILE

    if not outfile.exists():
        shutil.copy(geometry, outfile)
        print(f"Geometry written to:   {outfile}")
    else:
        print(f"Geometry already present:   {outfile}")

    # copy run script
    run_script = Path(configuration.common.home_dir) / f"hilde/scripts/run/{task}.py"
    script = Path(workdir) / f"run_{task}.py"
    shutil.copy(run_script, script)
    print(f"Run script written to: {script}")

    if "restart" in settings:
        if settings.restart.command.split()[-1] != script.name:
            print(f"** Check restart command in {settings_outfile}")


if __name__ == "__main__":
    main()
