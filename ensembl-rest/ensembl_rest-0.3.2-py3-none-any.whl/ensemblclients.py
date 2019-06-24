"""

This file is part of pyEnsembl.
    Copyright (C) 2018, Andrés García

    Any questions, comments or issues can be addressed to a.garcia230395@gmail.com.

"""

import json
from importlib_resources import open_text, path
from .core import build_client_class

# Import APIs information
with open_text('ensembl_rest.data','ensembl_rest_endpoints.json') as f:
    ensembl_rest_api = json.load(f)
    
with open_text('ensembl_rest.data','ensembl_genomes_endpoints.json') as f:
    ensembl_genomes_api = json.load(f)


# Now create the main classes 
EnsemblClient = build_client_class(
                'EnsemblClient', 
                ensembl_rest_api,
                doc=f'A client for the Ensembl REST API ({ensembl_rest_api["base_url"]})')

EnsemblGenomesClient = build_client_class(
                        'EnsemblGenomesClient', 
                        ensembl_genomes_api,
                        doc=f'A client for the EnsemblGenomes REST API ({ensembl_genomes_api["base_url"]})')
