'''Adds a general workflow to a launchpad'''
from argparse import ArgumentParser
from ase.io import read

from hilde.helpers.hash import hash_atoms_and_calc
from hilde.settings import Settings
from hilde.fireworks.workflows.workflow_generator import generate_workflow


def main():
    '''adds a workflow to the launchpad'''
    parser = ArgumentParser(description="create a configuration file and workdir")
    parser.add_argument("workflow", type=str, help="Workflow description file")
    parser.add_argument(
        "--make_abs_path", action="store_true", help="Make all paths absolute"
    )
    parser.add_argument("-l", "--launchpad", type=str, default=None, help="Path to launchpad file")
    parser.add_argument('--no_dep', action="store_true", help="No dependencies on Fireworks")
    args = parser.parse_args()

    workflow = Settings(settings_file=args.workflow)
    atoms = read(workflow.geometry.file, format='aims')
    steps = []

    for step_file in workflow.workflow.step_files:
        steps.append(Settings(settings_file=step_file))

    fw_settings = {"to_launchpad": True}
    if args.launchpad:
        fw_settings["launchpad_yaml"] = args.launchpad
    fw_settings["name"] = (
        atoms.symbols.get_chemical_formula() + "_" + hash_atoms_and_calc(atoms)[0]
    )
    generate_workflow(
        steps, atoms=atoms, fw_settings=fw_settings, make_abs_path=args.make_abs_path, no_dep=args.no_dep
    )
