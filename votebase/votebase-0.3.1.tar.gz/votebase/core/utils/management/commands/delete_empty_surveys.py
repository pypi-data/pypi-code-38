# -*- coding: utf-8 -*-

from progressbar import ProgressBar, Percentage, Bar

from django.db.models import Q, Count
from django.core.management.base import BaseCommand

from votebase.core.surveys.models import Survey


class Command(BaseCommand):

    def handle(self, *args, **options):
        empty_surveys = Survey.objects.\
            filter(Q(title='Your new survey') | Q(title='Tvoj nový prieskum')).\
            annotate(question_count=Count('question')).\
            filter(question_count=0).\
            order_by('-question_count')

        if not empty_surveys.exists():
            print 'There are not empty surveys with default title.'
            return

        total = empty_surveys.count()
        progress_bar = ProgressBar(widgets=[Percentage(), Bar()], maxval=total).start()

        print 'There are %s empty surveys with default title.' % total

        counter = 0
        for survey in empty_surveys:
            #print survey, survey.question_count
            if survey.question_count == 0:
                survey.delete()
            counter += 1
            progress_bar.update(counter)
        progress_bar.finish()

        print 'Successfully deleted %d surveys.' % total

        print 'Available surveys:'
        for survey in Survey.objects.all():
            print survey