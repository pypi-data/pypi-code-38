import boto3
import pinkboto.cache
from pinkboto.utils import path, unpack, flat, field_comparison


class aws(object):
    def __init__(self, profile=None, region=None, cache=120):
        """
        Create connection.
        :param profile: AWS profile
        :param region: AWS region
        :param cache: Cache usage
        """
        self.profile = profile
        self.region = region
        self.session = boto3.Session(profile_name=profile, region_name=region)

        import os
        self.__package_folder__, _ = os.path.split(__file__)

        resources_file = os.path.join(self.__package_folder__, 'resources.yml')

        import yaml
        self.resources = yaml.load(open(resources_file, "r"), Loader=yaml.FullLoader)

        self.cache = pinkboto.cache.Cache(lifetime=cache)

    # def client(self, resource):
    #     if 'client' in resource:
    #         return self.session.client(resource['client'])
    #     elif 'resource' in resource:
    #         return self.session.resource(resource['resource'])

    def pagination(self, params):
        """
        Make all pagination requests and return results
        :param params: query params
        :return: results
        """
        from copy import deepcopy
        method_params = deepcopy(params)
        resource = self.resources[method_params['resource']]
        if 'property' in resource['list']:
            list_property = resource['list']['property']
        else:
            # caso não houver list_property, não haverá paginação
            list_property = ''

        del method_params['resource']
        del method_params['profile']
        del method_params['region']

        client = self.session.client(resource['client'])
        method = getattr(client, resource['list']['method'])
        step = method(**method_params)
        results = path(list_property, step)
        results = unpack(results)
        results = flat(results)

        if 'pagination_field' in resource['list']:
            pagin_field = resource['list']['pagination_field']
            pagin_method_param = resource['list']['pagination_method_parameter']

            while len(path(list_property, step)) > 0 and pagin_field in step:
                kwargs = {
                    pagin_method_param: step[pagin_field]}
                kwargs.update(method_params)
                step = method(**kwargs)
                results += path(list_property, step)

        return results

    def find(self, query=None, projection=None):
        """
        Selects objects in a schema.
        :param query: Optional. Specifies selection filter. To return all
          objects in a schema, omit this parameter or pass an empty object ({}).
        :param projection: Optional. Specifies the fields to return in the
          objects that match the query filter.
          To return all fields in the matching objects, omit this parameter.
        :return:
        """
        from copy import deepcopy
        query = deepcopy(query)
        query = query if query else {}
        if not isinstance(query, dict):
            query = {"resource": query}

        projection = projection if projection else []
        if not isinstance(projection, list):
            raise TypeError("Projection must be a list")

        if 'resource' not in query:
            raise KeyError('query must have "resource" field')

        resource = self.resources[query['resource']]

        if 'parameters' in resource['list']:
            parameters = resource['list']['parameters']
            method_params = dict([(k, v) for k, v in query.items()
                                  if k in parameters])
            for m in method_params:
                del query[m]
        else:
            method_params = {}

        method_params['resource'] = query['resource']
        method_params['profile'] = self.profile
        method_params['region'] = self.region
        del query['resource']

        results = self.cache.caching(self.pagination, method_params)

        if not isinstance(results, list):
            results = [results]

        for k, v in query.items():
            results = [
                result for result in results
                if field_comparison(path(k, result), v) or (
                    isinstance(path(k, result), list) and v in path(k, result)
                )
             ]

        if projection:
            if len(projection) > 1:
                output = [{k: path(k, obj) for k in projection}
                    for obj in results]

            else:
                output = [path(k, obj) for k in projection
                          for obj in results]
        else:
            output = results

        return output

    def insert(self, objs, workers=10):
        """
        Inserts a object or objects into a schema.
        :param objs: A object or list of objects to insert into the schema.
        :param workers: Optional. If set to greater than 1, creates objects in
          parallel requests. default is serial(1).
        :return: inserted objects.
        """

        pass

        # if not (isinstance(objs, dict) or isinstance(objs, list)):
        #     raise TypeError("Query must be a object or list of objects")
        # objs = objs if isinstance(objs, list) else [objs]
        #
        # process output
        #
        #
        # return output

    def update(self, query, update, upsert=False, multi=False):
        """
        Modifies an existing object or objects in a schema. The method can
          modify specific fields of an existing object or objects or replace an
          existing object entirely, depending on the update parameter.

        By default, the update() method updates a single object. Set the Multi
          Parameter to update all objects that match the query criteria.

        Update() method can insert a object when query criteria not returns data
          if upsert property is True.

        :param query: The selection criteria for the update.
        :param update: The modifications to apply.
        :param upsert: Optional. If set to true, creates a new object when no
        object matches the query criteria.
          The default value is false, which does not insert a new object when
        no match is found.
        :param multi: Optional. If set to true, updates multiple objs that meet
          the query criteria.
          If set to false, updates one object. The default value is false.
        :return: List of Elements
        """
        # query = query if query else {}
        # if not isinstance(query, dict):
        #     raise TypeError("Query must be a dict")
        #
        # update = update if update else {}
        # if not isinstance(update, dict):
        #     raise TypeError("Query must be a dict")

        pass

    def remove(self, query):
        """

        :param query: Specifies deletion criteria. To delete all objects in a
        schema, pass an empty object ({}).
        :return:
        """

        query = query if query else {}
        if not isinstance(query, dict):
            raise TypeError("Query must be a dict")

        # Define o método de deleção no recurso
        resource = self.resources[query['resource']]
        if 'delete' not in resource or 'method' not in resource['delete']:
            raise KeyError('Delete method is not defined for resource')
        client = self.session.client(resource['client'])

        objs = self.find(query)

        resource_method = None
        if 'resource' in resource and 'method' in resource['resource']:
            resource_client = self.session.resource(resource['client'])
            resource_method = getattr(resource_client, resource['resource']['method'])

        result = []
        for obj in objs:
            key = obj[resource['list']['key']]
            if resource_method:
                delete_method = getattr(resource_method(key), resource['delete']['method'])
            else:
                delete_method = getattr(client, resource['delete']['method'])

            if 'parameter' in resource['delete']:
                result += [delete_method(resource['delete']['parameter'])]
            else:
                result += [delete_method()]

        result = [y for x in result for y in x]  # flat
        return result

    def sync(self, objs, keys=None, workers=10):
        """

        :param objs: A object or list of objects to insert into the schema
        :param keys:  Specifies a filter key list from object.
        :param workers: Optional. If set to greater than 1, creates objects in
        parallel requests. If is 1 is serial.
            default is 10.
        :return:
        """

        if not keys:
            keys = ['name']

        if not (isinstance(objs, list)):
           objs = [objs]

        # def step(obj):
        #     query = dict([(field, obj[field]) for field in obj if field in keys])
        #     return self.update(query, obj, upsert=True, multi=False)
        #
        # results = tmap(step, objs, workers=workers)
        # output = [item for result in results if result for item in result]
        #

        # return output

        pass


