# from pybman import local
# from pybman import export


class DataSet:

    def __init__(self, data_id, data=None, raw=None):

        self.idx = data_id

        if raw:
            self.collection = {"numberOfRecords": len(raw), "records": raw}
            self.num = len(raw)
            self.records = raw
            self.persons = self.get_cone_persons()

        elif data:
            self.collection = data
            self.num = len(data['records'])
            self.records = data['records']
            self.persons = self.get_cone_persons()

        else:
            # print("please pass (raw) data for initialization!")
            self.collection = {}
            self.num = 0
            self.records = []
            self.persons = {}
            # self.creators = []

    # get creators of items
    def get_creators(self):
        creators = []
        for record in self.records:
            if 'creators' in record['data']['metadata']:
                creators_list = record['data']['metadata']['creators']
                for creator in creators_list:
                    creators.append(creator)
        return creators

    def get_creators_from_records(self):
        creators = []
        for record in self.records:
            if 'creators' in record['data']['metadata']:
                creators.append(record['data']['metadata']['creators'])
        return creators

    def get_creators_data(self):
        creators = {}
        for record in self.records:
            if 'creators' in record['data']['metadata']:
                creators_list = record['data']['metadata']['creators']
                found = False
                for creator in creators_list:
                    if 'person' in creator:
                        found = True
                        if 'identifier' in creator['person']:
                            idx = creator['person']['identifier']['id'].split("/")[-1]
                            if idx in creators:
                                creators[idx].append(record)
                            else:
                                creators[idx] = [record]
                        else:
                            continue
                            # if 'givenName' in creator['person'] and 'familyName' in creator['person']:
                            #    pers_name = creator['person']['givenName'] + " " + creator['person']['familyName']
                            #    # print("no identifier found for", pers_name)
                            # elif 'givenName' not in person and 'familyName' in person:
                            #    # pers_name = creator['person']['familyName']
                            #    # print("no identifier found for", pers_name,"of",record['data']['objectId'])
                            # else:
                            #    # print("no identifier found for creator of", record['data']['objectId'])
                if not found:
                    print("no person found for", record['data']['objectId'])
        return creators

    def get_cone_persons(self):
        persons = {}
        for creator in self.get_creators():
            if creator['type'] == 'PERSON':
                if 'identifier' in creator['person']:
                    if creator['person']['identifier']['type'] == 'CONE':
                        if creator['person']['identifier']['id'] not in persons:
                            cone_id = creator['person']['identifier']['id'].split("/")[-1]
                            if 'givenName' in creator['person']:
                                name = creator['person']['givenName']
                                if 'familyName' in creator['person']:
                                    name += ' ' + creator['person']['familyName']
                            else:
                                if 'familyName' in creator['person']:
                                    name = creator['person']['familyName']
                                else:
                                    print('no name found for', cone_id)
                                    name = ''
                            persons[cone_id] = name
        return persons


#    def init_pers_data(self):
#        pers_data = []
#        for p in self.persons:
#            p_data = export.get_pers(p)
#            p_idx = p.split('/')[-1]
#            pers_data.append(DataSet(p_idx,data=p_data))
#        return pers_data

    def get_organizations(self):
        organizations = {}
        for record in self.records:
            if 'creators' in record['data']['metadata']:
                creators_list = record['data']['metadata']['creators']
                for creator in creators_list:
                    if creator['type'] == 'PERSON':
                        person = creator['person']
                        if 'organizations' in person:
                            for organization in person['organizations']:
                                if organization['name'] in organizations:
                                    organizations[organization['name']].append(record['data']['objectId'])
                                else:
                                    organizations[organization['name']] = [record['data']['objectId']]
                        else:
                            print("no organization found for", person)
                    elif creator['type'] == 'ORGANIZATION':
                        organization = creator['organization']
                        if organization['name'] in organizations:
                            organizations[organization['name']].append(record['data']['objectId'])
                        else:
                            organizations[organization['name']] = [record['data']['objectId']]
                    else:
                        print("unknown creator type", creator['type'])
            else:
                print(record['data']['objectId'], "has no creator!")
        return organizations

    # get titles of items
    def get_titles(self):
        titles = {}
        for record in self.records:
            title = record['data']['metadata']['title']
            if title in titles:
                titles[title].append(record['data']['objectId'])
            else:
                titles[title] = [record['data']['objectId']]
            # titles.append(record['data']['metadata']['title'])
        return titles

    # get titles from source of items
    def get_titles_from_source(self):
        source_titles = {}
        for record in self.records:
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    if source['title'] in source_titles:
                        source_titles[source['title']].append(record['data']['objectId'])
                    else:
                        source_titles[source['title']] = [record['data']['objectId']]
                    # source_titles.append(source['title'])
        return source_titles

    # get list of genres from collection
    def get_genres(self):
        genres = {}
        for record in self.records:
            if record['data']['metadata']['genre'] in genres:
                genres[record['data']['metadata']['genre']].append(record['data']['objectId'])
            else:
                genres[record['data']['metadata']['genre']] = [record['data']['objectId']]
        return genres

    # get list of genres from collection
    def get_genre_data(self):
        genres = {}
        for record in self.records:
            if record['data']['metadata']['genre'] in genres:
                genres[record['data']['metadata']['genre']].append(record)
            else:
                genres[record['data']['metadata']['genre']] = [record]
        return genres

    # get publication places of items
    def get_places(self):
        places = {}
        for record in self.records:
            if 'publishingInfo' in record['data']['metadata']:
                if 'place' in record['data']['metadata']['publishingInfo']:
                    place = record['data']['metadata']['publishingInfo']['place']
                    if place in places:
                        places[place].append(record['data']['objectId'])
                    else:
                        places[place] = [record['data']['objectId']]
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    if 'publishingInfo' in source:
                        if 'place' in source['publishingInfo']:
                            place = source['publishingInfo']['place']
                            if place in places:
                                places[place].append(record['data']['objectId'])
                            else:
                                places[place] = [record['data']['objectId']]
        return places
    
    def get_contexts(self):
        contexts = {}
        for record in self.records:
            item_idx = record['data']['objectId']
            ctx_idx = record['data']['context']['objectId']
            contexts[item_idx] = ctx_idx
        return contexts

    # get publishers of items
    def get_publishers(self):
        publishers = {}
        for record in self.records:
            if 'publishingInfo' in record['data']['metadata']:
                if 'publisher' in record['data']['metadata']['publishingInfo']:
                    publisher = record['data']['metadata']['publishingInfo']['publisher']
                    if publisher in publishers:
                        publishers[publisher].append(record['data']['objectId'])
                    else:
                        publishers[publisher] = [record['data']['objectId']]
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    if 'publishingInfo' in source:
                        if 'publisher' in source['publishingInfo']:
                            publisher = source['publishingInfo']['publisher']
                            if publisher in publishers:
                                publishers[publisher].append(record['data']['objectId'])
                            else:
                                publishers[publisher] = [record['data']['objectId']]
        return publishers

    def get_journals(self):
        journals = {}
        items = self.get_source_from_items_with_source_genre("JOURNAL")
        for k in items:
            if items[k]['title'] in journals:
                journals[items[k]['title']].append(k)
            else:
                journals[items[k]['title']] = [k]
        return journals

    def get_journals_data(self):
        journals = {}
        items = self.get_source_from_items_with_source_genre("JOURNAL")
        for k in items:
            if items[k]['title'] in journals:
                journals[items[k]['title']].append(self.get_item(k))
            else:
                journals[items[k]['title']] = [self.get_item(k)]
        return journals

    def get_series(self):
        series = {}
        items = self.get_source_from_items_with_source_genre("SERIES")
        for k in items:
            if items[k]['title'] in series:
                series[items[k]['title']].append(k)
            else:
                series[items[k]['title']] = [k]
        return series

    def get_years(self):
        years = {}
        for record in self.records:
            if 'datePublishedInPrint' in record['data']['metadata']:
                year = record['data']['metadata']['datePublishedInPrint'].split("-")[0]
                if year in years:
                    years[year].append(record['data']['objectId'])
                else:
                    years[year] = [record['data']['objectId']]
            elif 'datePublishedOnline' in record['data']['metadata']:
                year = record['data']['metadata']['datePublishedOnline'].split("-")[0]
                if year in years:
                    years[year].append(record['data']['objectId'])
                else:
                    years[year] = [record['data']['objectId']]
            else:
                print("no publication date found for", record['data']['objectId'])
        return years

    def get_years_data(self):
        years = {}
        for record in self.records:
            if 'datePublishedInPrint' in record['data']['metadata']:
                year = record['data']['metadata']['datePublishedInPrint'].split("-")[0]
                if year in years:
                    years[year].append(record)
                else:
                    years[year] = [record]
            elif 'datePublishedOnline' in record['data']['metadata']:
                year = record['data']['metadata']['datePublishedOnline'].split("-")[0]
                if year in years:
                    years[year].append(record)
                else:
                    years[year] = [record]
            else:
                print("no publication date found for", record['data']['objectId'])
        return years

    def get_languages(self):
        languages = {}
        #for record in self.records:
        #    if 'languages' in record['data']['metadata']:
        #        item_idx = record['data']['objectId']
        #        lang = record['data']['metadata']['languages']
        #        languages[item_idx] = lang
        #        else:
        #            print(record['data']['objectId'], "has no language!")
        return languages

    def get_languages_data(self):
        languages = {}
        for record in self.records:
            if 'languages' in record['data']['metadata']:
                lang = record['data']['metadata']['languages']
                if len(lang) == 1:
                    if lang[0] in languages:
                        languages[lang[0]].append(record)
                    else:
                        languages[lang[0]] = [record]
                elif len(lang) > 1:
                    # print(record['data']['objectId'], "has more than one language!")
                    for l in lang:
                        if l in languages:
                            languages[l].append(record)
                        else:
                            languages[l] = [record]
                else:
                    print(record['data']['objectId'], "has no language!")
        return languages

    # get identifiers from sources of items
    def get_sources_identifiers(self):
        source_idx = {}
        for record in self.records:
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    if 'identifiers' in source:
                        for identifier in source['identifiers']:
                            identifier_type = identifier['type']
                            if identifier_type in source_idx:
                                source_idx[identifier_type].append(record['data']['objectId'])
                            else:
                                source_idx[identifier_type] = [record['data']['objectId']]
        return source_idx

    def get_sources_titles(self, genre=None):
        source_titles = {}
        for record in self.records:
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    title = source['title']
                    if title in source_titles:
                        source_titles[title].append(record['data']['objectId'])
                    else:
                        source_titles[title] = [record['data']['objectId']]
        return source_titles

    # get items with state 'submitted'
    def get_items_submitted(self):
        submitted = {}
        for record in self.records:
            if record['data']['publicState'] == 'SUBMITTED':
                if record['data']['versionState'] == 'SUBMITTED':
                    submitted[record['persistenceId']] = record['data']
        return submitted

    # get items with state 'submitted'
    def get_items_released(self):
        released = []
        for record in self.records:
            if record['data']['publicState'] == 'RELEASED':
                if record['data']['versionState'] == 'RELEASED':
                    released.append(record)
        return released

    # get item from collection by given id
    def get_item(self, item_id):
        item = {}
        for record in self.records:
            if item_id == record['data']['objectId']:
                item = record
                break
        return item

    # get items from collection with given genre
    def get_items_with_genre(self, genre):
        records = {}
        for record in self.records:
            if genre == record['data']['metadata']['genre']:
                records[record['data']['objectId']] = record
        return records

    def get_items_with_publication_year(self, year):
        # dateAccepted
        # dateCreated
        # dateModified
        # datePublishedInPrint
        # datePublishedOnline
        # dateSubmitted
        pass

    # get items from collection with given source genre
    def get_items_with_source_genre(self, source_genre):
        records = {}
        for record in self.records:
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    if source_genre == source['genre']:
                        records[record['data']['objectId']] = record
        return records

    def get_source_from_items_with_source_genre(self, source_genre):
        records = {}
        for record in self.records:
            if 'sources' in record['data']['metadata']:
                for source in record['data']['metadata']['sources']:
                    if source_genre == source['genre']:
                        records[record['data']['objectId']] = source
        return records

    # get items from collection with external url
    def get_items_with_external_url(self):
        records = {}
        for record in self.records:
            if 'files' in record['data']:
                for f in record['data']['files']:
                    if f['storage'] == 'EXTERNAL_URL':
                        records[record['data']['objectId']] = record
        return records

    # get items from collection with uri as identifier
    def get_items_with_identifier_uri(self):
        records = {}
        for record in self.records:
            if 'identifiers' in record['data']['metadata']:
                identifiers = record['data']['metadata']['identifiers']
                for idx in identifiers:
                    if idx['type'] == 'URI':
                        records[record['data']['objectId']] = record
        return records

    def save_titles(self):
        # titles = self.get_titles()
        pass
