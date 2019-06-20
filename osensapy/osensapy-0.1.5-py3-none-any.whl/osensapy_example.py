import osensapy
from time import sleep

portname = "COM4"

try:
	while True:
		transmitter = osensapy.Transmitter(portname, 247)
		temperature = transmitter.read_channel_temp('A')
		print('Temperature (C): {}'.format(temperature))
		sleep(1)
except KeyboardInterrupt:
	pass