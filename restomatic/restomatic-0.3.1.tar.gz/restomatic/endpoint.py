from .shared_exceptions import StatusMessageException


class RestOMaticBadRequest(StatusMessageException):
    def __init__(self, message, status_code=None, additional_information=None):
        StatusMessageException.__init__(self, message, status_code, additional_information)


def detect_id_from_request(request, table_name):
    remaining_uri = request['uri']['path'].lstrip('/')
    if remaining_uri.startswith(table_name):
        remaining_uri = remaining_uri[len(table_name):].lstrip('/')

    requested_id = None

    if remaining_uri:
        if remaining_uri in ['where', 'search']:
            return remaining_uri

        try:
            requested_id = int(remaining_uri)
        except (ValueError, TypeError):
            requested_id = -1

        if requested_id < 1:
            raise RestOMaticBadRequest('Invalid ID, must be a positive integer, 1 or greater')

    return requested_id


# Supports: GET /example -> for all (if allow_all set to true in parameters)
# Or GET /example/1 -> for just 1
# Use POST to search
def restomatic_get(request, db, table_name, **parameters):
    requested_id = detect_id_from_request(request, table_name)

    if not parameters.get('allow_all') and not requested_id:
        raise RestOMaticBadRequest('Must specify an ID for this GET request')

    query = db.select_all(table_name)

    if requested_id:
        query = query.where(('id', 'eq', requested_id))

    result = query.one_or_none_mapped()
    if result:
        return result
    else:
        return {'message': 'Requested ID not found'}, 404


def perform_post(db, table_name, body):
    if not body or not isinstance(body, dict):
        raise RestOMaticBadRequest('Must specify a valid JSON object (dictionary) of columns to set for the new row')

    result = db.insert_mapped(table_name, body, autorun=True)

    return result.lastrowid()


def restomatic_post(request, db, table_name, **parameters):
    where_parameters = determine_where_parameters(request, table_name, 'POST', search_only=True)

    if where_parameters:
        body = request['body']

        query = db.select_all(table_name).where(where_parameters)

        if 'limit' in body:
            query = query.limit(body['limit'])

        if 'offset' in body:
            query = query.offset(body['offset'])

        if 'order_by' in body:
            query = query.order_by(body['order_by'])

        results = query.all_mapped()

        if results:
            return {'results': results}
        else:
            return {'results': None}

    body = request['body']

    if not body:
        raise RestOMaticBadRequest('Must specify a valid JSON object (dictionary) of columns to set for the new row')

    if isinstance(body, list):
        ids = []
        for b in body:
            ids.append(perform_post(db, table_name, b))

        db.commit()

        return {'success': True, 'ids': ids}, 201

    new_id = perform_post(db, table_name, body)

    db.commit()

    return {'success': True, 'id': new_id}, 201


def perform_put(db, table_name, body):
    if not body or not isinstance(body, dict):
        raise RestOMaticBadRequest('Must specify a valid JSON object (dictionary) of columns to set or update')

    if 'id' in body:
        update_id = body['id']
        del body['id']
        return db.update_mapped(table_name, body).where(('id', 'eq', update_id)).run()

    return db.insert_mapped(table_name, body, autorun=True)


def restomatic_put(request, db, table_name, **parameters):
    if detect_id_from_request(request, table_name):
        raise RestOMaticBadRequest('Cannot specify an ID for a PUT request - '
                                   'all IDs must be specified in the provided JSON objects, '
                                   'or use PATCH to update one object by ID')

    body = request['body']

    if not body:
        raise RestOMaticBadRequest('Must specify a valid JSON object (dictionary) of columns to set or update')

    if not isinstance(body, list):
        body = [body]

    for b in body:
        perform_put(db, table_name, b)

    db.commit()

    return {'success': True}


def restomatic_patch(request, db, table_name, **parameters):
    where_parameters, set_values = determine_where_parameters(request, table_name, 'PATCH', set_required=True)

    db.update_mapped(table_name, set_values).where(where_parameters).run()

    db.commit()

    return {'success': True}


def restomatic_delete(request, db, table_name, **parameters):
    where_parameters = determine_where_parameters(request, table_name, 'DELETE')

    db.delete(table_name).where(where_parameters).run()

    db.commit()

    return {'success': True}


def determine_where_parameters(request, table_name, request_type, search_only=False, set_required=False):
    requested_id = detect_id_from_request(request, table_name)

    if not requested_id and not search_only:
        raise RestOMaticBadRequest(f'Must specify an ID for a {request_type} request')

    body = request['body']

    if requested_id in ('where', 'search'):
        if not body or not isinstance(body, dict) or not body.get('where'):
            raise RestOMaticBadRequest('Must specify a valid JSON object (dictionary) with a valid where parameter list')

        where_parameters = body['where']

        if set_required:
            if 'set' not in body:
                raise RestOMaticBadRequest('Must specify a set JSON object (dictionary) with the columns to be set')
            return where_parameters, body['set']

        if 'set' in body:
            raise RestOMaticBadRequest('The set JSON object is not valid for this request (did you mean PATCH?)')

        return where_parameters

    elif search_only:
        if requested_id:
            raise RestOMaticBadRequest(f'Cannot specify an ID for a {request_type} request')
        return None

    where_parameters = ('id', 'eq', requested_id)

    if set_required:
        if not body or not isinstance(body, dict):
            raise RestOMaticBadRequest('Must specify a valid JSON object (dictionary) of columns to set for this ID')

        return where_parameters, body

    return where_parameters


def generate_rom_get(db, table_name, **parameters):
    def rom_get_wrapper(request):
        return restomatic_get(request, db, table_name, **parameters)

    return rom_get_wrapper


def generate_rom_post(db, table_name, **parameters):
    def rom_post_wrapper(request):
        return restomatic_post(request, db, table_name, **parameters)

    return rom_post_wrapper


def generate_rom_put(db, table_name, **parameters):
    def rom_put_wrapper(request):
        return restomatic_put(request, db, table_name, **parameters)

    return rom_put_wrapper


def generate_rom_patch(db, table_name, **parameters):
    def rom_patch_wrapper(request):
        return restomatic_patch(request, db, table_name, **parameters)

    return rom_patch_wrapper


def generate_rom_delete(db, table_name, **parameters):
    def rom_delete_wrapper(request):
        return restomatic_delete(request, db, table_name, **parameters)

    return rom_delete_wrapper


def register_restomatic_endpoint(endpoint_router, db, table_name, allowed_methods, **parameters):
    if not db.is_valid_table(table_name):
        raise RuntimeError(f'Unknown table: {table_name}')

    # Note that all operations are always done in one transation
    for method in allowed_methods:
        method = method.upper()
        if method == 'GET':
            # GET one: /table/1 (returns 200 if found, 404 if no match)
            endpoint_router.register_endpoint(in_format='json', out_format='json', prefix=f'/{table_name}', method=method,
                                              func=generate_rom_get(db, table_name, **parameters))
        elif method == 'POST':
            # This endpoint creates a new row (or multiple new rows) (returns 201)
            # Also supports a get-like search (but without the limits on uri size/format)
            # POST one: /table
            #   body: {...}
            # or POST many: /table
            #   body: [{...}, {...}]
            # or POST-based search: /table/search (returns 200 with a list of results if found, otherwise None)
            #   body: {'where': [...search criteria...]}
            endpoint_router.register_endpoint(in_format='json', out_format='json', prefix=f'/{table_name}', method=method,
                                              func=generate_rom_post(db, table_name, **parameters))
        elif method == 'PUT':
            # This endpoint can create or update the given rows (returns 200)
            # PUT one: /table
            #   body: {...} (if ID specified, update, otherwise create)
            # or PUT many: /table
            #   body: [{...}, {...}] (if ID specified, update, otherwise create)
            endpoint_router.register_endpoint(in_format='json', out_format='json', prefix=f'/{table_name}', method=method,
                                              func=generate_rom_put(db, table_name, **parameters))
        elif method == 'PATCH':
            # This endpoint updates the given row or based on the given where condition (returns 200)
            # PATCH one: /table/1
            #   body: {...}
            # or PATCH many: /table/where
            #   body: {'where': [...search criteria...], 'set': {...}}
            endpoint_router.register_endpoint(in_format='json', out_format='json', prefix=f'/{table_name}', method=method,
                                              func=generate_rom_patch(db, table_name, **parameters))
        elif method == 'DELETE':
            # This endpoint deletes the given row or based on the given where condition (returns 200)
            # DELETE one: /table/1
            # or DELETE many: /table/where
            #   body: {'where': [...search criteria...]}
            endpoint_router.register_endpoint(in_format='json', out_format='json', prefix=f'/{table_name}', method=method,
                                              func=generate_rom_delete(db, table_name, **parameters))
        else:
            raise RuntimeError(f'Method {method} not supported!')
