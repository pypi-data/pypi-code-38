from django.core.management.base import BaseCommand, CommandError
from djangoldp_joboffer.factories import JobOfferFactory
from djangoldp_skill.models import Skill

class Command(BaseCommand):
    help = 'Mock data'

    def randomSkill(self, quantity: int = 10):
        query_set = Skill.objects.order_by('?')[:quantity]
        return query_set

    def add_arguments(self, parser):
        parser.add_argument('--size', type=int, default=0, help='Number of job offer to create')
        parser.add_argument('--sizeof', type=int, default=3, help='Number of skill required into each job offer created')

    def handle(self, *args, **options):
        for i in range(0, options['size']):
            random_skill = self.randomSkill(options['sizeof']);
            JobOfferFactory.create(skills=random_skill)

        self.stdout.write(self.style.SUCCESS('Successful data mock install'))
