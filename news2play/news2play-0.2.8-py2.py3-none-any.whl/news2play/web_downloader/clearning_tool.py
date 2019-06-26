import re


class RemoveHTML:
    def filter_tags(self, html_str):
        re_cdata = re.compile("//<!CDATA\[[>]∗//\]>", re.I)
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')
        re_h = re.compile('</?\w+[^>]*>')
        re_comment = re.compile('<!--[^>]*-->')
        s = re_cdata.sub('', html_str)
        s = re_script.sub('', s)
        s = re_style.sub('', s)
        s = re_br.sub('\n', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replace_char_entity(s)
        # s = s.replace("\n", "")
        s = s.lstrip("\n")
        res_blank = r'(?<=\w)\n(?=\w)'
        s = re.sub(res_blank, " ", s)
        res_raw = r"(?<=[\)\'])\n(?=\w)"
        s = re.sub(res_raw, "", s)
        return s

    @staticmethod
    def replace_char_entity(html_str):
        char_entities = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"''"', '34': '"', }
        re_char_entity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_char_entity.search(html_str)
        while sz:
            key = sz.group('name')
            try:
                html_str = re_char_entity.sub(char_entities[key], html_str, 1)
                sz = re_char_entity.search(html_str)
            except KeyError:
                html_str = re_char_entity.sub('', html_str, 1)
                sz = re_char_entity.search(html_str)
        return html_str

    @staticmethod
    def replace(s, re_exp, repl_string):
        return re_exp.sub(repl_string, s)
