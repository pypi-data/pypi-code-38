"""
Base classes to do slowbreak applications
"""
from slowbreak.constants import Tag
from slowbreak.message import Message

class BaseApp(object):
    """
    Base class to be used to make chainable applications that can be added to the
    application 'stack'.

    Inbound messages will be passed to apps higher up in the stack once processed.

    Outbound messages will be passed down to apps lower down in the stack once processed.
    """

    def __init__(self, upper_klass=None, lower_app=None, name=None):
        self.upper_app = upper_klass(lower_app=self) if upper_klass else None
        self.lower_app = lower_app
        self.name = name

    def _on_msg_in(self, message):
        message = self.on_msg_in(message)
        if message and self.upper_app:
            message = self.upper_app._on_msg_in(message)

        return message

    def on_msg_in(self, message):
        """
        Override to define what to do when a message is received from the other party.

        :param message: Received message.
        :returns: message to be passed to the upper app. If None processing is stopped on the current
        level in the stack.
        """
        return message

    def _on_msg_not_rcvd(self, message):
        message = self.on_msg_not_rcvd(message)
        if message and self.upper_app:
            message = self.upper_app._on_msg_not_rcvd(message)

        return message

    def on_msg_not_rcvd(self, message):
        """
        Override to define what to do when a message was not received successfully by the other party.

        :param message: Message that was not received.
        :returns: message to be passed to the upper app. If None processing is stopped on the current
        level in the stack.
        """
        return message

    def send(self, message_or_batch):
        """
        Send message or batch of messages to the other party.

        :param message_or_batch: Message or batch of messages to be sent.
        :returns: batch sent
        """
        
        batch = (message_or_batch,) if isinstance(message_or_batch, Message) else message_or_batch
        batch = self.on_batch_send_request(batch)
        if batch and self.lower_app:
            batch = self.lower_app.send(batch)
        return batch
    
    def on_batch_send_request(self, batch):
        """
        Override to define what to do with the hole batch of messages.
        This method is called when someone calls 'send' on this app or any app higher up in the
        stack. If not overriden, this method calls on_send_request for each message.

        Can be used to prevent a message from being sent to the other party.

        :param message: Message to be sent.
        :returns: batch (iterable object) to be passed to the lower app. If bool(return value) is False, 
        processing is stopped on the current level in the stack. 
        """
        transformed = (self.on_send_request(message) for message in batch)
        return tuple(m for m in transformed if m)

    def on_send_request(self, message):
        """
        Override to define what to do with a message to be sent to the other party.
        This method is called when someone calls 'send' on this app or any app higher up in the
        stack.

        Can be used to prevent a message from being sent to the other party.

        :param message: Message to be sent.
        :returns: message to be passed to the lower app. If None processing of this message is stopped on the 
        current level in the stack.
        """
        return message
    
    def app_by_name(self, name):
        """
        Looks for an app upper in the stack
        
        :param name: Name of the app looked for
        :returns: an app (or None if nothing is found)
        """
        if self.name == name:
            return self
        
        if self.upper_app is None:
            return None
        
        return self.upper_app.app_by_name(name)


def stack(*args):
    """
    Builds a stack of apps. Each parameter represents a layer in the stack. Bottom first.

    :param *args: List of pairs (class, kwargs) for each app in the stack.
    :returns: stack of applications.

    Sample usage:

        stack = app.stack(
            (
                session.SessionApp,
                dict(
                    socket_klass = sb,
                    username = user,
                    password= password,
                    we = user,
                    you="NYSE",
                    reset_seq_nums=True
                )
            ),
            (
                MyStrategyApp,
                dict(
                    param1 = value1,
                    param2 = value2
                )
            )
        )
    """

    if not args:
        raise Exception("Cannot make an empty stack.")

    if len(args) == 1:
        raise Exception(
            "Cannot make a stack consisting of a single layer. Just run the app constructor instead!"
        )

    # Generate constructor for up-most app
    klass, kwargs = args[-1]
    upper_klass = (
        lambda klass, kwargs: lambda lower_app: klass(lower_app=lower_app, **kwargs)
    )(klass, kwargs)

    def build_constructor(klass, kwargs, upper_klass):
        return lambda lower_app: klass(
            lower_app=lower_app, upper_klass=upper_klass, **kwargs
        )

    # Chain middle
    for klass, kwargs in reversed(args[1:-1]):
        upper_klass = build_constructor(klass, kwargs, upper_klass)

    # Generate base and return
    klass, kwargs = args[0]
    return klass(upper_klass=upper_klass, **kwargs)


def on(type_):
    """
    Decorator to be used with a ByMessageTypeApp to handle messages received of a certain type.
    Compares field 35 of the message with type_.

    Sample usage:
        @on(MsgType.ExecutionReport)
        def on_execution_report(self, message):
            # do something with the execution report
            return message # pass the message to the upper app if exists.

    :param type_: bytestring containing the type of the message to be handled. Can also be a
    slowbreak.constants.MsgType constant.
    :returns: decorator to be used with a ByMessageTypeApp method.
    """

    def decorator(f):
        f.on_type = type_
        return f

    return decorator


class ByMessageTypeApp(BaseApp):
    """
    Utility class to handle each type of message received separately.

    Handlers for different types of messages can be defined using the on(type_) decorator.
    """

    def __init__(self, *args, **kwargs):

        self.handlers = {}

        method_list = [
            getattr(self, func)
            for func in dir(self)
            if callable(getattr(self, func)) and not func.startswith("__")
        ]

        for method in method_list:
            try:
                self.handlers[getattr(method, "on_type")] = method
            except AttributeError:
                # Method is not a message type handler, ignore
                pass

        super(ByMessageTypeApp, self).__init__(*args, **kwargs)

    def on_msg_in(self, message):
        t = message.get_field(Tag.MsgType)
        return self.handlers.get(t, self.on_unhandled)(message)

    def on_unhandled(self, message):
        """
        Method called when no handler has been defined for the type of message received.

        :params message: Unhandled message.
        :returns: message to be passed to the upper app. If None processing is stopped on the current
        level in the stack.
        """
        return message
