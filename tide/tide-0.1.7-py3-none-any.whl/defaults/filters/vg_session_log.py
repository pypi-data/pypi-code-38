from filter_predicate_base import filter_predicate_base

class vg_session_log(filter_predicate_base):

    @property
    def line_formatters(self):
        return [self.remove_unescaped_characters]

    @property
    def pre_processors(self):
        return [self.split_to_array_by_newline_char]

    def remove_unescaped_characters(self, line):
        return line.replace("\r", "").replace("'", "''").replace("\\t", "    ").replace("\\n", "")

    def split_to_array_by_newline_char(self, lines):
        if isinstance(lines, str):
            return lines.split("\n")
        return lines
