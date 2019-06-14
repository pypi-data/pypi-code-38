# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modul is used for GUI of Lisa
"""

from loguru import logger
import sys
import click
from pathlib import Path
# print("start")
# from . import image

# print("start 5")
# print("start 6")

from scaffan import algorithm

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# print("Running __main__.py")
# @batch_detect.command(context_settings=CONTEXT_SETTINGS)
# @click.argument("image_stack_dir", type=click.Path(exists=True))
# @click.argument("working_dir", type=click.Path())
# @click.option("--create-icon", is_flag=True,
#               help="Create desktop icon"
#               )
@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.pass_context
def run(ctx):
    if ctx.invoked_subcommand is None:
        # click.echo('I was invoked without subcommand')
        ctx.invoke(gui)
        # a.main()
    else:
        pass
        # click.echo('I am about to invoke %s' % ctx.invoked_subcommand)
    pass

@run.command(context_settings=CONTEXT_SETTINGS)
@click.option("--common-spreadsheet-file")
def set(common_spreadsheet_file=None):
    mainapp = algorithm.Scaffan()
    if common_spreadsheet_file is not None:
        mainapp.set_common_spreadsheet_file(path=common_spreadsheet_file)

@run.command(context_settings=CONTEXT_SETTINGS)
def gui():
    mainapp = algorithm.Scaffan()
    mainapp.start_gui()


@run.command(context_settings=CONTEXT_SETTINGS)
def install():
    import platform
    print(platform.system)
    if platform.system() == "Windows":
        import pathlib
        import os.path as op
        logo_fn2 = pathlib.Path(__file__).parent / pathlib.Path("scaffan_icon512.ico")

        logo_fn = op.join(op.dirname(__file__), "scaffan_icon512.ico")
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")

        pth = Path.home()
        pth = pth / "Desktop" / Path("Scaffan.lnk")
        shortcut = shell.CreateShortcut(str(pth))
        # cmd
        # ln =  "call activate scaffan; {} -m scaffan".format(sys.executable)
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = "-m scaffan"
        # shortcut.TargetPath = cmd
        # shortcut.Arguments = '/C "call activate scaffan & python -m scaffan" '
        shortcut.IconLocation = "{},0".format(logo_fn)
        shortcut.Save()
    pass


@run.command(context_settings=CONTEXT_SETTINGS)
def nogui():
    pass
# def install():

run()