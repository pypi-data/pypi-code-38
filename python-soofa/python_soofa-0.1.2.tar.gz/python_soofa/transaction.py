from datetime import datetime

__all__=["Transaction"]

class Transaction(object):
    def __init__(self, status, sender_currency, receiver_currency, tid, reference, sender, receiver,
                 receipt_no, timestamp, gross_amount, net_amount, transacted_via, is_money_in, **kwargs):
        self.sender = sender
        self.sender_currency = sender_currency
        self.status = status
        self.receiver_currency = receiver_currency
        self.tid = tid
        self.reference = reference
        self.receiver = receiver
        self.receipt_no = receipt_no
        self.timestamp = timestamp
        self.gross_amount = gross_amount
        self.net_amount = net_amount
        self.transacted_via = transacted_via
        self.is_money_in=is_money_in

    def json(self):
        return {
            "status": self.status,
            "sender_currency": self.sender_currency,
            "receiver_currency": self.receiver_currency,
            "tid": self.tid,
            "reference": self.reference,
            "receipt_no": self.receipt_no,
            "timestamp": self.timestamp,
            "gross_amount": self.gross_amount,
            "net_amount": self.net_amount,
            "transacted_via": self.transacted_via,
            "is_money_in": self.is_money_in,
            "sender": self.sender,
            "receiver": self.receiver
        }

    def get_time(self):
        return datetime.fromtimestamp(self.timestamp)
