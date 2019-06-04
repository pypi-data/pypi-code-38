from MultiSC.MultiClient.EasyClient import EasyClient


def main():
    address = "195.154.243.51", 84
    user = EasyClient(address)
    user.connect()
    
    while True:
        command = input(">>> ")
        if command == 'exit':
            break
        print(user.castom_request("admin", "run_python", command=command))


main()
input("Enter to exit")
