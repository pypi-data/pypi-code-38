from guillotina import configure
from guillotina.interfaces import IApplication

import prometheus_client


@configure.service(method='GET', name='metrics', context=IApplication,
                   permission='guillotina.AccessContent')
async def get_stats(context, request):
    output = prometheus_client.exposition.generate_latest()
    return output.decode('utf8')
