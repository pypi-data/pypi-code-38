import random
from functools import partial
from operator import itemgetter
from typing import Callable
from typing import List
from typing import Mapping
from typing import Sequence
from typing import Set
from typing import Tuple

import nltk

WORDNET_POS_TAGS = set()  # type: Set[str]
wordnet = None  # type: nltk.corpus.util.LazyCorpusLoader

def preset(*, chance: int = 20) -> Callable:
    """Randomly replaces words with synonyms from wordnet synsets.

    Tags each word in the utterance with nltk's part of speech tagger. Using
    the part of speech, each word in the utterance is replaced with a randomly
    chosen word from the first synset with the same part of speech as the word
    to replace, subject to the specified chance. If no synset exists with the
    same part of speech, the original word will not be replaced.

    Downloads nltk's wordnet, punkt, and averaged_perceptron_tagger if non-existent
    on the host.

    Args:
        chance: The chance between [0, 100] for each word to be replaced by
            a synonym.

    Returns:
        A Callable that when called returns parameters for instantiating a Pipeline.
        This Callable can be passed into putput.Pipeline as the 'preset' argument.

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> pattern_def_path = Path(__file__).parent.parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> p = Pipeline.from_preset(preset(chance=100),
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map,
        ...                          seed=0)
        >>> generator = p.flow(disable_progress_bar=True)
        >>> for utterance, tokens, groups in generator:
        ...     print(utterance)
        ...     print(tokens)
        ...     print(groups)
        ...     break
        can she acquire chips can she acquire french-fried_potatoes and french_fries
        ('[ADD(can she acquire)]', '[ITEM(chips)]',
         '[ADD(can she acquire)]', '[ITEM(french-fried_potatoes)]',
         '[CONJUNCTION(and)]', '[ITEM(french_fries)]')
        ('{[ADD(can she acquire)] [ITEM(chips)]}',
         '{[ADD(can she acquire)] [ITEM(french-fried_potatoes)]}',
         '{[CONJUNCTION(and)]}', '{[ITEM(french_fries)]}')
    """
    if chance not in range(101):
        raise ValueError('Invalid chance: {}. Chance accepts any integer between [0, 100]')
    _init_nltk()
    return partial(_preset, chance=chance)


def _preset(chance: int) -> Mapping:
    combo_hooks_map = {
        'DEFAULT': (partial(_replace_with_synonyms, chance=chance),)
    }
    return {
        'combo_hooks_map': combo_hooks_map
    }


def _init_nltk() -> None:
    global WORDNET_POS_TAGS  # pylint: disable=global-statement
    global wordnet  # pylint: disable=global-statement
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    from nltk.corpus import wordnet  # pylint: disable=redefined-outer-name
    WORDNET_POS_TAGS = {wordnet.ADJ, wordnet.VERB, wordnet.NOUN, wordnet.ADV}


def _replace_with_synonyms(utterance: str,
                           handled_tokens: Sequence[str],
                           handled_groups: Sequence[str],
                           chance: int
                           ) -> Tuple[str, Sequence[str], Sequence[str]]:
    _, _ = handled_tokens, handled_groups
    pos = _pos_tag_for_wordnet(utterance)
    return _replace_utterance_tokens_groups_with_synonyms(handled_groups, pos, chance)


def _replace_utterance_tokens_groups_with_synonyms(handled_groups: Sequence[str],
                                                   pos: Sequence[str],
                                                   chance: int
                                                   ) -> Tuple[str, Sequence[str], Sequence[str]]:
    pos_position = 0
    synonym_utterances, synonym_tokens, synonym_groups = [], [], [] # type: List[str], List[str], List[str]
    for handled_group in handled_groups:
        syn_utterance_components, syn_token_components, pos_position = _replace_components_with_synonyms(handled_group,
                                                                                                         pos,
                                                                                                         pos_position,
                                                                                                         chance)
        synonym_utterance_component = ' '.join(syn_utterance_components)
        synonym_utterances.append(synonym_utterance_component)

        synonym_token_components = ['[{}({})]'.format(t, u)
                                    for u, t in zip(syn_utterance_components, syn_token_components)]
        synonym_tokens += synonym_token_components

        synonym_group_component = '{{{}}}'.format(' '.join(synonym_token_components))
        synonym_groups.append(synonym_group_component)
    return ' '.join(synonym_utterances), tuple(synonym_tokens), tuple(synonym_groups)


def _replace_components_with_synonyms(handled_group: str,
                                      pos: Sequence[str],
                                      pos_position: int,
                                      chance: int
                                      ) -> Tuple[Sequence[str], Sequence[str], int]:
    num_parens = 0
    syn_utterance_components, syn_token_components = [], [] # type: List[str], List[str]
    for position, char in enumerate(handled_group):
        if char == '[':
            start_tokens_index = position + 1
        if char == '(':
            num_parens += 1
            if num_parens == 2:
                syn_token_components.append(handled_group[start_tokens_index:position])
                start_utterance_index = position + 1
        if char == ')':
            num_parens -= 1
            if num_parens == 1:
                handled_original_utterance_component = handled_group[start_utterance_index:position]
                handled_utterance_component_words = handled_original_utterance_component.split()
                for i, word in enumerate(handled_utterance_component_words):
                    if random.random() < (chance / 100) and pos[pos_position] in WORDNET_POS_TAGS:
                        handled_utterance_component_words[i] = _get_synonym(word, pos[pos_position])
                    pos_position += 1
                syn_utterance_components.append(' '.join(handled_utterance_component_words))
    return syn_utterance_components, syn_token_components, pos_position


def _get_wordnet_pos(tag: str) -> str:
    if tag.startswith('J'):
        return wordnet.ADJ
    if tag.startswith('V'):
        return wordnet.VERB
    if tag.startswith('N'):
        return wordnet.NOUN
    if tag.startswith('R'):
        return wordnet.ADV
    return ''


def _pos_tag_for_wordnet(utterance: str) -> Tuple[str, ...]:
    tags = nltk.pos_tag(nltk.word_tokenize(utterance))
    return tuple(map(_get_wordnet_pos, tuple(map(itemgetter(1), tags))))


def _get_synonym(word: str, tag: str) -> str:
    synsets = wordnet.synsets(word)
    for synset in synsets:
        if synset.pos() == tag:
            synonym = random.choice(synset.lemma_names())
            if synonym:
                word = synonym
                break
    return word
