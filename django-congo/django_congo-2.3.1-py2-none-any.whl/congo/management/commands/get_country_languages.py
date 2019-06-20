# encoding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings

# python manage.py get_country_languages


class Command(BaseCommand):
    help = u'Pobiera języki dla poszczególnych państw wg częstości używania'

    def add_arguments(self, parser):
        parser.add_argument('country_list', nargs = '*', type = str)

    def handle(self, *args, **options):
        country_list = options['country_list']

        if not country_list:
            country_list = dict(settings.CONGO_COUNTRIES).keys()

        self.init_territory_languages()

        for c in country_list:
            try:
                lang = self.get_official_locale_ids(c)[0].replace('_%s' % c, '')
                print "'%s': '%s'," % (c, lang)
            except IndexError:
                pass

    def init_territory_languages(self):
        import lxml
        import urllib

        langxml = urllib.urlopen('http://unicode.org/repos/cldr/trunk/common/supplemental/supplementalData.xml')
        langtree = lxml.etree.XML(langxml.read())

        self.territory_languages = {}

        for t in langtree.find('territoryInfo').findall('territory'):
            langs = {}
            for l in t.findall('languagePopulation'):
                langs[l.get('type')] = {
                    'percent': float(l.get('populationPercent')),
                    'official': bool(l.get('officialStatus'))
                }
            self.territory_languages[t.get('type')] = langs

    def get_official_locale_ids(self, country_code):
        country_code = country_code.upper()
        try:
            langs = self.territory_languages[country_code].items()
            # most widely-spoken first:
            langs.sort(key = lambda l: l[1]['percent'], reverse = True)
            return [
                '{lang}_{terr}'.format(lang = lang, terr = country_code)
                for lang, spec in langs if spec['official']
            ]
        except IndexError:
            return []
