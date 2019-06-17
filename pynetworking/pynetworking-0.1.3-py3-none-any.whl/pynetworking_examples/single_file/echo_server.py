"""
:synopsis: A simple echo server
:author: Julian Sobott

The server always prints the received message from the client.
If the client writes 'bye', the client calls a function at the client and prints the result.

"""

import pynetworking as net

# define the address at which the server listen and the clients connect to
server_address = "127.0.0.1", 5000

# Only log errors
net.Logging.logger.setLevel(40)


def main():
    # open and start the server and close afterwards
    # As arguments, the address, to which the server listens to and the class that overrides the ClientCommunicator is
    # needed
    with net.ClientManager(server_address, ClientCommunicator):
        # Connect a client to the server
        # The connection is stored statically. This means no object needs to be created and passed to other functions.
        # Once the connection is established, you can call the functions from everywhere
        ServerCommunicator.connect(server_address, blocking=True, timeout=2)

        # create an alias for all server functions (Not necessary, but code looks better)
        server = ServerCommunicator.remote_functions

        while True:
            message = input(">>>")
            server.recv_message_from_client(message)
            if message == "bye":
                break

        # Close the connection to the server at client-side
        ServerCommunicator.close_connection()


class ClientFunctions(net.ClientFunctions):
    # A class that defines every method that can be called at a client from the server
    @staticmethod
    def get_last_words() -> str:
        return "Please don't leave me alone!"


class ServerFunctions(net.ServerFunctions):
    # A class that defines every method that can be called at the server from a client
    @staticmethod
    def recv_message_from_client(message: str) -> None:
        print(f"Client: {message}")
        if message == "bye":
            client: ClientCommunicator = net.ClientManager().get()
            clients_last_words = client.remote_functions.get_last_words()
            print(clients_last_words)


class ClientCommunicator(net.ClientCommunicator):
    # Server-side class that sets the available functions and make them available for communication
    local_functions = ServerFunctions
    remote_functions = ClientFunctions


class ServerCommunicator(net.ServerCommunicator):
    # Client-side class that sets the available functions and make them available for communication
    local_functions = ClientFunctions
    remote_functions = ServerFunctions


if __name__ == '__main__':
    main()
