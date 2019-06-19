from ...database import db_session
from ...resources.Document.models import DocumentModel
from ...resources.Document.schemas import DocumentResourceSchema

schema = DocumentResourceSchema()


def get_documents_to_download_by_type(document_type):
    """
    Args:
        document_type: string

    Returns: List

    """
    document_query = _build_query({
        'file_id': None,
        'type': document_type,
    })

    response = schema.dump(document_query, many=True).data
    return response


def get_documents_to_download():
    """
    Returns: List

    """
    document_query = _build_query({
        'file_id': None,
    })

    response = schema.dump(document_query, many=True).data
    return response


def get_documents_to_download_by_trial_id(trial_id):
    """
    Args:
        trial_id: int

    Returns: List

    """
    document_query = _build_query({
        'file_id': None,
        'trial_id': trial_id,
    })

    response = schema.dump(document_query, many=True).data
    return response


def _build_query(params):
    q = db_session.query(DocumentModel)
    if 'file_id' in params:
        q = q.filter(DocumentModel.file_id == params['file_id'])
    if 'type' in params:
        q = q.filter_by(type=params['type'])
    if 'trial_id' in params:
        q = q.filter_by(trial_id=params['trial_id'])
    return q


if __name__ == '__main__':
    res = get_documents_to_download()
    print(len(res))
