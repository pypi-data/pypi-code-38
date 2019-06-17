"""
:synopsis: A example that shows very brief all important features of the pynetworking module


This is example is meant to demonstrate the use of the most important features of the pynetworking module.
This example has to be adjusted if you want to implement a real client server application. Here client and
server are executed in the same process which is ok for testing but not realistic in reality.

Features:
- call functions with arguments (server->client and client->server)
- get return values
- get Exceptions

What cannot be returned by a function:
- generator
- frame
- traceback
"""
import pynetworking as net

# define the address at which the server listen and the clients connect to
server_address = "127.0.0.1", 5000

# Only log errors
net.Logging.logger.setLevel(40)


def main():
    # open and start the server and close afterwards
    print("This program shows all important features that are possible with the pynetworking library.\n\n")
    with net.ClientManager(server_address, ClientCommunicator):
        # Connect a client to the server
        ServerCommunicator.connect(server_address, blocking=True, timeout=2)

        # create an alias for all server functions (Not necessary, but code looks better)
        server = ServerCommunicator.remote_functions

        # Call functions at the server
        print(f"{'='*7} Calling a function with arguments and return value {'=' * 7}\n")
        types = server.get_types(1, "He", [1, 2], main, lambda a, b: a+b)
        print(types)

        print(f"\n\n{'=' * 7} Calling a function that raises an error {'=' * 7}\n")
        try:
            server.risky_function()
        except NotImplementedError as e:
            print(e)
            print("Error successfully transmitted")

        print(f"\n\n{'=' * 7} Calling a function that calls a function at the client {'=' * 7}\n")
        server.start_communication()

        # Close the connection to the server at client-side
        ServerCommunicator.close_connection()


class ClientFunctions(net.ClientFunctions):
    # A class that defines every method that can be called at a client from the server
    @staticmethod
    def a_client_function(message: str) -> None:
        print(f"At Client: {message}")
        ServerCommunicator.remote_functions.a_communication_function("Hi from Client!")


class ServerFunctions(net.ServerFunctions):
    # A class that defines every method that can be called at the server from a client
    @staticmethod
    def get_types(*args, **kwargs) -> list:
        """returns a list of all types of the passed arguments.
        e.g. simple_function(10, [1,2]) will return [int, list]"""
        arg_types = []
        for arg in args:
            arg_types.append(type(arg))
        for values in kwargs.values():
            arg_types.append(type(values))
        return arg_types

    @staticmethod
    def risky_function():
        raise NotImplementedError("You successfully raised an error!")

    @staticmethod
    def start_communication():
        client: ClientCommunicator = net.ClientManager().get()
        client.remote_functions.a_client_function("Hi from Server!")

    @staticmethod
    def a_communication_function(message):
        print(f"At Server: {message}")


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
