# coding: utf-8
#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.abspath(__file__+'/..'))

from sharpenCommander.sc import main

def run():
	main()

if __name__ == "__main__":
	try:
		ret = run()
	except Exception as e:
		#print(e)
		#sys.exit(1)
		raise e
