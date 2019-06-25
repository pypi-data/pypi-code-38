from django.core.management.base import BaseCommand, CommandError
from pyelasticsearch import ElasticHttpNotFoundError

from ievv_opensource.ievv_elasticsearch import autoindex


class Command(BaseCommand):
    help = 'Rebuild elasticsearch index (one, many or all).'

    def add_arguments(self, parser):
        parser.add_argument('indexname', nargs='+', type=str,
                            help='Name of a search index. If you use the special value ALL, we will'
                                 're-build all search indexes.')

    def handle(self, *args, **options):
        indexnames = options['indexname']
        indexregistry = autoindex.Registry.get_instance()
        if len(indexnames) == 1 and indexnames[0] == 'ALL':
            indexnames = indexregistry.get_indexnames()
        else:
            for indexname in indexnames:
                if indexname not in indexregistry:
                    raise CommandError('No index named "{}" in the search index registry.'.format(indexname))
        if not indexnames:
            raise CommandError('No search indexes found.')
        self.stdout.write('Re-indexing the following indexes: {}.'.format(
            ', '.join(indexnames)))

        # Recreate the indexes
        for indexname in indexnames:
            index = indexregistry.get(indexname)
            try:
                index.delete_index()
            except ElasticHttpNotFoundError:
                pass
            index.create()

        # Index the most important items
        for indexname in indexnames:
            index = indexregistry.get(indexname)
            index.index_items(index.iterate_important_documents())

        # Last, index the all items
        for indexname in indexnames:
            index = indexregistry.get(indexname)
            index.index_items(index.iterate_all_documents())
