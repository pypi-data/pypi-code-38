###############################################
##### Multiple Choice Question Autograder #####
###############################################

import string
import re
import runpy

def repeat(x, n):
	"""
	Returns a list of a given value repeated a given number of times

	Args:
		x - value to repeat
		n - number of repetitions
	"""
	return [x for _ in range(n)]

class Notebook:
	"""Multiple choice question autograder for Jupyter Notebook"""

	def __init__(self, tests, scored=False, max_retakes="inf"):
		"""
		Initlaizes multiple choice autograder.

		Args:
			tests       - relative filepath to tests file
			scored      - whether or not the assignment is scored; default `False`
			max_retakes - if `"inf"`, no maximum retakes; maximum number of retakes
						  allowed; deault `"inf"`
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
		if max_retakes != "inf":
			assert max_retakes > 0 and type(max_retakes) == int, "max_retakes must be a positive integer"
			self._inf_retakes = False
			self._retakes = {identifier : zero for identifier, zero in zip(
				self._identifiers, 
				repeat(0, len(self._identifiers))
			)}
			self._max_retakes = max_retakes

	def _check_answer(self, identifier, answer):
		"""
		Checks whether or not answer is correct; returns boolean

		Args:
			identifier - question identifier
			answer     - student answer
		"""
		assert identifier in self._identifiers, "{} is not in the question bank".format(identifier)
		assert type(answer) in [str, int], "Answer must be a string or integer"
		if type(answer) == str:
			assert len(answer) == 1, "Answer must be of length 1"
		else:
			assert 0 <= answer < 10, "Answer must be a single digit"
		if not self._inf_retakes:
			assert self._retakes[identifier] < self._max_retakes, "No more retakes allowed."

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
		Visible wrapper for _check_answer to print output based on whether or not student's
		answer is correct

		Args:
			identifier - question identifier
			answer - student's answer
		"""
		result = self._check_answer(identifier, answer)
		if self._scored:
			if result:
				print("Correct. {} points added to your score.".format(self._points[identifier]))
			else:
				print("Try again.")
		else:
			if result:
				print("Correct.")
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