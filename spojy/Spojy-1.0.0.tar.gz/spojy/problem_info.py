''''
This module takes as input:
i> a list of problem urls
ii> network proxy (optional)
and returns a dictionary with the various problem tag as the key and the number of times each key occured as the
value. This module implements asynchronous requests communication to further
enhance performance.
'''

from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession


def filter_func(s):
	'''
	A filter function to remove some unnecessary tags.
	'''

	if s.isspace() == True or len(s) < 1:
		return False
	else:
		return True


def response_handling(responses):
	'''
	extracts the problem tags from the individual problems in conjunction with the dunction run
	'''
	for response in responses:
		soup = BeautifulSoup(response, "html.parser")
		problem_tag_div = soup.find("div", attrs= {"id" : "problem-tags"})

		links = problem_tag_div.find_all("a")

		problem_tags = list(filter(filter_func, problem_tag_div.text.split()))

		for tag in problem_tags:
			tags[tag] = tags.get(tag,0) + 1

		


async def fetch(url, session):
    async with session.get(url, proxy=proxy_used) as response:
        return await response.read()

async def run(urls):
	'''
	used for the asynchronous request routine in part with asyncio
	'''

	tasks = []

	async with ClientSession() as session:
		for url in urls:
			task = asyncio.ensure_future(fetch(url, session))
			tasks.append(task)

		responses = await asyncio.gather(*tasks)

	response_handling(responses)


def get_tags(problem_list, proxy=""):
	problem_list = list(map(str,problem_list))

	urls = ["https://www.spoj.com/problems/" + problem + "/" for problem in problem_list]
	proxy_used = proxy

	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future(run(urls))


	loop.run_until_complete(future)


	return tags
