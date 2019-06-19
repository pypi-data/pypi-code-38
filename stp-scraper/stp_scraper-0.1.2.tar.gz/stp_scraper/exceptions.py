class StpException(Exception):
    """
    An error has occurred obtaining the transaction file
    """


class EmptyFile(Exception):
    """
    The transaction file obtained is empty
    """
