DOCUMENT_TYPES = {
    'final': 'final decision',
    'institution': 'institution decision',
    'petition': 'petition',
}


def get_ptab_document_types():
    return [v for k, v in DOCUMENT_TYPES.items()]
