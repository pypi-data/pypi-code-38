import time


"""
Append Entries request message.
"""
APPEND_ENTRIES = 1

"""
Append Entries response message.
"""
APPEND_RESPONSE = 2

"""
Vote request message.
"""
VOTE_REQUEST = 3

"""
Vote response message.
"""
VOTE_RESPONSE = 4


class Message(object):
    """
    A container for RPC messages between consensus nodes.
    """

    def __init__(self, procedure, sender, recipient, term, mode, data, sent_time=None, recv_time=None):
        """
        :param procedure: Procedure (APPEND_ENTRIES, APPEND_RESPONSE, VOTE_REQUEST, VOTE_RESPONSE)
        :param sender: Name of the sender
        :param recipient: Name of the recipient
        :param term: Current term of the consensus node
        :param mode: Mode of the consensus node (NODE_MODE_ACTIVE, NODE_MODE_PASSIVE, NODE_MODE_RELUCTANT)
        :param data: Data to be sent
        :param sent_time: Time message was sent
        :type procedure: int
        :type sender: str
        :type recipient: str
        :type term: int
        :type mode: int
        :type data: dict
        :type sent_time: float
        """
        self.procedure = procedure
        self.sender = sender
        self.recipient = recipient
        self.term = term
        self.mode = mode
        self.data = data
        self.sent_time = sent_time
        self.recv_time = recv_time

    @staticmethod
    def build(procedure, node, state, recipient, data):
        """
        :param procedure: Procedure (APPEND_ENTRIES, APPEND_RESPONSE, VOTE_REQUEST, VOTE_RESPONSE)
        :param node: Node building the message
        :param state: State building the message
        :param recipient: Recipient of the message
        :param data: Data to be sent
        :type procedure: int
        :type node: pyraftlog.node.Node
        :type state: pyraftlog.state.State
        :type recipient: str
        :type data: dict
        :return: A built message
        :rtype: Message
        """
        return Message(procedure, state.name, recipient, state.current_term, node.mode, data)

    @staticmethod
    def recv(procedure, sender, recipient, term, mode, data, sent_time, recv_time):
        return Message(procedure, sender, recipient, term, mode, data, sent_time, recv_time or time.time())

    def __str__(self):
        # Reduce the length of entries
        data = {k: (lambda k, x: x[:1] if k == 'entries' else x)(k, v) for k, v in self.data.items()}

        return "{0}[{1}]({2}:{3}|{4})".format(self.name(), self.term, self.sender, self.recipient, data)

    def name(self):
        """
        :return: Name of the RPC
        :rtype: str
        """
        if self.procedure == APPEND_ENTRIES:
            return "APPEND_ENTRIES"
        elif self.procedure == APPEND_RESPONSE:
            return "APPEND_RESPONSE"
        elif self.procedure == VOTE_REQUEST:
            return "VOTE_REQUEST"
        elif self.procedure == VOTE_RESPONSE:
            return "VOTE_RESPONSE"
        else:
            return "UNKNOWN(%d)" % self.procedure

    def is_response(self):
        """
        :return: True if the message is a type of response, False otherwise
        :rtype: bool
        """
        return self.procedure in [VOTE_RESPONSE, APPEND_RESPONSE]

    def transport_time(self):
        return (self.recv_time or time.time()) - self.sent_time
