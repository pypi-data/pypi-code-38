from django.db.models.aggregates import Avg

from votebase.core.statistics.views.graphs.general import GraphOptionsQuestionView


class GraphStarsView(GraphOptionsQuestionView):
    template_name = 'statistics/graphs/stars.html'

    def get(self, request, pk, round_pk = None):
        # fast solution, but be aware!!! keep option ordering disabled
        # and let the weight be in sequence <1,n>
        self.average = self.all_answers.aggregate(Avg('option__weight'))['option__weight__avg']
        if self.average is None:
            self.average = 0

        # very slow solution, but safe:
#        sum = 0
#        for answer in self.all_answers:
#            sum += int(answer.option.title)
#        self.average = round(float(sum) / self.total_answers_count, 2)

        # final percentage
        num_options = self.question.option_set.all().count()

        self.percent = self.average * 100 / self.question.option_set.all().count() if num_options > 0 else 100

        return self.render_to_response({
            'survey': self.survey,
            'round': self.round,
            'question': self.question,
#            'options': self.options,
            'total_answers': self.total_answers_count,
            'average': round(self.average, 2),
            'average_int': int(round(self.average, 0)),
            'percent': self.percent,
            'export_url': self.get_export_url(),
            'is_public_view': self.is_public_view
            })
