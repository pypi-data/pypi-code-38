"""The objects used to represent a dataset."""

import json
import pickle
from functools import total_ordering
from collections import defaultdict
import os
from typing import Dict, List, Collection, Hashable, Callable, Set, Generator, Tuple, Optional
pair_delim = '-q-a-'


@total_ordering
class User:
    """Represents a single user in a dataset.

    :param name: name of the user.
    :type name: str
    :param meta: arbitrary dictionary of attributes associated
        with the user.
    :type meta: dict

    :ivar name: name of the user.
    :ivar meta: dictionary of attributes associated with the user.
    """

    def __init__(self, name: str=None, meta: Optional[Dict]=None):
        self._name = name
        self._meta = meta if meta is not None else {}
        self._split_attribs = set()
        self._update_uid()

    def identify_by_attribs(self, attribs: Collection) -> None:
        """Identify a user by a list of attributes. Sets which user info
        attributes should distinguish users of the same name in equality tests.
        For example, in the Supreme Court dataset, users are labeled with the
        current case id. Call this method with attribs = ["case"] to count
        the same person across different cases as different users.

        :param attribs: Collection of attribute names.
        :type attribs: Collection
        """

        self._split_attribs = set(attribs)
        self._update_uid()

    def _get_name(self): return self._name

    def _set_name(self, value: str):
        self._name = value
        self._update_uid()
    name = property(_get_name, _set_name)

    def _get_meta(self): return self._meta

    def _set_meta(self, value: Dict):
        self._meta = value
        self._update_uid()
    meta = property(_get_meta, _set_meta)

    def add_meta(self, key: Hashable, value) -> None:
        self.meta[key] = value

    def _update_uid(self):
        rep = dict()
        rep["name"] = self._name
        if self._split_attribs:
            rep["attribs"] = {k: self._meta[k] for k in self._split_attribs
                    if k in self._meta}
        self._uid = "User(" + str(sorted(rep.items())) + ")"

    def __eq__(self, other):
        return self._uid == other._uid

    def __lt__(self, other):
        return self._uid < other._uid

    def __hash__(self):
        return hash(self._uid)

    def __repr__(self):
        return self._uid

class Utterance:
    """Represents a single utterance in the dataset.

    :param id: the unique id of the utterance. Can be any hashable type.
    :param user: the user giving the utterance.
    :param root: the id of the root utterance of the conversation.
    :param reply_to: id of the utterance this was a reply to.
    :param timestamp: timestamp of the utterance. Can be any
        comparable type.
    :param text: text of the utterance.
    :type text: str

    :ivar id: the unique id of the utterance.
    :ivar user: the user giving the utterance.
    :ivar root: the id of the root utterance of the conversation.
    :ivar reply_to: id of the utterance this was a reply to.
    :ivar timestamp: timestamp of the utterance.
    :ivar text: text of the utterance.
    """

    def __init__(self, id: Optional[Hashable]=None, user: Optional[User]=None,
                 root: Optional[Hashable]=None, reply_to: Optional[Hashable]=None,
                 timestamp: Optional[int]=None, text: Optional[str]=None,
                 meta: Optional[Dict]=None):
        self.id = id
        self.user = user
        self.root = root
        self.reply_to = reply_to
        self.timestamp = timestamp
        self.text = text
        self.meta = meta if meta is not None else {}

    def get(self, key: str):
        if key == "id":
            return self.id
        elif key == "user":
            return self.user
        elif key == "root":
            return self.root
        elif key == "reply_to":
            return self.reply_to
        elif key == "timestamp":
            return self.timestamp
        elif key == "text":
            return self.text
        elif key == "meta":
            return self.meta

    def add_meta(self, key: Hashable, value) -> None:
        self.meta[key] = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "Utterance(" + str(self.__dict__) + ")"

class Conversation:
    """Represents a discrete subset of utterances in the dataset, connected by a
    reply-to chain.
    
    :param owner: The Corpus that this Conversation belongs to
    :param id: The unique ID of this Conversation
    :param utterances: A list of the IDs of the Utterances in this Conversation
    :param meta: Table of initial values for conversation-level metadata

    :ivar meta: A dictionary-like view object providing read-write access to
        conversation-level metadata. For utterance-level metadata, use 
        Utterance.meta. For user-level metadata, use User.meta. For corpus-level
        metadata, use Corpus.meta.
    """

    def __init__(self, owner, id: Optional[str]=None,
                 utterances: Optional[List[str]]=None,
                 meta: Optional[Dict]=None):
        self._owner = owner
        self._id = id
        self._utterance_ids = utterances
        self._usernames = None
        self._meta = {} if meta is None else meta

    # Conversation.meta property
    def _get_meta(self):
        """Provides read-write access to conversation-level metadata. For
        utterance-level metadata, use Utterance.meta. For user-level metadata,
        use User.meta. For corpus-level metadata, use Corpus.meta."""
        return self._meta
    def _set_meta(self, new_meta):
        self._meta = new_meta

    meta = property(_get_meta, _set_meta)

    # TODO: doublecheck if this is cool
    def add_meta(self, key: Hashable, value) -> None:
        self.meta[key] = value

    # Conversation.id property
    def _get_id(self):
        """The unique ID of this Conversation [read-only]"""
        return self._id
    id = property(_get_id)

    def get_utterance_ids(self) -> List[str]:
        """Produces a list of the unique IDs of all utterances in the 
        Conversation, which can be used in calls to get_utterance() to retrieve 
        specific utterances. Provides no ordering guarantees for the list.
        
        :return: a list of IDs of Utterances in the Conversation
        """
        # we construct a new list instead of returning self._utterance_ids in
        # order to prevent the user from accidentally modifying the internal
        # ID list (since lists are mutable)
        return [ut_id for ut_id in self._utterance_ids]

    def get_utterance(self, ut_id: Hashable) -> Utterance:
        """Looks up the Utterance associated with the given ID. Raises a 
        KeyError if no utterance by that ID exists.
        
        :return: the Utterance with the given ID
        """
        # delegate to the owner Corpus since Conversation does not itself own
        # any Utterances
        return self._owner.get_utterance(ut_id)

    def iter_utterances(self) -> Generator[Utterance, None, None]:
        """Generator allowing iteration over all utterances in the Conversation. 
        Provides no ordering guarantees.
        
        :return: Generator that produces Users
        """
        for ut_id in self._utterance_ids:
            yield self._owner.get_utterance(ut_id)

    def get_usernames(self) -> List[str]:
        """Produces a list of names of all users in the Conversation, which can 
        be used in calls to get_user() to retrieve specific users. Provides no 
        ordering guarantees for the list.
        
        :return: a list of usernames
        """
        if self._usernames is None:
            # first call to get_usernames or iter_users; precompute cached list
            # of usernames
            self._usernames = set()
            for ut_id in self._utterance_ids:
                ut = self._owner.get_utterance(ut_id)
                self._usernames.add(ut.user.name)
        return list(self._usernames)

    def get_user(self, username: str) -> User:
        """Looks up the User with the given name. Raises a KeyError if no user 
        with that name exists.

        :return: the User with the given username
        """
        # delegate to the owner Corpus since Conversation does not itself own
        # any Utterances
        return self._owner.get_user(username)

    def iter_users(self) -> Generator[User, None, None]:
        """Generator allowing iteration over all users in the Conversation. 
        Provides no ordering guarantees.

        :return: Generator that produces Users.
        """
        if self._usernames is None:
            # first call to get_usernames or iter_users; precompute cached list
            # of usernames
            self._usernames = set()
            for ut_id in self._utterance_ids:
                ut = self._owner.get_utterance(ut_id)
                self._usernames.add(ut.user.name)
        for username in self._usernames:
           yield self._owner.get_user(username)


KeyId = "id"
KeyUser = "user"
KeyConvoRoot = "root"
KeyReplyTo = "reply-to"
KeyTimestamp = "timestamp"
KeyText = "text"
DefinedKeys = {KeyId, KeyUser, KeyConvoRoot, KeyReplyTo, KeyTimestamp, KeyText}
KeyMeta = "meta"

BIN_DELIM_L, BIN_DELIM_R = "<##bin{", "}&&@**>"

class Corpus:
    """Represents a dataset, which can be loaded from a JSON file or a
    list of utterances.

    :param filename: path of json file to load
    :param utterances: list of utterances to load
    :param merge_lines: whether to merge adjacent
        lines from the same user if the two utterances have the same root.
    :param version: version number of the corpus

    :ivar utterances: dictionary of utterances in the dataset, indexed by id.
    """

    def __init__(self, filename: Optional[str]=None, utterances: Optional[List[Utterance]]=None,
                 merge_lines: bool=False, exclude_utterance_meta: Optional[List[str]]=None,
                 exclude_conversation_meta: Optional[List[str]]=None,
                 exclude_user_meta: Optional[List[str]]=None,
                 exclude_overall_meta: Optional[List[str]]=None,
                 version: Optional[int]=None):

        self.original_corpus_path = None if filename is None else os.path.dirname(filename)
        self.meta = {}
        self.meta_index = {}
        convos_meta = defaultdict(dict)
        if exclude_utterance_meta is None: exclude_utterance_meta = []
        if exclude_conversation_meta is None: exclude_conversation_meta = []
        if exclude_user_meta is None: exclude_user_meta = []
        if exclude_overall_meta is None: exclude_overall_meta = []

        self.version = version if version is not None else 0

        if filename is not None:
            if os.path.isdir(filename):
                with open(os.path.join(filename, "utterances.json"), "r") as f:
                    utterances = json.load(f)
                    if exclude_utterance_meta:
                        utterances_2 = []
                        for v in utterances:
                            v2 = v
                            for field in exclude_utterance_meta:
                                del v2["meta"][field]
                            utterances_2.append(v2)
                        utterances = utterances_2

                with open(os.path.join(filename, "users.json"), "r") as f:
                    users_meta = defaultdict(dict)
                    for k, v in json.load(f).items():
                        if k in exclude_user_meta: continue
                        users_meta[k] = v
                with open(os.path.join(filename, "conversations.json"), "r") as f:
                    for k, v in json.load(f).items():
                        if k in exclude_conversation_meta: continue
                        convos_meta[k] = v
                with open(os.path.join(filename, "corpus.json"), "r") as f:
                    for k, v in json.load(f).items():
                        if k in exclude_overall_meta: continue
                        self.meta[k] = v
                with open(os.path.join(filename, "index.json"), "r") as f:
                    self.meta_index = json.load(f)

                if version is not None:
                    if "version" in self.meta_index:
                        if self.meta_index["version"] != version:
                            raise Warning("Requested version does not match file version")
                        self.version = self.meta_index["version"]

                # unpack utterance meta
                for field, field_type in self.meta_index["utterances-index"].items():
                    if field_type == "bin" and field not in exclude_utterance_meta:
                        with open(os.path.join(filename, field + "-bin.p"), "rb") as f:
                            l_bin = pickle.load(f)
                        for i, ut in enumerate(utterances):
                            for k, v in ut[KeyMeta].items():
                                if k == field and type(v) == str and v.startswith(BIN_DELIM_L) and \
                                        v.endswith(BIN_DELIM_R):
                                        idx = int(v[len(BIN_DELIM_L):-len(BIN_DELIM_R)])
                                        utterances[i][KeyMeta][k] = l_bin[idx]
                for field in exclude_utterance_meta:
                    del self.meta_index["utterances-index"][field]

                # unpack user meta
                for field, field_type in self.meta_index["users-index"].items():
                    if field_type == "bin" and field not in exclude_utterance_meta:
                        with open(os.path.join(filename, field + "-user-bin.p"), "rb") as f:
                            l_bin = pickle.load(f)
                        for k, v in users_meta.items():
                            if k == field and type(v) == str and str(v).startswith(BIN_DELIM_L) and \
                                str(v).endswith(BIN_DELIM_R):
                                    idx = int(v[len(BIN_DELIM_L):-len(BIN_DELIM_R)])
                                    users_meta[k] = l_bin[idx]
                for field in exclude_user_meta:
                    del self.meta_index["users-index"][field]

                # unpack convo meta
                for field, field_type in self.meta_index["conversations-index"].items():
                    if field_type == "bin" and field not in exclude_utterance_meta:
                        with open(os.path.join(filename, field + "-convo-bin.p"), "rb") as f:
                            l_bin = pickle.load(f)
                        for k, v in convos_meta.items():
                            if k == field and type(v) == str and str(v).startswith(BIN_DELIM_L) and \
                                str(v).endswith(BIN_DELIM_R):
                                    idx = int(v[len(BIN_DELIM_L):-len(BIN_DELIM_R)])
                                    convos_meta[k] = l_bin[idx]

                for field in exclude_conversation_meta:
                    del self.meta_index["conversations-index"][field]

                # unpack overall meta
                for field, field_type in self.meta_index["overall-index"].items():
                    if field_type == "bin" and field not in exclude_utterance_meta:
                        with open(os.path.join(filename, field + "-overall-bin.p"), "rb") as f:
                            l_bin = pickle.load(f)
                        for k, v in self.meta.items():
                            if k == field and type(v) == str and v.startswith(BIN_DELIM_L) and \
                                v.endswith(BIN_DELIM_R):
                                    idx = int(v[len(BIN_DELIM_L):-len(BIN_DELIM_R)])
                                    self.meta[k] = l_bin[idx]
                for field in exclude_overall_meta:
                    del self.meta_index["overall-index"][field]

            else:
                users_meta = defaultdict(dict)
                convos_meta = defaultdict(dict)
                with open(filename, "r") as f:
                    try:
                        utterances = json.load(f)
                    except Exception as e:
                        raise Exception("Could not load corpus. Expected json file, encountered error: \n" + str(e))


            self.utterances = {}
            self.all_users = set()
            users_cache = {}   # avoids creating duplicate user objects

            for i, u in enumerate(utterances):

                u = defaultdict(lambda: None, u)
                user_key = u[KeyUser]
                if user_key not in users_cache:
                    users_cache[user_key] = User(name=u[KeyUser],
                        meta=users_meta[u[KeyUser]])
                user = users_cache[user_key]
                self.all_users.add(user)

                # temp fix
                if "reply_to" in u:
                    reply_to_data = u["reply_to"]
                else:
                    reply_to_data = u[KeyReplyTo]

                ut = Utterance(id=u[KeyId], user=user,
                        root=u[KeyConvoRoot],
                        reply_to=reply_to_data, timestamp=u[KeyTimestamp],
                        text=u[KeyText], meta=u[KeyMeta])
                self.utterances[ut.id] = ut
        elif utterances is not None:
            self.all_users = set([u.user for u in utterances])
            self.utterances = {u.id: u for u in utterances}

        if merge_lines:
            new_utterances = {}
            for uid, u in self.utterances.items():
                merged = False
                if u.reply_to is not None and u.user is not None:
                    u0 = self.utterances[u.reply_to]
                    if u0.root == u.root and u0.user == u.user:
                        new_utterances[u0.id].text += " " + u.text
                        merged = True
                if not merged:
                    new_utterances[u.id] = u
            self.utterances = new_utterances

        # organize utterances by conversation
        convo_to_utts = defaultdict(list) # temp container identifying utterances by conversation
        for u in self.utterances.values():
            convo_key = u.root # each root is considered a separate conversation
            convo_to_utts[convo_key].append(u.id)
        self.conversations = {}
        for convo_id in convo_to_utts:
            # look up the metadata associated with this conversation, if any
            convo_meta = convos_meta.get(convo_id, None)
            convo = Conversation(self, id=convo_id,
                        utterances=convo_to_utts[convo_id],
                        meta=convo_meta)
            self.conversations[convo_id] = convo


    # params: d is dict to encode, d_bin is dict of accumulated lists of binary attribs
    @staticmethod
    def dump_helper_bin(d: Dict, d_bin: Dict, utterances_idx: Dict) -> Dict:
        d_out = {}
        for k, v in d.items():
            try:   # try saving the field
                json.dumps(v)
                d_out[k] = v
                if k not in utterances_idx:
                    utterances_idx[k] = str(type(v))
            except (TypeError, OverflowError):   # unserializable
                d_out[k] = "{}{}{}".format(BIN_DELIM_L, len(d_bin[k]), BIN_DELIM_R)
                d_bin[k].append(v)
                utterances_idx[k] = "bin"   # overwrite non-bin type annotation if necessary
        #print(l_bin)
        #pickle.dump(l_bin, f)
        return d_out

    def dump(self, name: str, base_path: Optional[str]=None, save_to_existing_path: bool=False) -> None:
        """Dumps the corpus and its metadata to disk.

        :param name: name of corpus
        :param base_path: base directory to save corpus in (None to save to a default directory)
        :param save_to_existing_path: if True, save to the path you loaded the corpus from (supercedes base_path)
        """
        dir_name = name
        if base_path is not None and save_to_existing_path:
            raise ValueError("Not allowed to specify both base_path and save_to_existing_path!")
        if save_to_existing_path and self.original_corpus_path is None:
            raise ValueError("Cannot use save to existing path on Corpus generated from utterance list!")
        if not save_to_existing_path:
            if base_path is None:
                base_path = os.path.expanduser("~/.convokit/")
                if not os.path.exists(base_path):
                    os.mkdir(base_path)
                base_path = os.path.join(base_path, "saved-corpora/")
                if not os.path.exists(base_path):
                    os.mkdir(base_path)
            dir_name = os.path.join(base_path, dir_name)
        else:
            dir_name = os.path.join(self.original_corpus_path, name)

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        utterances_idx, users_idx, convos_idx, overall_idx = {}, {}, {}, {}

        with open(os.path.join(dir_name, "users.json"), "w") as f:
            d_bin = defaultdict(list)
            users = {u: Corpus.dump_helper_bin(self.get_user(u).meta, d_bin,
                users_idx) for u in self.get_usernames()}
            json.dump(users, f)
            for name, l_bin in d_bin.items():
                with open(os.path.join(dir_name, name + "-user-bin.p"), "wb") as f_pk:
                    pickle.dump(l_bin, f_pk)
        with open(os.path.join(dir_name, "conversations.json"), "w") as f:
            d_bin = defaultdict(list)
            convos = {c: Corpus.dump_helper_bin(self.get_conversation(c).meta,
                d_bin, convos_idx) for c in self.get_conversation_ids()}
            json.dump(convos, f)
            for name, l_bin in d_bin.items():
                with open(os.path.join(dir_name, name + "-convo-bin.p"), "wb") as f_pk:
                    pickle.dump(l_bin, f_pk)
        with open(os.path.join(dir_name, "utterances.json"), "w") as f:
            uts = []
            d_bin = defaultdict(list)
            for ut in self.iter_utterances():
                uts.append({
                    KeyId: ut.id,
                    KeyConvoRoot: ut.root,
                    KeyText: ut.text,
                    KeyUser: ut.user.name,
                    KeyMeta: self.dump_helper_bin(ut.meta, d_bin, utterances_idx),
                    KeyReplyTo: ut.reply_to,
                    KeyTimestamp: ut.timestamp
                })
            json.dump(uts, f)
            for name, l_bin in d_bin.items():
                with open(os.path.join(dir_name, name + "-bin.p"), "wb") as f_pk:
                    pickle.dump(l_bin, f_pk)

        with open(os.path.join(dir_name, "corpus.json"), "w") as f:
            d_bin = defaultdict(list)
            meta_up = Corpus.dump_helper_bin(self.meta, d_bin, overall_idx)
#            keys = ["utterances-index", "conversations-index", "users-index",
#                "overall-index"]
#            meta_minus = {k: v for k, v in overall_idx.items() if k not in keys}
#            meta_up["overall-index"] = meta_minus
            json.dump(meta_up, f)
            for name, l_bin in d_bin.items():
                with open(os.path.join(dir_name, name + "-overall-bin.p"), "wb") as f_pk:
                    pickle.dump(l_bin, f_pk)

        self.meta_index["utterances-index"] = utterances_idx
        self.meta_index["users-index"] = users_idx
        self.meta_index["conversations-index"] = convos_idx
        self.meta_index["overall-index"] = overall_idx
        self.meta_index["version"] = self.version

        with open(os.path.join(dir_name, "index.json"), "w") as f:
            json.dump(self.meta_index, f)

    def get_utterance_ids(self) -> List[Hashable]:
        return list(self.utterances.keys())

    def get_utterance(self, ut_id: Hashable) -> Utterance:
        return self.utterances[ut_id]

    def iter_utterances(self) -> Generator[Utterance, None, None]:
        for v in self.utterances.values():
            yield v

    def get_conversation_ids(self) -> List[str]:
        return list(self.conversations.keys())

    def get_conversation(self, cid: Hashable) -> Conversation:
        return self.conversations[cid]

    def iter_conversations(self) -> Generator[Conversation, None, None]:
        for v in self.conversations.values():
            yield v

    def filter_utterances_by(self, regular_kv_pairs: Optional[Dict]=None,
                             meta_kv_pairs: Optional[Dict]=None) -> None:
        """
        Creates a subset of the utterances filtered by certain attributes. Irreversible.
        If the method is run again, it will filter the already filtered subset.
        Always takes the intersection of the specified key-pairs
        """
        if regular_kv_pairs is None: regular_kv_pairs = dict()
        if meta_kv_pairs is None: meta_kv_pairs = dict()
        new_utterances = dict()

        regular_keys = list(regular_kv_pairs.keys())
        meta_keys = list(meta_kv_pairs.keys())
        for uid, utterance in self.utterances.items():
            meta_dict = utterance.meta
            regular = all(utterance.get(key) == regular_kv_pairs[key] for key in regular_keys)
            meta = all(meta_dict[key] == meta_kv_pairs[key] for key in meta_keys)
            if regular and meta:
                new_utterances[uid] = utterance

        self.utterances = new_utterances

#    def earliest_n_utterances(self, n, uts=None):
#        """Returns the first n utterances (ordered by time)."""
#        if uts is None:
#            uts = self.utterances
#        uts = list(sorted(uts.values(), key=lambda u: u.timestamp))
#        return uts[:n]

    def utterance_threads(self, prefix_len: Optional[int]=None,
                          suffix_len: int=0,
                          include_root: bool=True) -> Dict[Hashable, Dict[Hashable, Utterance]]:
        """
        Returns dict of threads, where a thread is all utterances with the
        same root.

        :param prefix_len: if an integer n, only get the first n utterances
            of each thread (sorted by ascending timestamp value)
        :param suffix_len: if an integer n, only get the last n utterances
            of each thread (sorted by descending timestamp value)
        :param include_root: True if root utterance should be included in the utterance thread.
            If False, thread begins from top level comment.

        :return: Dictionary from thread root ids to threads, where a thread is
            itself a dictionary from utterance ids to utterances.
        """
        threads = defaultdict(list)
        for ut in self.utterances.values():
            if include_root:
                threads[ut.root].append(ut)
            else:
                top_level_comment = ut.get("meta")["top_level_comment"]
                if top_level_comment is None: continue # i.e. this is a post (root) utterance
                threads[top_level_comment].append(ut)
        return {root: {utt.id: utt for utt in list(sorted(l,
            key=lambda ut: ut.timestamp))[-suffix_len:prefix_len]}
            for root, l in threads.items()}

    def get_meta(self) -> Dict:
        return self.meta

    def add_meta(self, key: Hashable, value) -> None:
        self.meta[key] = value

    def iter_users(self, selector: Optional[Callable[[User], bool]]=None) -> Set[User]:
        """Get users in the dataset.

        :param selector: optional function that takes in a
            `User` and returns True to include the user in the
            resulting list, or False otherwise.

        :return: Set containing all users selected by the selector function,
            or all users in the dataset if no selector function was
            used.
        """
        if selector is None:
            return self.all_users
        else:
            return set([u for u in self.all_users if selector(u)])

    def get_user(self, name: str) -> User:
        return [u for u in self.all_users if u.name == name][0]

    def get_usernames(self, selector: Optional[Callable[[User], bool]]=None) -> Set[str]:
        """Get names of users in the dataset.

        :param selector: optional function that takes in a
            `User` and returns True to include the user's name in the
            resulting list, or False otherwise.

        :return: Set containing all user names selected by the selector
            function, or all user names in the dataset if no selector function
            was used.
        """
        return set([u.name for u in self.iter_users(selector)])

    def speaking_pairs(self, selector: Optional[Callable[[User, User], bool]]=None,
                       user_names_only: bool=False) -> Set[Tuple]:
        """Get all directed speaking pairs (a, b) of users such that a replies
            to b at least once in the dataset.

        :param selector: optional function that takes in
            a speaker user and a replied-to user and returns True to include
            the pair in the result, or False otherwise.
        :param user_names_only: if True, return just pairs of
            user names rather than user objects.
        :type user_names_only: bool

        :return: Set containing all speaking pairs selected by the selector
            function, or all speaking pairs in the dataset if no selector
            function was used.
        """
        pairs = set()
        for u2 in self.utterances.values():
            if u2.user is not None and u2.reply_to is not None and u2.reply_to in self.utterances:
                u1 = self.utterances[u2.reply_to]
                if u1.user is not None:
                    if selector is None or selector(u2.user, u1.user):
                        pairs.add((u2.user.name, u1.user.name) if
                                user_names_only else (u2.user, u1.user))
        return pairs

    def pairwise_exchanges(self, selector: Optional[Callable[[User, User], bool]]=None,
                           user_names_only: bool=False) -> Dict[Tuple, List[Utterance]]:
        """Get all directed pairwise exchanges in the dataset.

        :param selector: optional function that takes in a
            speaker user and a replied-to user and returns True to include
            the pair in the result, or False otherwise.
        :param user_names_only: if True, index conversations
            by user names rather than user objects.
        :type user_names_only: bool

        :return: Dictionary mapping (speaker, target) tuples to a list of
            utterances given by the speaker in reply to the target.
        """
        pairs = defaultdict(list)
        for u2 in self.utterances.values():
            if u2.user is not None and u2.reply_to is not None:
                u1 = self.utterances[u2.reply_to]
                if u1.user is not None:
                    if selector is None or selector(u2.user, u1.user):
                        key = (u2.user.name, u1.user.name) if user_names_only else (u2.user, u1.user)
                        pairs[key].append(u2)
        return pairs

    def iterate_by(self, iter_type: str,
                   is_utterance_question: Callable[[str], bool]) -> Generator[Tuple[str, str, str], None, None]:
        """Iterator for utterances.

        Can give just questions, just answers or questions followed by their answers
        """
        i = -1
        for utterance in self.utterances.values():
            if utterance.reply_to is not None:
                root_text = self.utterances[utterance.reply_to].text
                if is_utterance_question(root_text):
                    i += 1
                    if iter_type == 'answers':
                        pair_idx = utterance.reply_to + pair_delim + str(utterance.id)
                        yield utterance.id, utterance.text, pair_idx
                        continue
                    question = self.utterances[utterance.reply_to]
                    pair_idx = question.id + pair_delim + utterance.id
                    yield question.id, question.text, pair_idx
                    if iter_type == 'both':
                        pair_idx = utterance.reply_to + pair_delim + str(utterance.id)
                        yield utterance.id, utterance.text, pair_idx
