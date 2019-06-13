from unittest import TestCase

from sekg.wiki.search_domain_wiki.search import WikiTool


class TestWikiTool(TestCase):

    def test_wiki_tool(self):
        test_set = set()
        test_set.add("Peer alarm")
        wiki_tool = WikiTool(domain_name_set_to_search=test_set, use_proxies=False, max_candidate_num=5)
        # wiki_tool.start_search()
        # p = "."
        # wiki_tool.save(p)
        # w = WikiTool(domain_name_set_to_search=set(), use_proxies=False, max_candidate_num=5)
        # w.load(p)
        # print(w.title_2_wiki)
        result = wiki_tool.search_title("Peer alarm")
        print(result)
