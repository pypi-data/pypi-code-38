from pathlib import Path
from unittest import TestCase

from gensim.models.keyedvectors import Word2VecKeyedVectors

from sekg.graph.util.name_searcher import KGNameSearcher
from sekg.ir.doc.wrapper import PreprocessMultiFieldDocumentCollection
from sekg.ir.models.n2v.svm.avg_n2v import AVGNode2VectorModel
from test.data.definition import ROOT_DIR


class TestAVGNode2VectorModel(TestCase):
    def test_load_name_searcher(self):
        data_dir = Path(ROOT_DIR)
        kg_name_searcher_path = str(data_dir / "JabRef-2.6.v3.namesearcher")
        kg_name_searcher: KGNameSearcher = KGNameSearcher.load(kg_name_searcher_path)
        result = kg_name_searcher.search_by_keyword("pdf")
        print(result)

    def test_n2v(self):
        data_dir = Path(ROOT_DIR)
        node2vec_path = str(data_dir / "JabRef-2.6.v3.weight.node2vec")

        full_node2vec_model = Word2VecKeyedVectors.load(node2vec_path)
        vector = full_node2vec_model["1"]
        result = full_node2vec_model.similar_by_vector(vector=vector, topn=10)
        print(result)
        # todo: doc problem
        result = full_node2vec_model.similar_by_vector(vector=vector, topn=None)
        print(result)
        print(type(result))

    def test_train_from_doc_collection_with_preprocessor(self):
        data_dir = Path(ROOT_DIR)

        model_dir = data_dir / "avg_n2v"
        model_dir.mkdir(exist_ok=True, parents=True)

        doc_collection: PreprocessMultiFieldDocumentCollection = PreprocessMultiFieldDocumentCollection.load(
            str(data_dir / "JabRef-2.6.v3.spacy-pre.sub.dc"))
        embedding_size = 100
        kg_name_searcher_path = str(data_dir / "JabRef-2.6.v3.namesearcher")
        pretrain_node2vec_path = str(data_dir / "JabRef-2.6.v3.weight.node2vec")
        graph_data_path = str(data_dir / "JabRef-2.6.v3.graph")

        AVGNode2VectorModel.train(model_dir_path=str(model_dir),
                                  doc_collection=doc_collection,
                                  embedding_size=embedding_size,
                                  pretrain_node2vec_path=pretrain_node2vec_path,
                                  graph_data_path=graph_data_path,
                                  kg_name_searcher_path=kg_name_searcher_path,
                                  )

    def test_search(self):
        model_dir = Path(ROOT_DIR) / "avg_n2v"
        model_dir.mkdir(exist_ok=True, parents=True)
        query = "download pdf produces unsupported filename"
        model = AVGNode2VectorModel.load(str(model_dir))

        result = model.search(top_num=10, query=query)
        for t in result:
            print(t)
