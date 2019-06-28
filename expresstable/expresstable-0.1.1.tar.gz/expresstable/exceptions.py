class BaseTableError(BaseException):
    '''
    Base exception for the table package from which all other exceptions are
    derived
    '''

class TableEmptyError(BaseTableError):
    '''
    Raised when an operation which requires the table be populated with some
    data is attempted on an empty table
    '''
