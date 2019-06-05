from django.core.management.base import BaseCommand, CommandError
from matialvarezs_grafana_customers import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
import os



class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        data = {
            "name": settings.DATASOURCE_NAME,
            "type": "influxdb",
            "access": "proxy",
            # "url": settings.DATABASE_HOST + ":" + settings.DATABASE_PORT,
            "url": 'http://localhost:8086',
            # "host":settings.DATABASE_HOST,
            # "port":settings.DATABASE_PORT,
            "secureJsonData": {
                "password": "root"
            },
            "user": "root",
            "database": "create_siscorvac_influxdb_test",
            "jsonData": {
                "host": 'localhost',
                "port": 8086,
                "sslmode": "disable",
                "default": True
            },

        }
        # organisation = models.OrganisationGrafana.objects.get(object_project_id=1)
        url = settings.GRAFANA_API_BASE_URL + 'datasources'
        res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                            data=data,
                                                                            headers=settings.GRAFANA_API_HEADERS,
                                                                            convert_data_to_json=True)