#/usr/bin/python
__version__ = 0.22
__author__ = 'alastair.maxwell@glasgow.ac.uk'

##
##Imports
import sys
import os
import argparse
import subprocess
import glob
import errno
import progressbar
import logging as log

class clr:
	def __init__(self):
		pass
	purple = '\033[95m'
	cyan = '\033[96m'
	darkcyan = '\033[36m'
	blue = '\033[94m'
	green = '\033[92m'
	yellow = '\033[93m'
	red = '\033[91m'
	bold = '\033[1m'
	underline = '\033[4m'
	end = '\033[0m'

def check_positive(value):
	ivalue = int(value)
	if ivalue <= 0:
		raise argparse.ArgumentTypeError("Integers for -max must be positive, you provided: %s." % value)
	return str(ivalue)

class BatchAdapt:
	def __init__(self):

		##
		## Argument parser from CLI
		self.parser = argparse.ArgumentParser(prog='batchadapt', description='BatchAdapt: Batch demulitplexing via cutadapt.')
		## I/O arguments
		self.parser.add_argument('-v', '--verbose', help='Verbose output mode. Setting this flag enables verbose output. Default: off.', action='store_true')
		self.parser.add_argument('-i', '--input', help='Path to a folder with forward and reverse fastq/fastq.gz files within.', nargs=1, required=True)
		self.parser.add_argument('-o', '--output', help='Path to your desired output. All demultiplexed files and a processing report will be saved here.', nargs=1, required=True)
		## Forward adapter arguments
		fw_group = self.parser.add_mutually_exclusive_group(required=True)
		fw_group.add_argument('-fwtp', '--fwthreeprime', help='FORWARD sequence of a 3\' adapter.', nargs=1, type=str)
		fw_group.add_argument('-fwfp', '--fwfiveprime', help='FORWARD sequence of a 5\' adapter.', nargs=1, type=str)
		fw_group.add_argument('-fwap', '--fwanyprime', help='FORWARD sequence of an adapter ligated to either 3\' or 5\' end of a read.', nargs=1, type=str)
		## Reverse adapter arguments
		rv_group = self.parser.add_mutually_exclusive_group(required=True)
		rv_group.add_argument('-rvtp', '--rvthreeprime', help='REVERSE sequence of a e\' adapter.', nargs=1, type=str)
		rv_group.add_argument('-rvfp', '--rvfiveprime', help='REVERSE sequence of a 5\' adapter.', nargs=1, type=str)
		rv_group.add_argument('-rvap', '--rvanyprime', help='REVERSE sequence of an adapter ligated to either 3\' or 5\' end of a read.', nargs=1, type=str)
		## Quality arguments
		self.parser.add_argument('-e', '--errorrate', help='Maximum allowed error rate. I.e. num of errors over the length of a matching region. [0]', nargs=1, default='0', type=int)
		self.parser.add_argument('-ni', '--noindels', help='Do not allow indels in any alignments -- only mismatches). Only works on anchored adapters.', action='store_true')
		self.parser.add_argument('-ov', '--overlap', help='Minimum overlap length. [10]', nargs=1, default='10', type=int)
		## Read arguments
		self.parser.add_argument('-dt', '--discardtrimmed', help='Discard reads that contain the adapter. [False]', action='store_true')
		self.parser.add_argument('-du', '--discarduntrimmed', help='Discard reads that do not contain the adapter. [True]', action='store_false')
		self.parser.add_argument('-min', '--minlength', help='Discard trimmed reads shorter than <length>.', nargs=1, type=int, default='0')
		self.parser.add_argument('-max', '--maxlength', help='Discard trimmed reads longer than <length>.', nargs=1, type=check_positive, default='999999')
		self.parser.add_argument('-u', '--cut', help='Remove <length> bases from beginning/end of a read. >0 values removes from beginning. <0 values, remove from end.', nargs=1, type=int, default=0)
		self.args = self.parser.parse_args()

		##
		## Set verbosity for CLI output
		if self.args.verbose:
			log.basicConfig(format='%(message)s', level=log.DEBUG)
			log.info('\n{}{}{}{}'.format(clr.bold,'adpt__ ',clr.end,'BatchAdapt: Batch demulitplexing via cutadapt.'))
			log.info('{}{}{}{}'.format(clr.bold,'adpt__ ',clr.end,'alastair.maxwell@glasgow.ac.uk\n'))
		else:
			log.basicConfig(format='%(message)s')

		##
		## Adapter objects, check+create
		self.forward_command = None; self.forward_adapter = None
		self.reverse_command = None; self.reverse_adapter = None
		self.assign_adapters()

		##
		## Check input/output...
		self.input_files = None
		if self.check_io():
			log.error('{}{}{}{}'.format(clr.red,'sdha__ ',clr.end,'Exception occurred in I/O function. Check input/output.'))
			sys.exit(2)

		## Execute cutadapt
		self.run_binary()

		##
		## If we get here, we're finished with no immediate issues.
		log.info('{}{}{}{}'.format(clr.green,'adpt__ ',clr.end,'Workflow complete! Terminating.'))
		sys.exit(2)

	def assign_adapters(self):

		## Check forward adapter
		if self.args.fwthreeprime: self.forward_command = '-a'; self.forward_adapter = self.args.fwthreeprime
		if self.args.fwfiveprime: self.forward_command = '-g'; self.forward_adapter = self.args.fwfiveprime
		if self.args.fwanyprime: self.forward_command = '-b'; self.forward_adapter = self.args.fwanyprime
		## Check reverse adpater
		if self.args.rvthreeprime: self.reverse_command = '-a'; self.reverse_adapter = self.args.rvthreeprime
		if self.args.rvfiveprime: self.reverse_command = '-g'; self.reverse_adapter = self.args.rvfiveprime
		if self.args.rvanyprime: self.reverse_command = '-b'; self.reverse_adapter = self.args.rvanyprime

	def check_io(self, raise_exception = False):


		## check input path exists
		if os.path.lexists(self.args.input[0]):
			log.info('{}{}{}{}{}'.format(clr.green, 'adpt__ ', clr.end, 'Working from: ', self.args.input[0]))
		else:
			log.error('{}{}{}{}'.format(clr.red, 'adpt__ ', clr.end, 'Specified input path could not be found. Exiting.'))
			raise_exception = True

		## check even number of files
		self.input_files = glob.glob(os.path.join(self.args.input[0], '*'))
		sorted_input = sorted(self.input_files)
		file_count = len(sorted_input)
		if not file_count % 2 == 0:
			log.warn('{}{}{}{}'.format(clr.yellow, 'adpt__ ', clr.end, 'I/O: Non-even number of input files specified. Results may be undesired.'))

		## check files end in _R1 and _R2
		for i in range(0, len(sorted_input), 2):
			forward_data = sorted_input[i];	reverse_data = sorted_input[i+1]
			## Forward check
			forward_data_name = sorted_input[i].split('/')[-1].split('.')[0]
			if not forward_data_name.endswith('_R1'):
				log.error('{}{}{}{}{}'.format(clr.red, 'adpt__  ', clr.end, 'I/O: Forward input file does not end in _R1. ', forward_data))
				raise_exception = True
			## Reverse check
			reverse_data_name = sorted_input[i + 1].split('/')[-1].split('.')[0]
			if not reverse_data_name.endswith('_R2'):
				log.error('{}{}{}{}{}'.format(clr.red, 'adpt__ ', clr.end, 'I/O: Reverse input file does not end in _R2. ', reverse_data))
				raise_exception = True

		## check output path, create if missing
		if not os.path.exists(self.args.output[0]):
			log.info('{}{}{}{}{}'.format(clr.bold, 'shda__ ', clr.end, 'Creating output root: ', self.args.output[0]))
			try:
				os.makedirs(self.args.output[0])
			except OSError as exc:
				if exc.errno == errno.EEXIST and os.path.isdir(self.args.output[0]):
					pass
				else:
					raise

		return raise_exception

	def lookup_command(self, given_arg):

		## hideous lmao
		for adapter in [self.forward_adapter, self.reverse_adapter]:
			if '^' or '$' not in adapter:
				if given_arg[0] == 'noindels': return [0,0,0]
			else:
				if given_arg[0] == 'noindels': return ['--no-indels']
		if given_arg[0] == 'cut': return ['-u', str(given_arg[1])]
		if given_arg[0] == 'verbose': return [0,0,0]
		if given_arg[0] == 'rvanyprime': return [0,0,0]
		if given_arg[0] == 'minlength': return ['-m', str(given_arg[1])]
		if given_arg[0] == 'discarduntrimmed':
			if given_arg[1]: return ['--discard-untrimmed']
			else: return [0,0,0]
		if given_arg[0] == 'fwfiveprime': return [0,0,0]
		if given_arg[0] == 'overlap': return ['-O', str(given_arg[1][0])]
		if given_arg[0] == 'rvthreeprime': return [0,0,0]
		if given_arg[0] == 'fwthreeprime': return [0,0,0]
		if given_arg[0] == 'errorrate': return ['-e', str(given_arg[1][0])]
		if given_arg[0] == 'input': return [0,0,0]
		if given_arg[0] == 'output': return [0,0,0]
		if given_arg[0] == 'discardtrimmed':
			if given_arg[1]: return ['--discard-trimmed']
			else: return [0,0,0]
		if given_arg[0] == 'fwanyprime': return [0,0,0]
		if given_arg[0] == 'rvfiveprime': return [0,0,0]
		if given_arg[0] == 'maxlength': return ['-M', str(given_arg[1])]

	def run_binary(self):

		## Check binary exists...
		library_subprocess = subprocess.Popen(['which', 'cutadapt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		library_directory = library_subprocess.communicate()
		library_subprocess.wait()
		if not 'cutadapt' in library_directory[0]:
			log.critical('{}{}{}{}'.format(clr.red, 'adpt__ ', clr.end, 'Cutadapt is missing! Not installed or not on $PATH'))
			sys.exit(20)

		if self.args.verbose:
			bar = progressbar.ProgressBar()
			for i in bar(range(0, len(self.input_files))):
				curr_file = self.input_files[i]; curr_root = self.input_files[i].split('/')[-1].split('.')[0]
				curr_suffix = curr_root.split('_')[-1]

				## adapter and command to use
				command = None; adapter = None
				if curr_suffix == 'R1': command = self.forward_command; adapter = self.forward_adapter[0]
				if curr_suffix == 'R2': command = self.reverse_command; adapter = self.reverse_adapter[0]

				## command to build upon with arguments
				cutadapt_command = ['cutadapt', command, adapter]
				for arg in vars(self.args):
					arg_command = self.lookup_command([arg, getattr(self.args, arg)])
					if len(arg_command) == 1: cutadapt_command.append(arg_command[0])
					elif len(arg_command) == 2: cutadapt_command.append(arg_command[0]); cutadapt_command.append(arg_command[1])
					elif len(arg_command) > 2: pass

				## add output
				outfi = 'DMPX_' + curr_file.split('/')[-1].split('.')[0] + '.fastq'
				reportfi = curr_file.split('/')[-1].split('.')[0]+'_REPORT.txt'
				target_output = os.path.join(self.args.output[0], outfi)
				report_output = os.path.join(self.args.output[0], reportfi)
				cutadapt_command.append('--output'); cutadapt_command.append(target_output)
				## add input
				cutadapt_command.append(curr_file)
				## run command

				report_outfi = open(report_output, 'w')
				cutadapt_subprocess = subprocess.Popen(cutadapt_command, stdout=report_outfi, stderr=subprocess.PIPE)
				cutadapt_subprocess.wait()
		else:
			for i in range(0, len(self.input_files)):
				curr_file = self.input_files[i]; curr_root = self.input_files[i].split('/')[-1].split('.')[0]
				curr_suffix = curr_root.split('_')[-1]

				## adapter and command to use
				command = None; adapter = None
				if curr_suffix == 'R1': command = self.forward_command; adapter = self.forward_adapter[0]
				if curr_suffix == 'R2': command = self.reverse_command; adapter = self.reverse_adapter[0]

				## command to build upon with arguments
				cutadapt_command = ['cutadapt', command, adapter]
				for arg in vars(self.args):
					arg_command = self.lookup_command([arg, getattr(self.args, arg)])
					if len(arg_command) == 1: cutadapt_command.append(arg_command[0])
					elif len(arg_command) == 2: cutadapt_command.append(arg_command[0]); cutadapt_command.append(arg_command[1])
					elif len(arg_command) > 2: pass

				## add output
				outfi = 'DMPX_' + curr_file.split('/')[-1].split('.')[0] + '.fastq'
				reportfi = curr_file.split('/')[-1].split('.')[0]+'_REPORT.txt'
				target_output = os.path.join(self.args.output[0], outfi)
				report_output = os.path.join(self.args.output[0], reportfi)
				cutadapt_command.append('--output'); cutadapt_command.append(target_output)
				## add input
				cutadapt_command.append(curr_file)
				## run command

				cutadapt_subprocess = subprocess.Popen(cutadapt_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				cutadapt_subprocess.wait()

def main():
	try:
		BatchAdapt()
	except KeyboardInterrupt:
		log.error('{}{}{}{}'.format(clr.red,'adpt__ ',clr.end,'Keyboard Interrupt detected. Exiting.'))
		sys.exit(2)
