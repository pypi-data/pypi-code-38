
"""Compute first two isotopologues intensities from sequences.

The program differentiate labelled and unlabelled amino acids
for the case of a 99.99 % C[12] enrichment.

Read a file composed of sequences of amino acids on each line and return :
    sequence, mass, formula, formula_X, M0_NC, M1_NC, M0_12C and M1_12C
as a tsv file.
Where formula X is the chemical formula with carbon of unlabelled
amino acids marked as X.
NC are Normal Conditions, 12C are C[12] enrichment Conditions.


Example
-------
Running the script directly
    $ python seq_to_first_iso sequences.txt
will provide file 'sequences_stfi.tsv'


Notes
-----
Carbon of unlabelled amino acids keep default isotopic abundance,
and are represented as X in formulas.
Naming conventions for isotopes follow pyteomics's conventions.


Attributes
----------
USAGE_ERROR : str
    Default message for errors.
AMINO_ACIDS : set
    Set of supported 1-letter amino acids.
XTANDEM_MOD_PATTERN : re.Pattern
    Regular expression capturing XTandem Post Translational Modifications.
UNIMOD_MODS : pyteomics.mass.Unimod
    Dictionary with Unimods entries.
USED_ELEMS : str
    String of used/recognized elements.
isotopic_abundance : dict
    Dictionary of isotopic abundances with values taken from MIDAs.
C12_abundance : dict
    Dictionary of isotopic abundances with C[12] abundance at 0.9999.
log : logging.Logger
    Logger outputting in text terminals.

"""

import argparse
import logging
from pathlib import Path
import re
import sys

import pandas as pd
from pyteomics import mass


USAGE_ERROR = "Usage: python seq-to-first-iso.py filename " \
             + "[-o output] [-n aa]"
# Note: pyteomics also have U, O, H- and -OH that can be used for sequences
# which are not supported in this version.
AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")

XTANDEM_MOD_PATTERN = re.compile(r"""
                                 \.?       # 0 or 1 dot
                                 \(        # Opening parenthesis
                                   (       # Begin capture
                                    (?:        # Not capture the following
                                     [^\(\)] | # Either not parentheses or
                                     \(-?\d+\) # parentheses containing an int
                                    )+         # multiple times
                                   )       # End capture
                                 \)        # Closing parenthesis
                                 """, re.VERBOSE)

UNIMOD_MODS = mass.Unimod()
# This variable is obsoleted if an natural element shall be named X.
USED_ELEMS = "CHONPSX"

# Set custom logger.
log = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s: %(message)s",
                                  "%Y-%m-%d, %H:%M:%S")
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)
log.setLevel(logging.INFO)


# Default isotopic abundances from MIDAs website:
# https://www.ncbi.nlm.nih.gov/CBBresearch/Yu/midas/index.html .
# X is C with default abundance.
isotopic_abundance = {"H[1]": 0.999885, "H[2]": 0.000115,
                      "C[12]": 0.9893,  "C[13]": 0.0107,
                      "X[12]": 0.9893,  "X[13]": 0.0107,
                      "N[14]": 0.99632, "N[15]": 0.00368,
                      "O[16]": 0.99757, "O[17]": 0.00038, "O[18]": 0.00205,
                      "S[32]": 0.9493,  "S[33]": 0.0076,  "S[34]": 0.0429}

C12_abundance = dict(isotopic_abundance)
prop = 0.9999
C12_abundance["C[12]"] = prop
C12_abundance["C[13]"] = 1-prop


def user_input(args):
    """Parse and handle the submitted command line.

    Parameters
    ----------
    args : list of str
        List of arguments received from the CLI.

    Returns
    -------
    argparse.Namespace
        Object containing the arguments parsed from the CLI.

    Raises
    ------
    SystemExit
        If the file provided is not found.

    """
    parser = argparse.ArgumentParser(
        description="Read a file of sequences and creates a tsv file")

    # Input file is required as a positional argument.
    parser.add_argument("input", type=Path, help="file to parse")

    # Optional arguments.
    parser.add_argument("-o", "--output", type=str,
                        help="name of output file")
    parser.add_argument("-n", "--non-labelled-aa",
                        metavar="amino_a",
                        help="amino acids with default abundance")

    options = parser.parse_args(args)

    # Check if file exists.
    if not options.input.is_file():
        log.error(f"file {options.input} does not exist in "
                  f"current directory '{options.input.cwd()}'\n{USAGE_ERROR}"
                  )
        exit()

    # Check if amino acids are correct.  If not, tell which one.
    if not options.non_labelled_aa:
        # Change to empty list to avoid Nonetype errors.
        options.non_labelled_aa = []
    else:
        options.non_labelled_aa = options.non_labelled_aa.split(",")
        # Convert amino acids to uppercase for compatibility.
        options.non_labelled_aa = [char.upper()
                                   for char in options.non_labelled_aa]
        unrecognized_aa = []

        for arg in options.non_labelled_aa:
            if arg not in AMINO_ACIDS:
                unrecognized_aa.append(arg)

        if unrecognized_aa:
            log.warning(f"{unrecognized_aa} not recognized as amino acid")

    return options


def sequence_parser(file, sep="\t"):
    """Return information on sequences parsed from a file.

    Parameters
    ----------
    file : str
        Filename, the file can either just have sequences for each line or
        can have have annotations and sequences with a separator in-between.
    sep : str, optional
        Separator for files with annotations.

    Returns
    -------
    dict
        Parsed output with "key: values" :
        - "annotations": a list of annotations if any.
        - "raw_sequences": a list of unmodified peptide sequences.
        - "sequences": a list of uppercase peptide sequences.
        - "modifications": a list of lists of PTMs.
        - "ignored_lines": and the number of ignored lines.

    Warnings
    --------
    The function uses the first line to evaluate if the file has
    annotations or not, hence a file should have a consistent format.

    Notes
    -----
    Supports Xtandem's Post-Translational Modification notation (0.4.0).

    """
    # Obtain a list of sequences as string if they are amino acids.
    with open(file, "r") as filin:
        annotations = []
        raw_sequences = []
        sequences = []
        modifications = []
        ignored_lines = 0
        lines = filin.readlines()

        if not sep:
            log.warning("separator is empty, default value '\t' used")
            sep = "\t"

        # Split the first line to determine if the file has annotations.
        try:
            has_annotations = (len(lines[0].split(sep)) > 1)
        except IndexError:
            log.warning("the file is empty")

        for line in lines:
            split_line = line.split(sep)

            if has_annotations:
                try:
                    raw_sequence = split_line[1].strip()
                    annotation = split_line[0].strip()
                except IndexError:
                    # The line only has one column.
                    ignored_lines += 1
                    continue
            else:
                raw_sequence = split_line[0].strip()

            # Convert potential HTML residues.
            raw_sequence = re.sub("&gt;", ">", raw_sequence)
            # No verification is done on modifications here.
            modification = re.findall(XTANDEM_MOD_PATTERN, raw_sequence)
            # Remove PTMs and capitalize the sequence.
            sequence = re.sub(XTANDEM_MOD_PATTERN, "", raw_sequence).upper()

            # Verify if sequence is valid and not empty.
            if not(set(sequence) - AMINO_ACIDS) and sequence:
                # Everything should be clear.
                raw_sequences.append(raw_sequence)
                sequences.append(sequence)
                modifications.append(modification)
                if has_annotations:
                    annotations.append(annotation)
            else:
                ignored_lines += 1

    parsed_output = {"annotations": annotations,
                     "raw_sequences": raw_sequences,
                     "sequences": sequences,
                     "modifications": modifications,
                     "ignored_lines": ignored_lines}

    return parsed_output


def compute_M0(f, a):
    """Return the monoisotopic abundance M0 of a sequence with its formula.

    Parameters
    ----------
    f : pyteomics.mass.Composition
        Chemical formula, as a dict of counts for each element:
        {element_name: count_of_element_in_sequence, ...}.
    a : dict
        Dictionary of abundances of isotopes, in the format:
        {element_name[isotope_number]: relative abundance, ..}.

    Returns:
    float
        Value of M0.

    Notes
    -----
    Unused. Use compute_M0_nl instead.

    """
    M0 = a["C[12]"]**f["C"] * a["H[1]"]**f["H"] * a["N[14]"]**f["N"] \
        * a["O[16]"]**f["O"] * a["S[32]"]**f["S"]
    return M0


def compute_M1(f, a):
    """Compute abundance of second isotopologue M1 from its formula.

    Parameters
    ----------
    f : pyteomics.mass.Composition
        Chemical formula, as a dict of counts for each element:
        {element_name: count_of_element_in_sequence, ...}.
    a : dict
        Dictionary of abundances of isotopes, in the format:
        {element_name[isotope_number]: relative abundance, ..}.

    Returns:
    float
        Value of M1.

    Notes
    -----
    Unused. Use compute_M1_nl instead.

    """
    M1 = (
          (f["C"] * a["C[12]"]**(f["C"]-1) * a["C[13]"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["H"] * a["C[12]"]**f["C"]
              * a["H[1]"]**(f["H"]-1) * a["H[2]"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["N"] * a["C[12]"]**f["C"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**(f["N"]-1) * a["N[15]"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["O"] * a["C[12]"]**f["C"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**(f["O"]-1) * a["O[17]"]
              * a["S[32]"]**f["S"])

          + (f["S"] * a["C[12]"]**f["C"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**(f["S"]-1) * a["S[33]"])
          )
    return M1


def separate_labelled(sequence, unlabelled_aa):
    """Get the sequence of unlabelled amino acids from a sequence.

    Parameters
    ----------
    sequence : str
        String of amino acids
    unlabelled_aa
        Container (list, string...) of unlabelled amino acids

    Returns
    -------
    tuple(str, str)
        The sequences as a tuple of string with:
        - the sequence without the unlabelled amino acids
        - the unlabelled amino acids in the sequence

    """
    labelled_seq = []
    unlabelled_seq = []
    for char in sequence:
        if char in unlabelled_aa:
            unlabelled_seq.append(char)
        else:
            labelled_seq.append(char)
    return "".join(labelled_seq), "".join(unlabelled_seq)


def compute_M0_nl(f, a):
    """Return the monoisotopic abundance M0 of a formula with mixed labels.

    Parameters
    ----------
    f : pyteomics.mass.Composition
        Chemical formula, as a dict of counts for each element:
        {element_name: count_of_element_in_sequence, ...}.
    a : dict
        Dictionary of abundances of isotopes, in the format:
        {element_name[isotope_number]: relative abundance, ..}.

    Returns:
    float
        Value of M0.

    Notes
    -----
    X represents C with default isotopic abundance.

    """
    M0 = a["C[12]"]**f["C"] * a["X[12]"]**f["X"] * a["H[1]"]**f["H"] \
        * a["N[14]"]**f["N"] * a["O[16]"]**f["O"] * a["S[32]"]**f["S"]
    return M0


def compute_M1_nl(f, a):
    """Compute abundance of second isotopologue M1 from its formula.

    Parameters
    ----------
    f : pyteomics.mass.Composition
        Chemical formula, as a dict of counts for each element:
        {element_name: count_of_element_in_sequence, ...}.
    a : dict
        Dictionary of abundances of isotopes, in the format:
        {element_name[isotope_number]: relative abundance, ..}.

    Returns:
    float
        Value of M1.

    Notes
    -----
    X represents C with default isotopic abundance.

    """
    M1 = (
          (f["C"] * a["C[12]"]**(f["C"]-1) * a["C[13]"]
              * a["X[12]"]**f["X"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["X"] * a["C[12]"]**f["C"]
              * a["X[12]"]**(f["X"]-1) * a["X[13]"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["H"] * a["C[12]"]**f["C"]
              * a["X[12]"]**f["X"]
              * a["H[1]"]**(f["H"]-1) * a["H[2]"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["N"] * a["C[12]"]**f["C"]
              * a["X[12]"]**f["X"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**(f["N"]-1) * a["N[15]"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**f["S"])

          + (f["O"] * a["C[12]"]**f["C"]
              * a["X[12]"]**f["X"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**(f["O"]-1) * a["O[17]"]
              * a["S[32]"]**f["S"])

          + (f["S"] * a["C[12]"]**f["C"]
              * a["X[12]"]**f["X"]
              * a["H[1]"]**f["H"]
              * a["N[14]"]**f["N"]
              * a["O[16]"]**f["O"]
              * a["S[32]"]**(f["S"]-1) * a["S[33]"])
          )

    return M1


def formula_to_str(composition):
    """Return formula from Composition as a string.

    Parameters
    ----------
    composition : pyteomics.mass.Composition
        Chemical formula.

    Returns
    -------
    str
        Human-readable string of the formula.

    Warnings
    --------
    If the composition has elements not in USED_ELEMS, they will not
    be added to the output.

    """
    formula_str = ""
    for element in USED_ELEMS:
        if element in composition:
            formula_str += f"{element}{composition[element]}"
    return formula_str


def seq_to_midas(sequence_l, sequence_nl):
    """Take 2 amino acid sequences and return the composition for MIDAs.

    Parameters
    ----------
    sequence_l : str
        Sequence with labelled amino acids.
    sequence_nl : str
        Sequence where amino acids are not labelled.

    Notes
    -----
    The function assumes the second sequence has no terminii.

    """
    formula_l = mass.Composition(sequence_l)
    formula_nl = mass.Composition(parsed_sequence=sequence_nl)
    try:
        formula_nl["X"] = formula_nl.pop("C")
    except KeyError:
        pass
    return formula_l+formula_nl


def get_mods_composition(modifications):
    """Return the composition of a list of modifications.

    Parameters
    ----------
    modifications: list of str
        List of modifications string (corresponding to Unimod titles).

    Returns
    -------
    pyteomics.mass.Composition
        The total composition change.

    ???: Have the mass.Unimod() dict as parameter ?

    """
    total_mod_composition = mass.Composition()
    for mod in modifications:
        try:
            mod_composition = UNIMOD_MODS.by_title(mod)["composition"]
            total_mod_composition += mod_composition
            # Using set comparison here won't work with elements as isotopes.
            for elem in mod_composition:
                if elem not in USED_ELEMS:
                    log.warning(f"{elem} is not supported in the computation "
                                "of M0 and M1")

        except (KeyError, AttributeError, TypeError):
            log.warning(f"Unimod entry not found for : {mod}")
    return total_mod_composition


def seq_to_tsv(sequences, unlabelled_aa, **kwargs):
    """Create a dataframe from sequences and return its name.

    Parameters
    ----------
    sequences : list of str
        List of pure peptide sequences string.
    unlabelled_aa : container object
        Container of unlabelled amino acids.
    **kwargs
        Optional keyword arguments:
            annotations : list of str, optional
                 List of IDs for the sequences.
            raw_sequences : list of str, optional
                 List of sequences with Xtandem PTMs.
            modifications : list of str, optional
                 List of modifications for raw_sequences.

    Returns
    -------
    pandas.Dataframe
        Dataframe with : annotation (optional), sequence, mass,
                         formula, formula_X, M0_NC, M1_NC, M0_12C, M1_12C.

    Warnings
    --------
    If raw_sequence is provided, modifications must also be provided.

    TODO: change name with version change.

    """
    accepted_input = ["sequences", "unlabelled_aa", "annotations",
                      "raw_sequences", "modifications"]
    for key in kwargs:
        if key not in accepted_input:
            log.warning(f"argument {key} not recognized")

    annotations = kwargs.get("annotations", [])
    raw_sequences = kwargs.get("raw_sequences", [])
    modifications = kwargs.get("modifications", [])

    # Dataframe of sequences.
    df_peptides = pd.DataFrame({"sequence": sequences})

    if raw_sequences or modifications:
        # Testing if they have the same length as sequences.
        if len(raw_sequences) != len(sequences):
            log.warning("raw_sequences and sequences have different "
                        + "lengths, raw_sequences will be ignored")
            raw_sequences = []
            modifications = []
        elif len(raw_sequences) != len(modifications):
            log.warning("raw_sequences and modifications have different "
                        + "lengths, they will be ignored")
            raw_sequences = []
            modifications = []
        else:
            df_peptides["raw_sequence"] = raw_sequences
            df_peptides["mods"] = modifications

    if annotations:
        # We can't associate a sequence with its annotation.
        if len(sequences) != len(annotations):
            log.warning("annotations and sequences have different lengths, "
                        + "annotations will be ignored")
            annotations = []
        else:
            df_peptides["annotation"] = annotations

    # Separate sequences.
    df_peptides["labelled"], df_peptides["unlabelled"] = zip(
            *df_peptides["sequence"].apply(separate_labelled,
                                           unlabelled_aa=unlabelled_aa))

    # Add formulas and mass  of sequences.
    log.info("Computing formula")
    df_peptides["f"] = df_peptides["sequence"].apply(mass.Composition)
    # Composition, with unlabelled C as element X.
    df_peptides["f_X"] = df_peptides.apply(lambda x:
                                           seq_to_midas(x["labelled"],
                                                        x["unlabelled"]),
                                           axis=1)

    # Get the composition of the modifications.
    if modifications:
        log.info("Computing composition of modifications")
        df_peptides["m_comp"] = df_peptides["mods"].apply(get_mods_composition)
        df_peptides["f"] = df_peptides["f"] + df_peptides["m_comp"]
        df_peptides["f_X"] = df_peptides["f_X"] + df_peptides["m_comp"]

    # Formula as a string (instead of mass.Composition).
    df_peptides["formula"] = df_peptides["f"].apply(formula_to_str)

    log.info("Computing mass")
    df_peptides["mass"] = df_peptides["f"].map(mass.calculate_mass)

    # Add M0 and M1 in normal conditions.
    log.info("Computing M0 and M1")
    # Can use compute_M0_nl with isotopic abundance twice
    df_peptides["M0_NC"] = df_peptides["f_X"].apply(compute_M0_nl,
                                                    a=isotopic_abundance)
    df_peptides["M1_NC"] = df_peptides["f_X"].apply(compute_M1_nl,
                                                    a=isotopic_abundance)

    df_peptides["M0_12C"] = df_peptides["f_X"].apply(compute_M0_nl,
                                                     a=C12_abundance)
    df_peptides["M1_12C"] = df_peptides["f_X"].apply(compute_M1_nl,
                                                     a=C12_abundance)

    # For verification with MIDAs, might be removed.
    df_peptides["formula_X"] = df_peptides["f_X"].apply(formula_to_str)

    wanted_columns = ["sequence", "mass", "formula", "formula_X",
                      "M0_NC", "M1_NC", "M0_12C", "M1_12C"]
    # Take raw sequence if available.
    if raw_sequences:
        df_peptides.rename(index=str, columns={"sequence": "pure_seq",
                                               "raw_sequence": "sequence"},
                           inplace=True)
    if annotations:
        wanted_columns.insert(0, "annotation")

    return df_peptides[wanted_columns]


def cli(args=None):
    """Entry point for seq_to_first_iso's CLI.

    Parameters
    ----------
    args : list of str, optional
        CLI arguments, args are used for testing.

    Returns
    -------
    None
        Writes a tsv file.

    Raises
    ------
    SystemExit
        If no sequences were found on the file.

    Notes
    -----
    Main function of the script, for use with CLI.

    """
    if not args:
        args = sys.argv[1:]

    options = user_input(args)
    input_file = options.input
    unlabelled_aa = options.non_labelled_aa

    if unlabelled_aa:
        log.info(f"Amino acid with default abundance: {unlabelled_aa}")

    log.info("Parsing file")
    parsed_output = sequence_parser(input_file)
    sequences = parsed_output["sequences"]
    # Remove from parsed_output dict.
    ignored_lines = parsed_output.pop("ignored_lines")

    if not sequences:
        log.error(f"incorrect format, make sure that lines "
                  f"in {str(input_file)} are valid sequences of amino acids")
        exit()
    if ignored_lines:
        log.warning(f"{ignored_lines} lines ignored out of "
                    f"{ignored_lines+len(sequences)}")

    # Choose output filename.
    if not options.output:
        output_file = input_file.stem + "_stfi.tsv"
    else:
        output_file = options.output + ".tsv"

    df = seq_to_tsv(unlabelled_aa=unlabelled_aa, **parsed_output)
    df.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    cli()  # pragma: no cover
