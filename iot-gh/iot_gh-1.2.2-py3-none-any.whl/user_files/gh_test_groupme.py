import time
from spi_mock import spidev_mock
from pigpio_mock import pi_mock
from iot_gh.GHService import GHService
from iot_gh.GHTextingService import GHTextingService

def main():
    spi = spidev_mock()
    pi = pi_mock()
    ghs = GHService(pi, spi)

    ACCESS_TOKEN = ""
    ACCESS_TOKEN = input("Please enter your dev.groupme.com access token: ").strip()
    t_service = GHTextingService(ACCESS_TOKEN, ghs,"iot_gh_testing")

    last_message_id = None;
    while True:
        if t_service.last_message != None:
            if t_service.last_message.id != last_message_id:
                name = t_service.last_message.name
                text = t_service.last_message.text
                print(name + "   " + text)
                print()

                last_message_id = t_service.last_message.id
            time.sleep(1)
              
    
if __name__ == "__main__":
    main()