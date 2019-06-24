# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from oe_geoutils.utils import AdminGrenzenClient


def includeme(config):
    '''
    Include `oe_geoutils` in this `Pyramid` application.
    :param pyramid.config.Configurator config: A Pyramid configurator.
    '''

    config.registry.admin_grenzen_client = AdminGrenzenClient(
        config.registry.settings.get('administratievegrenzen.url'))

    config.add_route('home', pattern='/', request_method='GET', accept='text/html')
    config.add_route('nearest_address', pattern='/nearest_address', request_method='POST', accept='application/json')
    config.add_route('check_in_flanders', pattern='/check_in_flanders', request_method='POST',
                     accept='application/json')
    config.add_route('check_within_flanders', pattern='/check_within_flanders', request_method='POST',
                     accept='application/json')
    config.add_route('check_in_erfgoedgemeente', pattern='/check_in_erfgoedgemeente', request_method='POST',
                     accept='application/json')
    config.add_route('gemeente', pattern='/gemeente', request_method='POST', accept='application/json')
    config.add_route('provincie', pattern='/provincie', request_method='POST', accept='application/json')

    # Add crabpy_pyramid
    config.include('crabpy_pyramid')

    # Scanning the view package to load view_config objects
    config.scan('oe_geoutils.views')


def main(global_config, **settings):
    '''
     This function returns a Pyramid WSGI application.
    '''
    config = Configurator(settings=settings)

    includeme(config)

    return config.make_wsgi_app()
