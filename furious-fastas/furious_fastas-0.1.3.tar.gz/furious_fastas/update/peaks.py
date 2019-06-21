from datetime import datetime
from shutil import move as mv
from pathlib import Path

from ..download import download
from ..contaminants import uniprot_contaminants as conts
from ..fastas import UniprotFastas


def update_peaks_fasta_db(db_path,
                          species2url,
                          contaminants=conts,
                          verbose=True):
    """Update the fasta data bases for the Peaks software.

    Args:
        db_path (str): Path to the folder where we will store the files.
        species2url (iterable of tuples): Each tuple consists of the species name and its Uniprot url.
        contaminants (Fastas): Fastas with contaminants.
        verbose (boolean): Be verbose.
    """
    if verbose:
        print("Creating necessary folders.")
    db_path = Path(db_path)
    current = db_path/"current"
    old = db_path/"old"
    old.mkdir(exist_ok=True, parents=True)
    current.mkdir(exist_ok=True, parents=True)

    for f in current.iterdir():
        if f.is_file():
            mv(src=str(current/f), dst=str(old))

    now = str(datetime.now()).replace(" ", "_").split('.')[0].replace(":","-")
    if verbose:
        print("Downloading files from Uniprot.")
    
    # peaks must accept uniprot format
    for name, url in species2url:
        fastas = UniprotFastas()
        fastas.parse_raw(download(url))
        fastas.append(conts)
        reviewed = "SP" if 'reviewed:yes' in url else "TR"
        file = "{}_{}_{}_{}_contaminated.fasta".format(now,
                                                       name,
                                                       reviewed,
                                                       str(len(fastas)))
        fastas.write(current/file)
        if verbose:
            print("\t{} x".format(name))
    if verbose:
        print("Succeeeded!")
