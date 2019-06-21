from datetime import datetime
from shutil import move as mv
from pathlib import Path
import json

from ..download import download
from ..contaminants import uniprot_contaminants
from ..fastas import UniprotFastas
# from .misc import create_xml_description


def update_plgs_fasta_db(db_path,
                         species2url,
                         contaminants=uniprot_contaminants,
                         write_intermediate_sequences=False,
                         indent=4,
                         verbose=True):
    """Update the fasta data bases for the PLGS software.

    Args:
        db_path (str): Path to the folder where we will store the files.
        species2url (iterable of tuples): Each tuple consists of the species name and its Uniprot url.
        contaminants (Fastas): Fastas with contaminants.
        write_intermediate_sequences (boolean): Should we also output the original sequences and the original with contaminants?
        indent (int): Indent of the json file.
        verbose (boolean): Be verbose.
    """
    if verbose:
        print("Creating necessary folders.")
    db_path = Path(db_path)
    now = str(datetime.now()).replace(" ", "_").split('.')[0].replace(":","-")
    folder = db_path/now
    original = folder/'original'
    with_conts = folder/'with_contaminants'
    with_conts_rev = folder/'with_contaminants_and_reversed'
    if verbose:
        print("Downloading files from Uniprot.")
    stats = [("contaminants", len(contaminants))]
    visited_names = set([])
    for name, url in species2url:
        if name not in visited_names:
            visited_names.add(name)
        else:
            raise Exception("species2url contains non-unique name ({})".format(name))
        fastas = UniprotFastas()
        fastas.parse_raw(download(url))
        if write_intermediate_sequences:
            original.mkdir(exist_ok=True, parents=True)
            fastas.write(original/(name+".fasta"))
        fastas.append(contaminants)
        if write_intermediate_sequences:
            with_conts.mkdir(exist_ok=True, parents=True)
            fastas.write(with_conts/(name+".fasta"))
        fastas = fastas.to_ncbi_general()
        fastas.add_reversed_fastas_for_plgs()
        with_conts_rev.mkdir(exist_ok=True, parents=True)
        fastas.write(with_conts_rev/(name+".fasta"))
        stats.append((name, len(fastas)))
        if verbose:
            print("\t{} x".format(name))
    with open(folder/"stats.json", 'w+') as h:
        json.dump(stats, h, indent=indent)    
    if verbose:
        print("Success.")
