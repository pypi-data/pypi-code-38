def sort_file(filename):
    with open(filename, "rb") as fp:
        lines = fp.readlines()
    lines.sort()
    with open(filename, "wb") as fp:
        for line in lines:
            fp.write(line)

    def _sort_sense_index(self):
        data_dir = self._get_data_dir()
        sort_file(pjoin(data_dir, "dict", "index.sense"))

    def fi_lemma_key(self, en_lemma, fi_lemma_str):
        name = fi_lemma_str.replace(" ", "_")
        tup = (
            name,
            self._pos_numbers[en_lemma.synset().pos()],
            en_lemma._lexname_index,
            en_lemma._lex_id,
            "",
            "",
        )
        return ("%s%%%d:%02d:%02d:%s:%s" % tup).lower()

        self._counts = None

    def open(self, filename):
        if filename == "lexnames":
            return wordnet.open("lexnames")
        return open(fiwn_resman.get_res(filename))


from finntk.wordnet.reader import fiwn

fiwn.lemmas("puhua")[0].count()
