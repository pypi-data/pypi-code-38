# encoding: utf-8
# Created by chenghaomou at 2019-05-09

import logging
import emoji
import regex as re
from elisa_patch.utils import is_ascii
from itertools import product

logger = logging.getLogger("Postprocessor")


def extract_oov(translation: str,
                source: str,
                english_vocab: set = None,
                romanization: bool = True):
    # Remove Emojis
    translation = ''.join(filter(lambda c: c not in emoji.UNICODE_EMOJI, translation))

    if romanization:
        # Find non-ascii words include hyphens and numbers
        matches = re.findall(r"([^\x00-\x7F]+(\-[^\x00-\x7F]+)*)|(\p{N}+(,\p{N}+)?(.\p{N}+)?)", translation)
        candidates = []
        for match in matches:
            if match[0]:  # alien word
                candidates.append(match[0])
            if match[2] and not is_ascii(match[2]):  # alien number
                candidates.append(match[2])
        return candidates

    else:
        # Remove urls and emails
        translation = re.sub(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", translation)
        translation = re.sub(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", "", translation)
        matches = re.findall(r"([\b@#]?([a-zA-Z]+((\-|\')[a-zA-Z]+)?)\b)", " " + translation)
        candidates = []
        for match in matches:
            if not match[0]:
                continue
            if match[0].startswith("@"):  # Ignore mentions
                continue
            if match[0].startswith("#"):  # Ignore tags
                continue

            title_case = match[0][0].isupper()  # Ignore title case words
            english_word = match[0].lower() in english_vocab  # Ignore english words
            copied_word = match[0] in source  # OOV have to be present in source

            if not title_case and not english_word and copied_word:
                candidates.append(match[0])

        return candidates


def translate_oov(translation: str,
                  oovs: list,
                  similarity: callable = None,
                  scorer: callable = None,
                  length_ratio: int = 1):
    translations = [translation]
    modifications = {}

    for oov in oovs:
        alt, trans = similarity(oov, translation)

        assert trans != set(), f"Translation error for word {oov}"

        alt_comp = None
        trans_comp = None
        give_up = False

        # Translate compound words
        if '-' in oov:
            alt_list = []
            trans_list = []
            for seg in oov.split('-'):
                a, t = similarity(seg, translation)
                if t and seg in t:
                    give_up = True
                    break
                alt_list.append(a)
                trans_list.append(t)
            alt_comp = '-'.join(alt_list)
            trans_comp = ['-'.join(tl) for tl in product(*trans_list)]

        trans = [t for t in trans if t.count(' ') <= length_ratio - 1]
        if (len(trans) == 1 and oov in trans) and not give_up and alt_comp is not None:
            alt = alt_comp
            trans = [t for t in trans_comp if t.count(' ') <= length_ratio - 1]
            logger.warning(msg=f"split match: {oov} -> {alt} : {trans}")

        trans = trans if trans else [oov]
        modifications[oov] = {alt: trans}
        translations = [path.replace(oov, t) for t in trans for path in translations]

    return sorted(translations, key=scorer, reverse=True)[0], modifications
