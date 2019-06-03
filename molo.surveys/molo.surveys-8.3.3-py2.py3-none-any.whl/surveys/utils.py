from __future__ import unicode_literals

from django.core.paginator import Page, Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.functional import cached_property

from .blocks import SkipState


class SkipLogicPaginator(Paginator):
    """
    Breaks a series of questions into pages based on the logic
    associated with the question. Skipped questions result in
    empty entries to the data.
    """
    def __init__(self, object_list, data=dict(), answered=dict()):
        # Create a mutatable version of the query data
        self.new_answers = data.copy()
        self.previous_answers = answered

        super(SkipLogicPaginator, self).__init__(object_list, per_page=1)

        self.question_labels = [
            question.clean_name for question in self.object_list
        ]

        self.page_breaks = [
            i + 1 for i, field in enumerate(self.object_list)
            if field.has_skipping or field.page_break
        ]

        num_questions = self.object_list.count()

        if self.page_breaks:
            # Always have a break at start to create first page
            self.page_breaks.insert(0, 0)
            if self.page_breaks[-1] != num_questions:
                # Must break for last page
                self.page_breaks.append(num_questions)
        else:
            # display one question per page
            self.page_breaks = list(range(num_questions + 1))

        # add the missing data
        self.new_answers.update({
            checkbox.clean_name: 'off'
            for checkbox in self.missing_checkboxes
        })

    def _get_page(self, *args, **kwargs):
        return SkipLogicPage(*args, **kwargs)

    @cached_property
    def num_pages(self):
        return len(self.page_breaks) - 1

    @cached_property
    def last_question_index(self):
        # The last question on the current page
        return self.page_breaks[self.current_page] - 1

    @cached_property
    def current_page(self):
        # search backwards to ensure we find correct lower bound
        reversed_breaks = reversed(self.page_breaks)
        page_break = next(
            index for index in reversed_breaks
            if index <= self.first_question_index
        )
        return self.page_breaks.index(page_break) + 1

    @cached_property
    def first_question_index(self):
        # The first question on the current page
        last_answer = self.last_question_previous_page
        if last_answer >= 0:
            # It isn't the first page
            return self.next_question_from_previous_index(
                last_answer, self.previous_answers)
        return 0

    @cached_property
    def last_question_previous_page(self):
        previous_answers_indexes = self.index_of_questions(
            self.previous_answers)
        try:
            return max(previous_answers_indexes)
        except ValueError:
            # There have been no previous questions, its the first page
            return -1

    def next_question_from_previous_index(self, index, data):
        last_question = self.object_list[index]
        last_answer = data.get(last_question.clean_name)
        if last_question.is_next_action(last_answer, SkipState.QUESTION):
            # Sorted or is 0 based in the backend and 1 on the front
            next_question_id = last_question.next_page(last_answer) - 1
            question_ids = [
                question.sort_order for question in self.object_list
            ]
            return question_ids.index(next_question_id)

        return index + 1

    @cached_property
    def next_question_index(self):
        if self.new_answers:
            return self.next_question_from_previous_index(
                self.last_question_index,
                self.new_answers,
            )
        return 0

    @cached_property
    def next_page(self):
        try:
            return next(
                page for page, break_index in enumerate(self.page_breaks)
                if break_index > self.next_question_index
            )
        except StopIteration:
            return self.num_pages

    @cached_property
    def previous_page(self):
        # Prevent returning 0 if the on the first page
        return max(1, next(
            page for page, break_index in enumerate(self.page_breaks)
            if break_index > self.last_question_previous_page
        ))

    def index_of_questions(self, data):
        return [
            self.question_labels.index(question) for question in data
            if question in self.question_labels
        ]

    @cached_property
    def missing_checkboxes(self):
        return [
            question
            for question in self.object_list[
                # Correct for the slice
                self.first_question_index:self.last_question_index + 1
            ]
            if question.field_type == 'checkbox' and
            question.clean_name not in self.new_answers
        ]

    def page(self, number):
        number = self.validate_number(number)
        index = number - 1
        if not self.new_answers:
            top_index = index + self.per_page
            bottom = self.page_breaks[index]
            top = self.page_breaks[top_index]
        elif self.previous_page == number or self.current_page == number:
            # We are rebuilding the page with the data just submitted
            bottom = self.first_question_index
            # Correct for the slice
            top = self.last_question_index + 1
        else:
            index = self.next_page - 1
            bottom = self.next_question_index
            top_index = index + self.per_page
            top = self.page_breaks[top_index]

        return self._get_page(self.object_list[bottom:top], index + 1, self)


class SkipLogicPage(Page):
    def has_next(self):
        return super(SkipLogicPage, self).has_next() and not self.is_end()

    def possibly_has_next(self):
        return super(SkipLogicPage, self).has_next()

    @cached_property
    def last_question(self):
        return self.object_list[-1]

    @cached_property
    def last_response(self):
        return self.paginator.new_answers[self.last_question.clean_name]

    def is_next_action(self, *actions):
        try:
            question_response = self.last_response
        except KeyError:
            return False
        return self.last_question.is_next_action(question_response, *actions)

    def is_end(self):
        return self.is_next_action(SkipState.END, SkipState.SURVEY)

    def success(self, slug):
        if self.is_next_action(SkipState.SURVEY):
            return redirect(
                self.last_question.next_page(self.last_response).url
            )
        return redirect(
            reverse('molo.surveys:success', args=(slug, ))
        )

    def next_page_number(self):
        return self.paginator.next_page

    def previous_page_number(self):
        return self.paginator.previous_page
