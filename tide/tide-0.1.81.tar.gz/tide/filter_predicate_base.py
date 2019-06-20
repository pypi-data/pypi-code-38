from abc import ABC, abstractmethod
import re
from config import Config

class filter_predicate_base(ABC):

    def __init__(self, lines):
        self.__get_set_matches(lines, self.line_matchers_pre)
        self.processed_lines = self.__process_lines(lines)
        self.__get_set_matches(self.processed_lines, self.line_matchers_post)

    def __process_lines(self, lines):
        lines = self.__run_pre_processors(lines)
        lines = self.__check_for_excluded(lines)
        lines = self.__run_formatters(lines)
        lines = self.__run_post_processors(lines)
        return lines

    def __check_for_excluded(self, lines):
        for line in lines:
            for excluded_line in self.excluded_lines:
                if excluded_line in line:
                    lines.remove(line)
        return lines

    def __run_formatters(self, lines):
        for formatter in self.line_formatters:
            single_formatter = []
            for line in lines:
                tmp_line = formatter(line)
                if tmp_line:
                    if isinstance(tmp_line, list):
                        single_formatter.extend(tmp_line)
                    else:
                        single_formatter.append(tmp_line)
            lines = single_formatter
        return lines

    def __get_set_matches(self, lines, line_matchers):
        for matcher in line_matchers:
            matcher_type = matcher['type'].lower()
            if matcher_type == 'array':
                self.__iterate_lines_for_array_match(lines, matcher)
            elif matcher_type == 'bool':
                self.__iterate_lines_for_bool_match(lines, matcher)

    def __iterate_lines_for_bool_match(self, lines, matcher):
        regex = re.compile(matcher['regex'])
        for line in lines:
            match = re.search(matcher['regex'], line)
            if match:
                Config().get()["variables"][matcher["variable_name"]] = 1
                return

    def __iterate_lines_for_array_match(self, lines, matcher):
        matches_list = []
        for line in lines:
            match = re.search(matcher['regex'], line)
            if match:
                matches_list.append(match.group(1))
        Config().get()["variables"][matcher["variable_name"]] = matches_list

    def __run_pre_processors(self, lines):
        for processor in self.pre_processors:
            lines = processor(lines)
        return lines

    def __run_post_processors(self, lines):
        for processor in self.post_processors:
            lines = processor(lines)
        return lines

    # the following properties/methods are intended to be overwritten

    @property
    def excluded_lines(self):
        return []

    @property
    def line_formatters(self):
        return []

    @property
    def line_matchers_pre(self):
        return []

    @property
    def line_matchers_post(self):
        return []

    @property
    def pre_processors(self):
        return []

    @property
    def post_processors(self):
        return []
