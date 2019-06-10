import networkx as nx
from gensim.models.keyedvectors import Word2VecKeyedVectors

from sekg.graph.el.base import EntryPointLinker, EntityLinkResult
from sekg.graph.util.name_searcher import KGNameSearcher
from sekg.ir.models.base import DocumentSimModel
from sekg.ir.preprocessor.base import Preprocessor


class BestSeqSelector:

    def __init__(self, ):
        self.keyword2candidate_map = {}
        self.G = nx.Graph()
        self.best_selection = []
        self.best_score = 0.0

    def get_candidate_ids(self):
        result = set([])
        for keyword, ids in self.keyword2candidate_map.items():
            result = result | ids
        return list(result)

    def get_keyword_list(self):
        return list(self.keyword2candidate_map.keys())

    def add_candidate_for_keyword(self, keyword, candidate_node_id, score):
        if keyword not in self.keyword2candidate_map:
            self.keyword2candidate_map[keyword] = set([])

        self.keyword2candidate_map[keyword].add(candidate_node_id)
        self.add_candidate_entity_score(node_id=candidate_node_id, score=score)

    def add_candidate_entity_score(self, node_id, score):
        self.G.add_node(node_id, score=score)

    def add_pair_score(self, start_id, end_id, score):
        self.G.add_edge(start_id, end_id, score=score)

    def search_best_combination(self):
        self.chosen([], score=0.0, current_chosen_keyword_index=0)

        return self.get_best_selection()

    def get_best_score(self):
        return self.best_score

    def get_best_selection(self):
        keyword_list = self.get_keyword_list()
        result = {}
        for keyword, node_id in zip(keyword_list, self.best_selection):
            result[keyword] = node_id
        return result

    def chosen(self, history_chosen, score, current_chosen_keyword_index):
        if current_chosen_keyword_index >= len(self.get_keyword_list()):
            if self.best_score < score:
                self.best_score = score
                self.best_selection = history_chosen
            else:
                return
        else:
            current_keyword = self.get_keyword_list()[current_chosen_keyword_index]

            candidate_ids = self.keyword2candidate_map[current_keyword]

            for candidate_entity_id in candidate_ids:
                extra_score = self.G.nodes[candidate_entity_id]["score"]
                for history_chosen_entity_id in history_chosen:
                    extra_score += self.G[candidate_entity_id][history_chosen_entity_id]["score"]

                self.chosen(history_chosen + [candidate_entity_id], score=score + extra_score,
                            current_chosen_keyword_index=current_chosen_keyword_index + 1)


class GlobalEntryPointLinker(EntryPointLinker):
    DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT = 3

    def __init__(self, preprocessor: Preprocessor, doc_sim_model: DocumentSimModel, kg_name_searcher: KGNameSearcher,
                 graph2vecModel: Word2VecKeyedVectors,
                 ):
        self.preprocessor = preprocessor
        self.doc_sim_model = doc_sim_model
        self.graph2vecModel = graph2vecModel
        self.kg_name_searcher = kg_name_searcher

    def link(self, query, candidate_num=DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT):
        selector = BestSeqSelector()

        keywords = self.preprocessor.extract_words_for_query(query=query)

        keyword_2_candidate_ids_map = {}
        doc_id_2_doc_retrieval_result_map = {}
        for keyword in keywords:
            valid_id_set = self.kg_name_searcher.search_by_keyword(keyword)
            doc_retrieval_result_list = self.doc_sim_model.search(query=query, top_num=candidate_num,
                                                                  valid_doc_id_set=valid_id_set)

            if len(doc_retrieval_result_list) > 0:
                keyword_2_candidate_ids_map[keyword] = doc_retrieval_result_list
            for doc_retrieval_result in doc_retrieval_result_list:
                # print("candidate keyword=%s %r" % (keyword, doc_retrieval_result))

                selector.add_candidate_for_keyword(keyword=keyword,
                                                   candidate_node_id=doc_retrieval_result.doc_id,
                                                   score=doc_retrieval_result.score)
                doc_id_2_doc_retrieval_result_map[doc_retrieval_result.doc_id] = doc_retrieval_result
        candidate_ids = selector.get_candidate_ids()

        vector_map = {}

        all_vectors = []

        for candidate_id in candidate_ids:
            vector_map[candidate_id] = self.graph2vecModel.wv[str(candidate_id)]
            all_vectors.append(vector_map[candidate_id])

        for start_id in candidate_ids:
            start_vector = vector_map[start_id]
            sim_vector = self.graph2vecModel.wv.cosine_similarities(start_vector, all_vectors)

            for end_id, score in zip(candidate_ids, sim_vector):
                selector.add_pair_score(start_id=start_id, end_id=end_id, score=score)
                # print("pair score =%r %r %r" % (start_id, end_id, score))

        best_linking_result = selector.search_best_combination()

        result = {}
        for keyword, node_id in best_linking_result.items():
            doc_retrieval_result = doc_id_2_doc_retrieval_result_map[node_id]

            result[keyword] = EntityLinkResult(mention=keyword, node_id=node_id,
                                               node_name=doc_retrieval_result.doc_name,
                                               score=doc_retrieval_result.score)

        return result
