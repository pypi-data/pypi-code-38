# encoding: utf-8
# Created by chenghaomou at 2019-05-22

import itertools
import regex as re
import warnings
from collections import namedtuple

Match = namedtuple('Match', 'start end cls')

MARKERS = [chr(x) for x in range(0x4DC0, 0x4DFF)]


def generate_options(path: str = 'elisa_dnt/rules.ini') -> dict:
    colors = [
        '#e3f2fd',
        '#bbdefb',
        '#90caf9',
        '#64b5f6',
        '#42a5f5',
        '#2196f3',
        '#1e88e5',
        '#1976d2',
        '#1565c0',
        '#0d47a1'
    ]
    options = {'colors': {'comb': 'background-color: #4caf50;' }, 'categories': ['comb']}
    with open(path) as i:
        for j, line in enumerate(map(lambda x: x.strip('\n'), i.readlines())):
            name, _ = line.split('=', 1)
            options['categories'].append(name)
            options['colors'][name] = f'background-color: {colors[j]};'
        options['categories'].append('emoji')
        options['colors']['emoji'] = f'background-color: {colors[(j+1)%len(colors)]};'

    return options


def load_rules(emoji_path: str = 'elisa_dnt/emojis.ini',
               rule_path: str = 'elisa_dnt/rules.ini',
               scheme: str = 'del',
               ) -> dict:

    with open(emoji_path) as i:
        emojis = '|'.join(list(map(lambda x: x.strip('\n'), i.readlines())))

    rules = {}

    with open(rule_path) as i:
        for rule in map(lambda x: x.strip('\n'), i.readlines()):
            name, value = rule.split('=', 1)
            if scheme == "del":
                rules[name] = re.compile(u"([ \u202b]*{}[ \u202b]*)".format(value))
            else:
                rules[name] = re.compile(r"({})".format(value))
        if scheme == "del":
            rules['emoji'] = re.compile(u'([ \u202b]*(?:' + emojis + ')[ \u202b]*)', re.UNICODE)
        else:
            rules['emoji'] = re.compile(r'(' + emojis + ')', re.UNICODE)

        # print(rules['emoji'])

    return rules


def find(string: str, rules: dict) -> list:
    # matches = itertools.chain(*[(key, exp.finditer(string)) ])
    matches = [(key, match) for key, exp in rules.items() for match in exp.finditer(string)]
    matches = [match for match in sorted(matches, key=lambda m: (m[-1].start(0), -(m[-1].end(0))))]
    merged_matches = []

    for i, (name, match) in enumerate(matches):
        if i > 0 and merged_matches[-1].start <= match.start(0) < match.end(0) <= merged_matches[-1].end:
            continue
        elif i > 0 and merged_matches[-1].start <= match.start(0) <= merged_matches[-1].end + 1:
            merged_matches[-1] = Match(merged_matches[-1].start,
                                       max(match.end(0), merged_matches[-1].end),
                                       'comb')
        else:
            merged_matches.append(Match(match.start(0),
                                        match.end(0),
                                        name))

    return merged_matches


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


def visual(string: str, matches: list, options: dict, rules: dict) -> str:
    def colorize(match, text):
        cls = match.cls
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
    matched = set()
    for match in matches:
        start, end = match.start, match.end
        text = string[start:end]
        if text not in matched:
            res = res.replace(text, colorize(match, text))
            matched.add(text)

    return res


def split(corpus_path, corpus_output, ini_output, scheme: str, ref: str, rules: dict):
    with open(corpus_path) as source, open(corpus_output, "w") as o_source, open(ini_output, "w") as o_source_ini:

        if ref == "":
            total_sents, total_matches, total_match_sents = 0, 0, 0
            for src in source.readlines():
                total_sents += 1
                src = src.strip('\n')
                src_matches = find(src, rules)
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

                src_matches = find(src_line, rules)
                tgt_matches = find(tgt_line, rules)
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


if __name__ == "__main__":

    txt = """RT @jokateM: Utu humfanya mtu awe kipenzi cha watu,utu humfanya mtu awe kimbilio la watu,aliyekosa utu hana mvuto kwa watu. 🙏🏽❤ She writes [ar]: ملخص تغطية وكالة الانباء الرسمية لمظاهرات امس: مواطنين اعتدوا على الشرطة فاضطروها لاستخدام الغاز المسيل للدموع http://suna-sd.net/suna/showNews/-fJi7HGycvs26Azq7aG4mmjptp-NQZ_WndSuVb1-KMY/1 #الخرا ds.CRIME BE PART OF VODACOM SUCCESS: https://t.co/Wzo1EckNhe via @YouTube CEO wa @MeTL_Group, @moodewji akiwa katika majadiliano kwenye mkutano wa @africaceoforum unaofanyika Geneva, Switze... https://t.co/uBAXDYfmlQ
@earadiofm: #MICHEZO Msanii na Mbunge wa Mikumi @ProfessorJayTz akiwa na Seleman Matola katika uwanja wa Taifa kushuhudia mechi kati ya...RT @earadiofm: #MICHEZO Msanii na Mbunge wa Mikumi @ProfessorJayTz akiwa na Seleman Matola katika uwanja wa Taifa kushuhudia mechi kati ya...@Youtube She writes [ar]: ملخص تغطية وكالة الانباء الرسمية لمظاهرات امس: مواطنين اعتدوا على الشرطة فاضطروها لاستخدام الغاز المسيل للدموع http://suna-sd.net/suna/showNews/-fJi7HGycvs26Azq7aG4mmjptp-NQZ_WndSuVb1-KMY/1 ‫#الخراء‬"""

    rules = load_rules('emojis.ini', 'rules.ini', 'del')
    options = generate_options('rules.ini')
    matches = find(txt, rules)
    spans = [txt[m.start:m.end] for m in matches]

    print(spans)
    print(mark(txt, find(txt, rules), 'del'))
    print(visual(txt, matches, options, rules))
