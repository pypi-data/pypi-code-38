#!/usr/bin/env python
# encoding: utf-8

"""
Producing then compiling templates
"""

import os
import logging
import optparse
import sys

from path import Path
import pytex
import mapytex
import bopytex.filters as filters

formatter = logging.Formatter('%(name)s :: %(levelname)s :: %(message)s')
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
steam_handler.setFormatter(formatter)
# création de l'objet logger qui va nous servir à écrire dans les logs
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)


def setup():
    mapytex_tools = {
        "Expression": mapytex.Expression,
        "Polynom": mapytex.Polynom,
        "Fraction": mapytex.Fraction,
        "Equation": mapytex.Equation,
        "random_str": mapytex.random_str,
        "random_pythagore": mapytex.random_pythagore,
        "Dataset": mapytex.Dataset,
        "WeightedDataset": mapytex.WeightedDataset,
        }
    pytex.update_export_dict(mapytex_tools)

    pytex.add_filter("calculus", filters.do_calculus)


def get_working_dir(options):
    """ Get the working directory """
    if options.working_dir:
        working_dir = Path(options.working_dir)
    else:
        try:
            template = Path(options.template)
        except TypeError:
            raise ValueError("Need to set the working directory \
                    or to give a template")
        else:
            working_dir = template.dirname()
    logger.debug(f"The output directory will be {working_dir}")
    return working_dir


def activate_printanswers(texfile):
    """ Activate printanswers mod in texfile """
    output_fname = "corr_" + texfile
    with open(texfile, 'r') as input_f:
        with open(output_fname, "w") as output_f:
            for line in input_f.readlines():
                output_f.write(line.replace(
                    r'solution/print = false',
                    r'solution/print = true',
                    ))
    return output_fname


def deactivate_printanswers(corr_fname):
    """ Activate printanswers mod in texfile """
    Path(corr_fname).remove()


def pdfjoin(pdf_files, destname, working_dir=".", rm_pdfs=1):
    """TODO: Docstring for pdfjoin.

    :param pdf_files: list of pdf files to join
    :param destname: name for joined pdf
    :param working_dir: the working directory
    :param rm_pdfs: Remove pdf_files after joining them
    :returns: TODO

    """
    joined_pdfs = Path(working_dir) / Path(destname)
    pdf_files_str = " ".join(pdf_files)
    pdfjam = f"pdfjam {pdf_files_str} -o {joined_pdfs}"
    logger.debug(f"Run {pdfjam}")
    logger.info("Joining pdf files")
    os.system(pdfjam)
    if rm_pdfs:
        logger.info(f"Remove {pdf_files_str}")
        os.system(f"rm {pdf_files_str}")


def produce_and_compile(options):
    """ Produce and compile subjects
    """
    working_dir = get_working_dir(options)

    if options.only_corr:
        options.corr = True
        tex_files = working_dir.files("[0-9]*_*.tex")
    else:
        template = Path(options.template)
        logger.debug(f"Template will be {template}")

        list_infos = [
            {"num": f"{i+1:02d}"}
            for i in range(options.num_subj)
            ]

        tex_files = []
        for infos in list_infos:
            dest = (
                working_dir
                / Path(template.replace("tpl", infos["num"]))
                )
            logger.debug(f"Feeding template toward {dest}")
            tex_files.append(dest)
            pytex.feed(
                template,
                {"infos": infos},
                output=dest,
                force=1
                )
            logger.debug(f"{dest} fed")

        if not options.no_compil:
            pdf_files = []
            for texfile in tex_files:
                logger.debug(f"Start compiling {texfile}")
                pytex.pdflatex(texfile)
                logger.debug(f"End compiling {texfile}")
                pdf_files.append(str(texfile[:-4] + ".pdf"))
            logger.debug(f"Compiled files : {pdf_files}")

        if not options.no_join and not options.no_compil:
            pdfjoin(
                pdf_files,
                template.replace('tpl', "all").replace(".tex",".pdf"),
                working_dir,
                rm_pdfs=1
                )

    if options.corr:
        pdf_files = []
        for texfile in tex_files:
            corr_fname = activate_printanswers(texfile)
            if not options.no_compil:
                logger.debug(f"Start compiling {texfile}")
                pytex.pdflatex(corr_fname)
                logger.debug(f"End compiling {texfile}")
                pdf_files.append(str(corr_fname[:-4] + ".pdf"))
                deactivate_printanswers(corr_fname)

        if not options.no_join and not options.no_compil:
            pdfjoin(
                pdf_files,
                template.replace('tpl', "corr").replace(".tex",".pdf"),
                working_dir,
                rm_pdfs=1
                )

    if not options.dirty:
        pytex.clean(working_dir)


def main():
    setup()

    parser = optparse.OptionParser()
    parser.add_option(
        "-t",
        "--template",
        action="store",
        type="string",
        dest="template",
        help="File with the template. The name should have the following form tpl_... ."
        )
    parser.add_option(
        "-w",
        "--working-dir",
        action="store",
        type="string",
        dest="working_dir",
        help="Where fed templates and compiled files will be placed"
        )
    parser.add_option(
        "-N",
        "--number_subjects",
        action="store",
        type="int",
        dest="num_subj",
        default = 1,
        help="The number of subjects to make"
        )
    parser.add_option(
        "-d",
        "--dirty",
        action="store_true",
        dest="dirty",
        help="Do not clean after compilation"
        )
    parser.add_option(
        "-n",
        "--no-compile",
        action="store_true",
        dest="no_compil",
        help="Do not compile source code"
        )
    parser.add_option(
        "-j",
        "--no-join",
        action="store_true",
        dest="no_join",
        help="Do not join pdf and clean single pdf"
        )
    parser.add_option(
        "-O",
        "--only-corr",
        action="store_true",
        dest="only_corr",
        help="Create and compile only correction from existing subjects"
        )
    parser.add_option(
        "-c",
        "--corr",
        action="store_true",
        dest="corr",
        help="Create and compile correction while making subjects"
        )

    (options, _) = parser.parse_args()

    logger.debug(f"CI parser gets {options}")

    if not options.template:
        print("I need a template!")
        sys.exit(0)

    produce_and_compile(options)


if __name__ == '__main__':
    main()


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
