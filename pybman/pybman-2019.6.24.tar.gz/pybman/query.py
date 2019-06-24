from copy import deepcopy
from pybman import utils


class Query:

    def __init__(self):
        pass


class ConeQuery:

    def __init__(self):
        pass

class AllQuery:

    def __init__(self):
        self.files_query_fp = utils.resolve_path('static/elastic/item-all-files-released.json')
        self.locators_query_fp = utils.resolve_path('static/elastic/item-all-locators-released.json')

        self.files_query = utils.read_json(self.files_query_fp)
        self.locators_query = utils.read_json(self.locators_query_fp)

    def get_files_query(self):
        data = deepcopy(self.files_query)
        return data

    def get_locators_query(self):
        data = deepcopy(self.locators_query)
        return data

class ContextQuery:

    def __init__(self):

        self.item_query_fp = utils.resolve_path('static/elastic/item-ctx.json')
        self.item_released_query_fp = utils.resolve_path('static/elastic/item-ctx-released.json')

        self.item_query = utils.read_json(self.item_query_fp)
        self.item_released_query = utils.read_json(self.item_released_query_fp)

    def get_item_query(self, ctx_id):
        data = deepcopy(self.item_query)
        data['query']['term']['context.objectId']['value'] = ctx_id
        return data

    def get_released_item_query(self, ctx_id):
        data = deepcopy(self.item_released_query)
        data['query']['bool']['must'][2]['term']['context.objectId']['value'] = ctx_id
        return data


class OrgUnitQuery:

    def __init__(self):

        self.item_query_fp = utils.resolve_path('static/elastic/item-ou.json')
        self.item_released_query_fp = utils.resolve_path('static/elastic/item-ou-released.json')

        self.item_query = utils.read_json(self.item_query_fp)
        self.item_released_query = utils.read_json(self.item_released_query_fp)

    def get_item_query(self, ou_id):
        data = deepcopy(self.item_query)
        term = data['query']['bool']['should'][0]['term']
        term['metadata.creators.person.organizations.identifierPath']['value'] = ou_id
        term = data['query']['bool']['should'][1]['term']
        term['metadata.creators.organization.identifierPath']['value'] = ou_id
        return data

    def get_item_released_query(self, ou_id):
        data = deepcopy(self.item_released_query)
        term = data['query']['bool']['must'][2]['bool']['should'][0]['term']
        term['metadata.creators.person.organizations.identifierPath']['value'] = ou_id
        term = data['query']['bool']['must'][2]['bool']['should'][1]['term']
        term['metadata.creators.organization.identifierPath']['value'] = ou_id
        return data


class PersQuery:

    def __init__(self):

        self.item_query_fp = utils.resolve_path('static/elastic/item-pers.json')
        self.item_released_query_fp = utils.resolve_path('static/elastic/item-pers-released.json')

        self.item_query = utils.read_json(self.item_query_fp)
        self.item_released_query = utils.read_json(self.item_released_query_fp)

        self.cone_id_format = '/persons/resource/'

    def get_item_query(self, cone_id):
        data = deepcopy(self.item_query)
        data['query']['term']['metadata.creators.person.identifier.id']['value'] = self.cone_id_format + cone_id
        return data

    def get_item_released_query(self, cone_id):
        data = deepcopy(self.item_released_query)
        term = data['query']['bool']['must'][2]['term']
        term['metadata.creators.person.identifier.id']['value'] = self.cone_id_format + cone_id
        return data


class LangQuery:

    def __init__(self):
        self.item_query_fp = utils.resolve_path('static/elastic/item-lang.json')
        self.item_released_query_fp = utils.resolve_path('static/elastic/item-lang-released.json')

        self.item_query = utils.read_json(self.item_query_fp)
        self.item_released_query = utils.read_json(self.item_released_query_fp)

    def get_item_query(self, lang_id):
        data = deepcopy(self.item_query)
        data['query']['term']['metadata.languages']['value'] = lang_id
        return data

    def get_released_item_query(self, lang_id):
        data = deepcopy(self.item_released_query)
        data['query']['bool']['must'][2]['term']['metadata.languages']['value'] = lang_id
        return data

class JournalQuery:

    def __init__(self):
        self.item_query_fp = utils.resolve_path('static/elastic/item-jour.json')
        self.item_released_query_fp = utils.resolve_path('static/elastic/item-jour-released.json')

        self.item_query = utils.read_json(self.item_query_fp)
        self.item_released_query = utils.read_json(self.item_released_query_fp)

    def get_item_query(self, jour_name):
        data = deepcopy(self.item_query)
        data['query']['bool']['should'][0]['match_phrase']['metadata.sources.title']['query'] = jour_name
        data['query']['bool']['should'][1]['match_phrase']['metadata.sources.alternativeTitles.value']['query'] = jour_name
        return data

    def get_released_item_query(self, jour_name):
        data = deepcopy(self.item_released_query)
        data['query']['bool']['must'][2]['bool']['should'][0]['match_phrase']['metadata.sources.title']['query'] = jour_name
        data['query']['bool']['must'][2]['bool']['should'][1]['match_phrase']['metadata.sources.alternativeTitles.value']['query'] = jour_name
        return data
