import socket
import threading
from multiprocessing.connection import Listener, Client

from .cmd_parser import CommandError, ACK, NACK


__all__ = ['MY_IP', 'listener_handler', 'run_listener', 'send_command']


MY_IP = socket.gethostbyname(socket.gethostname())


def listener_handler(alive, sock, cmd_handler):
    """Continuously listen for communication"""
    while alive.is_set():
        try:
            cmd = sock.recv()
            # sock.send(ACK(cmd))
            cmd_handler(sock, cmd)
        except EOFError as err:
            break  # Socket disconnected
        except CommandError as err:
            # sock.send(NACK(err))
            print('Command Error:', err)

    print('Client closed {}!'.format(sock))


def run_listener(cmd_handler, address, port, authkey=None):
    """Run the listener to listen for a client connection and handle the communication between this process and the
    other process.

    Args:
        cmd_handler (function/callable): Function that takes in (socket, cmd) and handles the communication.
        address (str): IP Address to connect to.
        port (int): Port to connect with.
        authkey (bytes)[None]: Password to protect the socket communication.
    """
    alive_event = threading.Event()
    alive_event.set()

    with Listener((address, port), authkey=authkey) as listener:
        print('listening . . .')
        while alive_event.is_set():
            sock = listener.accept()
            print('Client connected {}!'.format(sock))
            th = threading.Thread(target=listener_handler, args=(alive_event, sock, cmd_handler))
            th.daemon = True  # Python keeps track and a reference of all daemon threads
            th.start()

    alive_event.clear()
    print('listener closed')


def send_command(cmd, address, port, authkey=None, attempts=5, response_handler=None):
    """Send a command to a schedule listener.

    Args:
        cmd (object/ipc.CommandInterface): Command to send.
        address (str): IP Address to connect to.
        port (int): Port to connect with.
        authkey (bytes)[None]: Password to protect the socket communication.
        attempts (int)[5]: Number of times to send the command and attempt to get an ack.
        response_handler (function/callable)[None]: Handle the response after an ACK.
            This function should take in (client socket).
    """
    success = False
    trials = 0
    with Client((address, port), authkey=authkey) as client:
        while not success and trials <= attempts:
            # Send the command
            if trials > 0:
                print('Retrying to send the command attempt {} of {} . . .'.format(trials, attempts))
            client.send(cmd)

            # Try to receive an ACK or NACK
            try:
                if client.poll(timeout=3):
                    msg = client.recv()
                    if isinstance(msg, ACK):
                        # Mark that the message was ACKed
                        success = True

                        # Call the response handler
                        if callable(response_handler):
                            response_handler(client)

                    elif isinstance(msg, NACK):
                        print('NACK:', msg.error)
            except EOFError:
                break  # socket disconnected
            except (socket.error, Exception) as error:
                print('Send Error:', error)

            trials += 1

    if not success:
        raise CommandError('Command Failed! Did not receive Acknowledgement for command {}'.format(str(cmd)))
