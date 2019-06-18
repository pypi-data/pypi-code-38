from guillotina.utils import get_dotted_name
from guillotina_prometheus import metrics


class Handler:

    def __init__(self, app, handler):
        self.app = app
        self.handler = handler

    async def __call__(self, request):
        try:
            try:
                view_name = get_dotted_name(request.found_view.view_func)
            except AttributeError:
                view_name = get_dotted_name(request.found_view)
        except AttributeError:
            view_name = 'unknown'

        resp = await self.handler(request)

        metric = metrics.request_summary.labels(
            method=request.method,
            view=view_name,
            response_code=resp.status)

        try:
            metric.observe(request.events['finish'] - request.events['start'])
        except (AttributeError, KeyError):
            pass

        return resp


async def middleware_factory(app, handler):
    return Handler(app, handler)
