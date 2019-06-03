from __future__ import division

from django.utils.translation import ugettext as _
from votebase.core.statistics.handlers.general import CsvHandler


class MatrixRadioCsvHandler(CsvHandler):
    def write_options(self):
        # set row information
        self.options_rows = self.question.option_set.all().orientation_row()
        self.options_columns = self.question.option_set.all().orientation_column()

        self.rows=[]
        for option_row in self.options_rows:
            columns = []

            for option_column in self.options_columns:
                answers = self.answers.filter(
                    option=option_row, option_column=option_column)
                count = answers.count()

                try:
                    percent = count * 100 / self.total_answers_count
                except ZeroDivisionError:
                    percent = 0

                columns.append({
                    'count': answers.count(),
                    'percent': round(percent, 2)
                })

            self.rows.append({
                'id': option_row.id,
                'title': option_row.get_image_title(),
                'columns': columns
            })


        #HEADER
        self.writer.writerow([_(u'Rows and columns'),])

        columns_header_ids = [_(u'ID'), '']
        columns_header_ids += self.options_columns.values_list(
            'id', flat=True)

        columns_header_titles = ['', _(u'Title')]
        columns_header_titles += self.options_columns.values_list(
            'title', flat=True)

        self.writer.writerow(columns_header_ids)
        self.writer.writerow(columns_header_titles)

        for row in self.rows:
            row_to_write = [row['id'],row['title']]

            for column in row['columns']:
                row_to_write.append('%d (%s%%)' % (
                    column['count'], column['percent']))

            self.writer.writerow(row_to_write)

        self.writer.writerow([
            '',
            _(u'Total answers'),
            self.total_answers_count
        ])

        self.writer.writerow([])

    def write_answers(self):
        self.writer.writerow([_(u'Answers and voters'),])
        self.writer.writerow([_(u'Total answers'), self.total_answers_count,])
        self.writer.writerow([_(u'Total voters'), self.total_voters_count,])
        self.writer.writerow([
            _(u'Answer ID'),
            _(u'Voter ID'),
            _(u'User ID'),
            _(u'User fullname'),
            #            _(u'Question ID'),
            #            _(u'Question Title'),
            _(u'Row option ID'),
            _(u'Row option title'),
            _(u'Column option ID'),
            _(u'Column option title'),
            _(u'Created'),
            ])

        for answer in self.answers:
            # user
            user = answer.voter.user
            user_id = '' if user is None else user.id
            full_name = '' if user is None else user.get_profile().get_full_name()

            # row option
            row_option = answer.option
            row_option_id = '' if row_option is None else row_option.id
            row_option_title = '' if row_option is None else row_option.title

            # column option
            column_option = answer.option_column
            column_option_id = '' if column_option is None else column_option.id
            column_option_title = '' if column_option is None else column_option.title

            self.writer.writerow([
                answer.id,
                answer.voter.id,
                user_id,
                full_name,
                #                answer.question.id,
                #                answer.question.title,
                row_option_id,
                row_option_title,
                column_option_id,
                column_option_title,
                answer.created.astimezone(self.tz)
            ])

    def export(self):
        self.count_answers()
        self.write_header()
        self.write_options()
#        self.write_answers()
        return super(MatrixRadioCsvHandler, self).export()

