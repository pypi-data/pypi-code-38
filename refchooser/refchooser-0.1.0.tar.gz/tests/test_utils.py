# -*- coding: utf-8 -*-

"""
test_utils
----------------------------------

Tests for `utils` module.
"""

from refchooser import utils


def test_get_file_list_with_globs(tmpdir):
    """Verify globs are resolved correctly."""
    fasta_directory = tmpdir.mkdir("fasta")
    fasta_files = []
    fa_files = []
    for i in range(0, 10):
        path = fasta_directory.join("file" + str(i) + ".fasta")
        path.write("hello")
        fasta_files.append(path)
    for i in range(10, 20):
        path = fasta_directory.join("file" + str(i) + ".fa")
        path.write("hello")
        fa_files.append(path)

    list_file_path = tmpdir.join("list")
    list_file_path.write("%s/*.fasta\n%s/*.fa" % (fasta_directory, fasta_directory))

    file_list = utils.get_file_list(str(list_file_path))

    assert len(fasta_files) == 10
    assert len(fa_files) == 10
    assert len(file_list) == 20
    for p in fasta_files:
        assert p in file_list
    for p in fa_files:
        assert p in file_list
