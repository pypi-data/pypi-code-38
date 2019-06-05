import spacy
from spacy.tokens import Doc, Span
from benepar.spacy_plugin import BeneparComponent
import nltk
import re


def normalize_text(text):
    paragrahs = text.split('\n')
    new_paragrahs = []
    for paragrah in paragrahs:
        if paragrah.strip() == "":
            continue
        new_paragraph = ' '.join(re.split('\s+', paragrah.strip()))
        new_paragrahs.append(new_paragraph)
    return '\n'.join(new_paragrahs)


class _MedTokenizer(object):

    def __init__(self, vocab=None):
        self.vocab = vocab
        self.find_prefix = re.compile(r'''^[/"':\-~(\[\{\n]''').search
        self.find_suffix = re.compile(
            r'''([/,.;!?:"')}\-~\]\n])$''').search
        self.find_infix = re.compile(r'''[:/~\-\(\)\[\]{}\n]''').search
        self.is_exception = re.compile(
            r'''(^https?://|^[0-9a-zA-Z]+,[0-9a-zA-Z]+$)''').match

    def __call__(self, text):
        if re.search('\\s\\s', text):
            raise RuntimeError('Tokenizer doesn\'t support double space. '
                               'Pls normalize the text first!')
        words = re.split(' ', text)
        # All tokens 'own' a subsequent space character in this tokenizer
        tokens, spaces = [], []
        for word in words:
            toks = self.tokenize(word)
            if len(toks) == 0:
                tokens.append('')
                spaces.append(False)
            else:
                tokens.extend(toks)
                spaces.extend([False] * (len(toks) - 1) + [True])
            assert len(tokens) == len(spaces)
        spaces[-1] = False
        return Doc(self.vocab, words=tokens, spaces=spaces)

    def tokenize(self, substring):
        tokens = []
        if self.is_exception(substring):
            tokens.append(substring)
            return tokens
        elif self.find_prefix(substring):
            start, end = self.find_prefix(substring).span()
            assert start == 0
            tok = substring[:end]
            if tok:
                tokens.append(tok)
            tokens.extend(self.tokenize(substring[end:]))
        elif self.find_suffix(substring):
            suffix = self.find_suffix(substring).group(1)
            start = len(substring) - len(suffix)
            tokens.extend(self.tokenize(substring[:start]))
            if suffix:
                tokens.append(suffix)
        elif self.find_infix(substring):
            start, end = self.find_infix(substring).span()
            tokens.extend(self.tokenize(substring[:start]))
            tok = substring[start:end]
            if tok:
                tokens.append(tok)
            tokens.extend(self.tokenize(substring[end:]))
        else:
            if substring:
                tokens.append(substring)
        return tokens


def check_sentence_incomplete(phrase):
    opening = tuple('({[')
    closing = tuple(')}]')
    mapping = dict(zip(opening, closing))
    queue = []

    for letter in phrase:
        if letter in opening:
            queue.append(mapping[letter])
        elif letter in closing:
            if len(queue) == 0 or letter != queue.pop():
                return True
    return len(queue) > 0 \
           or phrase.endswith('-') \
           or phrase.count('"') % 2 != 0 \
           or phrase.endswith('i.e.')


def _segment_sentence(doc):
    prev_incomplete = False
    sents = []
    sent_text = ''
    search_idx = 0
    for sent in nltk.sent_tokenize(doc.text):
        if prev_incomplete:
            sent_text += ' ' + sent
            prev_incomplete = check_sentence_incomplete(sent_text)
            if not prev_incomplete:
                # sents.append(doc.text.index(sent, search_idx))
                sent_text = ''
                prev_incomplete = False
        else:
            if check_sentence_incomplete(sent):
                prev_incomplete = True
                sent_text = sent
            else:
                sents.append(doc.text.index(sent, search_idx))
                sent_text = ''
                prev_incomplete = False
        search_idx += len(sent)

    is_first_tok = True
    for token in doc:
        if is_first_tok:
            is_first_tok = False
            token.sent_start = True
        elif token.idx in sents:
            token.sent_start = True
        else:
            token.sent_start = False

    return doc


def _get_dependancy_tree_roots(toks):
    '''
    check the roots of the dependency tree of the given tokens
    :param toks: an enumarator of Token
    :return: a list roots of the toks
    '''
    idx = {x.i for x in toks}
    roots = []
    for tok in toks:
        if tok.i == tok.head.i or tok.head.i not in idx:
            roots.append(tok)
    return roots


def _get_target_phrases(doc, constituent_tags=('NP', 'ADJP'),
                        pos_tags=('ADJ', 'NOUN')):
    for sent in doc.sents:
        for tok in sent:
            if tok.pos_ in pos_tags:
                doc._.phrases.append(Span(doc, tok.i, tok.i + 1))
        for phrase in sent._.constituents:
            for constituent in constituent_tags:
                if constituent in phrase._.labels:
                    m = re.search(' \(.*\)$', str(phrase))
                    if m is None:
                        doc._.phrases.append(
                            Span(doc, phrase.start, phrase.end))
                    else:
                        n = 0
                        for i, tok in enumerate(reversed(phrase)):
                            if str(tok) == ')':
                                n += 1
                            if str(tok) == '(':
                                n -= 1
                            if n == 0:
                                break

                        doc._.phrases.append(
                            Span(doc, phrase.start, phrase.end - i - 1))
                        doc._.phrases.append(
                            Span(doc, phrase.end - i, phrase.end - 1))
    doc._.phrases = sorted(set(doc._.phrases))
    return doc


spacy_nlp = spacy.load('en_core_web_sm')
spacy_nlp.tokenizer = _MedTokenizer(spacy_nlp.vocab)
spacy_nlp.add_pipe(_segment_sentence, before='parser')

spacy_nlp.add_pipe(BeneparComponent("benepar_en2"))
Doc.set_extension("phrases", default=[])
spacy_nlp.add_pipe(_get_target_phrases, last=True)
