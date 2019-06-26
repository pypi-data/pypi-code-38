from django.utils.translation import ugettext_lazy as _

from django_vox import settings

from . import base

__all__ = ("Backend",)


class Backend(base.Backend):
    """This backends implements message sending via XMPP

    Warning, it makes a new connection for each message which in practice can
    be pretty slow.
    """

    ID = "xmpp"
    PROTOCOL = "xmpp"
    EDITOR_TYPE = "basic"
    ESCAPE_HTML = False
    VERBOSE_NAME = _("XMPP")
    DEPENDS = ("sleekxmpp",)

    # TODO: implement __init__ and do the heavy work there
    # so that sending multiple messages at once isn't stupidly slow

    def send_message(self, _from_address, to_addresses, message):
        for address in to_addresses:
            try:
                client = Client(
                    settings.XMPP_JID, settings.XMPP_PASSWORD, address, message
                )
            except NameError:
                raise ImportError("sleekxmpp is required to use this backend")
            if client.connect():
                client.process(block=True)
            else:
                raise RuntimeError("Unable to connect to XMPP account")


try:
    import sleekxmpp
except ImportError:
    pass
else:
    # largely copied from sleekxmpp examples
    class Client(sleekxmpp.ClientXMPP):
        def __init__(self, jid: str, password: str, recipient: str, message: str):
            super().__init__(jid, password)
            # The message we wish to send, and the JID that will receive it.
            self.recipient = recipient
            self.msg = message
            # The session_start event will be triggered when the bot
            # establishes its connection with the server and the XML
            # streams are ready for use. We want to listen for this
            # event so that we we can initialize our roster.
            self.add_event_handler("session_start", self.start, threaded=True)

        def start(self, _event):
            """
            Process the session_start event.
            Typical actions for the session_start event are
            requesting the roster and broadcasting an initial
            presence stanza.
            Arguments:
                event -- An empty dictionary. The session_start
                         event does not provide any additional
                         data.
            """
            self.send_presence()
            self.get_roster()
            self.send_message(mto=self.recipient, mbody=self.msg, mtype="chat")
            # Using wait=True ensures that the send queue will be emptied
            # before ending the session.
            self.disconnect(wait=True)
