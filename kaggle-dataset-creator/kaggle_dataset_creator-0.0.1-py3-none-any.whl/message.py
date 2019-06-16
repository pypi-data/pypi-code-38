from colorama import init, Fore


#  strip=False is necessary to print colorful text on GIT bash like terminals (tty)
init(autoreset=True, strip=False);

class Message(object):
	"""
	Description
	===========

		- Parent class of KaggleDataSet (as it inherits it)
		- A class which contains different methods to print message of 
		  type success, error, warning, data on console
	"""

	def __warning(self, message, **kwargs):
		print(Fore.YELLOW + '\nWARNING: %s' % message)


	def __success(self, message, **kwargs):
		print(Fore.GREEN + "\nSUCCESS: %s" % message)


	def __error(self, message, **kwargs):
		print(Fore.RED + "\nERROR: %s" % message)


	def __data(self, df, add_slashes = True, slash_count = 50, **kwargs):
		if add_slashes:
			print('\n' + '-' * slash_count);

		print(df)

		if add_slashes:
			print('-' * slash_count);


	def __message(self, msg, **kwargs):
		print('\n' + msg + '\n')