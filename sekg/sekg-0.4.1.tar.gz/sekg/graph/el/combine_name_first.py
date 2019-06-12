import math
import networkx as nx
from gensim.models.keyedvectors import Word2VecKeyedVectors
from nltk import WordNetLemmatizer

from sekg.constant.code import CodeEntityCategory
from sekg.constant.constant import OperationConstance, DomainConstant
from sekg.graph.el.base import EntryPointLinker, EntityLinkResult
from sekg.graph.exporter.graph_data import GraphData
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


class NFGlobalEntryPointLinker(EntryPointLinker):
    DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT = 3

    def __init__(self, preprocessor: Preprocessor,
                 doc_sim_model: DocumentSimModel,
                 kg_name_searcher: KGNameSearcher,
                 graph2vecModel: Word2VecKeyedVectors,
                 graph_data: GraphData,
                 ):
        self.preprocessor = preprocessor
        self.doc_sim_model = doc_sim_model
        self.graph2vecModel = graph2vecModel
        self.kg_name_searcher = kg_name_searcher
        self.graph_data = graph_data
        self.lemmatizer = WordNetLemmatizer()
        # to start the util
        self.lemmatizer.lemmatize(word="test")

    def score_full_name(self, candidate_node_ids, keywords, name_score_map, original_query):
        new_keywords = set([])
        for keyword in keywords:
            new_keywords.add(keyword.lower())
        keywords = new_keywords
        clean_query_string = " ".join(list(keywords))

        for node_id in candidate_node_ids:
            if node_id not in name_score_map:
                name_score_map[node_id] = self.compute_name_score_for_one_node(keywords, clean_query_string, node_id,
                                                                               original_query)
        return name_score_map

    def compute_name_score_for_one_node(self, keywords, query_string, node_id, original_query):
        full_names = self.kg_name_searcher.get_full_names(node_id)
        score_list = []
        for full_name in full_names:
            full_name = full_name.lower()
            name_set = set(full_name.split(" "))
            word_count = len(name_set)
            token_score = 1.0 * len(name_set & keywords) / word_count

            appearing = 0.0
            for word in name_set:
                if word in query_string or word in original_query:
                    appearing += 1

            appearing_score = appearing / word_count
            score_list.append(appearing_score)

            score_list.append(token_score)

        if score_list:
            return max(score_list)
        return 0.0

    def select_candidates_for_keyword(self, query, keywords, candidate_num):

        keyword_to_candidate_list_map = {}
        name_score_map = {}

        for keyword in keywords:
            doc_retrieval_result_list = self.get_candidate_for_keyword(candidate_num, keyword, query, name_score_map,
                                                                       keywords)
            if len(doc_retrieval_result_list) > 0:
                keyword_to_candidate_list_map[keyword] = doc_retrieval_result_list

        return keyword_to_candidate_list_map


    def link(self, query, candidate_num=DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT):
        selector = BestSeqSelector()
        keywords = self.preprocessor.extract_words_for_query(query=query)

        doc_id_2_doc_retrieval_result_map = {}

        keyword_to_candidate_list_map = self.select_candidates_for_keyword(query=query, keywords=keywords,
                                                                           candidate_num=candidate_num)

        for keyword, doc_retrieval_result_list in keyword_to_candidate_list_map.items():

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

        if len(keywords) == 1:
            rate = 0.0
        else:
            rate = 2.0 / (len(keywords) - 1.0)

        for start_id in candidate_ids:
            start_vector = vector_map[start_id]
            sim_vector = self.graph2vecModel.wv.cosine_similarities(start_vector, all_vectors)

            for end_id, score in zip(candidate_ids, sim_vector):
                # print("pair score =%r %r %r" % (start_id, end_id, score))
                selector.add_pair_score(start_id=start_id, end_id=end_id, score=score * rate)

        best_linking_result = selector.search_best_combination()

        result = {}
        for keyword, node_id in best_linking_result.items():
            doc_retrieval_result = doc_id_2_doc_retrieval_result_map[node_id]

            result[keyword] = EntityLinkResult(mention=keyword, node_id=node_id,
                                               node_name=doc_retrieval_result.doc_name,
                                               score=doc_retrieval_result.score)

        return result

    def get_candidate_for_keyword(self, candidate_num, keyword, query, name_score_map, keywords):

        candidate_doc_result_list = []

        full_name_match_id_set = self.kg_name_searcher.search_by_full_name(keyword.lower())
        keyword_match_id_set = self.kg_name_searcher.search_by_keyword(keyword.lower())

        new_keyword = self.lemmatizer.lemmatize(word=keyword, pos="v")
        new_keyword = new_keyword.lower()

        extra_veb_keywords = set([])
        if new_keyword != keyword:
            t = self.kg_name_searcher.search_by_full_name(new_keyword)
            full_name_match_id_set = full_name_match_id_set | t
            extra_veb_keywords = extra_veb_keywords | t
            t = self.kg_name_searcher.search_by_keyword(new_keyword)
            keyword_match_id_set = keyword_match_id_set | t
            extra_veb_keywords = extra_veb_keywords | t

        ## todo: this is only for code kg
        operation_ids = self.graph_data.get_node_ids_by_label(OperationConstance.LABEL_OPERATION)
        domain_term_ids = self.graph_data.get_node_ids_by_label(DomainConstant.LABEL_DOMAIN_TERM)

        method_ids = self.graph_data.get_node_ids_by_label(
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD))
        method_ids = method_ids | self.graph_data.get_node_ids_by_label(
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD))

        class_field_ids = self.graph_data.get_node_ids_by_label(
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_FIELD_OF_CLASS))

        if len(operation_ids & full_name_match_id_set) > 0 or len(domain_term_ids & full_name_match_id_set) > 0:
            full_name_match_id_set = full_name_match_id_set - method_ids

            keyword_match_id_set = keyword_match_id_set - (full_name_match_id_set & method_ids)

        if len(class_field_ids & full_name_match_id_set) > 0:
            full_name_match_id_set = full_name_match_id_set - class_field_ids

            keyword_match_id_set = keyword_match_id_set - (full_name_match_id_set & class_field_ids)

        chosen_ids = set([])

        large_candidate_num = candidate_num + 5
        if len(full_name_match_id_set) > 0:
            doc_retrieval_result_list = self.doc_sim_model.search(query=query, top_num=large_candidate_num,
                                                                  valid_doc_id_set=full_name_match_id_set)

            for doc in doc_retrieval_result_list:
                if doc.doc_id not in chosen_ids:
                    chosen_ids.add(doc.doc_id)
                    candidate_doc_result_list.append(doc)

        if len(keyword_match_id_set) > 0:
            doc_retrieval_result_list = self.doc_sim_model.search(query=query, top_num=large_candidate_num,
                                                                  valid_doc_id_set=keyword_match_id_set)

            for doc in doc_retrieval_result_list:
                if doc.doc_id not in chosen_ids:
                    chosen_ids.add(doc.doc_id)
                    candidate_doc_result_list.append(doc)

        self.score_full_name(candidate_node_ids=chosen_ids, keywords=keywords, name_score_map=name_score_map,
                             original_query=query)

        for candidate_doc in candidate_doc_result_list:
            if candidate_doc.doc_id in extra_veb_keywords:
                candidate_doc.score += 1.0 / (math.log10(len(extra_veb_keywords)) + 1)

            candidate_doc.extra_info["name_score"] = name_score_map[candidate_doc.doc_id]
            candidate_doc.extra_info["doc_score"] = candidate_doc.score
            candidate_doc.score = candidate_doc.extra_info["name_score"] + candidate_doc.extra_info["doc_score"]

        candidate_doc_result_list = sorted(candidate_doc_result_list, key=lambda candidate_doc: candidate_doc.score,
                                           reverse=True)

        # for t in candidate_doc_result_list:
        #     print("name score=%r doc_score %r %r %r" % (
        #         t.extra_info["name_score"], t.extra_info["doc_score"], t, self.graph_data.get_node_info_dict(t.doc_id)))
        # print("--------")
        if len(candidate_doc_result_list) >= 2:
            if candidate_doc_result_list[0].score / candidate_doc_result_list[1].score > 1.5:
                return [candidate_doc_result_list[0]]

        return candidate_doc_result_list[:candidate_num]
