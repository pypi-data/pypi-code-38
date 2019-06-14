from ..pipe import Pipe


vocab_tokens = [
    "[UNK]", "[CLS]", "[SEP]", "want", "##want",
    "##ed", "wa", "un", "runn", "##ing",
]
vocab = {token: ind for ind, token in enumerate(vocab_tokens)}


word_piece_pipe = Pipe()
word_piece_pipe.add('WhiteSpaceTokenizer')
word_piece_pipe.add(
    'SpanSubwords', {
        'vocab': vocab,
        'unk_token': "[UNK]",
        'maxlen_per_token': 200,
    },
)
