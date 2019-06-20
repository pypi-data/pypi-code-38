from crossref_commons.retrieval import get_publication_as_xml
from crossref_commons.types import RelationType


def get_alias(doi):
    """Get the prime DOI of the given DOI."""
    xml = get_publication_as_xml(doi)
    alias = xml.findall(
        './/c:crm-item[@name="prime-doi"]',
        namespaces={'c': 'http://www.crossref.org/qrschema/3.0'})
    return None if not alias else alias[0].text


def get_related(eid, relation_type):
    """Get the DOI related to the given DOI."""
    if relation_type == RelationType.ALIAS:
        return get_alias(eid)
    else:
        raise ValueError(
            'Relation type {} not supported'.format(relation_type))
