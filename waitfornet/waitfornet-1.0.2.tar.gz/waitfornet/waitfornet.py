import requests
import argparse
import waitfornet
from time import sleep

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-w', '--wait',  default=False, action='store_true', help='Wait until online, keep trying')
	parser.add_argument('-v', '--version',  default=False, action='store_true', help='Display the version number')
	args = parser.parse_args()
	if args.version:
		print("waitfornet v%s" % (waitfornet.__version__) )
		return
	while(True):
		try:
			req = requests.get("https://www.google.com")
			s = req.text
			print("All OK")
			return
		except Exception as ex:
			if args.wait:
				print("Sleeping for 5 seconds before trying again")
				sleep(5)
			else:
				raise Exception("Not online")

if __name__ == "__main__":
	main()