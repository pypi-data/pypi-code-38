from ..pipe import Pipe


vocab_tokens = [
    "[UNK]", "[CLS]", "[SEP]", "want", "##want", "##ed", "wa", "un", "runn",
    "##ing", ",",
]
vocab = {token: ind for ind, token in enumerate(vocab_tokens)}


full_pipe = Pipe()
full_pipe.add('Lowercase')
full_pipe.add('AddWhitespaceAroundCJK')
full_pipe.add('AddWhitespaceAroundPunctuation')
full_pipe.add('MergeWhiteSpaceCharacters')
full_pipe.add('StripWhiteSpaceCharacters')
full_pipe.add('StripAccentToken')
full_pipe.add('WhiteSpaceTokenizer')
full_pipe.add(
    'SpanSubwords', {
        'vocab': vocab,
        'unk_token': "[UNK]",
        'maxlen_per_token': 200,
    },
)
