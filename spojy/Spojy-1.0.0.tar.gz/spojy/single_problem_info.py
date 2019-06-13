'''
This module returns an array of tags pertaining to a single problem.
'''

import requests
from bs4 import BeautifulSoup


#A filter function to remove some unnecessary tags.
def filter_func(s):
	if s.isspace() == True or len(s) < 1:
		return False
	else:
		return True


def get_tags(problem_url):
	'''
	utility function to fetch all the problem tags from the response page
	'''

	response = requests.get(problem_url)
	response.raise_for_status()

	soup = BeautifulSoup(response.text, "html.parser")
	problem_tag_div = soup.find("div", attrs= {"id" : "problem-tags"})
	
	try:
		links = problem_tag_div.find_all("a")
	except:
		print ("No problem by this name")
		exit(0)

	problem_tags = list(filter(filter_func, problem_tag_div.text.split()))

	return problem_tags


def get_single_problem_tags(problem):
	'''
	Main function which takes the problem name as input and returns an array of tags pertaining to that problem.
	'''

	problem = str(problem)

	problem_url = "https://www.spoj.com/problems/" + problem + "/"

	problem_tags = get_tags(problem_url)

	return problem_tags
