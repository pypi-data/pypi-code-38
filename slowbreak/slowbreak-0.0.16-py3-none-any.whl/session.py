from .app import BaseApp
from .message import Message, Tag, MsgType, TagNotFound, from_int, to_int, from_bool, to_bool, timestamp
from . import comm
from . import bursty_queue

import threading
from six.moves import queue
import logging
import functools

LOG = logging.getLogger(__name__)
LOG_IN = LOG.getChild("in")
LOG_OUT = LOG.getChild("out")

def not_new_order_or_cancel(message):
    return not message[0][1] in (MsgType.OrderCancelRequest, MsgType.NewOrderSingle)

def thread_fun(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        LOG.info(threading.current_thread().name + " started")
        try:
            f(*args, **kwargs)
            LOG.info(threading.current_thread().name + " finished gracefully")
        except:
            LOG.exception(threading.current_thread().name + " terminated abnormally")
            
    return decorated

class OutMessageStore(object): 
    
    def __init__(self, seq_num=1):
        self.lock = threading.Lock()
        self.messages = []
        self.first_seq_num = seq_num
        
    @property
    def next_seq_num(self):
        return self.first_seq_num + len(self.messages)
    
    def decorate(self, message):
        rv = Message(
            message[0],
            ( 34, from_int(self.next_seq_num))
        )
        return rv + message[1:]
        
    def decorate_and_register(self, message):
        with self.lock:
            decorated = self.decorate(message)
            self.messages.append(decorated)
            
            return decorated
        
    def get(self, seq_num):
        with self.lock:
            index = seq_num - self.first_seq_num
            if index < 0:
                raise IndexError("Invalid seq_num %s" % seq_num)
            return self.messages[index]
        
    def drop(self, seq_num):
        with self.lock:
            new_first = seq_num + 1
            delta = new_first - self.first_seq_num
            
            del self.messages[:delta]
            
            self.first_seq_num = new_first
            
        LOG.info("Dropping %s messages. New first %s" % (delta, new_first))
    
    def __len__(self):
        with self.lock:
            return len(self.messages)


class BaseSessionApp(BaseApp):
    
    class InvalidMessage(Exception):
        pass
    
    class SignalStop(Exception):
        pass
    
    class WaitTimeout(BaseException):
        pass
    
    class MasterThread(threading.Thread):
        def __init__(self, app):
            super(BaseSessionApp.MasterThread, self).__init__(name="SessionApp.master")
            self.app = app
            self.out_queue = bursty_queue.BurstyQueue(app.send_period)
            
        def store_and_send(self, message):
            LOG.warning("Skipping message %r. Attempted to send in master thread" % message)
            self.app._on_msg_not_rcvd(message)
            
        def send(self, message):
            self.out_queue.put(
                lambda thread: thread.store_and_send(message),
                low_priority = self.app.low_priority(message)
            )
            
        def send_and_disconnect(self, message):
            def send_and_disconnect_action(thread):
                thread.store_and_send(message)
                self.app.gtfo = True
                raise self.app.SignalStop()
            
            self.out_queue.put(
                send_and_disconnect_action,
                low_priority = False
            )
            
        def stop_request(self):
            def stop_request_action(thread):
                raise BaseSessionApp.SignalStop()
            
            self.out_queue.put(stop_request_action, low_priority = False)
            
        def stop_this_thread(self, thread):
            def stop_this_thread_action(other_thread):
                if thread is other_thread:
                    raise self.app.SignalStop()
                
            self.out_queue.put(stop_this_thread_action, low_priority = False)
            
        def set_heartbeat_time(self):
            def set_heartbeat_time_action(thread):
                if hasattr(thread, 'socket'):
                    # timeout if heartbeat is missing by over 20% of the expected time
                    thread.socket.settimeout(self.app.heartbeat_time * 1.2)
                    
                    LOG.info("New heartbeat time %s set in current socket" % self.app.heartbeat_time)
                
            self.out_queue.put(set_heartbeat_time_action)
            
        def gap_fill(self, seq_no):
            
            def gap_fill_action(thread):
                
                # Find next seq_no
                new_seq_no = self.app.oms.next_seq_num
                
                # Drop confirmed messages
                self.app.oms.drop(seq_no - 1)
                
                # Report not received messages
                for m in self.app.oms.messages:
                    LOG.warning("Gap fill: Msg not received %r" % m)
                    self.app._on_msg_not_rcvd(m)
                
                # Drop not sent messages
                self.app.oms.drop(new_seq_no)
                
                # Send gap fill
                self.app.oms.first_seq_num = seq_no
                decorated = self.app.oms.decorate(
                    self.app._add_static_header_fields(Message(
                        (35,b'4'),
                        (36, from_int(new_seq_no)),
                        (123, from_bool(True))
                    ))
                )
                LOG_OUT.info("Sending %r" % decorated)
                thread.socket.sendall(decorated.to_buf())
                
                # Set expected sequence number for future interaction
                self.app.oms.first_seq_num = new_seq_no
                
            self.out_queue.put(gap_fill_action, low_priority = False)
            
        @thread_fun
        def run(self):
            while True:
                socket = self.app.socket_klass()
                
                if socket:
                    out_thread = self.app.OutThread(app=self.app, socket=socket, queue=self.out_queue)
                    out_thread.start()
    
                    in_thread = self.app.InThread(app=self.app, socket=socket, out_thread=out_thread)
                    in_thread.start()
                    
                    in_thread.join()
                    out_thread.join()
                    
                else: 
                    LOG.warn("Could not connect to the server :(")
    
                while True:
                
                    if self.app.gtfo or not self.app.reconnect:
                        LOG.info("Our job is done. Finishing")
                        return # Nothing else will be made 
                    
                    try:
                        self.out_queue.get(timeout=self.app.reconnect_time, ignore_throttling=True)(self) # No write thread, handle this things here
                    except self.app.SignalStop:
                        pass # 
                    except queue.Empty:
                        break # Now it is time to reconnect
                        
                    

                if self.app.gtfo:
                    LOG.info("gtfo set. Finishing main thread.")
                    return # Get the fuck out requested
                
                if self.app.reconnect:
                    LOG.info("Sleeping %s seconds before reconnecting" % self.app.reconnect_time)
                else:
                    LOG.info("reconnect is false. Finishing main thread.")
                    return 
                        
    
    class InThread(threading.Thread):
        def __init__(self, app, socket, out_thread):
            super(BaseSessionApp.InThread, self).__init__(name="SessionApp.in")
            self.app = app
            self.socket = socket
            self.out_thread = out_thread

        @thread_fun      
        def run(self):
            try:
                self.socket.settimeout(self.app.heartbeat_time * 1.2) # timeout if heartbeat is missing by over 20% of the expected time
                messages = Message.from_socket(self.socket, begin_string=self.app.begin_string)
                if self.app.reset_seq_nums:
                    self.app.next_in_seq_num = 1
                logon = next(messages)
            
                if logon is None:
                    LOG.error("Timed out reading while logging in")
                    return
                
                LOG_IN.info("Received %r" % logon)
                if MsgType.Logon != logon.get_field(Tag.MsgType):
                    LOG.error("Received %r instead of logon" % logon)
                    return

                try:
                    self.app._on_msg_in(logon)
                except Exception as e:
                    LOG.warning("Ignoring exception %s while processing message %r" % (e, logon), exc_info=True)
                    
                timed_out = False
                for message in messages:
                    try:
                        LOG_IN.info("Received %r" % message)
                        if message is None:
                            LOG.warning("Timeout while waiting for message")
                            if not timed_out:
                                timed_out = True
                                self.app.send(
                                    Message((35,b"1"), (112, b"TEST"))
                                )
                                continue
                            
                            # Missing test request
                            LOG.error("Timeout while waiting for test request, disconnecting")
                            return
                            
                        timed_out = False
                        self.app._on_msg_in(message)
                        
                        if MsgType.Logout == message.get_field(Tag.MsgType):
                            LOG.info("Received logout. Stopping thread")
                            return
                    except Exception as e:
                        LOG.warning("Ignoring exception %s while processing message %r" % (e, message), exc_info=True)
                raise Exception("Connection closed without logout")
            finally:
                self.app.master_thread.stop_this_thread(self.out_thread)                
        
    
    class OutThread(threading.Thread):
        def __init__(self, app, socket, queue):
            super(BaseSessionApp.OutThread, self).__init__(name="SessionApp.out")
            
            self.app = app
            self.queue = queue
            self.socket = socket
            self.store_and_send = self.store_and_send_skip
            
        def store_and_send_skip(self, message):
            LOG.warning("Skipping message %r. Attempted to send before login" % message)
            self.app._on_msg_not_rcvd(message)
            
        def store_and_send_normal(self, message):
            decorated = self.app.oms.decorate_and_register(
                self.app._add_static_header_fields(message)
            )

            LOG_OUT.info("Sending %r" % decorated)
            self.socket.sendall(decorated.to_buf(begin_string=self.app.begin_string))
            
        @thread_fun            
        def run(self):
            try:
                # Empty message queue
                while True:
                    try:
                        self.queue.get(timeout=0, ignore_throttling=True)(self)
                    except queue.Empty:
                        break
                    
                if self.app.reset_seq_nums or not self.app.oms:
                    self.app.oms = OutMessageStore(
                        seq_num=1
                    )  
                    
                # Newer messages will be sent
                self.store_and_send = self.store_and_send_normal
                
                self.app.on_connect(out_thread=self)
                
                while True:
                    try:
                        self.queue.get(timeout=self.app.heartbeat_time)(self)
                    except queue.Empty:
                        self.store_and_send(Message((35, b'0'))) # send keepalive on timeout 
    
                    if self.app.confirm_request_msg_count <= len(self.app.oms) and not self.app.waiting_for_confirmation:
                        self.store_and_send( Message(
                            (35, b'1'),
                            (112, b'CONFIRM %d' % self.app.oms.next_seq_num)
                        ) )
                        self.app.waiting_for_confirmation = True
            except BaseSessionApp.SignalStop:
                pass # stop gracefully when signalled
            finally:
                comm.close(self.socket) # also stops in thread if required

    def __init__(self, 
        we, 
        socket = None,
        socket_klass = None, 
        heartbeat_time=1000,
        confirm_request_msg_count=100, 
        reconnect=False,
        reconnect_time=60,
        send_period=0.1,
        low_priority=lambda _: True,
        extra_header_fields_fun=None, 
        begin_string=b'FIXT.1.1',
        *args, 
        **kwargs
    ):
        super(BaseSessionApp, self).__init__(*args, **kwargs)

        self.we = we
        self.heartbeat_time = heartbeat_time
        self.confirm_request_msg_count = confirm_request_msg_count
        self.reconnect = reconnect
        self.reconnect_time = reconnect_time
        self.waiting_for_confirmation=False
        self.send_period = send_period
        self.low_priority = low_priority
        self.extra_header_fields_fun = extra_header_fields_fun
        self.begin_string = begin_string
        
        self.socket_klass = (lambda: socket) if socket else socket_klass
        
        self.oms = None # will be set in the out thread
        self.next_in_seq_num = 1
        
        self.gtfo = False # get the fuck out
        
        self.master_thread = self.MasterThread(app=self)
        self.master_thread.start()

    def _add_static_header_fields(self, message):
        # Always call before adding field 34 (SeqNum)
        static_fields = Message(
            ( 49, self.we ),
            ( 52, timestamp() ),
            ( 56, self.you )
        )
        if self.extra_header_fields_fun:
            static_fields += self.extra_header_fields_fun(message)
            
        return message[0:1] + static_fields + message[1:]
    
    def _set_heartbeat_time(self, t):
        self.heartbeat_time = t
        self.master_thread.set_heartbeat_time()

            
    def logout(self, msg=b"User generated logout"):
        self.gtfo = True
        self.send(
            Message(
                (35, b'5'),
                (58, msg)
            )
        )
        
    def on_msg_in(self, message):
        
        seq_num = to_int(message.get_field(34))
        pos_dup = to_bool( message.get_field(43, b'N') )
        
        if seq_num < self.next_in_seq_num:
            if not pos_dup:
                LOG.error("Expecting seq_num %s but got %s. Disconnecting" % (self.next_in_seq_num, seq_num))
                self.disconnect()
            return # message already processed
            
        if seq_num > self.next_in_seq_num:
            # Resend request
            LOG.warning("Resend request starting at %s" % self.next_in_seq_num)
            self.send(
                Message(
                    (35,b'2'),
                    (7,from_int(self.next_in_seq_num)),
                    (16,b"0")
                )
            )
            return
        
        # Everything is fine :D
        self.next_in_seq_num += 1
        
        _type = message.get_field(35)
        
        if MsgType.TestRequest == _type:
            req_id = message.get_field(112)
            self.send(
                Message(
                    (35, b'0'),
                    (112, req_id)
                )
            )
        elif MsgType.Heartbeat == _type:
            try:
                confirm = message.get_field(112)
                if confirm.startswith(b"CONFIRM "):
                    conf_seq_num = to_int(confirm[len(b"CONFIRM "):])
                    LOG.debug("Message %s confirmed" % conf_seq_num)
                    self.oms.drop(conf_seq_num)
                    self.waiting_for_confirmation = False
            except TagNotFound:
                pass
        elif MsgType.ResendRequest == _type:
            self.master_thread.gap_fill(to_int(message.get_field(7)))
        
        return message
        
    def on_send_request(self, message):
        if 35 != message[0][0]:
            raise self.InvalidMessage('First tag in message must be 35 for message %r' % message)
        
        self.master_thread.send(message)
        
        return None
        
    def send_and_disconnect(self, message):
        if 35 != message[0][0]:
            raise self.InvalidMessage('First tag in message must be 35 for message %r' % message)
        
        self.master_thread.send_and_disconnect(message)
        
    def disconnect(self):
        self.master_thread.stop_request()
        
    def force_stop(self):
        self.gtfo = True
        self.disconnect()
        
    def wait(self, timeout=None):
        self.master_thread.join(timeout)
        if self.master_thread.is_alive():
            raise self.WaitTimeout()
        
    def on_connect(self, out_thread):
        "What to do when the connection is established, or when the app is started if a socket is provided. Runs in the out_thread"
        pass
    
class AcceptorSessionApp(BaseSessionApp):
    "Session initiated by the counter-party"
    
    class InvalidLogonMessage(Exception):
        def __init__(self, fix_message, desc=None):
            message = "Invalid logon message %r. " % fix_message
            if desc:
                message = desc + ". " + message
            self.fix_message = fix_message
            super(AcceptorSessionApp.InvalidLogonMessage, self).__init__(message)
            
    
    def __init__(self, *args, **kwargs):
        
        self.logon_received = False
        self.reset_seq_nums= True
        super(AcceptorSessionApp, self).__init__(
            reconnect = False,
            *args,
            **kwargs
        )

    def on_msg_in(self, message):
        message = super(AcceptorSessionApp, self).on_msg_in(message)
        if not message: 
            return
        
        _type = message.get_field(35)
        
        # handle 
        if self.logon_received:
            if _type != MsgType.Logon:
                return message
            else:
                self.send(Message(
                    (35, MsgType.Reject),
                    (45, message.get_field(34)),
                    (58, b"Logon received twice")
                ))
                return # Signal logon repetition, do not bubble message to upper apps
        
        # Logon was not received yet
        try:
            self.you = message.get_field(49) # SenderCompID
            self._set_heartbeat_time(to_int(message.get_field(108))) # HeartBtInt
            if _type != MsgType.Logon:
                raise self.InvalidLogonMessage(fix_message=message, desc="Logon (35=A) expected")
            
            self.logon_received = True
            if b'0' != message.get_field(98):
                raise self.InvalidLogonMessage(fix_message=message, desc="Tag 98 has to be 0")
            
            return message
        except (self.InvalidLogonMessage, TagNotFound) as e:
            LOG.exception("Error in logon")
            self.send_and_disconnect((Message(
                (35, MsgType.Reject),
                (45, message.get_field(34)),
                (58, str(e).encode(encoding='ascii', errors='replace'))
            )))
            
        
class InitiatorSessionApp(BaseSessionApp):
    "Session initiated by ourselves"
    
    def __init__(self,         
        username, 
        password, 
        you,
        heartbeat_time=10,
        reset_seq_nums=False,
        low_priority=not_new_order_or_cancel,
        test_mode=None, 
        app_ver_id=b'9', # FIX50SP2
        extra_logon_fields_fun=None,
        *args, 
        **kwargs
    ):
        self.username = username
        self.password = password
        self.you = you
        self.reset_seq_nums = reset_seq_nums
        self.test_mode = test_mode
        self.app_ver_id = app_ver_id
        self.extra_logon_fields_fun = extra_logon_fields_fun

        super(InitiatorSessionApp, self).__init__(
            heartbeat_time = heartbeat_time,
            low_priority=low_priority,
            *args, 
            **kwargs
        )
    
    def on_connect(self, out_thread):
        
        logon_msg = Message(
            (35, b'A'),
            (98, b'0'),
            (108, from_int(self.heartbeat_time)),
            (553, self.username),
            (554, self.password),
        )
        
        if self.app_ver_id:
            logon_msg.append(1137, self.app_ver_id)

        if self.reset_seq_nums:
            logon_msg.append(141, from_bool(True))
        
        if self.test_mode == True:
            logon_msg.append(464, from_bool(True))
        elif self.test_mode == False:
            logon_msg.append(464, from_bool(False))
        # No 464 (Test message indicator) if test mode is None
        
        if self.extra_logon_fields_fun:
            logon_msg += self.extra_logon_fields_fun(logon_msg)
            
        out_thread.store_and_send( logon_msg )

SessionApp = InitiatorSessionApp # Kept for retrocompatibility
    