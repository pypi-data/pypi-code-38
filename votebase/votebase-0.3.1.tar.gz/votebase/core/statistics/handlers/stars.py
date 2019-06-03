from __future__ import division

import unicodecsv

from django.core.validators import EMPTY_VALUES
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from votebase.core.statistics.handlers.general import OptionsQuestionCsvHandler

from votebase.core.voting.models import Answer

class StarsCsvHandler(OptionsQuestionCsvHandler):
    def write_options(self):
        # set option information
        self.options = []
        for option in self.question.option_set.all():
            option_answers = self.answers.filter(option=option)
            count = option_answers.count()

            try:
                percent = count * 100 / self.total_answers_count
            except ZeroDivisionError:
                percent = 0

            self.options.append({
                'id': option.id,
                'title': option.title,
                'count': count,
                'percent': round(percent, 2)
            })

        #HEADER
        self.writer.writerow([_(u'Options'),])
        self.writer.writerow([
            _(u'ID'),
            _(u'Title'),
            _(u'Count'),
            _(u'Percent'),
            ])

        for option in self.options:
            self.writer.writerow([
                option['id'],
                option['title'],
                option['count'],
                '%s%%' % option['percent']
            ])

        self.writer.writerow([
            '',
            _(u'Total answers'),
            self.total_answers_count
        ])

        # AVERAGE
        sum = 0
        for answer in self.answers:
            sum += int(answer.option.title)
        self.average = round(float(sum) / self.total_answers_count, 2)
        self.average_percent = self.average * 100 / self.question.option_set.all().count()

        self.writer.writerow([
            '',
            _(u'Average'),
            self.average,
            '%s%%' % self.average_percent
        ])

        self.writer.writerow([])

    def export(self):
        self.count_answers()
        self.write_header()
        self.write_options()
#        self.write_answers()
        return super(OptionsQuestionCsvHandler, self).export()

