_query_prepend = "http://www.uniprot.org/uniprot/?query="

uniprot_url = {
    "human": _query_prepend + "reviewed:yes+AND+organism:9606&format=fasta",
    "yeast": _query_prepend + "organism:643680&format=fasta",
    "ecoli": _query_prepend + "reviewed:yes+AND+organism:83333&format=fasta",
    "wheat": _query_prepend + "organism:4565&format=fasta",
    "mouse": _query_prepend + "reviewed:yes+AND+organism:10090&format=fasta",
    "leishmania" : _query_prepend + "organism:5664&format=fasta"
}

