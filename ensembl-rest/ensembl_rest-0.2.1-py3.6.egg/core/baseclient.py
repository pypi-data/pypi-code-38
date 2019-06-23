"""

This file is part of pyEnsembl.
    Copyright (C) 2018, Andrés García

    Any questions, comments or issues can be addressed to a.garcia230395@gmail.com.

"""

from .restclient import RESTClient, HTTPError


class BaseEnsemblRESTClient:
    """Base client for an Ensembl REST API."""
    
    def __init__(self, base_url=None):
        if base_url is None:
            base_url = self.base_url
            
        self.rest_client = RESTClient(base_url)
    # ----
        
    def make_request(self, resource, *args, params=None, headers=None, **kwargs):
        "Follow the route mapping the arguments to the correct place."
        # Assemble the request
        request_type, route_template = resource.split(' ')
        route = self._map_arguments(route_template, *args, **kwargs)
        
        endpoint = self.rest_client.route(*route)
        
        # Perform the request
        while True:
            try:
                return endpoint.do(request_type, params, headers=headers)

            # Handle rate limit
            except HTTPError as e:
                    if e.response.status_code == 429:
                        # Maximum requests rate exceded
                        # Need to wait
                        response = e.response
                        wait_time = float(response.headers["Retry-After"])
                        sys.stderr.write('Maximum requests limit reached, waiting for ' 
                                         + str(wait_time)
                                         + 'secs')
                        time.sleep(wait_time)
                    else:
                        raise
    # ---        
        
    def _map_arguments(self, route, *args, **kwargs):
        """Map the arguments to the template.
        
        The template is a string of the form:
        "some/:string/with/:semicolons"
        
        First maps the **kwargs, then maps the *args in order.
        If this fails throw an exception.
        
        """
        # First split into arguments: 
        # "some/:string/with/:semicolons" -> ['some', ':string', 'with', ':semicolons'] 
        parts = route.split('/')
        # Then replace the semicolons with format strings
        parts = ['{' + s[1:] + '}' if s.startswith(':') else s for s in parts]
        
        # Then map the keyword arguments
        parts = [self._format_if_possible(s, **kwargs) for s in parts]
        
        # Finally, map the positional arguments
        args_iter = iter(args)
        mapped_parts = []
        for s in parts:
            if s.startswith('{'):
                try:
                    mapped_parts.append(next(args_iter))
                except StopIteration:
                    # Parameter not provided, skip in case it is optional
                    pass
            else:
                mapped_parts.append(s)
        
        return mapped_parts
    # ---
           
    def _format_if_possible(self, format_string, **kwargs):
        """Try to apply the arguments to the format string.
        
        If not possible, return the string unchanged.
        """
        try:
            return format_string.format(**kwargs)
        except KeyError:
            return format_string
    # ---
    
# --- BaseClient




## Now are the factories for the automated creation of the classes
##  Y Y Y Y Y
##  | | | | |
##  v v v v v

def _endpoint_docstring(endpoint):
    return (
        f"``{endpoint['resource']}``\n\n"
        f"{endpoint['description']}\n"
        f"- More info: {endpoint['documentation_link']}"
    )
# ---

def _create_method(method_name, endpoint):
    """Create a class method"""
    
    def method(self, *args, **kwargs):
        return self.make_request(endpoint['resource'], *args, **kwargs)
    # ---
    
    method.__doc__ = _endpoint_docstring(endpoint)
    method.__name__ = method_name
    
    return method
# ---

def build_client_class(name, api_table, doc=''):
    """Create a new class that implements the methods of the API."""
    # Create the class dictionary
    class_dict = {'__doc__': doc,
                  'api_version': api_table['api_version'],
                  'base_url': api_table['base_url']}
    
    # Create the class methods
    methods = {ep_name : _create_method(ep_name, endpoint) 
               for ep_name, endpoint in api_table['endpoints'].items()}
    
    class_dict.update(methods)
    
    # Create the class (a subclass of the BaseEnsemblRESTClient)
    return type(name, (BaseEnsemblRESTClient,), class_dict)
# ---
