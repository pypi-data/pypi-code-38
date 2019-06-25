import json

from django.views.generic import TemplateView
from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listfilter.basefilters.single.abstracttextinput import AbstractSearch
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from ievv_opensource import ievv_elasticsearch2


class IndexItemValue(listbuilder.itemvalue.FocusBox):
    template_name = 'ievv_elasticsearch2browser/indexbrowse/itemvalue.django.html'

    def prettify(self):
        jsonstring = json.dumps(self.value.to_dict(), indent=2)
        return highlight(jsonstring, JsonLexer(), HtmlFormatter(
            style='tango', noclasses=True,
            nowrap=True))


class SearchFilter(AbstractSearch):
    def __init__(self, *args, **kwargs):
        self.indexname = kwargs.pop('indexname', None)
        super(SearchFilter, self).__init__(*args, **kwargs)

    def copy(self):
        copy = super(SearchFilter, self).copy()
        copy.indexname = self.indexname
        return copy

    # def __get_all_string_fields(self):
    #     searchapi = search.Connection.get_instance()
    #     searchresponse = searchapi.elasticsearch.get_mapping(index=self.indexname)
    #     stringfields = ['_id']
    #     nestedfields = {}
    #     for indexname, indexdict in searchresponse.items():
    #         for doc_type, mappingdict in indexdict['mappings'].items():
    #             for fieldname, propertydict in mappingdict.get('properties', {}).items():
    #                 if propertydict['type'] == 'string':
    #                     stringfields.append(fieldname)
    #                 elif propertydict['type'] == 'nested':
    #                     nestedfieldfieldslist = []
    #                     for nestedfieldname, nestedpropertydict in propertydict['properties'].items():
    #                         if nestedpropertydict['type'] == 'string':
    #                             nestedfieldpath = '{}.{}'.format(fieldname, nestedfieldname)
    #                             nestedfieldfieldslist.append(nestedfieldpath)
    #                     nestedfields[fieldname] = nestedfieldfieldslist
    #
    #     return stringfields, nestedfields
    #
    # def __make_globalfields_query(self, stringfields, cleaned_value):
    #     return {
    #         'multi_match': {
    #             'query': cleaned_value,
    #             'fields': stringfields
    #         }
    #     }

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        print()
        print("*" * 70)
        print()
        print(cleaned_value)
        print()
        print("*" * 70)
        print()

        if cleaned_value in ('', None):
            return queryobject
        else:
            return queryobject.query('multi_match', query=cleaned_value, fields=['_all'])
            # stringfields, nestedfields = self.__get_all_string_fields()
            # if nestedfields:
            #     query = {
            #         'bool': {
            #             'should': [
            #                 self.__make_globalfields_query(stringfields=stringfields,
            #                                                cleaned_value=cleaned_value)
            #             ]
            #         }
            #     }
            #     for nestedfieldname, nestedfields in nestedfields.items():
            #         query['bool']['should'].append({
            #             'nested': {
            #                 'path': nestedfieldname,
            #                 'query': self.__make_globalfields_query(stringfields=nestedfields,
            #                                                         cleaned_value=cleaned_value)
            #             }
            #         })
            #     return query
            # else:
            #     return self.__make_globalfields_query(stringfields=stringfields, cleaned_value=cleaned_value)


class IndexItemView(listbuilderview.FilterListMixin, listbuilderview.ViewMixin, TemplateView):
    MAX_ITEMS = 2000
    value_renderer_class = IndexItemValue

    def get_pagetitle(self):
        return 'TODO'

    def get_no_items_message(self):
        return 'Nothing matching your search found'

    def get_indexname(self):
        return None

    def get(self, *args, **kwargs):
        return super(IndexItemView, self).get(*args, **kwargs)

    def __get_searchresult(self):
        search = ievv_elasticsearch2.Search()\
            .query('match_all')
        search = self.get_filterlist().filter(search)
        return search.execute()

        # query = {
        #     'match_all': {}
        # }
        # query = self.get_filterlist().filter(query)
        # return searchapi.wrapped_search(index=self.get_indexname(), query={
        #     'size': self.MAX_ITEMS,
        #     'query': query
        # })

    def get_listbuilder_list_value_iterable(self, context):
        return self.__get_searchresult()

    def add_filterlist_items(self, filterlist):
        """
        Add the filters to the filterlist.
        """
        filterlist.append(SearchFilter(
            slug='search',
            label='Search',
            label_is_screenreader_only=True,
            indexname=self.get_indexname()))

    def get_filterlist_url(self, filters_string):
        """
        This is used by the filterlist to create URLs.
        """
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME, kwargs={'filters_string': filters_string})


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^(?P<filters_string>.+)?$',
            IndexItemView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
