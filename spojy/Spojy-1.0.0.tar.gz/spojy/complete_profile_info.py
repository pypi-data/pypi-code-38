'''
This module takes as input:
i> the username of the profile that you want to gather data about.
ii> network proxy (optional)
iii> the maximum number of asynchronous that can be sent at a time,this defaults to 77

and returns the following:
i> world rank of the user.
ii> total points of the user.
iii> a dictionary with languages used as the key and the number of problems solved with that language as the value.
iv> a dictionary with problem tag as the key and the number of problems with that problem tag as value. 

'''


from profile_info import get_profile
from solution_info import get_langs
from problem_info import get_tags

def get_complete_profile_info(profile_name,proxy_used="",max_async_requests=77):
	'''
	Takes proxy(optional) and maximum number of asynchonous requests as input
	returns the above mentioned properties
	'''

	solved_list, unsolved_list,world_rank, points = get_profile(profile_name)


	#to get the languages used by the user to solve the problems
	st = 0
	ed = max_async_requests

	while st < len(solved_list):
		langs = get_langs(solved_list[st:ed],profile_name)

		st = ed
		ed = min(ed + max_async_requests,len(solved_list))

	#to get the tags of the problems that the user has solved
	st = 0
	ed = max_async_requests

	while st < len(solved_list):
		tags = get_tags(solved_list[st:ed])

		st = ed
		ed = min(ed+max_async_requests, len(solved_list))


	'''the languages that the api will consider, will add some more in future
	I have clustered some versions of the same language to the core language, like CPP14, C++4.3.2, CPP all map to CPP
	'''
	langs_used = {
		"ADA" 	: 0,
		"CPP" 	: 0,
		"C"   	: 0,
		"PYTHON": 0,
		"JAVA"  : 0,
		"PASCAL": 0,
		"HASKEL": 0,
		"PERL"  : 0,
		"C#"    : 0
	}

	'''the topics that the api will consider, again will add some more in future
	Again, problem tags are user generated and as such there are various versions of the same topic
	I have grouped all these sub-topics to the same core topic
	'''

	tags_solved = {
		"dp" 	 		 : 0,
		"greedy" 		 : 0,
		"math" 	 		 : 0,
		"graph"	 		 : 0,
		"adhoc"  		 : 0,
		"sorting"		 : 0,
		"tree"	 		 : 0,
		"datastructures" : 0,
		"recursion"		 : 0
	}



	#mapping the languages taken from spoj to the list of languages supported by the api.
	for lang in langs.keys():
		if lang == "4.3.2" or "CPP" in lang:
			langs_used["CPP"] += langs[lang]

		elif "PY" in lang:
			langs_used["PYTHON"] += langs[lang]

		elif "JAVA" in lang:
			langs_used["JAVA"] += langs[lang]

		elif "C#" in lang:
			langs_used["C#"] += langs[lang]

		elif "C" in lang:
			langs_used["C"] += langs[lang]

		elif "ADA" in lang:
			langs_used["ADA"] += langs[lang]

		elif "PAS" in lang:
			langs_used["PASCAL"] += langs[lang]

		elif "HAS" in lang:
			langs_used["HASKEL"] += langs[lang]

		elif "PERL" in lang:
			langs_used["PERL"] += langs[lang]


	for tag in tags.keys():

		if "dynamic" in tag:
			tags_solved["dp"] += tags[tag]

		elif "greedy" in tag or "sweep" in tag:
			tags_solved["greedy"] += tags[tag]

		elif "math" in tag or "combinatorics" in tag or "number-theory" in tag or "gcd" in tag or "number" in tag or "geometry" in tag:
			tags_solved["math"] += tags[tag]

		elif "lis" in tag or "lds" in tag:
			tags_solved["dp"] += tags[tag]
			tags_solved["greedy"] += tags[tag]


		elif "graph" in tag or "bfs" in tag or "dfs" in tag or "shortest-path" in tag or "dijkstra" in tag or "mst" in tag:
			tags_solved["graph"] += tags[tag]

		elif "sorting" in tag:
			tags_solved["sorting"] += tags[tag]

		elif "datastructure" in tag or  "data-structure" in tag or "stack" in tag or "queue" in tag:
			tags_solved["datastructures"] += tags[tag]


		elif "adhoc" in tag or "map" in tag or "set" in tag :
			tags_solved["adhoc"] += tags[tag]

		elif "tree" in tag or "trie" in tag:
			tags_solved["tree"] += tags[tag]

		elif "recursion" in tag or "backtracking" in tag:
			tags_solved["recursion"] += tags[tag]

	return world_rank, points, langs_used, tags_solved
