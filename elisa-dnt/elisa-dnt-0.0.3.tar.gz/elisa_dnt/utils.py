# encoding: utf-8
# Created by chenghaomou at 2019-05-22
import itertools
import emoji
import string
import warnings
from collections import namedtuple

Match = namedtuple('Match', 'start end re')

rules = {
    "del": {
        "email": r"(?i)( *[\w!#$%&'*+/=?^`{|}~-]+(?:\.[\w!#$%&'*+/=?^`{|}~-]+)*@(?:[a-z\d](?:[a-z\d-]*[a-z\d])?\.)+[a-z\d](?:[a-z\d-]*[a-z\d])? *)",
        "url": r"( *\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@))) *)",
        "hashtag": r"( *(#\p{N}*[\p{L}_'-]+[\p{L}\p{N}_+-]*)+ *)",
        "mention": r"( *(@[\w\-]+)+ *)",
        "time": r"(?i)( *@((([01]?\d|2[0-3]):([0-5]\d)|24:00) ?(pm|am|p\.m|a\.m)?) *)",
        "html": r"( *(<\/?(a|img|div).*?>)+ *)",
        "twitter": r"( *pic\.twitter\.com/[a-zA-Z0-9]+ *)",
        "emoticon": r"((?![\w]) *(:\)+|:-+\)+|:\(+|:-+\(+|;\)+|;-+\)+|:-+O|8-+|:P|<3|:<|:D|:\||:S|:\$|:\/|:-+\/)+ *(?![\w]))",
        "emoji": u" *[" + "".join(set(x for y in list(map(list, emoji.EMOJI_UNICODE.values())) for x in y if
                                      len(x) == 1 and x not in string.punctuation + '0123456789')) + "]+ *"
    },
    "sub": {
        "email": r"(?i)([\w!#$%&'*+/=?^`{|}~-]+(?:\.[\w!#$%&'*+/=?^`{|}~-]+)*@(?:[a-z\d](?:[a-z\d-]*[a-z\d])?\.)+[a-z\d](?:[a-z\d-]*[a-z\d])?)",
        "url": r"(\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@))))",
        "hashtag": r"((#\p{N}*[\p{L}_'-]+[\p{L}\p{N}_+-]*)+)",
        "mention": r"((@[\w\-]+)+)",
        "time": r"(?i)(@((([01]?\d|2[0-3]):([0-5]\d)|24:00) ?(pm|am|p\.m|a\.m)?))",
        "html": r"((<\/?(a|img|div).*?>)+)",
        "twitter": r"(pic\.twitter\.com/[a-zA-Z0-9]+)",
        "emoticon": r"((?![\w])(:\)+|:-+\)+|:\(+|:-+\(+|;\)+|;-+\)+|:-+O|8-+|:P|<3|:<|:D|:\||:S|:\$|:\/|:-+\/)+(?![\w]))",
        "emoji": u"[" + "".join(set(x for y in list(map(list, emoji.EMOJI_UNICODE.values())) for x in y if
                                    len(x) == 1 and x not in string.punctuation + '0123456789')) + "]+"
    }
}

MARKERS = [chr(x) for x in range(0x4DC0, 0x4DFF)]

options = {
    "colors": {
        "email": "background-image:linear-gradient(90deg, #a2fafc, #11a9fc);",
        "url": "background-image:linear-gradient(90deg, #fcd766, #fc7f00);",
        "html": "background-image:linear-gradient(90deg, #aa9cfc, #11a9fc);",
        "mention": "background-image:linear-gradient(90deg, #abfca5, #fce43d);",
        "time": "background-image:linear-gradient(90deg, #abfca5, #fce43d);",
        "hashtag": "background-image:linear-gradient(90deg, #aa9cfc, #fc9ce7);",
        "comb": "background-image:linear-gradient(90deg, #a2fafc, #fce43d);",
        "emoticon": "background-image:linear-gradient(90deg, #FFFFFF, #fce43d);",
        "emoji": "background-image:linear-gradient(90deg, #fce43d, #FFFFFF);",
    },
    "categories": ["email", "url", "html", "mention", "time", "hashtag", "comb", "emoticon", "emoji"],
}


def find(string: str, RULES: dict) -> list:
    matches = itertools.chain(*[exp.finditer(string) for key, exp in RULES.items() if key != "comb"])
    matches = [match for match in sorted(matches, key=lambda m: (m.start(0), -m.end(0)))]
    filtered_matches = []

    for i, match in enumerate(matches):
        if i > 0 and filtered_matches[-1].start <= match.start(0) < match.end(0) <= filtered_matches[-1].end:
            continue
        elif i > 0 and filtered_matches[-1].start <= match.start(0) <= filtered_matches[-1].end:
            filtered_matches[-1] = Match(filtered_matches[-1].start, max(match.end(0), filtered_matches[-1].end),
                                         re=RULES["comb"])
        else:
            filtered_matches.append(Match(match.start(0), match.end(0), re=match.re))

    return filtered_matches


def mark(string: str, matches: list, scheme: str = "sub") -> tuple:
    global MARKERS
    if scheme == "sub":

        modification = []

        for i, match in enumerate(matches):
            start, end = match.start, match.end
            text = string[start:end]
            modification.append(text)

        for key, value in zip(MARKERS, modification):
            string = string.replace(value, f"{key}")

        return string, modification, None

    elif scheme == "del":
        lead = False
        modification = []
        segments = []
        remain = string
        for i, match in enumerate(matches):
            start, end = match.start, match.end
            if start == 0:
                lead = True
            text = string[start:end]
            modification.append(text)
            if remain:
                segment, remain = remain.split(text, maxsplit=1)
            if segment:
                segments.append(segment)

        if remain:
            segments.append(remain)

        restore = []
        i, j = 0, 0
        curr = 0
        while i < len(modification) and j < len(segments):
            if lead and (i == 0 or curr % 2 == 0):
                restore.append(modification[i])
                i += 1
                curr += 1
            elif not lead and (j == 0 or curr % 2 == 0):
                restore.append(segments[j])
                j += 1
                curr += 1
            elif not lead and curr % 2 == 1:
                restore.append(modification[i])
                i += 1
                curr += 1
            elif lead and curr % 2 == 1:
                restore.append(segments[j])
                j += 1
                curr += 1

        while i < len(modification):
            restore.append(modification[i])
            i += 1
            curr += 1
        while j < len(segments):
            restore.append(segments[j])
            j += 1
            curr += 1

        try:
            assert "".join(restore) == string, "".join(restore)
        except AssertionError as ae:
            print(string)
            print(matches)
            print(segments)
            print(modification)
            print(restore)
            print(ae)
            print()

        return segments, modification, lead


def visual(string: str, matches: list, options: dict, RULES: dict) -> str:
    def colorize(match, text):
        cls = [key for key, value in RULES.items() if value == match.re][0]
        if cls in options["categories"]:
            if "<" not in text and ">" not in text:
                return f"""<span class="{cls}" title="{cls}">{text}</span>"""
            else:
                text = text.replace("<", "&lt;")
                text = text.replace(">", "&gt;")
                return f"""<span class="{cls}" title="{cls}">{text}</span>"""
        else:
            return text

    res = string
    for match in matches:
        start, end = match.start, match.end
        text = string[start:end]
        res = res.replace(text, colorize(match, text))

    return res


def split(corpus_path, corpus_output, ini_output, scheme: str, ref: str, RULES: dict):
    with open(corpus_path) as source, open(corpus_output, "w") as o_source, open(ini_output, "w") as o_source_ini:

        if ref == "":
            total_sents, total_matches, total_match_sents = 0, 0, 0
            for src in source.readlines():
                total_sents += 1
                src = src.strip('\n')
                src_matches = find(src, RULES)
                src_after, src_mod, src_lead = mark(src, src_matches, scheme=scheme)
                if scheme == "del":
                    for seg in src_after:
                        o_source.write(seg + "\n")
                else:
                    o_source.write(src_after + "\n")

                if src_matches:
                    total_match_sents += 1
                    total_matches += len(src_mod)
                    if scheme == "del":
                        if src_after:
                            o_source_ini.write(
                                ("YL" if src_lead and len(src_after) >= len(src_mod) else "YS" if src_lead else \
                                    "NL" if not src_lead and len(src_after) > len(src_mod) else "NS"
                                 ) + "\t" + "\t".join(src_mod) + "\n")
                        else:
                            o_source_ini.write("EMPTY" + "\t" + "\t".join(src_mod) + "\n")
                    else:
                        o_source_ini.write('\t'.join(["SUB"] + src_mod) + "\n")
                else:
                    o_source_ini.write("IGNORE\n")
            print(f"{total_matches} LI tokens found in {total_match_sents}/{total_sents} sentences {corpus_path}")
        else:
            assert scheme != "del", "ref is not required for del scheme!"

            src_lines = source.readlines()
            tgt_lines = open(ref).readlines()

            for src_line, tgt_line in zip(src_lines, tgt_lines):
                src_line = src_line.strip('\n')
                tgt_line = tgt_line.strip('\n')

                src_matches = find(src_line, RULES)
                tgt_matches = find(tgt_line, RULES)
                src_matches_text = [src_line[m.start(0):m.end(0)] for m in src_matches]
                tgt_matches_text = [tgt_line[m.start(0):m.end(0)] for m in tgt_matches]
                x_matches = list(set(src_matches_text).intersection(set(tgt_matches_text)))
                x_src_matches = [m for m in src_matches if src_line[m.start(0):m.end(0)] in x_matches]

                src_after, src_mod, src_lead = mark(src_line, x_src_matches, scheme=scheme)

                o_source.write(src_after + "\n")

                if x_matches:
                    o_source_ini.write('\t'.join(["SUB"] + src_mod) + "\n")
                else:
                    o_source_ini.write("IGNORE\n")


def restore(dnt_path, ini_path, output, scheme="del"):
    global MARKERS

    with open(output, "w") as o, open(dnt_path) as i_source, open(ini_path) as i_source_ini:

        translations = list(map(lambda x: x.strip('\n'), i_source.readlines()))
        instructions = list(map(lambda x: x.strip('\n'), i_source_ini.readlines()))

        if scheme == "del":
            i = 0
            j = 0
            placeholder = []
            while i < len(instructions) and j < len(translations):
                lead, *tokens = instructions[i].split('\t')
                if lead == "IGNORE":
                    o.write(translations[j] + "\n")
                    j += 1
                    i += 1
                    continue

                if lead == "EMPTY":
                    o.write("".join(tokens) + "\n")
                    i += 1
                    continue

                if lead == "YL":
                    for token in tokens:
                        placeholder.append(token)
                        placeholder.append(translations[j])
                        j += 1
                elif lead == "YS":
                    for x, token in enumerate(tokens):
                        placeholder.append(token)
                        if x < len(tokens) - 1:
                            placeholder.append(translations[j])
                            j += 1
                if lead == "NL":
                    for token in tokens:
                        placeholder.append(translations[j])
                        placeholder.append(token)
                        j += 1
                    placeholder.append(translations[j])
                    j += 1
                elif lead == "NS":
                    for token in tokens:
                        placeholder.append(translations[j])
                        placeholder.append(token)
                        j += 1
                o.write("".join(placeholder) + "\n")
                placeholder = []
                i += 1
        else:
            for translation, instruction in zip(translations, instructions):
                flag, *segments = instruction.split('\t')
                if flag == "IGNORE":
                    o.write(translation + '\n')
                    continue
                new_translation = translation
                for char in translation:
                    if char in MARKERS:
                        if ord(char) - 0x4DC0 >= len(segments):
                            warnings.warn("Wired source sentence: {}".format(translation), Warning)
                            warnings.warn(" ".join(segments), Warning)
                            continue
                        new_translation = new_translation.replace(char,
                                                                  segments[min(ord(char) - 0x4DC0, len(segments) - 1)])
                o.write(new_translation + '\n')
