from pyark.errors import CvaClientError

from pyark import cva_client
from protocols.protocol_7_2.cva import Transaction


class TransactionsClient(cva_client.CvaClient):

    _BASE_ENDPOINT = "transactions"

    def __init__(self, url_base, token):
        cva_client.CvaClient.__init__(self, url_base, token=token)

    def get_transaction(self, transaction_id):
        """
        :type transaction_id: str
        :rtype: Transaction
        """
        results, _ = self._get("{endpoint}/{identifier}".format(
            endpoint=self._BASE_ENDPOINT, identifier=transaction_id))
        result = self._render_single_result(results, as_data_frame=False)
        return Transaction.fromJsonDict(result) if result else None

    def retry_transaction(self, transaction_id):
        """
        :type transaction_id: str
        :rtype: Transaction
        """
        results, _ = self._patch("{endpoint}/{identifier}".format(
            endpoint=self._BASE_ENDPOINT, identifier=transaction_id))
        result = self._render_single_result(results, as_data_frame=False)
        return Transaction.fromJsonDict(result) if result else None

    def delete_transaction(self, **params):
        id = params.get('id', None)

        message = params.get('message', None)
        if not id:
            raise CvaClientError("You must specify an transaction id to delete a transaction")

        return self._delete(
            "{endpoint}/{identifier}".format(endpoint=self._BASE_ENDPOINT, identifier=params.get('id')),
            params={'message': message}
        )
