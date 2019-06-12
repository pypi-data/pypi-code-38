# test input/output functions from hicstuff
# 20190402
from tempfile import NamedTemporaryFile
import os
import gzip
import zipfile
import bz2
import pandas as pd
import filecmp
import numpy as np
import hicstuff.io as hio
import cooler

MAT_GRAAL = hio.load_sparse_matrix(
    "test_data/abs_fragments_contacts_weighted.txt"
)
FRAGS_GRAAL = pd.read_csv("test_data/fragments_list.txt", delimiter="\t")

def test_compress():
    """Test reading and checking of compressed files"""

    # Generate temp files and store path
    f = NamedTemporaryFile(delete=False, mode="w")
    fgz = NamedTemporaryFile(delete=False, mode="wb")
    fbz = NamedTemporaryFile(delete=False)
    fz = NamedTemporaryFile(delete=False)
    fgz.close()
    fbz.close()
    fz.close()
    # Fill with some text
    f.write("xyz")
    f.close()
    # Write text to compressed file using different compression types
    raw = open(f.name, mode="rb").read()
    gz = gzip.open(fgz.name, mode="wb")
    gz.write(raw)
    gz.close()
    bz = bz2.BZ2File(fbz.name, "wb")
    bz.write(raw)
    bz.close()
    z = zipfile.ZipFile(fz.name, "w")
    z.write(f.name)
    z.close()
    exp_compress = {
        f.name: False,
        fgz.name: True,
        fz.name: True,
        fbz.name: True,
    }
    for fh in [f, fgz, fbz, fz]:
        content = hio.read_compressed(fh.name).read()
        # Check reading
        assert content == "xyz"
        # Check guessing compression state
        assert hio.is_compressed(fh.name) == exp_compress[fh.name]
        # Clean files
        os.unlink(fh.name)


def test_save_bedgraph2d():
    """Test saving 2D bedgraph files"""
    # Create temp file and write a 2D bedgraph matrix inside
    f = NamedTemporaryFile("w", delete=False)
    f.close
    # Load GRAAL Matrix from test_data
    hio.save_bedgraph2d(MAT_GRAAL, FRAGS_GRAAL, f.name)
    # Check if the file created is identical to the 2D bedgraph matrix
    # containing the same dataset as the GRAAL matrix used as input
    assert filecmp.cmp(f.name, "test_data/mat.bg2")
    os.unlink(f.name)


def test_load_bedgraph2d():
    """Test loading sparse matrices from 2D bedgraph files"""
    mat_bg = hio.load_bedgraph2d(
        "test_data/mat.bg2", fragments_file="test_data/fragments_list.txt"
    )[0]
    assert np.allclose(MAT_GRAAL.todense(), mat_bg.todense())

    # Load using fixed bin sizes
    mat_bg = hio.load_bedgraph2d("test_data/mat_5kb.bg2", bin_size=5000)[0]
    mat_graal = hio.load_sparse_matrix("test_data/mat_5kb.tsv")
    assert mat_bg.shape == mat_graal.shape


def test_cooler_io():
    """Test input output operations on cool files"""
    f = NamedTemporaryFile("w", delete=False)
    f.close
    # Write cool from GRAAL objects
    hio.write_cool(f.name, MAT_GRAAL, FRAGS_GRAAL)
    c = cooler.Cooler(f.name)
    # Just copy the start column and write it as a new one
    dummycol = c.bins()[:].loc[:,'start'] #pylint: disable=no-member
    hio.add_cool_column(c, dummycol, 'dummy', dtype=np.int64)
    # Read custom cool into GRAAL objects
    mat, frags, chroms = hio.load_cool(f.name)
    os.unlink(f.name)
