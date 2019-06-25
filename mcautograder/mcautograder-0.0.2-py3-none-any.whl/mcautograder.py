###############################################
##### Multiple Choice Question Autograder #####
###############################################

import string
import re

def repeat(x, n):
	return [x for _ in range(n)]

class Notebook:
	def __init__(self, tests, scored=False, max_retakes="inf"):
		"""
		Initlaizes multiple choice autograder. Tests should be saved in a
		hidden text file (by appending a period to the filename). The format
		for the tests should be "q_name answer points", e.g.:

			q1_1 1 1
			q1_2 2 0
			q1_3 2 0
			q2_1 4 1
			q2_2 3 2
			q3_1 A 0
			q3_2 D 3
			q3_3 B 2
			
		"""
		with open(tests) as tests_file:
			self._tests = tests_file.readlines()
		if self._tests[-1][-1] != "\n":
			self._tests[-1] += "\n"
		self._questions = [q[:-5] for q in self._tests]

		self._inf_retakes = True
		self._scored = scored

		if self._scored:
			point_by_question = [int(q.split(" ")[2][:-1]) for q in self._tests]
			self._points = {q:p for q, p in zip(self._questions, point_by_question)}
			self._answered = {q:f for q, f in zip(self._questions, repeat(False, len(self._questions)))}
			self._possible = sum(self._points.values())
			self._earned = 0

		if max_retakes != "inf":
			self._inf_retakes = False
			self._retakes = {q:r for q, r in zip(self._questions, repeat(0, len(self._questions)))}
			self._max_retakes = max_retakes

	def _check_answer(self, q_name, answer):
		assert q_name in self._questions, "{} is not in the question bank".format(q_name)
		assert type(answer) in [str, int], "Answer must be a string or integer"
		if type(answer) == str:
			assert len(answer) == 1, "Answer must be of length 1"
		else:
			assert 0 <= answer < 10, "Answer must be a single digit"
		if not self._inf_retakes:
			assert self._retakes[q_name] < self._max_retakes, "No more retakes allowed."

		for test in self._tests:
			if q_name in test[:-4]:
				if test[-4] in string.digits:
					if answer == int(test[-4]):
						if self._scored and not self._answered[q_name]:
							self._answered[q_name] = True
							self._earned += self._points[q_name]
						if not self._inf_retakes:
							self._retakes[q_name] += 1
						return True
				elif answer == test[-4]:
					if self._scored and not self._answered[q_name]:
						self._answered[q_name] = True
						self._earned += self._points[q_name]
					if not self._inf_retakes:
						self._retakes[q_name] += 1
					return True
		return False

	def check(self, q_name, answer):
		result = self._check_answer(q_name, answer)
		if self._scored:
			if result:
				print("Correct. {} points added to your score.".format(self._points[q_name]))
			else:
				print("Try again.")
		else:
			if result:
				print("Correct.")
			else:
				print("Try again.")

	def score(self):
		if self._scored:
			print("{}/{}: {:.3f}%".format(self._earned, self._possible, self._earned/self._possible*100))
		else:
			print("This notebook is not scored.")