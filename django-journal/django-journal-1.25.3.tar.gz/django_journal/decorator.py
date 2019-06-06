from functools import wraps
from django.db import transaction, DEFAULT_DB_ALIAS

if hasattr(transaction, 'atomic'):
    atomic = transaction.atomic
else:
    class Transaction(object):
        sid = None

        def __init__(self, using=None):
            self.using = using

        def __enter__(self):
            if transaction.is_managed():
                self.sid = transaction.savepoint()
                pass
            else:
                transaction.enter_transaction_management(using=self.using)

        def __exit__(self, exc_type, exc_value, traceback):
            if self.sid is not None:
                if exc_value is not None:
                    transaction.savepoint_rollback(self.sid, using=self.using)
            else:
                try:
                    if exc_value is not None:
                        if transaction.is_dirty(using=self.using):
                            transaction.rollback(using=self.using)
                    else:
                        if transaction.is_dirty(using=self.using):
                            try:
                                transaction.commit(using=self.using)
                            except:
                                transaction.rollback(using=self.using)
                                raise
                finally:
                    transaction.leave_transaction_management(using=self.using)

        def __call__(self, func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.__class__(using=self.using):
                    return func(*args, **kwargs)
            return wrapper


    def atomic(using=None):
        """
        This decorator activates commit on response. This way, if the view function
        runs successfully, a commit is made; if the viewfunc produces an exception,
        a rollback is made. This is one of the most common ways to do transaction
        control in Web apps.
        """
        if using is None:
            using = DEFAULT_DB_ALIAS
        if callable(using):
            return Transaction(DEFAULT_DB_ALIAS)(using)
        return Transaction(using)


