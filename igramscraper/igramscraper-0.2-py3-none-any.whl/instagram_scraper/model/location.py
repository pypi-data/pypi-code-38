from .initializer_model import InitializerModel
import textwrap

class Location(InitializerModel):

    def __str__(self):
        string = f'''
        Location info:
        Id: {self.identifier}
        Name: {self.name}
        Latitude: {self.lat}
        Longitude: {self.lng}
        Slug: {self.slug}
        Is public page available: {self.has_public_page}
        '''

        return textwrap.dedent(string)

    def _init_properties_custom(self, value, prop, arr):

        if prop == 'id':
            self.identifier = value

        standart_properties = [
            'has_public_page',
            'name',
            'slug',
            'lat',
            'lng',
            'modified',
        ]

        if prop in standart_properties:
            self.__setattr__(prop, value)
