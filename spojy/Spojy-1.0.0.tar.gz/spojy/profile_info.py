'''
This module takes as input:
i>username of the user, whom you want to gather information about.
and returns:
i> the list of problem codes of the solved problems by the user.
ii> the list of problem codes of the unsolved problems by the user.
iii> world_rank of the user
i> total points of the user
'''

import requests
from bs4 import BeautifulSoup
import re

def filter_func(s):
	'''
	A filter function to remove empty or unnecessary problem names.
	'''
	if s.isspace() == True or len(s) < 1:
		return False
	else:
		return True


def get_profile(profile_name):
	'''
	The main function which takes the username as input and 
	returns the rank, the total points and the list of solved and unsolved problems.
	'''

	profile_name = str(profile_name)

	url = "https://www.spoj.com/users/" + profile_name + "/"

	print (url)
	res = requests.get(url)
	res.raise_for_status

	soup = BeautifulSoup(res.content, "html.parser")

	all_tables = soup.find_all("table")

	
	profile_div = soup.find("div", attrs={"id" : "user-profile-left"})

	#to make sure that the username entered is a valid username	
	try:
		profile_paras = profile_div.find_all('p')
	except:
		print ("There's no profile by this name")
		exit(0)

	world_rank_para = profile_paras[2].text

	rank_pat = re.compile(r'#(\d)+')
	point_pat = re.compile(r'\((.)*\)')

	rank = rank_pat.search(world_rank_para).group(0)
	point_line = point_pat.search(world_rank_para).group(0)
	points = point_line.split()[0][1:]


	for i in range(2):
		if i == 0:
			solved_problems_unfiltered = all_tables[i].text.split('\n')
			solved_problems = list(filter(filter_func, solved_problems_unfiltered))

		else:
			unsolved_problems_unfiltered = all_tables[i].text.split('\n')
			unsolved_problems = list(filter(filter_func, unsolved_problems_unfiltered))

	return solved_problems, unsolved_problems,rank,points
