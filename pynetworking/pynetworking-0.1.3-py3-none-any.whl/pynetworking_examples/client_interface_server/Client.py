"""
:synopsis: All functions located at the client_side
"""
import pynetworking as net
import Interface


def client_func(name) -> bool:
    print(f"Hello {name}")
    return True


def client_faculty(number: int) -> int:
    if number <= 1:
        return number
    return number * Interface.ServerCommunicator.remote_functions.server_faculty(number - 1)


if __name__ == '__main__':
    address = ("127.0.0.1", 5000)
    with net.ClientManager(address, Interface.ClientCommunicator):
        Interface.ServerCommunicator.connect(address)
        ret_value = Interface.ServerCommunicator.remote_functions.server_faculty(5)
        print(f"Client: {ret_value}")

        ret_value = Interface.ServerCommunicator.remote_functions.greet_client("Walter")
        print(f"Client: {ret_value}")
        Interface.ServerCommunicator.close_connection()

