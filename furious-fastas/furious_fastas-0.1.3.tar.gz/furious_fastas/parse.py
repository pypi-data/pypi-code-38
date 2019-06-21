import re

from .fasta import UniprotFasta, NCBIgeneralFasta



def parse_fastas(raw_fastas, pattern, FASTA):
    """Parse fasta with a specific pattern and save under a given fomatting."""
    for f in re.finditer(pattern, raw_fastas):
        sequence = "".join(f[0].split('\n')[1:])
        header = f[1]
        yield FASTA(sequence, header)




uniprot_fastas_pattern = re.compile(r"(>.+\|.+\|.*)\n([\w+\n|\w+])+")

def parse_uniprot_fastas(raw_fastas):
    """Parse raw uniprot fastas.

    Args:
        raw_fastas (str): a string containing text in the downloaded fasta file.
    Returns:
        UniprotFastas
    """
    return parse_fastas(raw_fastas, uniprot_fastas_pattern, UniprotFasta)




ncbi_general_fastas_pattern = re.compile(r"(>.*\|.*\|\w+\s.*)\n([\w+\n|\w+])+")

def parse_ncbi_general_fastas(raw_fastas):
    """Parse ncbi general fastas.

    Args:
        raw_fastas (str): a string containing text in the downloaded fasta file.
    Returns:
        NCBIgeneralFasta
    """
    return parse_fastas(raw_fastas, ncbi_general_fastas_pattern, NCBIgeneralFasta)



def test_parse():
    uniprot_fasta = ">sp|P61513|RL37A_HUMAN 60S ribosomal protein L37a OS=Homo sapiens OX=9606 GN=RPL37A PE=1 SV=2\nMAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSC\nMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ\n>sp|P61513|RL37A_HUMAN 60S ribosomal protein L37a OS=Homo sapiens OX=9606 GN=RPL37A PE=1 SV=2\nMAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSC\nMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ\n"
    r = list(parse_uniprot_fastas(uniprot_fasta))
    assert len(r) == 2
    assert str(r[0]) == "MAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSCMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ"
    assert str(r[1]) == "MAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSCMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ"
