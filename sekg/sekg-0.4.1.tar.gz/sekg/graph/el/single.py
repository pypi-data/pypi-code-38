from sekg.graph.el.base import EntityLinkResult, EntryPointLinker
from sekg.graph.util.name_searcher import KGNameSearcher
from sekg.ir.models.base import DocumentSimModel
from sekg.ir.preprocessor.base import Preprocessor


class SingleEntryPointLinker(EntryPointLinker):

    def __init__(self, preprocessor: Preprocessor, doc_sim_model: DocumentSimModel, kg_name_searcher: KGNameSearcher):
        self.preprocessor = preprocessor
        self.doc_sim_model = doc_sim_model
        self.kg_name_searcher = kg_name_searcher

    def link(self, query, **config):
        result = {}

        keywords = self.preprocessor.extract_words_for_query(query=query)

        for keyword in keywords:
            valid_id_set = self.kg_name_searcher.search_by_keyword(keyword)
            doc_retrieval_result_list = self.doc_sim_model.search(query=query, top_num=1, valid_doc_id_set=valid_id_set)

            if len(doc_retrieval_result_list) > 0:
                doc_retrieval_result = doc_retrieval_result_list[0]

                result[keyword] = EntityLinkResult(mention=keyword, node_id=doc_retrieval_result.doc_id,
                                                   node_name=doc_retrieval_result.doc_name,
                                                   score=doc_retrieval_result.score)

        return result
