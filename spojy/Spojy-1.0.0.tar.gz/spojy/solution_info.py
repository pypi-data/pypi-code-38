''''
This module takes as input:
i> a list of problem urls
ii> username of the user that submitted the solutions to the problems in the above list
iii> network proxy (optional)
and returns a dictionary with the various programming languages as the key and the number of times they were used as the
value. This module implements asynchronous requests communication to further
enhance performance.
'''

from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession

langs_used = {}
proxy_used = ""


def filter_func(s):
	'''
	A filter function to remove some broken/wrong language names used.
	'''

	if s.isspace() == True or len(s) < 1:
		return False
	else:
		return True


def response_handling(responses):
	'''
	used for the asynchronous request handling in part with asyncio
	'''

	for response in responses:
		soup = BeautifulSoup(response, "html.parser")
		acc = soup.find_all("tr", attrs={"class" : "kol1"})

		for solution in acc:
			sol = list(filter(filter_func,solution.text.split()))

			lang = sol[-1]
			langs_used[lang] = langs_used.get(lang,0) + 1


async def fetch(url, session):
    async with session.get(url, proxy=proxy_used) as response:
        return await response.read()

async def run(urls):
    tasks = []

    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)


    response_handling(responses)


def get_langs(problem_list,user,proxy=""):
	'''
	Main function which takes the input as problem list and an optional proxy
	It also initialises proxy_used if the user provides any proxy 
	'''

	
	problem_list = list(map(str,problem_list))
	user = str(user)

	urls = ["https://www.spoj.com/status/" + problem + "," + user + "/" for problem in problem_list]
	proxy_used = proxy	
	
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future(run(urls))


	loop.run_until_complete(future)

	return langs_used
