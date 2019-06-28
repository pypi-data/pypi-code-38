###############################################
##### Multiple Choice Question Autograder #####
###############################################

import string
import re
import runpy
from .utils import *

class Notebook:
	"""Multiple choice question autograder for Jupyter Notebook"""

	def __init__(self, tests, scored=False, max_attempts=None):
		"""
		Initlaizes multiple choice autograder.
    
		Args:
			tests (``str``): The relative filepath to tests file
			
		Kwargs:
			scored (``bool``): Whether or not the assignment is scored
			max_attempts (``int``): The maximum number of takes allowed; deault ``None``

		Returns:
			``Notebook``. The ``Notebook`` instance for the autograder
		"""
		self._tests_raw = runpy.run_path(tests)["answers"]
		self._identifiers = [answer["identifier"] for answer in self._tests_raw]
		self._tests = {identifier : test for identifier, test in zip(
			self._identifiers,
			self._tests_raw
		)}



		self._scored = scored
		if self._scored:
			self._points = {identifier : self._tests[identifier]["points"] for identifier in self._identifiers}
			self._answered = {identifier : false for identifier, false in zip(
				self._identifiers, 
				repeat(False, len(self._identifiers))
			)}
			self._possible = sum(self._points.values())
			self._earned = 0

		self._inf_retakes = True
		if max_attempts:
			assert max_attempts > 0 and type(max_attempts) == int, "max_attempts must be a positive integer"
			self._inf_retakes = False
			self._retakes = {identifier : zero for identifier, zero in zip(
				self._identifiers, 
				repeat(0, len(self._identifiers))
			)}
			self._max_attempts = max_attempts

	def _check_answer(self, identifier, answer):
		"""
		Checks whether or not answer is correct; returns boolean
    
		Args:
			identifier (``str``): The question identifier
			answer (``str``, ``int``): The student's answer

		Returns:
			``bool``. Whether or not the answer is correct
		"""
		assert identifier in self._identifiers, "{} is not in the question bank".format(identifier)
		assert type(answer) in [str, int], "Answer must be a string or integer"
		if type(answer) == str:
			assert len(answer) == 1, "Answer must be of length 1"
		else:
			assert 0 <= answer < 10, "Answer must be a single digit"
		if not self._inf_retakes:
			if self._retakes[identifier] >= self._max_attempts:
				print("No more retakes allowed.")
				return None

		correct_answer = self._tests[identifier]["answer"]
		assert type(correct_answer) == type(answer), "Answer is not a(n) {}".format(type(correct_answer))

		if correct_answer == answer:
			if self._scored and not self._answered[identifier]:
				self._answered[identifier] = True
				self._earned += self._points[identifier]
			if not self._inf_retakes:
				self._retakes[identifier] += 1
			return True
		else:
			if not self._inf_retakes:
				self._retakes[identifier] += 1
			return False

	def check(self, identifier, answer):
		"""
		Visible wrapper for ``Notebook._check_answer`` to print output based on whether or not student's
		answer is correct

    	Args:
			identifier (``str``): The question identifier
			answer (``str``, ``int``): The student's answer

		Returns:
			``None``. Prints out student's result on question
		"""
		result = self._check_answer(identifier, answer)
		if self._scored:
			if result:
				print("Correct. {} points added to your score.".format(self._points[identifier]))
			elif result == None:
				return None
			else:
				print("Try again.")
		else:
			if result:
				print("Correct.")
			elif result == None:
				return None
			else:
				print("Try again.")

	def score(self):
		"""
		If assignment is scored, displays student's score as fraction and percentage.

		Args:			
			None
		"""
		if self._scored:
			print("{}/{}: {:.3f}%".format(self._earned, self._possible, self._earned/self._possible*100))
		else:
			print("This notebook is not scored.")