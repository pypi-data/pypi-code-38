from pathlib import Path
from unittest import TestCase

from sekg.graph.util.name_searcher import KGNameSearcher
from test.data.definition import ROOT_DIR


class TestAVGNode2VectorModel(TestCase):

    def test_load_name_searcher(self):
        data_dir = Path(ROOT_DIR)
        kg_name_searcher_path = str(data_dir / "JabRef-2.6.v3.namesearcher")
        kg_name_searcher: KGNameSearcher = KGNameSearcher.load(kg_name_searcher_path)
        result = kg_name_searcher.search_by_keyword("pdf")
        print(result)
