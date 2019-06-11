import re

class DictBuilder:
    """Generic element structure builder.
    This builder converts a sequence of start, data, and end method
    calls to a dict.
    """

    def __init__(self, value_processor=None, object_processor=None, trim_spaces=False, del_empty=True, cleanup_namespaces=True):
        """[summary]

        Keyword Arguments:
            trim_spaces {bool} -- [description] (default: {False})
            value_processor {[type]} -- [description] (default: {None})
            object_processor {[type]} -- [description] (default: {None})
        """
        self.dict = {}
        self.path = []
        self.leaf = {}
        self.trim_spaces = trim_spaces
        self.object_processor = object_processor
        self.value_processor = value_processor
        self.del_empty = del_empty
        self.cleanup_namespaces = cleanup_namespaces

    def getLeaf(self):
        """Used to get the dict of the current path

        Returns:
            dict -- the dict of the current path
        """
        leaf = self.dict
        for i in self.path:
            l = leaf["#alldata"]
            le = l[-1]
            leaf = le[i]

        return leaf

    def getParentLeaf(self):
        """Used to get the parent dict of the current path

        Returns:
            dict -- the dict of the current path-1
        """
        leaf = self.dict
        for i in self.path[:-1]:
            l = leaf["#alldata"]
            le = l[-1]
            leaf = le[i]

        return leaf

    def close(self):
        """called at the end of the parsing

        Returns:
            dict -- the dict corresponding to the data parsed
        """
        root = self.dict["#alldata"][0]
        self.path2 = []
        self.clean(root)
        if root[next(iter(root))] == {} and self.del_empty:
            return None
        return root

    def data(self, data):
        """called when data is encountered during parsing

        Arguments:
            data {string} -- text between tags
        """
        if data.isspace():
            return
        if self.trim_spaces:
            data = " ".join(data.split())
        self.leaf = self.getLeaf()
        self.leaf["#alldata"].append(data)

    def start(self, tag, attrs):
        """called when a new tag is encountered during parsing

        Arguments:
            tag {string} -- the tag name
            attrs {[type]} -- [description]
        """
        if self.cleanup_namespaces:
            tag = re.sub('{.*}', '', tag)
        self.leaf = self.getLeaf()
        if self.leaf.get("#alldata") is None:
            self.leaf["#alldata"] = []

        new_tag = {tag: {"#alldata": []}}
        for k, v in attrs.items():
            new_tag[tag]["@"+k] = v

        self.leaf["#alldata"].append(new_tag)

        self.path.append(tag)

    def merge_tag_text(self, o):
        """called when merging mixed tag and text

        Arguments:
            o {object} -- something we want to transform into a string

        Returns:
            string -- the transformed object
        """
        r = ""
        if isinstance(o, list):
            for i in o:
                r = r+self.merge_tag_text(i)
        elif isinstance(o, str):
            return o
        elif isinstance(o, (int, float)):
            return str(o)
        elif isinstance(o, dict):
            if o.get("#alldata") is None:
                for v in o.values():
                    r = r+self.merge_tag_text(v)
            else:
                r = r+self.merge_tag_text(o["#alldata"])
        return r

    def add_tag(self, d, k, v):
        """add a subdict (the tag) in a dict

        Arguments:
            d {dict} -- element in which we want to add a tag
            k {string} -- tag name
            v {?} -- content of the tag
        """
        t = d.get(k)

        # if tag didn't exist, create it
        if t is None:
            d[k] = v
        # if tag existed, and was a single value, transform it into a list
        elif isinstance(t, (int, float, str, dict)):
            d[k] = [d[k], v]
        # if tag existed and was a list, append the new tag
        elif isinstance(t, list):
            t.append(v)

    def merge_tag(self, l):
        """merge a list of tags into a dict

        Arguments:
            l {list} -- [{'content1': ...}, {'content2': ...}]

        Returns:
            dict -- dict with all the tags
        """
        r = {}

        for i in l:
            # i : 'content1': ...
            self.clean(i)
            for k, v in i.items():
                if self.del_empty and v == {}:
                    continue
                else:
                    self.add_tag(r, k, v)

        return r

    def clean(self, d):
        '''transform a dict structured with #alldata into a "normal" dict

        Arguments:
            d {[type]} -- {'i': {'#alldata': [{'content1': {'#alldata': ...}, {'content2': {'#alldata': ...},'oui']}}}
        '''
        k = next(iter(d))  # k='i'
        self.path2.append(k)

        # test if tag has attrs
        has_attrs = False
        for i in d[k]:
            if i != "#alldata":
                has_attrs = True
                break
        # get the list, eg : [{'content1': {'#alldata': ...}, {'content2': {'#alldata': ...},'oui']
        l = d[k]["#alldata"]

        # check tag and text presence
        tag_presence = False
        n_text = False
        for i in l:
            if isinstance(i, dict):
                tag_presence = True
            elif isinstance(i, str):
                n_text = True

        if n_text and not tag_presence:  # if ['oui']
            content = ""
            for i in l:
                content = content+i
            if self.value_processor is not None:
                r = self.value_processor(content)
            else:
                r = content
            if has_attrs:
                d[k]["#text"] = r
                d[k].pop("#alldata", None)
            else:
                d[k] = r

        # if [{'content1': {'#alldata': ...}}, {'content2': {'#alldata': ...}}]
        elif tag_presence and not n_text:

            # processed means replacing #alldata by a value
            processed = False
            if self.object_processor is not None:
                r = self.object_processor(self.path2, d[k])
                if r != d[k]:
                    d[k] = r
                    if d[k].get("#alldata") is None:
                        processed = True

            if processed is False:
                # reassign because maybe it has changed
                l = d[k]["#alldata"]
                if has_attrs:
                    for key, val in d[k].items():
                        if key != "#alldata":
                            l.append({key:  {'#alldata': [val]}})
                d[k] = self.merge_tag(l)

        # if [{'content1': {'#alldata': ...},'oui']
        elif tag_presence and n_text :
            if has_attrs:
                d[k]["#text"] = self.merge_tag_text(l)
                del d[k]["#alldata"]

            else:
                d[k] = self.merge_tag_text(l)

        elif not tag_presence  and not n_text :
            if has_attrs:
                del d[k]["#alldata"]
            elif self.del_empty:
                del d[k]

        del self.path2[-1]

    def end(self, tag):
        """called at the end of a tag

        Arguments:
            tag {string} -- tag name
        """
        del self.path[-1]
