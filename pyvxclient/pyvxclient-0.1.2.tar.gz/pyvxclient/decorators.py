import time
import logging
from bravado.exception import HTTPBadRequest, HTTPNotAcceptable
from pyvxclient.common import ApiResponse

log = logging.getLogger(__name__)

LIMIT = 1000


def handle_response(func):
    def call(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
            result = data.result
            return ApiResponse(data=result.get('data', None), message=result.get('message', None),
                               status_code=data.incoming_response.status_code)
        except (HTTPNotAcceptable, HTTPBadRequest) as e:
            log.error(e)
            # TODO: fixed vxctl version or there is anything better?
            msg = None
            if hasattr(e, 'swagger_result') and e.swagger_result and 'message' in e.swagger_result:
                msg = e.swagger_result['message']
            elif hasattr(e, 'response') and e.response and 'message' in e.response.json():
                msg = e.response.json()['message']
            return ApiResponse(message=msg, status_code=e.status_code)

    return call


def paginate(func):
    def call(*args, **kwargs):
        result = []
        wanted_result = kwargs.get('limit', LIMIT)
        if wanted_result >= LIMIT or wanted_result == 0:
            kwargs['limit'] = LIMIT  # force this limit of 1000

        i = 0
        # always send in page
        kwargs.setdefault('page', 1)
        start = time.time()
        while True:
            i += 1
            data = func(*args, **kwargs)
            result.extend(data.get('data'))

            # clean the result to match fields.
            # TODO: fixed vxctl version
            if 'fields' in kwargs and len(kwargs['fields']) >= 1:
                new_result = []
                log.debug("fields is set (%s), strip result from all other fields" % ",".join(kwargs['fields']))
                for row in result:
                    new_row = {}
                    for n in row.keys():
                        if n in kwargs['fields']:
                            new_row[n] = row[n]
                    if row != {}:
                        new_result.append(new_row)
                result = new_result

            items_left = (wanted_result - len(result)) if wanted_result != 0 else kwargs['limit']
            if items_left <= kwargs['limit']:
                kwargs['limit'] = items_left
            per_page = data.get('pagination').get('per_page')
            page = data.get('pagination').get('page')

            # if the result is zero or not a full page (known last page)
            if len(data.get('data')) == 0 or len(data.get('data')) < kwargs['limit']:
                break
            # if the wanted result is retrieved
            if wanted_result != 0 and ((per_page * page) >= wanted_result or len(result) == wanted_result):
                break
            else:
                kwargs["page"] += 1

        # create stats for output.
        data['data'] = result
        out = {
            "data": result,
            "pagination": data['pagination'],
            "stats": {
                "api_calls": i,
                "total_rows": len(result),
                "execution_time": time.time() - start
            }
        }
        return out

    return call
