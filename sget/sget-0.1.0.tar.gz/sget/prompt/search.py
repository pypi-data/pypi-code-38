import re


from prompt_toolkit.completion import FuzzyCompleter, Completion
from prompt_toolkit.completion.fuzzy_completer import _FuzzyMatch
from prompt_toolkit.layout.menus import _get_menu_item_fragments
from prompt_toolkit.layout.controls import UIControl, UIContent
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Document


def _content_match(snippet, word):
    if snippet.content.startswith(word):
        return snippet.content
    return None


def _name_match(snippet, word):
    if snippet.name.startswith(word):
        return snippet.name
    return None


def _description_match(snippet, word):
    if snippet.description.startswith(word):
        return snippet.description
    return None


def _filter_by_group(snippets, filter_groups):
    for snippet in snippets:
        for group in snippet.groups:
            if group in filter_groups:
                yield snippet
                break


class SnippetSearcher(FuzzyCompleter):
    SEARCH_MODES = {'CONTENT': _content_match,
                    'NAME': _name_match,
                    'DESCRIPTION': _description_match}

    def __init__(self, snippets):
        super(SnippetSearcher).__init__()
        self._snippets = snippets
        self._mode_idx = -1
        self.match = None
        self.search_mode = ''
        self.toggle_search_mode()

    def toggle_search_mode(self):
        self._mode_idx = (self._mode_idx + 1) % len(SnippetSearcher.SEARCH_MODES)
        self.search_mode = list(SnippetSearcher.SEARCH_MODES.keys())[self._mode_idx]
        self.match = SnippetSearcher.SEARCH_MODES[self.search_mode]

    def get_completions(self, document, complete_event):
        prompt_content = document.text_before_cursor
        text, groups = SnippetSearcher.parse_group_filters(prompt_content)
        offset = len(prompt_content) - len(text)
        doc_text = document.text[offset:document.cursor_position - len(text)]
        cursor_pos = document.cursor_position - len(text) - offset
        doc2 = Document(text=doc_text, cursor_position=cursor_pos)

        word_completions = self._get_completions(doc2, groups)
        completions = self._to_fuzzy_completions(word_completions, text)
        return completions

    @staticmethod
    def parse_group_filters(text):
        filtered_groups = []
        rest_text = text
        if text.startswith('group='):
            filter_content = text.split(' ')[0]
            rest_text = ' '.join(text.split(' ')[1:])
            groups = filter_content.split('=')[1]
            filtered_groups = groups.split(',')
        return rest_text, filtered_groups

    def _get_completions(self, doc, filter_groups):
        word = doc.get_word_before_cursor().strip()
        snippets = self._snippets
        if filter_groups:
            snippets = _filter_by_group(self._snippets, filter_groups)
        for snippet in snippets:
            match = self.match(snippet, word)
            if match is None:
                continue
            yield Completion(match,
                             start_position=-len(word),
                             style='fg:white bg:black',
                             selected_style='bg:green')

    def _to_fuzzy_completions(self, completions, word):
        fuzzy_matches = []
        pat = '.*?'.join(map(re.escape, word))
        pat = '(?=({0}))'.format(pat)
        regex = re.compile(pat, re.IGNORECASE)
        for compl in completions:
            matches = list(regex.finditer(compl.text))
            if matches:
                # Prefer the match, closest to the left, then shortest.
                best = min(matches, key=lambda m: (m.start(), len(m.group(1))))
                fuzzy_matches.append(_FuzzyMatch(len(best.group(1)),
                                                 best.start(),
                                                 compl))

        def sort_key(fuzzy_match):
            " Sort by start position, then by the length of the match. "
            return fuzzy_match.start_pos, fuzzy_match.match_length

        fuzzy_matches = sorted(fuzzy_matches, key=sort_key)

        for match in fuzzy_matches:
            old_comp = match.completion
            start_pos = old_comp.start_position - len(word)
            display = self._get_display(match, word)
            style = old_comp.style
            selected_style = old_comp.selected_style
            completion = Completion(old_comp.text,
                                    display=display,
                                    start_position=start_pos,
                                    style=style,
                                    selected_style=selected_style)
            yield completion


class SearchControl(UIControl):
    def create_content(self, width, height):
        complete_state = get_app().current_buffer.complete_state
        if complete_state:
            completions = complete_state.completions
            completion_index = complete_state.complete_index
        else:
            completions = []
            completion_index = -1

        def get_line(idx):
            completion = completions[idx]
            is_curr_completion = (idx == completion_index)
            return _get_menu_item_fragments(completion,
                                            is_curr_completion,
                                            width)
        return UIContent(get_line, line_count=len(completions))
