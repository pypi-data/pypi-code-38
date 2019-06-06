'''Adds a Phonon Workflow to the launchpad'''
from argparse import ArgumentParser

from hilde.fireworks.workflows.phonon_wf import generate_phonon_workflow
from hilde.helpers.attribute_dict import AttributeDict
from hilde.helpers.hash import hash_atoms_and_calc
from hilde.templates.aims import setup_aims
from hilde.settings import Settings


def main():
    '''Function takes in an input file and adds the resulting workflow to the launchpad'''
    parser = ArgumentParser(
        description="generate a phonon workflow and submit it to fireworks"
    )
    parser.add_argument("workflow", type=str, help="workflow file")
    args = parser.parse_args()

    workflow = Settings(settings_file=args.workflow)
    workflow["basisset"] = AttributeDict({"type": "light"})
    atoms = workflow.get_atoms()
    calc = setup_aims(settings=workflow)
    atoms.calc = calc
    fw_settings = {"to_launchpad": True}
    fw_settings["name"] = (
        atoms.symbols.get_chemical_formula() + "_" + hash_atoms_and_calc(atoms)[0]
    )
    generate_phonon_workflow(workflow, atoms, fw_settings)
