class ErrorMessage:
    def __init__(self, transaction_id, errors):
        self.transaction_id = transaction_id
        self.errors = errors

    def __str__(self):
        return '\n'.join([f'{err.code}: {err.message}' for err in self.errors])
