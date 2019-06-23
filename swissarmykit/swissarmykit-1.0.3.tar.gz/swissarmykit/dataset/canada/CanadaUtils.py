

class CanadaUtils:

    def __init__(self):
        pass

    def get_all_state(self):
        ''' https://www.quora.com/How-many-states-are-there-in-Canada
        3 territories: Northwest Territories, Nunavut, Yukon '''
        print('Warning: There is no state in Canada. Use get_all_provinces instead')

        return self.get_all_provinces()

    def get_all_provinces(self):
        return ['Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador', 'Nova Scotia', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan']


if __name__ == '__main__':
    pass