"""Implements the hypergraph conversation model from
http://www.cs.cornell.edu/~cristian/Patterns_of_participant_interactions.html.

Example usage: hypergraph creation and feature extraction, visualization and interpretation on a subsample of Reddit.
(https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/hyperconvo/demo.ipynb)
"""

import itertools
from collections import defaultdict
import numpy as np
import scipy.stats
from .transformer import Transformer
from typing import Tuple, List, Dict, Optional, Hashable, Collection
from .model import Corpus, Utterance

class Hypergraph:
    """
    Represents a hypergraph, consisting of nodes, directed edges,
    hypernodes (each of which is a set of nodes) and hyperedges (directed edges
    from hypernodes to hypernodes). Contains functionality to extract motifs
    from hypergraphs (Fig 2 of
    http://www.cs.cornell.edu/~cristian/Patterns_of_participant_interactions.html)
    """
    def __init__(self):
        # public
        self.nodes = dict()
        self.hypernodes = dict()

        # private
        self.adj_out = dict()  # out edges for each (hyper)node
        self.adj_in = dict()   # in edges for each (hyper)node

    def add_node(self, u: Hashable, info: Optional[Dict]=None) -> None:
        self.nodes[u] = info if info is not None else dict()
        self.adj_out[u] = dict()
        self.adj_in[u] = dict()

    def add_hypernode(self, name: Hashable,
                      nodes: Collection[Hashable],
                      info: Optional[dict]=None) -> None:
        self.hypernodes[name] = set(nodes)
        self.adj_out[name] = dict()
        self.adj_in[name] = dict()

    # edge or hyperedge
    def add_edge(self, u: Hashable, v: Hashable, info: Optional[dict]=None) -> None:
        assert u in self.nodes or u in self.hypernodes
        assert v in self.nodes or v in self.hypernodes
        if u in self.hypernodes and v in self.hypernodes:
            assert len(info.keys()) > 0
        if v not in self.adj_out[u]:
            self.adj_out[u][v] = []
        if u not in self.adj_in[v]:
            self.adj_in[v][u] = []
        if info is None: info = dict()
        self.adj_out[u][v].append(info)
        self.adj_in[v][u].append(info)

    def edges(self) -> Dict[Tuple[Hashable, Hashable], List]:
        return dict(((u, v), lst) for u, d in self.adj_out.items()
                           for v, lst in d.items())

    def outgoing_nodes(self, u: Hashable) -> Dict[Hashable, List]:
        assert u in self.adj_out
        return dict((v, lst) for v, lst in self.adj_out[u].items()
                           if v in self.nodes)

    def outgoing_hypernodes(self, u) -> Dict[Hashable, List]:
        assert u in self.adj_out
        return dict((v, lst) for v, lst in self.adj_out[u].items()
                           if v in self.hypernodes)

    def incoming_nodes(self, v: Hashable) -> Dict[Hashable, List]:
        assert v in self.adj_in
        return dict((u, lst) for u, lst in self.adj_in[v].items() if u in
                           self.nodes)

    def incoming_hypernodes(self, v: Hashable) -> Dict[Hashable, List]:
        assert v in self.adj_in
        return dict((u, lst) for u, lst in self.adj_in[v].items() if u in
                           self.hypernodes)

    def outdegrees(self, from_hyper: bool=False, to_hyper: bool=False) -> List[int]:
        return [sum([len(l) for v, l in self.adj_out[u].items() if v in
                     (self.hypernodes if to_hyper else self.nodes)]) for u in
                (self.hypernodes if from_hyper else self.nodes)]

    def indegrees(self, from_hyper: bool=False, to_hyper: bool=False) -> List[int]:
        return [sum([len(l) for u, l in self.adj_in[v].items() if u in
                     (self.hypernodes if from_hyper else self.nodes)]) for v in
                (self.hypernodes if to_hyper else self.nodes)]

    def reciprocity_motifs(self) -> List[Tuple]:
        """
        :return: List of tuples of form (C1, c1, c2, C1->c2, c2->c1) as in paper
        """
        motifs = []
        for C1, c1_nodes in self.hypernodes.items():
            for c1 in c1_nodes:
                motifs += [(C1, c1, c2, e1, e2) for c2 in self.adj_in[c1] if
                           c2 in self.nodes and c2 in self.adj_out[C1]
                           for e1 in self.adj_out[C1][c2]
                           for e2 in self.adj_out[c2][c1]]
        return motifs

    def external_reciprocity_motifs(self) -> List[Tuple]:
        """
        :return: List of tuples of form (C3, c2, c1, C3->c2, c2->c1) as in paper
        """
        motifs = []
        for C3 in self.hypernodes:
            for c2 in self.adj_out[C3]:
                if c2 in self.nodes:
                    motifs += [(C3, c2, c1, e1, e2) for c1 in
                               set(self.adj_out[c2].keys()) - self.hypernodes[C3]
                               if c1 in self.nodes
                               for e1 in self.adj_out[C3][c2]
                               for e2 in self.adj_out[c2][c1]]
        return motifs

    def dyadic_interaction_motifs(self) -> List[Tuple]:
        """
        :return: List of tuples of form (C1, C2, C1->C2, C2->C1) as in paper
        """

        motifs = []
        for C1 in self.hypernodes:
            motifs += [(C1, C2, e1, e2) for C2 in self.adj_out[C1] if C2 in
                       self.hypernodes and C1 in self.adj_out[C2]
                       for e1 in self.adj_out[C1][C2]
                       for e2 in self.adj_out[C2][C1]]
        return motifs

    def incoming_triad_motifs(self) -> List[Tuple]:
        """
        :return: List of tuples of form (C1, C2, C3, C2->C1, C3->C1) as in paper
        """
        motifs = []
        for C1 in self.hypernodes:
            incoming = list(self.adj_in[C1].keys())
            motifs += [(C1, C2, C3, e1, e2) for C2, C3 in
                       itertools.combinations(incoming, 2)
                       for e1 in self.adj_out[C2][C1]
                       for e2 in self.adj_out[C3][C1]]
        return motifs

    def outgoing_triad_motifs(self) -> List[Tuple]:
        """
        :return: List of tuples of form (C1, C2, C3, C1->C2, C1->C3) as in paper
        """
        motifs = []
        for C1 in self.hypernodes:
            outgoing = list(self.adj_out[C1].keys())
            motifs += [(C1, C2, C3, e1, e2) for C2, C3 in
                       itertools.combinations(outgoing, 2)
                       for e1 in self.adj_out[C1][C2]
                       for e2 in self.adj_out[C1][C3]]
        return motifs

class HyperConvo(Transformer):
    """
    Encapsulates computation of hypergraph features for a particular
    corpus.

    fit_transform() retrieves features from the corpus conversational
    threads using retrieve_feats, and stores it in the corpus's conversations'
    meta field under the key "hyperconvo"

    Either use the features directly, or use the other transformers, threadEmbedder (https://zissou.infosci.cornell.edu/socialkit/documentation/threadEmbedder.html)
    or communityEmbedder (https://zissou.infosci.cornell.edu/socialkit/documentation/communityEmbedder.html) to embed communities or threads respectively in a low-dimensional
    space for further analysis or visualization.

    As features, we compute the degree distribution statistics from Table 4 of
    http://www.cs.cornell.edu/~cristian/Patterns_of_participant_interactions.html,
    for both a whole conversation and its midthread, and for indegree and
    outdegree distributions of C->C, C->c and c->c edges, as in the paper.
    We also compute the presence and count of each motif type specified in Fig 2.
    However, we do not include features making use of reaction edges, due to our
    inability to release the Facebook data used in the paper (which reaction
    edges are most naturally suited for). In particular, we do not include edge
    distribution statistics from Table 4, as these rely on the presence of
    reaction edges. We hope to implement a more general version of these
    reaction features in an upcoming release.

    :param prefix_len: Length (in number of utterances) of each thread to
            consider when constructing its hypergraph
    :param min_thread_len: Only consider threads of at least this length
    :param include_root: True if root utterance should be included in the utterance thread,
    False otherwise, i.e. thread begins from top level comment. (Affects prefix_len and min_thread_len counts.)
    (If include_root is True, then each Conversation will have metadata for one thread, otherwise each Conversation
    will have metadata for multiple threads - equal to the number of top-level comments.)
    """

    def __init__(self, prefix_len: int=10, min_thread_len: int=10, include_root: bool=True):
        self.prefix_len = prefix_len
        self.min_thread_len = min_thread_len
        self.include_root = include_root

    def transform(self, corpus: Corpus) -> Corpus:
        """
        Same as fit_transform()
        """
        return self.fit_transform(corpus)

    def fit_transform(self, corpus: Corpus) -> Corpus:
        """
        fit_transform() retrieves features from the corpus conversational
        threads using retrieve_feats()
        :param corpus: Corpus object to retrieve feature information from
        :return: corpus with conversations having a new meta field "hyperconvo" containing
                the stats generated by retrieve_feats(). Each conversation's metadata then contains
                the stats for the thread(s) it contains
        """
        feats = HyperConvo.retrieve_feats(corpus,
                                          prefix_len=self.prefix_len,
                                          min_thread_len=self.min_thread_len,
                                          include_root=self.include_root)
        if self.include_root: # threads start at root (post)
            for root_id in feats.keys():
                convo = corpus.get_conversation(root_id)
                convo.add_meta("hyperconvo", {root_id: feats[root_id]})
        else: # threads start at top-level-comment
            # Construct top-level-comment to root mapping
            tlc_to_root_mapping = dict() # tlc = top level comment
            threads = corpus.utterance_threads(prefix_len=self.prefix_len, include_root=False)

            root_to_tlc = dict()
            for tlc_id, utts in threads.items():
                thread_root = threads[tlc_id][tlc_id].root
                if thread_root in root_to_tlc:
                    root_to_tlc[thread_root][tlc_id] = feats[tlc_id]
                else:
                    root_to_tlc[thread_root] = {tlc_id: feats[tlc_id]}

            for root_id in root_to_tlc:
                convo = corpus.get_conversation(root_id)
                convo.add_meta("hyperconvo", root_to_tlc[root_id])

        return corpus

    @staticmethod
    def _make_hypergraph(corpus: Optional[Corpus]=None,
                         uts: Optional[Dict[Hashable, Utterance]]=None,
                         exclude_id: Hashable=None) -> Hypergraph:
        """
        Construct a Hypergraph from all the utterances of a Corpus, or a specified subset of utterances
        :param corpus: A Corpus to extract utterances from
        :param uts: Subset of utterances to construct a Hypergraph from
        :param exclude_id: id of utterance to exclude from Hypergraph construction
        :return: Hypergraph object
        """
        if uts is None:
            if corpus is None:
                raise RuntimeError("fit_transform() helper method _make_hypergraph()"
                                   "has no valid corpus / utterances input")
            uts = {utt.id: utt for utt in corpus.iter_utterances()}

        G = Hypergraph()
        username_to_utt_ids = dict()
        reply_edges = []
        speaker_to_reply_tos = defaultdict(list)
        speaker_target_pairs = set()
        # nodes
        for ut in sorted(uts.values(), key=lambda h: h.get("timestamp")):
            if ut.get("id") != exclude_id:
                if ut.get("user") not in username_to_utt_ids:
                    username_to_utt_ids[ut.get("user")] = set()
                username_to_utt_ids[ut.get("user")].add(ut.get("id"))
                if ut.get("reply_to") is not None and ut.get("reply_to") in uts \
                        and ut.get("reply_to") != exclude_id:
                    reply_edges.append((ut.get("id"), ut.get("reply_to")))
                    speaker_to_reply_tos[ut.user].append(ut.get("reply_to"))
                    speaker_target_pairs.add((ut.user, uts[ut.get("reply_to")].user, ut.get("timestamp")))
                G.add_node(ut.get("id"), info=ut.__dict__)
        # hypernodes
        for u, ids in username_to_utt_ids.items():
            G.add_hypernode(u, ids, info=u.meta)
        # reply edges
        for u, v in reply_edges:
            # print("ADDING TIMESTAMP")
            G.add_edge(u, v)
        # user to utterance response edges
        for u, reply_tos in speaker_to_reply_tos.items():
            for reply_to in reply_tos:
                G.add_edge(u, reply_to)
        # user to user response edges
        for u, v, timestamp in speaker_target_pairs:
            G.add_edge(u, v, {'timestamp': timestamp})
        return G

    @staticmethod
    def _node_type_name(b: bool) -> str:
        """
        Helper method to get node type name (C or c)
        :param b: Bool, where True indicates node is a Hypernode
        :return: "C" if True, "c" if False
        """
        return "C" if b else "c"

    @staticmethod
    def _degree_feats(uts: Optional[Dict[Hashable, Utterance]]=None,
                      G: Optional[Hypergraph]=None,
                      name_ext: str="",
                      exclude_id: Optional[Hashable]=None) -> Dict:
        """
        Helper method for retrieve_feats().
        Generate statistics on degree-related features in a Hypergraph (G), or a Hypergraph
        constructed from provided utterances (uts)
        :param uts: utterances to construct Hypergraph from
        :param G: Hypergraph to calculate degree features statistics from
        :param name_ext: Suffix to append to feature name
        :param exclude_id: id of utterance to exclude from Hypergraph construction
        :return: A stats dictionary, i.e. a dictionary of feature names to feature values. For degree-related
            features specifically.
        """
        assert uts is None or G is None
        if G is None:
            G = HyperConvo._make_hypergraph(uts, exclude_id=exclude_id)

        stat_funcs = {
            "max": np.max,
            "argmax": np.argmax,
            "norm.max": lambda l: np.max(l) / np.sum(l),
            "2nd-largest": lambda l: np.partition(l, -2)[-2] if len(l) > 1
            else np.nan,
            "2nd-argmax": lambda l: (-l).argsort()[1] if len(l) > 1 else np.nan,
            "norm.2nd-largest": lambda l: np.partition(l, -2)[-2] / np.sum(l)
            if len(l) > 1 else np.nan,
            "mean": np.mean,
            "mean-nonzero": lambda l: np.mean(l[l != 0]),
            "prop-nonzero": lambda l: np.mean(l != 0),
            "prop-multiple": lambda l: np.mean(l[l != 0] > 1),
            "entropy": scipy.stats.entropy,
            "2nd-largest / max": lambda l: np.partition(l, -2)[-2] / np.max(l)
            if len(l) > 1 else np.nan
        }

        stats = {}
        for from_hyper in [False, True]:
            for to_hyper in [False, True]:
                if not from_hyper and to_hyper: continue  # skip c -> C
                outdegrees = np.array(G.outdegrees(from_hyper, to_hyper))
                indegrees = np.array(G.indegrees(from_hyper, to_hyper))

                for stat, stat_func in stat_funcs.items():
                    stats["{}[outdegree over {}->{} {}responses]".format(stat,
                                                                         HyperConvo._node_type_name(from_hyper),
                                                                         HyperConvo._node_type_name(to_hyper),
                                                                         name_ext)] = stat_func(outdegrees)
                    stats["{}[indegree over {}->{} {}responses]".format(stat,
                                                                        HyperConvo._node_type_name(from_hyper),
                                                                        HyperConvo._node_type_name(to_hyper),
                                                                        name_ext)] = stat_func(indegrees)
        return stats

    @staticmethod
    def _motif_feats(uts: Optional[Dict[Hashable, Utterance]]=None,
                     G: Hypergraph=None,
                     name_ext: str="",
                     exclude_id: str=None) -> Dict:
        """
        Helper method for retrieve_feats().
        Generate statistics on degree-related features in a Hypergraph (G), or a Hypergraph
        constructed from provided utterances (uts)
        :param uts: utterances to construct Hypergraph from
        :param G: Hypergraph to calculate degree features statistics from
        :param name_ext: Suffix to append to feature name
        :param exclude_id: id of utterance to exclude from Hypergraph construction
        :return: A dictionary from a thread root id to its stats dictionary,
            which is a dictionary from feature names to feature values. For motif-related
            features specifically.
        """
        assert uts is None or G is None
        if G is None:
            G = HyperConvo._make_hypergraph(uts=uts, exclude_id=exclude_id)

        stat_funcs = {
            "is-present": lambda l: len(l) > 0,
            "count": len
        }

        stats = {}
        for motif, motif_func in [
            ("reciprocity motif", G.reciprocity_motifs),
            ("external reciprocity motif", G.external_reciprocity_motifs),
            ("dyadic interaction motif", G.dyadic_interaction_motifs),
            ("incoming triads", G.incoming_triad_motifs),
            ("outgoing triads", G.outgoing_triad_motifs)]:
            motifs = motif_func()
            for stat, stat_func in stat_funcs.items():
                stats["{}[{}{}]".format(stat, motif, name_ext)] = \
                    stat_func(motifs)
        return stats

    @staticmethod
    def retrieve_feats(corpus: Corpus, prefix_len: int=10,
                       min_thread_len: int=10,
                       include_root: bool=True) -> Dict[Hashable, Dict]:
        """
        Retrieve all hypergraph features for a given corpus (viewed as a set
        of conversation threads).

        See init() for further documentation.

        :return: A dictionary from a thread root id to its stats dictionary,
            which is a dictionary from feature names to feature values. For degree-related
            features specifically.
        """

        threads_stats = dict()

        for i, (root, thread) in enumerate(
                corpus.utterance_threads(prefix_len=prefix_len, include_root=include_root).items()):
            if len(thread) < min_thread_len: continue
            stats = {}
            G = HyperConvo._make_hypergraph(uts=thread)
            G_mid = HyperConvo._make_hypergraph(uts=thread, exclude_id=root)
            for k, v in HyperConvo._degree_feats(G=G).items(): stats[k] = v
            for k, v in HyperConvo._motif_feats(G=G).items(): stats[k] = v
            for k, v in HyperConvo._degree_feats(G=G_mid,
                                           name_ext="mid-thread ").items(): stats[k] = v
            for k, v in HyperConvo._motif_feats(G=G_mid,
                                          name_ext=" over mid-thread").items(): stats[k] = v
            threads_stats[root] = stats
        return threads_stats

